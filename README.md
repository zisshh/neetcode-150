# NeetCode 150 — my C++ practice harness

This is how I grind the [NeetCode 150](neeetcode-150.md) in C++. I wrote a small
toolchain that scrapes a problem into a local folder so I can solve it offline,
test it against the examples on my own machine, and only then upload it to the
website. **No AI, no hints — I solve every problem myself.** The scripts just
remove the boring parts (copying the problem text, wiring up a compiler).

## My process for one problem

```bash
# 1. fetch the problem
./new contains-duplicate
#    or paste the full URL:  ./new https://leetcode.com/problems/contains-duplicate/

# 2. read the description, solve, write tests  (details below)

# 3. run my tests locally until they pass
./run 0217-contains-duplicate

# 4. green? -> paste solution.cpp into LeetCode/NeetCode myself
```

### Step 1 — `./new <slug>` fetches the problem

`./new` takes a LeetCode **slug** (the `leetcode.com/problems/<slug>/` part, always
hyphenated, e.g. `contains-duplicate`) or the full URL. It hits LeetCode's public
GraphQL API and scaffolds a folder named `NNNN-slug/` containing:

| file          | what it is                                                             |
|---------------|------------------------------------------------------------------------|
| `README.md`   | the scraped problem — description, constraints, examples, raw test data |
| `solution.cpp`| an **empty signature stub** of the exact function I have to implement   |

It does **not** write tests for me — that's the point, I want to think about the
cases myself.

### Step 2 — solve it

1. Read `NNNN-slug/README.md` — the full problem, scraped from LeetCode.
2. Write my solution inside `NNNN-slug/solution.cpp` (fill in the empty stub).
3. Write `NNNN-slug/tests.cpp` by hand — turn the examples into `CHECK(...)`
   assertions. See **[TESTING_GUIDE.md](TESTING_GUIDE.md)** for the skeleton and
   the doctest macros.

### Step 3 — `./run <folder>` compiles + tests locally

`./run 0217-contains-duplicate` compiles `tests.cpp` + `solution.cpp` together with
the header-only [doctest](https://github.com/doctest/doctest) framework
(`clang++ -std=c++20`) and runs the resulting binary. Output looks like:

```
[doctest] test cases: 2 | 2 passed | 0 failed | 0 skipped
[doctest] assertions: 4 | 4 passed | 0 failed |
[doctest] Status: SUCCESS!
```

`Status: SUCCESS!` + `0 failed` = every example I wrote passes. If something
breaks, doctest prints the exact `CHECK` line, what I expected, and what my code
actually returned — so I know precisely which case is wrong before I touch the
website.

### Step 4 — upload

Once it's green locally, I paste `solution.cpp` into the site and submit it myself.

## What's tracked in this repo

Only problems I've **actually solved** get committed. Unsolved stub folders stay
local and untracked until I finish them.

## Layout

```
new              ./new <url-or-slug>   scaffold a problem folder
run              ./run <folder>        compile tests.cpp + run
lib/doctest.h    header-only test framework (no install, no linking)
tools/fetch.py   LeetCode GraphQL fetch + scaffold generator
TESTING_GUIDE.md how I write tests.cpp by hand
neeetcode-150.md the 150 checklist, section by section
NNNN-slug/       one folder per solved problem
```

## Notes

- Fetch uses LeetCode's public GraphQL API — works for free problems, no login.
- `solution.cpp` is `#include`d directly by `tests.cpp` (it's `#pragma once`), so
  `Solution` is available in tests with no extra wiring. Remember `Solution sol;`
  first — `Solution` is a class, call methods on an instance.
- Compiler defaults to `clang++ -std=c++20`. Override: `CXX=g++ ./run <folder>`.
- `./new` refuses to overwrite an existing folder — move it aside first to refetch.
