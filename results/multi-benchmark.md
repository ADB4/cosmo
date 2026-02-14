# Multi-Quiz Benchmark Report

**Quizzes:** 6

- Week 1: TypeScript Fundamentals
- Week 13: Testing Philosophy and Vitest Fundamentals
- Week 14: React Testing Library — Rendering, Queries, and user-event
- Week 15: Mocking, Async Testing, and Hook Testing
- Week 16: Test Architecture, Patterns, and Coverage
- Week 2: Advanced TypeScript

---

## Aggregate Summary

| Rank | Config | Overall | Week 1: TypeScript Fundam | Week 13: Testing Philosop | Week 14: React Testing Li | Week 15: Mocking, Async T | Week 16: Test Architectur | Week 2: Advanced TypeScri | Total Time |
|------|--------|---------|------|------|------|------|------|------|------|
| 1 | deep / rag / grounded | 90.6% | 93.8% | 90.6% | 96.9% | 84.4% | 81.2% | 96.9% | 2356s |
| 2 | deep / rag / broad | 90.6% | 93.8% | 90.6% | 96.9% | 84.4% | 81.2% | 96.9% | 2314s |
| 3 | quick / no-rag / broad | 89.6% | 90.6% | 90.6% | 87.5% | 90.6% | 87.5% | 90.6% | 749s |
| 4 | deep / no-rag / broad | 88.0% | 93.8% | 84.4% | 78.1% | 84.4% | 93.8% | 93.8% | 1415s |
| 5 | quick / rag / grounded | 85.4% | 93.8% | 78.1% | 90.6% | 84.4% | 75.0% | 90.6% | 1163s |
| 6 | quick / rag / broad | 85.4% | 93.8% | 78.1% | 90.6% | 84.4% | 75.0% | 90.6% | 1143s |
| 7 | fast / rag / grounded | 83.3% | 84.4% | 81.2% | 90.6% | 84.4% | 68.8% | 90.6% | 1325s |
| 8 | fast / rag / broad | 83.3% | 84.4% | 81.2% | 90.6% | 84.4% | 68.8% | 90.6% | 1309s |
| 9 | general / rag / grounded | 71.9% | 71.9% | 56.2% | 65.6% | 78.1% | 78.1% | 81.2% | 1226s |
| 10 | general / rag / broad | 71.9% | 71.9% | 56.2% | 65.6% | 78.1% | 78.1% | 81.2% | 1202s |
| 11 | fast / no-rag / broad | 60.4% | 68.8% | 53.1% | 68.8% | 53.1% | 68.8% | 50.0% | 804s |
| 12 | general / no-rag / broad | 56.8% | 46.9% | 46.9% | 59.4% | 50.0% | 81.2% | 56.2% | 565s |

---

## Quiz 1: Week 1: TypeScript Fundamentals

| Rank | Config | Accuracy | Correct | Time | Per-Q |
|------|--------|----------|---------|------|-------|
| 1 | quick / rag / grounded | 93.8% | 30/32 | 201.3s | 6.3s |
| 2 | quick / rag / broad | 93.8% | 30/32 | 197.8s | 6.2s |
| 3 | deep / rag / grounded | 93.8% | 30/32 | 412.3s | 12.9s |
| 4 | deep / rag / broad | 93.8% | 30/32 | 404.9s | 12.7s |
| 5 | deep / no-rag / broad | 93.8% | 30/32 | 233.0s | 7.3s |
| 6 | quick / no-rag / broad | 90.6% | 29/32 | 125.9s | 3.9s |
| 7 | fast / rag / grounded | 84.4% | 27/32 | 231.5s | 7.2s |
| 8 | fast / rag / broad | 84.4% | 27/32 | 228.4s | 7.1s |
| 9 | general / rag / grounded | 71.9% | 23/32 | 213.9s | 6.7s |
| 10 | general / rag / broad | 71.9% | 23/32 | 209.8s | 6.6s |
| 11 | fast / no-rag / broad | 68.8% | 22/32 | 129.2s | 4.0s |
| 12 | general / no-rag / broad | 46.9% | 15/32 | 101.4s | 3.2s |

| Question | quick / rag / grounded | quick / rag / broad | deep / rag / grounded | deep / rag / broad | deep / no-rag / broad | quick / no-rag / broad | fast / rag / grounded | fast / rag / broad | general / rag / grounded | general / rag / broad | fast / no-rag / broad | general / no-rag / broad |
|----------|------|------|------|------|------|------|------|------|------|------|------|------|
| TF-1 | + | + | + | + | + | + | + | + | + | + | x (F) | + |
| TF-2 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-3 | + | + | + | + | + | + | + | + | x (F) | x (F) | + | + |
| TF-4 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-5 | + | + | + | + | + | + | + | + | x (F) | x (F) | + | x (F) |
| TF-6 | + | + | + | + | + | + | + | + | x (F) | x (F) | + | x (F) |
| TF-7 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-8 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-9 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-10 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-11 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-12 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-13 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-14 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-15 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-16 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-17 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-18 | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | + | x (T) |
| TF-19 | + | + | + | + | + | + | + | + | x (F) | x (F) | + | x (F) |
| TF-20 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-33 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-34 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-35 | + | + | + | + | + | + | + | + | x (F) | x (F) | x (F) | x (F) |
| TF-36 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-37 | + | + | + | + | + | x (F) | + | + | + | + | + | + |
| TF-38 | + | + | + | + | + | x (T) | x (T) | x (T) | x (T) | x (T) | + | + |
| TF-39 | + | + | + | + | + | + | x (T) | x (T) | + | + | + | + |
| TF-40 | + | + | + | + | x (F) | + | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-41 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-42 | x (F) | x (F) | x (F) | x (F) | + | + | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-43 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-44 | + | + | + | + | + | + | + | + | + | + | + | + |

---

## Quiz 2: Week 13: Testing Philosophy and Vitest Fundamentals

| Rank | Config | Accuracy | Correct | Time | Per-Q |
|------|--------|----------|---------|------|-------|
| 1 | quick / no-rag / broad | 90.6% | 29/32 | 122.3s | 3.8s |
| 2 | deep / rag / grounded | 90.6% | 29/32 | 369.7s | 11.6s |
| 3 | deep / rag / broad | 90.6% | 29/32 | 361.8s | 11.3s |
| 4 | deep / no-rag / broad | 84.4% | 27/32 | 217.4s | 6.8s |
| 5 | fast / rag / grounded | 81.2% | 26/32 | 200.3s | 6.3s |
| 6 | fast / rag / broad | 81.2% | 26/32 | 197.4s | 6.2s |
| 7 | quick / rag / grounded | 78.1% | 25/32 | 176.5s | 5.5s |
| 8 | quick / rag / broad | 78.1% | 25/32 | 173.3s | 5.4s |
| 9 | general / rag / grounded | 56.2% | 18/32 | 189.8s | 5.9s |
| 10 | general / rag / broad | 56.2% | 18/32 | 184.6s | 5.8s |
| 11 | fast / no-rag / broad | 53.1% | 17/32 | 118.7s | 3.7s |
| 12 | general / no-rag / broad | 46.9% | 15/32 | 92.5s | 2.9s |

| Question | quick / no-rag / broad | deep / rag / grounded | deep / rag / broad | deep / no-rag / broad | fast / rag / grounded | fast / rag / broad | quick / rag / grounded | quick / rag / broad | general / rag / grounded | general / rag / broad | fast / no-rag / broad | general / no-rag / broad |
|----------|------|------|------|------|------|------|------|------|------|------|------|------|
| TF-1 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-2 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-3 | + | x (F) | x (F) | x (F) | + | + | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-4 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-5 | x (T) | + | + | + | x (T) | x (T) | x (T) | x (T) | + | + | + | + |
| TF-6 | + | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-7 | + | + | + | x (F) | + | + | + | + | x (F) | x (F) | x (F) | x (F) |
| TF-8 | + | + | + | + | + | + | + | + | x (T) | x (T) | + | + |
| TF-9 | + | + | + | x (F) | + | + | + | + | + | + | x (F) | x (F) |
| TF-10 | + | + | + | + | + | + | + | + | x (F) | x (F) | + | x (F) |
| TF-11 | x (T) | x (T) | x (T) | + | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | + |
| TF-12 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-13 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-14 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-15 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-16 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-17 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-18 | + | + | + | + | + | + | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-19 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-20 | + | + | + | + | + | + | + | + | x (F) | x (F) | x (F) | + |
| TF-21 | + | + | + | + | + | + | + | + | x (F) | x (F) | x (F) | x (F) |
| TF-22 | x (T) | + | + | x (T) | x (T) | x (T) | x (T) | x (T) | + | + | x (T) | + |
| TF-23 | + | + | + | + | + | + | + | + | x (F) | x (F) | x (F) | x (F) |
| TF-24 | + | + | + | + | + | + | x (F) | x (F) | x (F) | x (F) | + | x (F) |
| TF-25 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-26 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-27 | + | + | + | + | + | + | + | + | x (F) | x (F) | + | + |
| TF-28 | + | + | + | + | + | + | + | + | x (F) | x (F) | + | x (F) |
| TF-29 | + | + | + | + | x (F) | x (F) | + | + | x (F) | x (F) | x (F) | x (F) |
| TF-30 | + | + | + | + | + | + | + | + | + | + | x (F) | + |
| TF-31 | + | + | + | + | x (F) | x (F) | + | + | + | + | x (F) | x (F) |
| TF-32 | + | + | + | + | + | + | + | + | + | + | + | x (F) |

---

## Quiz 3: Week 14: React Testing Library — Rendering, Queries, and user-event

| Rank | Config | Accuracy | Correct | Time | Per-Q |
|------|--------|----------|---------|------|-------|
| 1 | deep / rag / grounded | 96.9% | 31/32 | 384.8s | 12.0s |
| 2 | deep / rag / broad | 96.9% | 31/32 | 378.5s | 11.8s |
| 3 | quick / rag / grounded | 90.6% | 29/32 | 192.1s | 6.0s |
| 4 | quick / rag / broad | 90.6% | 29/32 | 188.7s | 5.9s |
| 5 | fast / rag / grounded | 90.6% | 29/32 | 212.3s | 6.6s |
| 6 | fast / rag / broad | 90.6% | 29/32 | 210.0s | 6.6s |
| 7 | quick / no-rag / broad | 87.5% | 28/32 | 130.9s | 4.1s |
| 8 | deep / no-rag / broad | 78.1% | 25/32 | 235.5s | 7.4s |
| 9 | fast / no-rag / broad | 68.8% | 22/32 | 134.1s | 4.2s |
| 10 | general / rag / grounded | 65.6% | 21/32 | 201.6s | 6.3s |
| 11 | general / rag / broad | 65.6% | 21/32 | 198.4s | 6.2s |
| 12 | general / no-rag / broad | 59.4% | 19/32 | 95.6s | 3.0s |

| Question | deep / rag / grounded | deep / rag / broad | quick / rag / grounded | quick / rag / broad | fast / rag / grounded | fast / rag / broad | quick / no-rag / broad | deep / no-rag / broad | fast / no-rag / broad | general / rag / grounded | general / rag / broad | general / no-rag / broad |
|----------|------|------|------|------|------|------|------|------|------|------|------|------|
| TF-1 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-2 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-3 | + | + | + | + | + | + | + | + | + | x (F) | x (F) | + |
| TF-4 | + | + | + | + | + | + | + | + | x (F) | + | + | + |
| TF-5 | + | + | + | + | + | + | x (F) | x (F) | x (F) | + | + | x (F) |
| TF-6 | + | + | + | + | + | + | + | x (F) | x (F) | + | + | x (F) |
| TF-7 | + | + | + | + | + | + | + | x (F) | + | x (F) | x (F) | x (F) |
| TF-8 | + | + | + | + | + | + | + | + | x (F) | x (F) | x (F) | x (F) |
| TF-9 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-10 | + | + | + | + | + | + | + | + | x (F) | x (F) | x (F) | + |
| TF-11 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-12 | + | + | + | + | + | + | + | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-13 | + | + | + | + | + | + | + | + | + | x (?) | x (?) | + |
| TF-14 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-15 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-16 | + | + | x (F) | x (F) | x (F) | x (F) | + | + | + | + | + | x (F) |
| TF-17 | + | + | + | + | x (F) | x (F) | + | + | + | + | + | + |
| TF-18 | + | + | + | + | + | + | + | + | + | x (?) | x (?) | + |
| TF-19 | + | + | + | + | + | + | + | + | x (F) | + | + | x (F) |
| TF-20 | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-21 | + | + | + | + | + | + | + | + | + | x (F) | x (F) | x (F) |
| TF-22 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-23 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-24 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-25 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-26 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-27 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-28 | + | + | x (T) | x (T) | + | + | + | + | + | + | + | + |
| TF-29 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-30 | + | + | + | + | + | + | x (F) | x (F) | x (F) | + | + | x (F) |
| TF-31 | + | + | + | + | + | + | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-32 | + | + | + | + | + | + | + | + | + | x (F) | x (F) | + |

---

## Quiz 4: Week 15: Mocking, Async Testing, and Hook Testing

| Rank | Config | Accuracy | Correct | Time | Per-Q |
|------|--------|----------|---------|------|-------|
| 1 | quick / no-rag / broad | 90.6% | 29/32 | 111.1s | 3.5s |
| 2 | quick / rag / grounded | 84.4% | 27/32 | 175.5s | 5.5s |
| 3 | quick / rag / broad | 84.4% | 27/32 | 172.4s | 5.4s |
| 4 | fast / rag / grounded | 84.4% | 27/32 | 218.5s | 6.8s |
| 5 | fast / rag / broad | 84.4% | 27/32 | 215.8s | 6.7s |
| 6 | deep / rag / grounded | 84.4% | 27/32 | 364.9s | 11.4s |
| 7 | deep / rag / broad | 84.4% | 27/32 | 358.4s | 11.2s |
| 8 | deep / no-rag / broad | 84.4% | 27/32 | 247.7s | 7.7s |
| 9 | general / rag / grounded | 78.1% | 25/32 | 191.3s | 6.0s |
| 10 | general / rag / broad | 78.1% | 25/32 | 187.5s | 5.9s |
| 11 | fast / no-rag / broad | 53.1% | 17/32 | 128.5s | 4.0s |
| 12 | general / no-rag / broad | 50.0% | 16/32 | 91.5s | 2.9s |

| Question | quick / no-rag / broad | quick / rag / grounded | quick / rag / broad | fast / rag / grounded | fast / rag / broad | deep / rag / grounded | deep / rag / broad | deep / no-rag / broad | general / rag / grounded | general / rag / broad | fast / no-rag / broad | general / no-rag / broad |
|----------|------|------|------|------|------|------|------|------|------|------|------|------|
| TF-1 | + | + | + | + | + | + | + | + | + | + | x (F) | + |
| TF-2 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-3 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-4 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-5 | + | + | + | + | + | + | + | + | + | + | x (F) | + |
| TF-6 | + | + | + | + | + | + | + | + | x (F) | x (F) | + | x (F) |
| TF-7 | + | + | + | x (?) | x (?) | + | + | + | + | + | x (F) | x (F) |
| TF-8 | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | + | + | + | + | + |
| TF-9 | + | + | + | + | + | + | + | x (F) | + | + | x (F) | + |
| TF-10 | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-11 | + | + | + | + | + | + | + | x (F) | + | + | x (F) | + |
| TF-12 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-13 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-14 | x (T) | + | + | x (T) | x (T) | + | + | x (T) | + | + | x (T) | + |
| TF-15 | + | + | + | + | + | + | + | + | + | + | x (F) | + |
| TF-16 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-17 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-18 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-19 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-20 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-21 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-22 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-23 | + | x (F) | x (F) | + | + | + | + | + | x (F) | x (F) | + | x (F) |
| TF-24 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-25 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-26 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-27 | + | x (F) | x (F) | + | + | + | + | + | x (F) | x (F) | x (F) | x (F) |
| TF-28 | + | + | + | + | + | x (F) | x (F) | + | x (F) | x (F) | x (F) | + |
| TF-29 | + | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | + |
| TF-30 | + | + | + | + | + | x (F) | x (F) | + | x (F) | x (F) | x (F) | x (F) |
| TF-31 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-32 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |

---

## Quiz 5: Week 16: Test Architecture, Patterns, and Coverage

| Rank | Config | Accuracy | Correct | Time | Per-Q |
|------|--------|----------|---------|------|-------|
| 1 | deep / no-rag / broad | 93.8% | 30/32 | 253.2s | 7.9s |
| 2 | quick / no-rag / broad | 87.5% | 28/32 | 138.1s | 4.3s |
| 3 | deep / rag / grounded | 81.2% | 26/32 | 400.9s | 12.5s |
| 4 | deep / rag / broad | 81.2% | 26/32 | 393.6s | 12.3s |
| 5 | general / no-rag / broad | 81.2% | 26/32 | 82.0s | 2.6s |
| 6 | general / rag / grounded | 78.1% | 25/32 | 183.1s | 5.7s |
| 7 | general / rag / broad | 78.1% | 25/32 | 179.0s | 5.6s |
| 8 | quick / rag / grounded | 75.0% | 24/32 | 186.7s | 5.8s |
| 9 | quick / rag / broad | 75.0% | 24/32 | 183.4s | 5.7s |
| 10 | fast / rag / grounded | 68.8% | 22/32 | 208.9s | 6.5s |
| 11 | fast / rag / broad | 68.8% | 22/32 | 206.9s | 6.5s |
| 12 | fast / no-rag / broad | 68.8% | 22/32 | 132.5s | 4.1s |

| Question | deep / no-rag / broad | quick / no-rag / broad | deep / rag / grounded | deep / rag / broad | general / no-rag / broad | general / rag / grounded | general / rag / broad | quick / rag / grounded | quick / rag / broad | fast / rag / grounded | fast / rag / broad | fast / no-rag / broad |
|----------|------|------|------|------|------|------|------|------|------|------|------|------|
| TF-1 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-2 | x (F) | + | + | + | + | x (F) | x (F) | + | + | x (F) | x (F) | + |
| TF-3 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-4 | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-5 | + | + | + | + | + | x (F) | x (F) | + | + | x (F) | x (F) | + |
| TF-6 | + | + | + | + | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-7 | + | + | + | + | x (F) | + | + | + | + | + | + | x (F) |
| TF-8 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-9 | + | x (T) | + | + | + | + | + | x (T) | x (T) | + | + | + |
| TF-10 | + | + | x (F) | x (F) | x (F) | + | + | + | + | x (F) | x (F) | x (F) |
| TF-11 | + | + | x (F) | x (F) | + | + | + | + | + | + | + | + |
| TF-12 | + | x (T) | + | + | + | + | + | x (T) | x (T) | x (T) | x (T) | + |
| TF-13 | + | + | + | + | + | + | + | + | + | x (F) | x (F) | + |
| TF-14 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-15 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-16 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-17 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-18 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-19 | + | + | + | + | + | x (F) | x (F) | + | + | + | + | + |
| TF-20 | + | x (T) | x (T) | x (T) | + | + | + | x (T) | x (T) | x (T) | x (T) | x (T) |
| TF-21 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-22 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-23 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-24 | + | + | + | + | x (F) | x (F) | x (F) | x (F) | x (F) | + | + | x (F) |
| TF-25 | + | + | x (F) | x (F) | + | + | + | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-26 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-27 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-28 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-29 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-30 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-31 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-32 | + | + | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |

---

## Quiz 6: Week 2: Advanced TypeScript

| Rank | Config | Accuracy | Correct | Time | Per-Q |
|------|--------|----------|---------|------|-------|
| 1 | deep / rag / grounded | 96.9% | 31/32 | 423.0s | 13.2s |
| 2 | deep / rag / broad | 96.9% | 31/32 | 416.8s | 13.0s |
| 3 | deep / no-rag / broad | 93.8% | 30/32 | 228.3s | 7.1s |
| 4 | quick / rag / grounded | 90.6% | 29/32 | 230.6s | 7.2s |
| 5 | quick / rag / broad | 90.6% | 29/32 | 227.3s | 7.1s |
| 6 | quick / no-rag / broad | 90.6% | 29/32 | 120.1s | 3.8s |
| 7 | fast / rag / grounded | 90.6% | 29/32 | 253.1s | 7.9s |
| 8 | fast / rag / broad | 90.6% | 29/32 | 250.8s | 7.8s |
| 9 | general / rag / grounded | 81.2% | 26/32 | 246.6s | 7.7s |
| 10 | general / rag / broad | 81.2% | 26/32 | 242.8s | 7.6s |
| 11 | general / no-rag / broad | 56.2% | 18/32 | 102.3s | 3.2s |
| 12 | fast / no-rag / broad | 50.0% | 16/32 | 160.9s | 5.0s |

| Question | deep / rag / grounded | deep / rag / broad | deep / no-rag / broad | quick / rag / grounded | quick / rag / broad | quick / no-rag / broad | fast / rag / grounded | fast / rag / broad | general / rag / grounded | general / rag / broad | general / no-rag / broad | fast / no-rag / broad |
|----------|------|------|------|------|------|------|------|------|------|------|------|------|
| TF-1 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-2 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-3 | + | + | + | + | + | + | + | + | + | + | x (F) | + |
| TF-4 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-5 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-6 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-7 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-8 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-9 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-10 | + | + | + | + | + | + | + | + | x (F) | x (F) | + | + |
| TF-33 | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | x (T) | + | + | + | x (T) |
| TF-34 | + | + | + | x (F) | x (F) | + | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-35 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-36 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-37 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-38 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-39 | + | + | + | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) | x (F) |
| TF-40 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-41 | + | + | + | + | + | + | + | + | + | + | x (F) | + |
| TF-42 | + | + | + | + | + | + | + | + | x (F) | x (F) | x (F) | x (F) |
| TF-43 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-44 | + | + | + | + | + | + | + | + | + | + | x (F) | + |
| TF-45 | + | + | x (F) | + | + | + | + | + | x (F) | x (F) | x (F) | + |
| TF-46 | + | + | + | + | + | + | + | + | + | + | + | x (F) |
| TF-47 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-48 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-11 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-12 | + | + | + | + | + | + | + | + | + | + | + | + |
| TF-13 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-14 | + | + | + | + | + | + | + | + | + | + | x (F) | x (F) |
| TF-15 | + | + | + | + | + | x (F) | + | + | x (F) | x (F) | x (F) | x (F) |
| TF-16 | + | + | + | + | + | + | + | + | + | + | + | + |

---

