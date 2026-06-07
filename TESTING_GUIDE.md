# How to write `tests.cpp` (doctest)

`./new <slug>` creates `README.md` + `solution.cpp` only. **You write `tests.cpp`
yourself** in the problem folder. This guide is the reference. Then `./run <folder>`
compiles and runs it.

---

## 1. The skeleton every `tests.cpp` starts with

Create `tests.cpp` inside the problem folder (e.g. `0001-two-sum/tests.cpp`):

```cpp
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "../lib/doctest.h"
#include "solution.cpp"

TEST_CASE("two sum") {
    // your assertions go here
}
```

What each line does:

| Line | Why |
|------|-----|
| `#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN` | tells doctest to generate `int main()` for you. Put it in **exactly one** file (this one). |
| `#include "../lib/doctest.h"` | the whole framework — one header, no install. |
| `#include "solution.cpp"` | pastes your `Solution` class in, so tests can call it. (`solution.cpp` is `#pragma once`, safe to include.) |
| `TEST_CASE("name") { ... }` | one test. Auto-registers itself; `main` runs every `TEST_CASE` it finds. |

---

## 2. Assertions

```cpp
CHECK(expr);                 // expr should be true; if false, log + KEEP GOING
REQUIRE(expr);               // same, but STOP this test case on failure
CHECK(actual == expected);   // the usual form
```

- Use **`CHECK`** by default — you see all failures in one run.
- Use **`REQUIRE`** when continuing would crash, e.g. after checking a pointer
  isn't null, or a vector isn't empty, before you index into it.

---

## 3. Turning a LeetCode example into a test

`README.md` (bottom, "For your tests") gives you the signature and the raw inputs.

**Example — Two Sum.** Signature: `vector<int> Solution::twoSum(vector<int>& nums, int target)`
Example: `nums = [2,7,11,15], target = 9` → `[0,1]`.

```cpp
TEST_CASE("two sum") {
    vector<int> nums{2, 7, 11, 15};                 // (A) build the input
    CHECK(Solution().twoSum(nums, 9) == vector<int>{0, 1});   // (B) call + compare
}
```

- **`Solution()`** makes a temporary object, then `.twoSum(...)` calls the method.
- `nums` is taken **by reference** (`vector<int>&`), so it must be a **named
  variable** — you can't pass `{2,7,11,15}` literally to a `&` parameter.

You can put many `CHECK`s in one `TEST_CASE`, or split into several cases:

```cpp
TEST_CASE("two sum - examples") {
    vector<int> a{2,7,11,15};  CHECK(Solution().twoSum(a, 9) == vector<int>{0,1});
    vector<int> b{3,2,4};      CHECK(Solution().twoSum(b, 6) == vector<int>{1,2});
    vector<int> c{3,3};        CHECK(Solution().twoSum(c, 6) == vector<int>{0,1});
}

TEST_CASE("two sum - edge cases") {   // your own cases, not just the examples
    vector<int> d{-1,-2,-3,-4};  CHECK(Solution().twoSum(d, -7) == vector<int>{2,3});
}
```

---

## 4. Common input/output shapes

| Problem gives you | Build it like |
|-------------------|---------------|
| array `[1,2,3]` | `vector<int> v{1,2,3};` |
| string `"abc"` | `string s = "abc";` |
| 2D grid `[[1,2],[3,4]]` | `vector<vector<int>> g{{1,2},{3,4}};` |
| single int | pass `9` directly |
| bool result | `CHECK(Solution().isValid(s) == true);` |

**Order-independent results** (problem says "in any order"): sort both sides first.

```cpp
auto got = Solution().twoSum(nums, 9);
sort(got.begin(), got.end());
CHECK(got == vector<int>{0, 1});
```

**Floating-point results**: don't compare with `==`, use a tolerance.

```cpp
CHECK(Solution().myPow(2.0, 10) == doctest::Approx(1024.0));
```

---

## 5. Run it

```bash
./run 0001-two-sum
```

- All pass → `Status: SUCCESS!`, exit 0 → paste `solution.cpp` into the website.
- A `CHECK` fails → doctest prints the file:line and the expression. Fix and rerun.
- Compiler error → fix the C++ first (the error points at the line).

> Note: doctest prints `{?}` instead of the actual values for `vector`/custom types
> on a failed compare (it doesn't know how to print them). The pass/fail is still
> correct — to see real values, `cout` them, or add a small `operator<<` printer.

---

## 6. doctest macro quick reference

```cpp
TEST_CASE("name") { ... }              // a test
SUBCASE("part") { ... }                // optional: sub-sections within a case
CHECK(x == y);                         // soft assert
REQUIRE(x == y);                       // hard assert (stops case)
CHECK_FALSE(expr);                     // expr should be false
CHECK(v == doctest::Approx(1.5));      // float compare with tolerance
WARN(expr);                            // logs if false, never fails the run
```

That's everything you need for NeetCode 150.
