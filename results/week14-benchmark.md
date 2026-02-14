# Benchmark Report

**Quiz:** Week 14: React Testing Library — Rendering, Queries, and user-event

## Summary

| Rank | Config | Accuracy | Correct | Time | Per-Q |
|------|--------|----------|---------|------|-------|
| 1 | quick / rag / grounded | 90.6% | 29/32 | 187.0s | 5.8s |
| 2 | quick / rag / broad | 90.6% | 29/32 | 189.2s | 5.9s |
| 3 | general / rag / grounded | 65.6% | 21/32 | 202.8s | 6.3s |
| 4 | general / rag / broad | 65.6% | 21/32 | 198.8s | 6.2s |

---

## Per-Question Breakdown

| Question | quick / rag / grounded | quick / rag / broad | general / rag / grounded | general / rag / broad |
|----------|------|------|------|------|
| TF-1 | + | + | + | + |
| TF-2 | + | + | + | + |
| TF-3 | + | + | x (F) | x (F) |
| TF-4 | + | + | + | + |
| TF-5 | + | + | + | + |
| TF-6 | + | + | + | + |
| TF-7 | + | + | x (F) | x (F) |
| TF-8 | + | + | x (F) | x (F) |
| TF-9 | + | + | + | + |
| TF-10 | + | + | x (F) | x (F) |
| TF-11 | + | + | + | + |
| TF-12 | + | + | x (F) | x (F) |
| TF-13 | + | + | x (?) | x (?) |
| TF-14 | + | + | + | + |
| TF-15 | + | + | + | + |
| TF-16 | x (F) | x (F) | + | + |
| TF-17 | + | + | + | + |
| TF-18 | + | + | x (?) | x (?) |
| TF-19 | + | + | + | + |
| TF-20 | x (F) | x (F) | x (F) | x (F) |
| TF-21 | + | + | x (F) | x (F) |
| TF-22 | + | + | + | + |
| TF-23 | + | + | + | + |
| TF-24 | + | + | + | + |
| TF-25 | + | + | + | + |
| TF-26 | + | + | + | + |
| TF-27 | + | + | + | + |
| TF-28 | x (T) | x (T) | + | + |
| TF-29 | + | + | + | + |
| TF-30 | + | + | + | + |
| TF-31 | + | + | x (F) | x (F) |
| TF-32 | + | + | x (F) | x (F) |

---

## Disagreements

Questions where at least one config got it right and another wrong:

### TF-3

**Question:** RTL encourages testing components the way a user would interact with them: finding elements by visible text, labels, or roles, then simulating user actions.

**Correct answer:** T

**Got it right:** quick / rag / grounded, quick / rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered F
  - general / rag / broad: answered F

### TF-7

**Question:** The `render` function requires a DOM environment (like `jsdom`) because it renders the component into an actual DOM tree.

**Correct answer:** T

**Got it right:** quick / rag / grounded, quick / rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered F
  - general / rag / broad: answered F

### TF-8

**Question:** RTL's `cleanup` function unmounts the rendered component and removes it from the DOM. In Vitest with RTL, cleanup runs automatically after each test.

**Correct answer:** T

**Got it right:** quick / rag / grounded, quick / rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered F
  - general / rag / broad: answered F

### TF-10

**Question:** `getByRole` is the highest-priority query in RTL's recommended query hierarchy because it queries elements the way assistive technology sees them.

**Correct answer:** T

**Got it right:** quick / rag / grounded, quick / rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered F
  - general / rag / broad: answered F

### TF-12

**Question:** The recommended query priority order is: `getByRole` > `getByLabelText` > `getByText` > `getByTestId`.

**Correct answer:** T

**Got it right:** quick / rag / grounded, quick / rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered F
  - general / rag / broad: answered F

### TF-13

**Question:** `getByRole('button', { name: /submit/i })` finds a button whose accessible name matches the regex `/submit/i`.

**Correct answer:** T

**Got it right:** quick / rag / grounded, quick / rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered ?
  - general / rag / broad: answered ?

### TF-16

**Question:** An `<input type="text">` has an implicit ARIA role of `"textbox"`.

**Correct answer:** T

**Got it right:** general / rag / grounded, general / rag / broad

**Got it wrong:** quick / rag / grounded, quick / rag / broad
  - quick / rag / grounded: answered F
  - quick / rag / broad: answered F

### TF-18

**Question:** An `<h1>` element has an implicit ARIA role of `"heading"` with `level: 1`.

**Correct answer:** T

**Got it right:** quick / rag / grounded, quick / rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered ?
  - general / rag / broad: answered ?

### TF-21

**Question:** An `<input type="checkbox">` has an implicit ARIA role of `"checkbox"`.

**Correct answer:** T

**Got it right:** quick / rag / grounded, quick / rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered F
  - general / rag / broad: answered F

### TF-28

**Question:** `getByTitle` queries elements by their `title` attribute and is a higher-priority query than `getByRole`.

**Correct answer:** F

**Got it right:** general / rag / grounded, general / rag / broad

**Got it wrong:** quick / rag / grounded, quick / rag / broad
  - quick / rag / grounded: answered T
  - quick / rag / broad: answered T

### TF-31

**Question:** `getBy` queries throw an error if more than one matching element is found.

**Correct answer:** T

**Got it right:** quick / rag / grounded, quick / rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered F
  - general / rag / broad: answered F

### TF-32

**Question:** `queryBy` returns `null` if no matching element is found, rather than throwing.

**Correct answer:** T

**Got it right:** quick / rag / grounded, quick / rag / broad

**Got it wrong:** general / rag / grounded, general / rag / broad
  - general / rag / grounded: answered F
  - general / rag / broad: answered F

