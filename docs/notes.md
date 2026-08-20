# Notes

* **Note to self:** I want this implementation to keep the mathematical assumptions behind the Bloom filter. I don't want to treat the formulas like random constants that just happen to work.

---

# 1. Initial API Design

The public constructor should ask for:

```python
BloomFilter(capacity, error_rate)
```

The user knows approximately how many items they expect to insert and what false-positive rate they can tolerate.

The library can then work out the implementation details, like:

* how many bits are needed
* how many hash functions to use

The user shouldn't have to worry about those details.

---

# 2. Bit Representation

## Decision: Python `int`

One idea was to use a Python `set` and store the positions of all the bits that are `1`.

But a Bloom filter is supposed to be space-efficient. Using a large Python set would use quite a lot of memory, which goes against the point of using a Bloom filter.

So, for now, represent the whole bit array using a Python `int`.

For example:

```text
bits = 0
```

In binary:

```text
00000000
```

Now suppose we want bit `3` to become `1`.

We can create a mask with:

```python
1 << 3
```

which gives:

```text
00001000
```

Then we do:

```text
00000000
OR
00001000
---------
00001000
```

This is what `_set_bit()` is doing:

To check if a bit is set, we can use the same idea.

Suppose:

```python
self.bits = 00001000
```

and we want to check bit `3`.

We create the same mask:

```text
00001000
```

Then:

```text
00001000
AND
00001000
---------
00001000
```

The result is not zero, so the bit is set.

That's why this works:

```python
bool(self.bits & (1 << index))
```

It returns:

```text
True
```

If we check bit `2` instead:

```text
00001000
AND
00000100
---------
00000000
```

The result is zero, so:

```python
bool(...)
```

returns:

```text
False
```

The important thing here is that setting a bit only turns a `0` into a `1`. It never changes an existing `1` back to `0`.

---

# 3. Bit Array Size

The Bloom filter needs to determine how many bits it should allocate based on:

* `n` — the expected number of items
* `p` — the false-positive probability we want
* `m` — the number of bits

The formula is:

$$m = -\frac{n \ln(p)}{(\ln 2)^2}$$

For example:

```python
import math

n = 100
p = 0.01

m = -(n * math.log(p)) / (math.log(2) ** 2)
```

If:

```text
capacity = 100
error_rate = 0.01
```

we get approximately:

```text
958.5058 bits
```

Obviously, we can't have half a bit, so we need to round up:

```text
959 bits
```

So I think `ceil()` is the right choice here.

Rounding down would give fewer bits than the formula says it's need, which could make the false-positive rate worse than the requested rate.

---

# 4. Number of Hash Functions

The number of bit positions each inserted element sets is represented by `k` in the modern notation and `d` in Bloom's paper.

The optimal value is approximately:

$$k = \frac{m}{n}\ln 2$$

For:

```text
m = 959
n = 100
```

we get:

```text
k ≈ 6.647
```

But obviously, we can't have `6.647` hash functions.

So the question is:

**Should I round up or down?**

I checked the two closest values using the false-positive approximation:

$$p \approx (1-e^{-kn/m})^k$$

```python
import math

m = 959
n = 100

for k in [6, 7]:
    p = (1 - math.exp(-(k * n) / m)) ** k
    print(k, p)
```

This gives:

```text
k = 6 → 0.0101206
k = 7 → 0.0100147
```

So, `7` gives a slightly lower false-positive probability than `6`.

**Is using `floor()` the right thing to do?.**

---

# 5. Generating the Hash Positions

The basic idea is:

$$h_i = (h_1 + i \cdot h_2) \pmod m$$

Here:

* `h1` is the first hash value
* `h2` is the second hash value
* `i` is the position we are generating
* `m` is the size of the bit array

For example, if:

```text
m = 959
h1 = 421
h2 = 73
k = 7
```

then we can generate:

```text
i = 0 → (421 + 0 × 73) % 959
i = 1 → (421 + 1 × 73) % 959
i = 2 → (421 + 2 × 73) % 959
i = 3 → (421 + 3 × 73) % 959
...
```

This gives us the different bit positions we need.

The `% m` part is important because it keeps the position inside the bit array.

---

# 6. Double Hashing

At first, I thought I might need to calculate `k` separate hashes for every item.

For example, if:

```text
k = 7
```

we could calculate:

```text
hash1("alice")
hash2("alice")
hash3("alice")
...
hash7("alice")
```

But doing seven separate expensive hash calculations for every item isn't necessary.

Instead, we can use **double hashing**.

The idea is to calculate two hash values:

```text
h1 = hash1("alice")
h2 = hash2("alice")
```

and then use them to generate the other positions:

$$h_i = (h_1 + i \cdot h_2) \pmod m$$

So instead of calculating seven independent hashes, we calculate two values and derive the seven positions from them.

For example:

```text
i = 0 → h1
i = 1 → h1 + h2
i = 2 → h1 + 2h2
i = 3 → h1 + 3h2
...
```

and `% m` keeps each result inside the bit array.

---

# 7. Hashing Strategy

I need to separate the **Bloom filter mathematics** from the **specific hashing implementation**.

The mathematical model says that each item needs `k` hash positions.

Double hashing is the implementation technique I am using to generate those positions efficiently.

For my implementation, I am using SHA-256:

```python
digest = hashlib.sha256(item.encode()).digest()
```

SHA-256 gives me 32 bytes.

I can split those bytes into two 16-byte values:

```python
h1 = int.from_bytes(digest[:16]) # first hash
h2 = int.from_bytes(digest[16:]) # second hash
```

So I am getting two large integer values from the same SHA-256 digest.

Then I can generate the positions:

```python
positions = []

for i in range(self.hash_count):
    position = (h1 + i * h2) % self.bit_array_size
    positions.append(position)

# for i in range(3):
#      hi = (h1 + i * h2) % m
#      print(hi)
```

Note: I am **not** claiming that the original Bloom filter paper specifically says to use SHA-256 this way.

The Bloom filter mathematics says that we need multiple hash positions.

Double hashing gives a way to generate those positions efficiently.

Using SHA-256 and splitting the digest into `h1` and `h2` is my implementation choice.


# 8. Adding and Checking Items

Once `_hashes()` gives us the positions for an item, `add()` simply sets each of those positions to `1`.

For example, if:

```text
_hashes("alice")
→ [250, 264, 278, 292, 306, 320, 334]
```

then:

```python
for position in positions:
    self._set_bit(position)
```

sets all seven positions.

The important property is that adding an item only changes bits from `0` to `1`.

It never removes information from the filter.

---

## Checking an Item

`contains()` generates the same positions again and checks each one.

If even one position is `0`, the item is **definitely not present**.

Why?

Because if the item had previously been added, its corresponding bit would have been set to `1`.

If all the positions are `1`, the result is **maybe present**.

We cannot say the item is definitely present because other inserted items may have set the same bits.

Therefore:

```text
contains(item) == False
→ definitely not present

contains(item) == True
→ maybe present
```

This is the fundamental guarantee of the Bloom filter.

A false positive is possible, but a false negative should not be possible if the filter is used correctly.

---

# 9. Input Type
- For this first version , BloomFilter accepts strings (keeping it simple)

# 10. Capacity and Saturation
Capacity determines how much data the Bloom filter is designed to hold. Query count determines how many observations we make of its false-positive behavior.

If we insert 20,000 items into a filter designed for 10,000, the false-positive rate will go up

- Increasing k sets more bits per item.
- Increasing n adds more items.
- Both increase the number of 1s.
- Too many 1s → false positives increase.

When we say:

```python
BloomFilter(10_000, 0.01)
```
we're essentially saying:

"Design the filter's space and hash count under the assumption that approximately 10,000 items will be inserted while targeting a 1% false-positive probability."

A Bloom filter doesn't become "full" because it runs out of storage like a list or database table. It becomes less useful as its bits become saturated, because the probability of false positives increases.

That's why capacity is meaningful.

- fewer inserted items → lower false-positive rate
- more inserted items → higher false-positive rate

# 11. Experiment
**Experiment: changing the number of inserted items**

I kept the capacity and target error rate fixed and changed the number of inserted items. I observed that the fewer the inserted items, the lower the false positive rate, and the more inserted items, the higher the false positive rate

**Experiment: changing the target error rate**

I kept the capacity and number of inserted items fixed and changed the target error rate. I observed that the bit_array_size decrease, hash_count decrease, and the positive rate is lower

Additionally, The false-positive probability of the filter doesn't change because we perform more queries. Instead, increasing the number of queries gives us a larger sample, so our observed rate becomes a more stable estimate of the theoretical probability.
