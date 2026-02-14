# Benchmark Report

**Quiz:** Week 14: React Testing Library — Rendering, Queries, and user-event

## Summary

| Rank | Config | Accuracy | Correct | Time | Per-Q |
|------|--------|----------|---------|------|-------|
| 1 | quick / rag / grounded | 93.8% | 30/32 | 176.0s | 5.5s |
| 2 | quick / rag / broad | 93.8% | 30/32 | 172.1s | 5.4s |
| 3 | deep / rag / grounded | 90.6% | 29/32 | 370.3s | 11.6s |
| 4 | deep / rag / broad | 90.6% | 29/32 | 363.4s | 11.4s |
| 5 | quick / no-rag / broad | 87.5% | 28/32 | 124.5s | 3.9s |
| 6 | deep / no-rag / broad | 81.2% | 26/32 | 256.9s | 8.0s |
| 7 | fast / rag / grounded | 75.0% | 24/32 | 195.7s | 6.1s |
| 8 | fast / rag / broad | 75.0% | 24/32 | 192.1s | 6.0s |
| 9 | general / rag / grounded | 68.8% | 22/32 | 181.1s | 5.7s |
| 10 | general / rag / broad | 68.8% | 22/32 | 177.1s | 5.5s |
| 11 | fast / no-rag / broad | 59.4% | 19/32 | 136.0s | 4.3s |
| 12 | general / no-rag / broad | 50.0% | 16/32 | 112.8s | 3.5s |

---

## Per-Question Breakdown

| Question | quick / rag / grounded | quick / rag / broad | deep / rag / grounded | deep / rag / broad | quick / no-rag / broad | deep / no-rag / broad | fast / rag / grounded | fast / rag / broad | general / rag / grounded | general / rag / broad | fast / no-rag / broad | general / no-rag / broad |
|----------|------|------|------|------|------|------|------|------|------|------|------|------|
| MC-1 | + | + | + | + | + | + | + | + | + | + | + | + |
| MC-2 | + | + | + | + | + | + | x (a) | x (a) | + | + | x (a) | + |
| MC-3 | + | + | + | + | + | + | + | + | x (a) | x (a) | + | x (a) |
| MC-4 | + | + | + | + | + | + | + | + | x (a) | x (a) | + | + |
| MC-5 | + | + | + | + | + | + | x (b) | x (b) | + | + | x (b) | + |
| MC-6 | x (c) | x (c) | + | + | + | + | x (c) | x (c) | x (c) | x (c) | x (c) | x (d) |
| MC-7 | + | + | x (a) | x (a) | + | x (d) | x (d) | x (d) | x (a) | x (a) | + | x (d) |
| MC-8 | + | + | + | + | x (a) | x (b) | + | + | + | + | x (a) | x (d) |
| MC-9 | + | + | + | + | + | + | + | + | + | + | x (a) | x (d) |
| MC-10 | + | + | + | + | x (a) | x (a) | x (a) | x (a) | + | + | x (a) | x (d) |
| MC-11 | + | + | + | + | + | + | + | + | + | + | + | x (a) |
| MC-12 | + | + | + | + | + | x (b) | + | + | x (b) | x (b) | + | x (b) |
| MC-13 | + | + | + | + | + | + | + | + | + | + | + | x (d) |
| MC-14 | + | + | + | + | x (a) | x (a) | x (a) | x (a) | x (a) | x (a) | x (a) | x (d) |
| MC-15 | + | + | + | + | + | + | + | + | + | + | + | + |
| MC-16 | + | + | + | + | + | + | + | + | + | + | x (a) | + |
| MC-17 | + | + | + | + | + | + | + | + | + | + | + | + |
| MC-18 | + | + | + | + | + | + | + | + | + | + | + | + |
| MC-19 | + | + | + | + | + | + | + | + | + | + | x (a) | + |
| MC-20 | + | + | + | + | + | + | + | + | x (b) | x (b) | + | + |
| MC-21 | + | + | + | + | + | + | + | + | + | + | + | + |
| MC-22 | + | + | + | + | + | + | + | + | + | + | + | x (d) |
| MC-23 | + | + | + | + | + | + | + | + | + | + | + | + |
| MC-24 | + | + | + | + | + | + | + | + | + | + | + | + |
| MC-25 | + | + | + | + | + | + | + | + | + | + | + | + |
| MC-26 | + | + | + | + | + | x (d) | + | + | + | + | x (a) | x (d) |
| MC-27 | + | + | + | + | + | + | + | + | + | + | + | + |
| MC-28 | + | + | + | + | x (a) | + | + | + | + | + | x (a) | + |
| MC-29 | + | + | + | + | + | + | + | + | + | + | + | x (d) |
| MC-30 | + | + | x (a) | x (a) | + | + | x (b) | x (b) | x (b) | x (b) | x (a) | x (d) |
| MC-31 | + | + | x (d) | x (d) | + | + | x (a) | x (a) | x (d) | x (d) | x (a) | x (d) |
| MC-32 | x (b) | x (b) | + | + | + | + | + | + | x (b) | x (b) | + | x (d) |

---

## Disagreements

Questions where at least one config got it right and another wrong:

### MC-2

**Question:** What is the recommended way to access queries in RTL tests?

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad

**Got it wrong:** fast / rag / grounded, fast / rag / broad, fast / no-rag / broad
  - fast / rag / grounded: answered a
  - fast / rag / broad: answered a
  - fast / no-rag / broad: answered a

### MC-3

**Question:** Which query should you try first when looking for a button?

**Correct answer:** c

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad, general / no-rag / broad
  - general / rag / grounded: answered a
  - general / rag / broad: answered a
  - general / no-rag / broad: answered a

### MC-4

**Question:** Which query is best for finding a text input with a visible label "Email Address"?

**Correct answer:** c

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / no-rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered a
  - general / rag / broad: answered a

### MC-5

**Question:** `getByTestId` should be used:

**Correct answer:** c

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad

**Got it wrong:** fast / rag / grounded, fast / rag / broad, fast / no-rag / broad
  - fast / rag / grounded: answered b
  - fast / rag / broad: answered b
  - fast / no-rag / broad: answered b

### MC-6

**Question:** What does `getByRole('heading', { level: 2 })` match?

**Correct answer:** b

**Got it right:** quick / no-rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad

**Got it wrong:** quick / rag / grounded, quick / rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad
  - quick / rag / grounded: answered c
  - quick / rag / broad: answered c
  - fast / rag / grounded: answered c
  - fast / rag / broad: answered c
  - fast / no-rag / broad: answered c
  - general / rag / grounded: answered c
  - general / rag / broad: answered c
  - general / no-rag / broad: answered d

### MC-7

**Question:** What is the implicit ARIA role of a single-select `<select>` element?

**Correct answer:** c

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / no-rag / broad

**Got it wrong:** fast / rag / grounded, fast / rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad
  - fast / rag / grounded: answered d
  - fast / rag / broad: answered d
  - deep / rag / grounded: answered a
  - deep / rag / broad: answered a
  - deep / no-rag / broad: answered d
  - general / rag / grounded: answered a
  - general / rag / broad: answered a
  - general / no-rag / broad: answered d

### MC-8

**Question:** What does `getBy` do when no matching element is found?

**Correct answer:** c

**Got it right:** quick / rag / grounded, quick / rag / broad, fast / rag / grounded, fast / rag / broad, deep / rag / grounded, deep / rag / broad, general / rag / grounded, general / rag / broad

**Got it wrong:** quick / no-rag / broad, fast / no-rag / broad, deep / no-rag / broad, general / no-rag / broad
  - quick / no-rag / broad: answered a
  - fast / no-rag / broad: answered a
  - deep / no-rag / broad: answered b
  - general / no-rag / broad: answered d

### MC-9

**Question:** What does `queryBy` do when no matching element is found?

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad

**Got it wrong:** fast / no-rag / broad, general / no-rag / broad
  - fast / no-rag / broad: answered a
  - general / no-rag / broad: answered d

### MC-10

**Question:** When should you use `queryBy` instead of `getBy`?

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, deep / rag / grounded, deep / rag / broad, general / rag / grounded, general / rag / broad

**Got it wrong:** quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / no-rag / broad, general / no-rag / broad
  - quick / no-rag / broad: answered a
  - fast / rag / grounded: answered a
  - fast / rag / broad: answered a
  - fast / no-rag / broad: answered a
  - deep / no-rag / broad: answered a
  - general / no-rag / broad: answered d

### MC-11

**Question:** `findBy` queries are most useful when:

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad

**Got it wrong:** general / no-rag / broad
  - general / no-rag / broad: answered a

### MC-12

**Question:** `findBy` returns:

**Correct answer:** c

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / rag / grounded, deep / rag / broad

**Got it wrong:** deep / no-rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad
  - deep / no-rag / broad: answered b
  - general / rag / grounded: answered b
  - general / rag / broad: answered b
  - general / no-rag / broad: answered b

### MC-13

**Question:** What does `getAllByRole('listitem')` return?

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad

**Got it wrong:** general / no-rag / broad
  - general / no-rag / broad: answered d

### MC-14

**Question:** What happens when `getAllBy` finds no matching elements?

**Correct answer:** c

**Got it right:** quick / rag / grounded, quick / rag / broad, deep / rag / grounded, deep / rag / broad

**Got it wrong:** quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad
  - quick / no-rag / broad: answered a
  - fast / rag / grounded: answered a
  - fast / rag / broad: answered a
  - fast / no-rag / broad: answered a
  - deep / no-rag / broad: answered a
  - general / rag / grounded: answered a
  - general / rag / broad: answered a
  - general / no-rag / broad: answered d

### MC-16

**Question:** How do you set up `user-event` in a test?

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad

**Got it wrong:** fast / no-rag / broad
  - fast / no-rag / broad: answered a

### MC-19

**Question:** `user-event` methods are:

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad

**Got it wrong:** fast / no-rag / broad
  - fast / no-rag / broad: answered a

### MC-20

**Question:** `user.tab()` simulates:

**Correct answer:** c

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / no-rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered b
  - general / rag / broad: answered b

### MC-22

**Question:** What does `waitFor` do?

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad

**Got it wrong:** general / no-rag / broad
  - general / no-rag / broad: answered d

### MC-26

**Question:** `screen.debug()` prints:

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, deep / rag / grounded, deep / rag / broad, general / rag / grounded, general / rag / broad

**Got it wrong:** fast / no-rag / broad, deep / no-rag / broad, general / no-rag / broad
  - fast / no-rag / broad: answered a
  - deep / no-rag / broad: answered d
  - general / no-rag / broad: answered d

### MC-28

**Question:** The `within` function:

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, fast / rag / grounded, fast / rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad

**Got it wrong:** quick / no-rag / broad, fast / no-rag / broad
  - quick / no-rag / broad: answered a
  - fast / no-rag / broad: answered a

### MC-29

**Question:** What does the `wrapper` option in `render` do?

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad, general / rag / grounded, general / rag / broad

**Got it wrong:** general / no-rag / broad
  - general / no-rag / broad: answered d

### MC-30

**Question:** Which of the following is a "Common Mistake" identified by KCD?

**Correct answer:** c

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, deep / no-rag / broad

**Got it wrong:** fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / rag / grounded, deep / rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad
  - fast / rag / grounded: answered b
  - fast / rag / broad: answered b
  - fast / no-rag / broad: answered a
  - deep / rag / grounded: answered a
  - deep / rag / broad: answered a
  - general / rag / grounded: answered b
  - general / rag / broad: answered b
  - general / no-rag / broad: answered d

### MC-31

**Question:** Another common mistake identified by KCD is:

**Correct answer:** b

**Got it right:** quick / rag / grounded, quick / rag / broad, quick / no-rag / broad, deep / no-rag / broad

**Got it wrong:** fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / rag / grounded, deep / rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad
  - fast / rag / grounded: answered a
  - fast / rag / broad: answered a
  - fast / no-rag / broad: answered a
  - deep / rag / grounded: answered d
  - deep / rag / broad: answered d
  - general / rag / grounded: answered d
  - general / rag / broad: answered d
  - general / no-rag / broad: answered d

### MC-32

**Question:** KCD recommends using `findBy` instead of:

**Correct answer:** c

**Got it right:** quick / no-rag / broad, fast / rag / grounded, fast / rag / broad, fast / no-rag / broad, deep / rag / grounded, deep / rag / broad, deep / no-rag / broad

**Got it wrong:** quick / rag / grounded, quick / rag / broad, general / rag / grounded, general / rag / broad, general / no-rag / broad
  - quick / rag / grounded: answered b
  - quick / rag / broad: answered b
  - general / rag / grounded: answered b
  - general / rag / broad: answered b
  - general / no-rag / broad: answered d

