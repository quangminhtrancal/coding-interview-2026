# Confluent Interview Questions Summary

**Source:** LeetCode Discuss — Confluent company tag (https://leetcode.com/discuss/topic/confluent/)
**Date compiled:** October 12, 2026
**Coverage:** 75 total posts identified (infinite-scroll topic page, no numbered pagination). 44 posts opened and read in full (post body + all comments); 31 reviewed via listing excerpts/metadata. All 4 tabs checked (For You, Interview, Career, Compensation). Most Votes and Newest sorts verified against the same corpus.

---

## Coding Questions

### Highest-frequency

#### 1. Key-Value Store with TTL/Expiration + getAverage() (aka "WindowedMap" / "Windowed Average") — 8 posts
- Implement a key-value store where entries expire after EXPIRY_TIME.
- APIs: `put(key, value)`, `get(key)`, `get_average()` (average of non-expired values).
- Data streams in with increasing timestamps.
- Heavy focus on **concurrency** (strongly vs eventually consistent, locks for concurrent reads/writes).
- Related: LeetCode 2622 "Cache With Time Limit".

#### 2. Word Search / Phrase Search in List of Documents — 8 posts
- Given a list of documents (id + text), return document IDs containing a word.
- Follow-up: phrase search. Build inverted index (word → docId → positions).
- Follow-ups: AND/OR/bracket queries, single data store for both word and phrase search.

#### 3. Validate Sudoku / Solve Sudoku — 6 posts
- Validate a (partial) Sudoku board; follow-up: solve via backtracking with pruning.
- Emphasis on clean recursion, optimizing traversals (single pass); fully running code expected.

#### 4. LRU Cache (variants) — 4 posts
- Classic LRU; variants: LRU with TTL, "Modified LRU Cache", LRU-like cache with concurrency focus (locks for concurrent reads/writes).

#### 5. tail -n / Last N Lines of a File — 4 posts
- Implement `tail(file_name, n)` printing last n lines without loading the entire file.
- Handle n=0, n > total lines.
- Variants: logging system printing last N lines in original order without storing everything; optimize for huge files (streaming).

### Medium-frequency

| Question | Frequency | Notes |
|---|---|---|
| Function Signature Matching | 3 posts | Given function signatures + input args, return matching functions; follow-up: variadic args. Type matching/parsing focus. |
| Time-Based Key-Value Store | 2 posts | Variant maintaining sum/average; window with millisecond size, get/set with eviction. |
| Inverted Index | 2 posts | Build inverted index for document search. |
| Debounce (JavaScript) | 2 posts | Frontend roles; JS-only. |
| Combination Sum (with memoization) | 1 post | |
| Quicksort Bug Fix + Pivot Strategies | 1 post | Fix quicksort bugs; randomized/dual-pivot/median-of-three. |
| Monotonic Stack (OA) | 1 post | Previous/Next Greater Element pattern (HackerRank). |
| String Parsing/Matching | 1 post | Exact question not disclosed. |
| Prefix Matching / Common Sentences in Files | 1 post | |
| Task Scheduler (concurrency) | 1 post | Scheduler executing time-based tasks, multithreading. |
| Ad Rotation (OA) | 1 post | Binary bit-flip + REST API pulse rate (HackerRank). |
| The Bitwise Equation (OA) | 1 post | x+y, x^y, x&y bit manipulation. |
| Falling Dominoes (OA) | 1 post | Greedy/DP. |

### Interview format notes (coding)
- Screening: often 2 questions, 2nd is an extension of the 1st; any language allowed (except some frontend roles: JavaScript only).
- Onsite coding: fully running code expected; follow-ups common (phrase search after word search; solver after validator; concurrency after cache).
- Concurrency/multithreading is a recurring theme — mention it explicitly even if not asked to implement.

---

## System Design Questions

### Highest-frequency

#### 1. Podcast / Feed Service (subscribe, feed generation) — 6 posts
- Design podcast service: subscribe/unsubscribe, fetch top N episodes, feed view, add podcasts/episodes.
- Focus: API design (verbs, status codes, headers, auth), SQL/data modeling, pagination, scale (nodes, replicas, partitions), DB schema.
- Variants: Feedly-like, Spotify-like.

#### 2. URL Shortener / TinyURL — 4 posts
- Focus: scalability, reliability, DB/cache sharding, resource calculations (RPS, memory, servers); read-heavy optimization; range-based sharding.

#### 3. Key-Value Store (distributed, persistent) — 2 posts
- High throughput, low latency, fault-tolerant persistent KV store as network service; get/put/delete; high write throughput; distributed (Redis/Memcache) vs single-host (LevelDB).

### Others

| Question | Frequency | Notes |
|---|---|---|
| TempMail Service (5-hour expiry) | 1 post | Expiry mechanism, storage, access control. |
| Movie Ticketing Platform | 1 post | Requirements, HLD, APIs, DB schema, concurrency. |
| Stock Alert Notification System | 1 post | 1M+ rules, scan, notify within a minute. |
| Operations at Scale | 1 post | Bottlenecks, load balancers, slow queries, DB master-slave, IaC/Terraform, monolith→microservices, multi-region. |

---

## Behavioral Questions

- **Confluent "Values" / "Engineering Value" rounds:** going above and beyond for customers; initiative in challenging situations; pushing back on legacy decisions; mentoring peers; handling ambiguity in large-scale systems; experience/projects/challenges/volunteering/mentorship.
- **Hiring Manager / Team Match:** why Confluent; disagreement with teammate; most challenging work; why leaving; bug introduced and handled; strengths; customers; team culture; personal interests/motivations.
- **Standard behavioral:** biggest challenge, biggest failure, best manager; project with most impact; project most proud of, conflicts.
- **Screening behavioral:** "When was the last time a production incident happened, and how did you handle it?"

---

## Interview Experience Notes

- **Loop structure:** Typically Recruiter → Technical Screening (1-2 rounds) → Onsite (3-5 rounds: 2-3 coding, 1-2 design, 1 behavioral/values) → Hiring Manager → Team Matching → Offer. SSE2 requires a "strong hire" in design rounds.
- **Kafka basics** mentioned for screening prep.
- **Hiring freezes/pauses** reported multiple times — offers delayed after clearing rounds.
- **Feedback complaints:** rejections despite solving optimally; junior interviewers for senior roles; ghosting on rescheduling.
- **Confluent is now an IBM company** (multiple 2026 posts reference "Confluent (IBM)").
- **Roles seen:** SSE, SSE-2, Senior/Staff SWE, SDE-1/2/3, Frontend SWE, Security Engineer, Data Infrastructure Intern, SWE Intern.

---

## Deduplicated Question Frequency Table

| Question | Type | Frequency (posts) |
|---|---|---|
| KV store with TTL + getAverage (WindowedMap) | Coding | 8 |
| Word/Phrase search in documents | Coding | 8 |
| Validate/Solve Sudoku | Coding | 6 |
| Podcast/Feed service design | System Design | 6 |
| LRU Cache variants | Coding | 4 |
| tail -n / last N lines (file ops) | Coding | 4 |
| URL Shortener / TinyURL | System Design | 4 |
| Function signature matching | Coding | 3 |
| Time-based KV store | Coding | 2 |
| Inverted Index | Coding | 2 |
| Debounce (JavaScript) | Coding | 2 |
| Distributed KV store design | System Design | 2 |
| TempMail (expiry) | System Design | 1 |
| Movie Ticketing Platform | System Design | 1 |
| Stock Alert Notifications | System Design | 1 |
| Operations at Scale | System Design | 1 |
| Quicksort debug | Coding | 1 |
| Combination Sum + memoization | Coding | 1 |
| Ad Rotation (OA) | Coding | 1 |
| Bitwise Equation (OA) | Coding | 1 |
| Falling Dominoes (OA) | Coding | 1 |
| Task Scheduler (concurrency) | Coding | 1 |
| Prefix matching | Coding | 1 |

---

*Compiled from LeetCode Discuss Confluent tag. For full discussion threads, visit https://leetcode.com/discuss/topic/confluent/*
