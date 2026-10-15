# REST API & System Design Interview Prep

*Study document for Henry's two Confluent system design interviews. Read end-to-end.*

---

## 1. The two interviews — what to expect

### Side-by-side

| | Interview 1 — High-Level System Design | Interview 2 — Backend API Design |
|---|---|---|
| **Task** | Design a high-level system | Design backend APIs for a high-level problem |
| **Flow** | 1. Clarify requirements (scope, scale, constraints) → 2. High-level architecture (components, services) → 3. Drill into components & APIs | 1. Clarify functional + non-functional requirements → 2. Outline overall architecture (components & interactions) → 3. Drill into specific APIs & components |
| **Graded on** | Requirements gathering & capacity estimation; CAP trade-offs; DB design (SQL vs NoSQL, sharding, indexing, replication); HA & scalability; performance (caching, indexing, partitioning); concurrency & synchronization; replication & caching; monitoring & observability; compliance & security | HTTP + REST API design principles; distributed systems (scalable, reliable, performant); data handling (storage, retrieval, caching, replication) |
| **Mindset** | Breadth-first: show you can reason about the whole system and its trade-offs | Depth-first on the API surface: resources, endpoints, params, errors, versioning — then connect to architecture |

### Ground rules (both interviews)

- Complete the interview **independently**. AI tools are not permitted unless explicitly agreed in advance.
- No audio/video/screen recording without prior consent (confidentiality & privacy).

### The universal flow (memorize this)

1. **Clarify** — scope, users, scale, read/write ratio, latency targets, consistency needs, constraints. Never start drawing boxes before this.
2. **Requirements** — functional (what it does) + non-functional (scale, latency, availability, durability, security).
3. **Capacity estimation** — back-of-envelope: QPS, storage, bandwidth. Shows seniority fast.
4. **High-level architecture** — components, data flow, where state lives.
5. **Drill down** — APIs (Interview 2: this is the main event), DB schema, key algorithms, concurrency.
6. **Trade-offs & failure modes** — what breaks, what you chose and why, what you'd do with 10× scale.

---

## 2. Concept summaries

One tight brief per focus area from the interview scope. Format: what it is → what the interviewer probes → how to talk about it.

### 2.1 Requirements gathering & capacity estimation

**What it is:** Turning a vague prompt into quantified functional and non-functional requirements, then doing back-of-envelope math (QPS, storage, bandwidth, concurrent users) to size the system.

**Interviewer probes:** Do you ask about scale before designing? Can you estimate: requests/sec, bytes/request, storage over 5 years, cache size for hot data?

**How to talk about it:** Always start here — "Before architecture, let me pin down scale." State assumptions out loud and sanity-check them ("100M DAU, 10% write-heavy → ~10k writes/sec peak"). Round aggressively; the method matters more than the number. Use the estimates later to justify every choice (this QPS is why we need caching; this storage is why we shard).

### 2.2 CAP theorem trade-offs

**What it is:** In a distributed system facing a network partition, you must choose between consistency (every read sees the latest write) and availability (every request gets a response). PACELC extends it: even without partitions, there's a latency-vs-consistency trade-off.

**Interviewer probes:** "Your DB spans regions — what happens during a partition?" They want you to name the trade-off explicitly and pick a side with justification, not dodge it.

**How to talk about it:** Name it: "This is a CP vs AP decision." Tie the choice to the product: money/likes-counters need consistency (CP); a social feed or DNS can be AP with eventual consistency. Mention that most real systems are tunable (e.g., quorum reads/writes: W+R > N for strong consistency) rather than purely one letter.

### 2.3 Database design — SQL vs NoSQL, sharding, indexing, replication

**What it is:** Choosing the datastore from access patterns, then scaling it: sharding (horizontal partition by key), indexing (fast lookups, at write cost), replication (copies for availability/read scale).

**Interviewer probes:** "Why Postgres and not Cassandra here?" "How do you shard?" "What breaks when a shard gets hot?" They grade the *reasoning from access patterns*, not the brand name.

**How to talk about it:** Start from queries, not the DB: "Reads are by user_id, writes are append-only time-series → that points to X." Rule of thumb: relational + complex queries + transactions → SQL; massive write scale / flexible schema / key-based access → NoSQL. For sharding, name the shard key and defend it (cardinality, even distribution); name the hot-shard mitigation (consistent hashing, virtual nodes, or re-sharding). Indexes: "index what you filter/sort by; every index taxes writes."

### 2.4 High availability & scalability

**What it is:** HA = the system stays up when components fail (redundancy, failover, no single point of failure). Scalability = handling more load, ideally horizontally (add machines, not bigger machines).

**Interviewer probes:** "A zone goes down — what happens?" "10× traffic tomorrow — what breaks first?" They want failure domains named and a scaling story per tier.

**How to talk about it:** Walk each tier: "LB is multi-AZ; app servers are stateless so we add N more; DB fails over to a replica with <X seconds of lag." Distinguish scaling reads (replicas, caching) from writes (sharding, queuing). Name the bottleneck you *can't* fix by adding boxes (e.g., a single-leader DB's write throughput) and say so — honesty about limits scores well.

### 2.5 Performance — caching, indexing, partitioning

**What it is:** The latency toolkit: caching (serve hot data from memory), indexing (avoid full scans), partitioning (split data so each query touches less of it).

**Interviewer probes:** "P99 is 800ms, target is 100ms — where do you look?" They want a measurement-first answer, not a shopping list of caches.

**How to talk about it:** "First I'd find *where* time goes — traces, slow-query logs — then apply the cheapest fix for that layer." Cache at the layer closest to the request that repeats (CDN → app cache → DB query cache), and always name invalidation ("cache-aside with TTL; stale reads acceptable for Y minutes because…"). Partitioning is both a perf and scale lever: partition so hot queries hit one partition, not all.

### 2.6 Concurrency & synchronization

**What it is:** Correct behavior when many requests/threads touch shared state: race conditions, deadlocks, lost updates — and the tools: locks, CAS, idempotency, optimistic concurrency, partitioning work so it doesn't contend.

**Interviewer probes:** "Two requests decrement the same counter — what can go wrong?" They want the failure named (lost update) and the cheapest correct fix.

**How to talk about it:** Prefer designs that *avoid* coordination: partition by key so contenders never meet; make operations idempotent so retries are safe; use optimistic concurrency (version checks) over locks when contention is low. When you must synchronize, say what the lock protects and its blast radius ("per-user lock, not global — contention stays within one user's requests").

### 2.7 Replication & caching

**What it is:** Replication = copies of data across nodes for fault tolerance and read scale. Caching = copies of *computed or hot* data closer to the reader for speed. (Related but different jobs.)

**Interviewer probes:** "Leader fails mid-write — do we lose data?" "Cache and DB disagree — which wins?" They test your consistency model under failure.

**How to talk about it:** Separate the two jobs out loud: "Replication is for durability/availability; caching is for latency." For replication, state sync vs async and what each costs (sync = slower writes, no loss; async = fast, possible loss on failover — pick per data criticality). For caching, state the pattern (cache-aside, read/write-through) and the invalidation story; "stale for 60s is fine for a feed, unacceptable for a balance" is exactly the sentence they want.

### 2.8 Monitoring & observability

**What it is:** Metrics (numbers over time), logging (discrete events), tracing (request paths), alerts (actions on thresholds) — designed in, not bolted on.

**Interviewer probes:** "It's 3 AM and latency spikes — how do you find it?" They want to hear RED (rate, errors, duration) or USE (utilization, saturation, errors) applied per component.

**How to talk about it:** "Every component emits RED metrics; we alert on symptom (error rate, p99), not cause (CPU)." Name the dashboards you'd build per tier and one alert with its threshold and runbook ("p99 > 500ms for 5 min → page; runbook: check DB slow log, then cache hit rate"). Mention structured logs with request IDs so a single request is traceable across services.

### 2.9 Compliance & security

**What it is:** Protecting data and meeting legal obligations: authN/authZ, encryption in transit/at rest, PII handling, audit trails, data residency, retention/deletion.

**Interviewer probes:** Usually a "what about PII?" follow-up. They check you don't design a system that leaks tokens in URLs or stores passwords in plaintext.

**How to talk about it:** Touch it briefly but concretely: "TLS everywhere, encryption at rest with managed keys; PII tokenized, never in URLs or logs; OAuth2/OIDC for authN, RBAC for authZ; audit log on sensitive actions; retention policy with hard delete." For multi-region, add data residency ("EU user data stays in EU"). One crisp paragraph beats a hand-wave.

---

## 3. REST API design standards

*Summarized from "API Design Interview Preparation" by Tai Chia Makris Huang ([link](https://www.linkedin.com/pulse/api-design-interview-preparation-tai-chia-makris-huang/)). Paraphrased throughout; see §7 for the source.*

### The three goals

Design APIs to (1) serve more requirements with fewer endpoints — "fewer APIs serving more requirements" — rather than one endpoint per use case; (2) be idempotent where appropriate, so retries are safe; (3) give each API a single responsibility, so behavior stays predictable.

### Model resources first, like a class diagram

Before writing any endpoint, define your unit resources the way you'd sketch classes. Then let **has-a relationships drive nesting**: a parent resource owning children becomes a nested path. The article's example: `GET /api/zoos/1/animals` — animals belong to a zoo, so they nest under it. If you can't draw the resource model, your endpoints will sprawl.

### Robustness = cover inputs like test cases

Path and query parameters must cover **all** input values and corner cases — think of them the way you'd think of test cases. Empty results, missing filters, boundary values, invalid combos: the API contract should define behavior for each. Making full, deliberate use of path vs query variables (see §5) is part of this.

### Think whole-system, and the DB choice matters most

API design doesn't stop at URLs. The article stresses thinking about whole-system choices, with the **database choice being the most important** — the example given is image storage pointing toward a NoSQL/document database, because the access pattern (large blobs, key-based fetch) dictates the store, which in turn shapes what the API can efficiently offer.

### The meta-lesson: don't memorize, generalize

Interviewers deliberately ask follow-ups you haven't seen. The winning move is to always push the design further yourself: higher performance, lower latency, more robust handling — before they ask. If you only memorized patterns, unseen questions expose it; if you reason from principles (the three goals, resource modeling, robustness), you adapt.

---

## 4. Stripe API teardown — a real-world reference

*Observed from the [Stripe v2 Core Accounts API docs](https://docs.stripe.com/api/v2/core/accounts) (verified 2026-10-15). Study this as the gold standard for how a top-tier API is shaped.*

### Endpoint table

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v2/core/accounts` | Create an account |
| `POST` | `/v2/core/accounts/:id` | Update an account |
| `GET` | `/v2/core/accounts/:id` | Retrieve an account |
| `GET` | `/v2/core/accounts` | List accounts |
| `POST` | `/v2/core/accounts/:id/close` | Close an account |

### Conventions worth copying

- **Plural lowercase nouns**, no verbs in paths: `/accounts`, not `/getAccount`.
- **Path order is version → service → resource:** `/v2/core/accounts`. Version in the URL *plus* a `Stripe-Version` header.
- **IDs are prefixed and opaque:** `acct_1Nv0FGQ9RKHgCVdK` — the prefix names the type, the rest is unguessable (no sequential integers leaking count/order).
- **Namespaced object types:** `"v2.core.account"` — types carry their version and service.
- **Timestamps are RFC 3339** strings, not epoch ints.
- **Enums over booleans where states can grow:** `open` vs `closed` (a third state later won't break clients).
- **`metadata` map (≤50 keys)** for free-form extensibility without schema changes.
- **No `DELETE`.** Destructive state changes are `POST` to a verb sub-path (`/:id/close`), keeping the resource addressable afterward (you can still `GET` a closed account).
- **Updates are `POST`, not `PATCH`/`PUT`.** Stripe's house convention: partial updates via POST with only changed fields.
- **Capabilities are embedded config fields**, not separate endpoints — fewer APIs serving more requirements (§3, goal 1).
- **`Idempotency-Key` header** on mutating calls; a conflicting retry returns `409`. Retries are safe by contract.
- **Typed errors** (`400`/`403`/`404`/`409`/`429`) with exponential backoff on `429`.
- **`Stripe-Account` header** for Connect (acting on behalf of another account) — identity travels in headers, not in the path.
- **Auth:** Basic/Bearer over HTTPS only.

### Per-endpoint path-vs-query analysis (with WHY)

- **`GET /v2/core/accounts/:id` (retrieve)** — `:id` is a **path param** because it is the resource's identity. Changing it addresses a *different* account. It's required, cacheable, and shows up in access logs as the accessed resource. (Rule: identity → path.)
- **`POST /v2/core/accounts/:id` (update)** — same `:id` reasoning. Note Stripe uses POST rather than PATCH/PUT: a deliberate house convention — partial-update semantics on POST keeps one method for all mutations and pairs with `Idempotency-Key`.
- **`POST /v2/core/accounts/:id/close` (close)** — `:id` identifies the account (path); `close` is a **verb sub-path**, not a query param, because it names a state-changing *action* on the resource. Stripe avoids `DELETE` so the closed account remains retrievable — the resource lifecycle outlives the action. (If it were `?action=close`, the "action" would be an optional modifier on a GET-shaped URL — wrong semantics for a mutation.)
- **`GET /v2/core/accounts` (list)** — no path params; the collection itself is the resource. Filters and pagination ride as **query params**: `applied_configurations` (enum filter), `closed` (boolean filter), `limit` (page size), `page` (pagination token). All optional, none change *which* collection — they only shape the view. (Rule: filter/sort/page → query.)
- **`include` param (create/update/retrieve)** — a **query param** controlling response field expansion. It's an optional modifier of the representation, not of identity: `GET /v2/core/accounts/:id?include=capabilities` still addresses the same account.
- **Pagination via `next_page_url` / `previous_page_url`** — the list response embeds full URLs carrying the opaque page token. Clients don't construct tokens; the server owns cursor format. This is AIP-158-style token pagination done right: tokens are opaque, so the backend can change cursor mechanics without breaking clients.

---

## 5. Path parameter vs query parameter — the complete rulebook

### The decision rule

> **Path params = resource identity and hierarchy** — required, identifies *which* resource; changing the value addresses a *different* resource.
> **Query params = everything else** — filtering, sorting, pagination, field selection, optional modifiers; they change the *view*, never *which* resource.

### Decision flowchart (in words)

1. **Is the value required to address the resource?** → Path. (`/accounts/:id` — without the id there is no resource.)
2. **Does changing it address a different resource?** → Path. (`/zoos/1/animals` vs `/zoos/2/animals` are different collections — has-a nesting, §3.)
3. **Is it optional — a filter, sort, page size, page token, field selector, or display option?** → Query. (`?closed=true&limit=20`.)
4. **Is it sensitive (tokens, PII, secrets)?** → Neither in the URL. URLs land in access logs, browser history, and caches. Put it in headers (like Stripe's `Stripe-Account` / `Authorization`) or the body.
5. **Is it a verb/action?** → Don't put it in query (`?action=close`). Use the HTTP method (`POST`/`DELETE`) or, for non-CRUD actions, a verb sub-path (`/:id/close`) — Stripe's pattern.

### Why it matters (say this in the interview)

- **Cacheability:** `GET /accounts/acct_123` is cacheable per resource; query strings fragment caches (`?limit=20` vs `?limit=25` are different cache keys). Identity in path → clean cache keys.
- **Optionality & evolution:** query params can be added later without breaking the path contract; path params are part of the contract.
- **Logs & analytics:** path segments identify *what* was accessed; query strings describe *how*. This split makes access logs and metrics aggregation natural.
- **Hierarchy readability:** `/v2/core/accounts/:id` reads as version → service → resource → instance — self-documenting.

### Real-world examples (with references)

| API | Path param (identity) | Query param (modifier) | Why they did it that way |
|---|---|---|---|
| **Stripe** ([docs](https://docs.stripe.com/api/v2/core/accounts)) | `GET /v2/core/accounts/:id` — the account id | `GET /v2/core/accounts?closed=true&limit=20&page=…` — filters + pagination | The id *is* the resource; filters/page only shape the collection view. `include` expands the representation without changing identity. |
| **GitHub** ([docs](https://docs.github.com/en/rest/issues/issues#get-an-issue)) | `GET /repos/{owner}/{repo}/issues/{issue_number}` — owner/repo/issue identify the exact issue | `GET /repos/{owner}/{repo}/issues?state=open&per_page=30` — filter + page size | `{owner}/{repo}/{issue_number}` is a hierarchy of identities (has-a nesting); `state`/`per_page` are optional view modifiers on the issues collection. |
| **Google AIP** ([aip.dev](https://google.aip.dev/)) | AIP-122: resource names — `publishers/123/books/456` identify the resource | AIP-132 List + AIP-158 pagination: `pageSize`, `pageToken`; field selectors | AIPs codify the rulebook: identity lives in the resource name (path); List methods take standardized query params for paging. `pageToken` is opaque so servers can evolve cursor internals. |

### Common interview traps

- **Sensitive data in query params** (`GET /users?ssn=…`) — ends up in logs, caches, browser history. Instant red flag; move to headers/body.
- **Verbs in the path** (`POST /createAccount`, `GET /deleteUser?id=1`) — use HTTP methods; `GET` must never mutate.
- **Optional identifier as a path param** (`/accounts/:id?` where id may be absent) — if it's optional, it's not identity; make it a query param or a separate collection endpoint.
- **Filters smuggled into the path** (`/accounts/closed/true`) — path segments imply hierarchy/identity; filters belong in query.
- **Inconsistent nesting** (`/animals/5/zoo` vs `/zoos/1/animals`) — has-a direction must be consistent; the owner comes first.
- **Non-opaque pagination** (`?offset=200`) — deep offsets get slow and skip under concurrent writes; prefer opaque cursors (Stripe's `page` token, AIP-158 `pageToken`).

---

## 6. How to run the API-design interview (45-minute playbook)

| Time | Phase | Do this |
|---|---|---|
| 0–5 | **Clarify** | Scope, users, scale, read/write ratio, latency targets, consistency needs. Write functional + non-functional requirements visibly. |
| 5–12 | **Resources** | Model unit resources like a class diagram (§3). Draw has-a relations → nesting. Name the nouns; banish verbs. |
| 12–25 | **Endpoints** | Method + path per operation. Apply §5's rulebook aloud for every param ("id is identity → path; status filter → query, because…"). Cover the LinkedIn robustness bar: every input value and corner case gets defined behavior. |
| 25–32 | **Params, errors, idempotency** | Pagination scheme (opaque cursors), field selection (`include`-style), filtering/sorting. Error model: typed errors + status codes. Idempotency strategy for mutations (`Idempotency-Key` → `409` on conflict, Stripe-style). |
| 32–38 | **Versioning & evolution** | URL versioning (`/v2/…`) + headers; additive-only changes; how old clients keep working. |
| 38–45 | **Deep dive** | Pick the hardest endpoint and go deep: DB choice for its access pattern (§2.3), caching, concurrency, failure modes. End with trade-offs you'd revisit at 10× scale. |

### What "good" looks like

- Fewer, well-factored endpoints over one-per-screen (LinkedIn goal 1).
- Every param justified with the path-vs-query rule, stated out loud.
- Idempotent mutations; typed errors; versioned from day one.
- DB choice derived from the API's access patterns, not brand preference — and the *most important* whole-system decision, named explicitly (§3).
- You push past the happy path yourself: "at 10× writes I'd…", "if the cache is cold…", "during a partition…" — before the interviewer asks (the LinkedIn meta-lesson).

---

## 7. Reference links

- API Design Interview Preparation — Tai Chia Makris Huang (LinkedIn): https://www.linkedin.com/pulse/api-design-interview-preparation-tai-chia-makris-huang/
- Stripe API v2 — Core Accounts: https://docs.stripe.com/api/v2/core/accounts
- GitHub REST API — Issues: https://docs.github.com/en/rest/issues/issues#get-an-issue
- Google API Improvement Proposals (AIPs) — resource names, List, pagination: https://google.aip.dev/
