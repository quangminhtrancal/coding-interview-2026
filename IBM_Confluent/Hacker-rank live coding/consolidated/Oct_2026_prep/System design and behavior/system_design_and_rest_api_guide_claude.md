# Backend System Design & REST API Design: Interview Study Guide

> **Source note (please read):** The LinkedIn article you linked
> (`linkedin.com/pulse/api-design-interview-preparation-tai-chia-makris-huang/`) blocks automated
> access, so I could **not** read it directly. Section 2 (REST standards) therefore covers the
> commonly accepted REST conventions drawn from the standards and company docs listed in the
> references, not a summary of that specific article. Paste its text into the chat and I'll
> reconcile this guide with it.
> The Stripe sections **are** based on the live Stripe docs I fetched
> (`docs.stripe.com/api/v2/core/accounts`, its `list` and `close` pages, and Stripe's idempotency docs).

---

## Table of Contents

1. [System Design Interview Scope: Concept Summary](#1-system-design-interview-scope-concept-summary)
2. [REST API Standards](#2-rest-api-standards)
3. [Stripe Teardown: `/v2/core/accounts`](#3-stripe-teardown-v2coreaccounts)
4. [Query Parameter vs Path Parameter](#4-query-parameter-vs-path-parameter)
5. [Real-World Examples and Why They Do It That Way](#5-real-world-examples-and-why-they-do-it-that-way)
6. [API Design Interview Template](#6-api-design-interview-template)
7. [References](#7-references)

---

## 1. System Design Interview Scope: Concept Summary

### 1.1 What the interview looks like

| Phase | What you do | Time (rough) |
|---|---|---|
| Clarify requirements | Ask questions on scope, scale, constraints. Split functional vs non-functional. | 5-10 min |
| High-level architecture | Draw key components and how they interact (clients, gateway, services, DB, cache, queue). | 10-15 min |
| Drill down | Pick 1-2 components (often the **APIs**) and go deep: schemas, endpoints, data model, failure modes. | 15-20 min |
| Trade-offs and wrap-up | Bottlenecks, failure scenarios, monitoring, what you would improve. | 5-10 min |

The second brief you pasted is a **backend API** flavour: expect to define endpoints, request/response
shapes, status codes, pagination, idempotency, and how the API sits on top of a scalable system.

Interview rules from the brief: work independently, no AI tools unless agreed in advance, no recording
without consent.

### 1.2 Requirements gathering and capacity estimation

**Functional requirements:** what the system *does* (e.g. create an account, list accounts, close an account).

**Non-functional requirements:** how well it does it: latency (p50/p95/p99), availability (e.g. 99.9% vs 99.99%),
consistency needs, durability, scalability, security/compliance.

**Questions to ask:** Who are the clients (web, mobile, third parties)? Read-heavy or write-heavy? Expected
DAU/QPS? Data size and retention? Global or single region? Any regulatory constraints?

**Back-of-envelope estimation cheat sheet**

| Quantity | Formula / rule of thumb |
|---|---|
| Seconds per day | ~86,400 (use ~100K for easy math) |
| Average QPS | requests per day / 86,400 |
| Peak QPS | average QPS x 2-5 (state your assumption) |
| Storage | records/day x bytes/record x retention days (x replication factor) |
| Bandwidth | QPS x average payload size |
| Cache sizing | Often the "hot" 20% of data gets 80% of reads |

Example: 10M requests/day is about 115 QPS average, about 350-600 QPS peak. State the number, then say whether it
changes the design (it usually does not at this size; at 100K QPS it does).

### 1.3 Distributed systems principles (CAP, consistency)

- **CAP theorem:** when a network **P**artition happens, you must choose between **C**onsistency (every read sees the
  latest write) and **A**vailability (every request gets a response). In practice partitions *will* happen, so the
  real choice is CP vs AP *during a partition*.
- **CP examples:** systems that prefer rejecting requests over serving stale data (e.g. financial ledgers, leader-based
  stores).
- **AP examples:** systems that keep serving and reconcile later (e.g. Dynamo-style stores, shopping-cart style data).
- **Eventual consistency:** replicas converge over time. Fine for feeds, counters, "likes". Not fine for account balances.
- **Strong consistency:** reads reflect the latest committed write. Costs latency and availability.
- **PACELC refinement:** even without a partition, you trade **L**atency vs **C**onsistency.
- **Consistency models to name:** strong, read-your-writes, monotonic reads, causal, eventual.

**Talking point:** "For payments/balances I'd pick strong consistency (CP); for the activity feed I'd accept eventual consistency (AP)."

### 1.4 Database design

| | SQL (relational) | NoSQL |
|---|---|---|
| Strengths | ACID transactions, joins, strict schema, mature tooling | Horizontal scale, flexible schema, high write throughput |
| Use when | Relational data, money, strong integrity, complex queries | Massive scale, simple access patterns by key, denormalised/document data, time-series |
| Watch out | Vertical scaling limits, sharding is manual | Weaker transactions/joins, you design around access patterns |

NoSQL families: key-value (Redis, DynamoDB), document (MongoDB), wide-column (Cassandra), graph (Neo4j).

**Indexing:** speeds reads, slows writes, costs storage. Index columns used in `WHERE`, `JOIN`, `ORDER BY`. Composite
index column order matters (leftmost prefix). Avoid over-indexing.

**Sharding (partitioning):** split data across nodes.
- *Range-based:* simple range scans, but hot spots (e.g. latest timestamps).
- *Hash-based:* even distribution, but range queries and resharding are harder (use **consistent hashing**).
- *Directory/lookup-based:* flexible, but the lookup service is a dependency.
- Choose a **shard key** with high cardinality and even access. Beware hot keys and cross-shard joins/transactions.

**Replication:**
- *Leader-follower:* writes to leader, reads from followers. Replication lag means stale reads.
- *Multi-leader / leaderless (quorum):* better write availability, needs conflict resolution. Quorum rule: `R + W > N` for strong reads.
- *Sync vs async:* sync is safer but slower. Async is faster but can lose recent writes on failover.

### 1.5 High availability and scalability

- **Horizontal scaling:** add more stateless instances behind a load balancer (preferred) vs vertical scaling (bigger box).
- **Make services stateless:** push session/state to a shared store (Redis, DB).
- **Load balancing:** L4 vs L7, round-robin, least-connections, consistent hashing; health checks.
- **Eliminate single points of failure (SPOF):** redundant LBs, multi-AZ, replicated DBs.
- **Fault tolerance patterns:** timeouts, **retries with exponential backoff + jitter**, **circuit breakers**, bulkheads,
  graceful degradation, load shedding.
- **Failure recovery:** automatic failover, backups, point-in-time recovery, multi-region/disaster recovery.
  Define **RTO** (how long to recover) and **RPO** (how much data loss is acceptable).
- **Availability maths:** 99.9% is about 8.8 h downtime/year; 99.99% is about 53 min/year.

### 1.6 Performance: caching, indexing, partitioning

- **Caching layers:** client/browser, CDN, API gateway, application cache (Redis/Memcached), DB buffer cache.
- **Cache patterns:** cache-aside (most common), read-through, write-through, write-behind.
- **Invalidation:** TTL, explicit invalidation on write, versioned keys. ("The two hard things...")
- **Cache problems:** stampede/thundering herd (use locking or request coalescing), penetration (cache negative results /
  bloom filter), avalanche (jittered TTLs).
- **Other levers:** indexes, denormalisation, read replicas, pagination, batching, compression, async processing via queues.
- **Partitioning** also reduces per-node data and spreads load (see sharding).

### 1.7 Concurrency and synchronization

- **Problems:** lost updates, race conditions, double-spend, duplicate processing.
- **Optimistic concurrency:** version number/ETag; reject if changed (`409`/`412`). Good for low contention.
- **Pessimistic locking:** `SELECT ... FOR UPDATE`. Good for high contention, costs throughput.
- **Distributed locks:** Redis-based or ZooKeeper/etcd; always use lease/TTL and fencing tokens.
- **Idempotency:** make retries safe (see Stripe's `Idempotency-Key` in section 3).
- **Message processing:** at-least-once delivery + idempotent consumers is the usual practical combination.
- **Transactions across services:** prefer **sagas** (compensating actions) over 2PC; use the **outbox pattern** to
  atomically write data and publish an event.

### 1.8 Replication and caching (how they help response time and fault tolerance)

- Replication gives **fault tolerance** (survive node loss) and **read scalability** (serve reads from replicas) and can
  give **locality** (replicas near users).
- Caching gives **latency reduction** and **load reduction** on the DB.
- Both introduce **staleness**: say explicitly how stale data may be and why that is acceptable.

### 1.9 Monitoring and observability

- **Metrics (the "what"):** RED (Rate, Errors, Duration) for services; USE (Utilization, Saturation, Errors) for resources.
  Track p50/p95/p99 latency, not just averages.
- **Logs (the "why"):** structured (JSON), with a **correlation/request ID** propagated across services.
- **Traces (the "where"):** distributed tracing (OpenTelemetry) to find slow hops.
- **Alerting:** alert on symptoms tied to SLOs (error rate, latency), not every cause. Define **SLI/SLO/SLA** and error budgets.
- **Also:** dashboards, health checks, synthetic checks, audit logs for sensitive actions.

### 1.10 Compliance and security

- **AuthN/AuthZ:** OAuth 2.0 / OIDC, API keys, JWT; least privilege; scopes/RBAC.
- **Transport and storage:** TLS everywhere, encryption at rest, key management (KMS), secrets management.
- **API protection:** rate limiting/throttling, input validation, WAF, CORS, protection against injection and
  mass-assignment, no sensitive data in URLs (URLs get logged!).
- **Privacy/legal:** GDPR/CCPA (right to erasure, data minimisation, consent), PCI-DSS (card data), HIPAA (health data),
  data residency, retention policies, audit trails, PII masking in logs.
- **Soft delete vs hard delete** matters for compliance (Stripe "closes" accounts instead of deleting them; see section 3).

### 1.11 Discussing trade-offs (the thing interviewers grade hardest)

Always frame choices as **"X gives me ..., at the cost of ..."**:

| Choice | Gain | Cost |
|---|---|---|
| Strong consistency | Correctness | Latency, availability |
| Caching | Speed, lower DB load | Staleness, invalidation complexity |
| Sharding | Scale | Cross-shard queries/transactions, ops complexity |
| Microservices | Independent scaling/deploys | Network failures, distributed debugging |
| Async/queues | Decoupling, smoothing spikes | Eventual consistency, ordering/duplication issues |
| More replicas | Availability, read throughput | Cost, replication lag |

---

## 2. REST API Standards

### 2.1 HTTP fundamentals you must know

- **Methods and semantics** (RFC 9110):

| Method | Meaning | Safe | Idempotent | Typical success |
|---|---|---|---|---|
| `GET` | Read a resource/collection | Yes | Yes | `200` |
| `POST` | Create, or trigger an action | No | **No** (unless you add an idempotency key) | `201` (+`Location`), `200`, `202` |
| `PUT` | Replace a resource entirely | No | Yes | `200`, `204` |
| `PATCH` | Partially update | No | Not guaranteed | `200`, `204` |
| `DELETE` | Remove | No | Yes | `204`, `200`, `202` |

- **Safe** = no state change. **Idempotent** = repeating gives the same end state. This is why retries on `GET/PUT/DELETE`
  are fine but `POST` needs protection.
- **Stateless:** each request carries everything the server needs (auth token, params); no server-side session needed.
- **Headers worth naming:** `Content-Type`, `Accept`, `Authorization`, `Idempotency-Key`, `ETag`/`If-Match`
  (concurrency), `Cache-Control`, `Location`, `Retry-After`, `X-Request-Id`.

### 2.2 Resource modelling and URL design

1. **Use nouns, not verbs:** `/accounts`, not `/getAccounts`.
2. **Plural collection names:** `/accounts`, and `/accounts/{id}` for one item.
3. **Hierarchy for ownership/containment:** `/accounts/{id}/payment-methods`. Keep nesting shallow (about 2 levels);
   beyond that, expose the child at the top level with a filter.
4. **Consistent casing:** lowercase, hyphens (`kebab-case`) in paths; pick `snake_case` or `camelCase` for JSON fields and stick to it.
5. **No trailing slashes, no file extensions** (use `Accept` header for format).
6. **Actions that don't fit CRUD:** model as a sub-resource or a custom action (`POST /accounts/{id}/close`), see section 3.
7. **Version the API** (`/v1/...` in the path, or a header such as Stripe's `Stripe-Version`).

### 2.3 Status codes (use them precisely)

| Range | Code | When |
|---|---|---|
| 2xx | `200 OK` | Successful read/update with body |
| | `201 Created` | Resource created; include `Location` header |
| | `202 Accepted` | Accepted for async processing |
| | `204 No Content` | Success with no body (e.g. delete) |
| 3xx | `304 Not Modified` | Conditional GET (ETag) hit |
| 4xx | `400 Bad Request` | Malformed/invalid input |
| | `401 Unauthorized` | Missing/invalid credentials (really "unauthenticated") |
| | `403 Forbidden` | Authenticated but not allowed |
| | `404 Not Found` | Resource doesn't exist |
| | `409 Conflict` | State conflict (duplicate, version mismatch) |
| | `412 Precondition Failed` | `If-Match` failed |
| | `422 Unprocessable Content` | Syntactically valid but semantically invalid |
| | `429 Too Many Requests` | Rate limited (send `Retry-After`) |
| 5xx | `500` / `502` / `503` / `504` | Server error / bad upstream / unavailable / upstream timeout |

### 2.4 Errors

Return a **consistent, machine-readable error body**. Standard option: RFC 9457 "Problem Details"
(`application/problem+json`). Stripe-style: HTTP status + a stable string `code` + human message
(see the error tables in section 3).

```json
{
  "type": "https://example.com/errors/insufficient-funds",
  "title": "Insufficient funds",
  "status": 400,
  "code": "insufficient_funds",
  "detail": "Balance is 10.00 but 25.00 is required.",
  "request_id": "req_123"
}
```

### 2.5 Pagination, filtering, sorting

| Style | Params | Pros | Cons |
|---|---|---|---|
| **Offset/limit** | `?limit=20&offset=40` or `page`/`per_page` | Simple, allows jumping to a page | Slow on big offsets, inconsistent when data changes during paging |
| **Cursor/token** | `?limit=20&page=<token>` or `starting_after=<id>` | Stable, fast at scale, good for feeds | No random page access |
| **Keyset** | `?created_before=<ts>&limit=20` | Uses an index, very fast | Needs a stable sort key |

- Always enforce a **max `limit`** and a sensible default.
- Return pagination metadata (`next_page_url`, or a `Link` header).
- **Filtering:** `?status=active&created_after=...`. **Sorting:** `?sort=-created_at`. **Field selection:** `?fields=id,name`.

### 2.6 Idempotency, concurrency, caching

- **Idempotency key** on `POST` (client-generated UUID in an `Idempotency-Key` header). Server stores the first result and
  replays it for the same key. (Stripe details in section 3.)
- **Optimistic concurrency:** return an `ETag`; client sends `If-Match` on update; mismatch returns `412`.
- **Caching:** `Cache-Control`, `ETag`/`If-None-Match` for `GET`. Never cache authenticated private data in shared caches without `private`.

### 2.7 Security and operations

- Always HTTPS. Authenticate with OAuth 2.0 bearer tokens or API keys (`Authorization: Bearer ...`).
- **Rate limiting** per key/user/IP, return `429` + `Retry-After`.
- Validate and whitelist input; never put secrets or PII in the URL.
- Support **async long-running operations**: `202 Accepted` + a status resource (`/operations/{id}`) or webhooks.
- **Webhooks/events** for state changes instead of making clients poll.
- **Backwards compatibility:** adding fields is non-breaking; removing/renaming/changing meaning is breaking, so bump the version.

### 2.8 REST maturity (Richardson model), briefly

0. One endpoint, RPC style -> 1. Resources -> 2. HTTP verbs and status codes (**where most real APIs live**) -> 3. Hypermedia (HATEOAS, rare in practice).

---

## 3. Stripe Teardown: `/v2/core/accounts`

Source: <https://docs.stripe.com/api/v2/core/accounts> (and its `list` and `close` pages).

### 3.1 The endpoint map

| Operation | Endpoint (as documented) | Observation |
|---|---|---|
| Create | `POST /v2/core/accounts` | Collection URL + `POST` |
| Update | `POST /v2/core/accounts/:id` | **`POST`, not `PATCH`/`PUT`**, on the item URL |
| Retrieve | `GET /v2/core/accounts/:id` | Path param = identity of one resource |
| List | `GET /v2/core/accounts` | Collection URL + query params for filter/page |
| Close | `POST /v2/core/accounts/:id/close` | **Custom action** as a sub-path, instead of `DELETE` |

### 3.2 Design decisions visible in the docs, and why

**1. Versioned namespace and domain grouping: `/v2/core/accounts`.**
`v2` is the API generation; `core` groups related resources; `accounts` is the plural noun. Stripe also requires the
`Stripe-Version` header on `/v2` calls, so the *behaviour* version is pinned per request on top of the *URL* version.
*Why:* breaking changes can ship without breaking existing integrations.

**2. Identifier in the path: `/accounts/:id`.**
`:id` identifies *which* account. IDs are prefixed (`acct_1QP3oLBUFVXWiKFB`) and responses carry an `"object": "v2.core.account"` type field.
*Why:* prefixed IDs make logs and support debugging self-describing, and the path gives a stable, cacheable, bookmarkable identity.

**3. List uses query parameters for filters and paging.**
From the docs, `GET /v2/core/accounts` accepts:

| Query param | Type | Purpose |
|---|---|---|
| `applied_configurations` | array of enum | Filter: accounts that have **all** listed configurations (`customer`, `merchant`, `recipient`) |
| `closed` | boolean | Filter by closed state; **default omits closed accounts** |
| `limit` | integer | Page size |
| `page` | string | Opaque page token for next/previous batch |

Example from the docs:
```bash
curl -G https://api.stripe.com/v2/core/accounts \
  -H "Authorization: Bearer <<YOUR_SECRET_KEY>>" \
  -H "Stripe-Version: <version>" \
  -d limit=2 \
  -d "applied_configurations[0]=customer"
```
*Why query params:* these are optional ways to narrow or window a **collection**; they do not change *which resource* you
are addressing. The sensible default (exclude closed) keeps the common case simple.

**4. Cursor/token pagination.**
Response shape: `{"data": [...], "next_page_url": "...", "previous_page_url": ...}`. `next_page_url` is `null` when there are no more pages;
the URL embeds an opaque `page=<token>` plus the original filters.
*Why:* opaque tokens stay correct while data is inserted/deleted (offsets would skip or duplicate rows), scale on large tables,
and let Stripe change the paging internals without breaking clients. (Stripe's v1 list endpoints use `starting_after`/`ending_before`
cursors, and its search endpoints use a `page` token plus `next_page`, per Stripe's API reference.)

**5. "Close" instead of "delete", as `POST /accounts/:id/close`.**
The docs say closing removes access to the account and its resources, but *limited information can still be retrieved
through the API to track history*. It is not a hard delete, so `DELETE` would misrepresent it.
It also takes a body, `applied_configurations`, and **all configurations on the account must be passed** for it to succeed
(error `configs_must_match_to_close`).
*Why:* (a) financial and compliance records must be retained, so soft-close semantics fit; (b) it is a *state transition with business
rules* (balance checks, pending transactions), which is better as an explicit action endpoint than overloading `DELETE`;
(c) requiring the caller to echo the configurations is a deliberate **safety confirmation** against closing the wrong thing.

**6. Idempotency for safe retries.**
Per Stripe's docs, clients send an `Idempotency-Key` header (a UUID is recommended; keys are up to 255 chars). Stripe saves the status code and body of the first request for that key, **including `500` errors**, and replays it for retries. In `/v2`, all `POST` and `DELETE` requests accept idempotency keys, while `GET` is idempotent by definition.
*Why:* networks fail; without this, a timeout on "create payment" forces the client to choose between double-charging and not charging.
This is exactly why `POST` (the non-idempotent verb) carries the key.

**7. Structured error contract.**
Each endpoint documents `HTTP status | code | description`, for example:

| HTTP | Code | Meaning |
|---|---|---|
| 400 | `cannot_delete_account_with_balance` | Can't close an account that still holds a cash balance |
| 400 | `pending_transactions_cannot_be_deleted` | Pending resources block closing |
| 400 | `configs_must_match_to_close` | Wrong set of configurations supplied |
| 404 | `not_found` | Resource doesn't exist |
| 429 | `account_rate_limit_exceeded` | Concurrency rate limit hit on updates |

*Why:* the HTTP status tells generic clients/proxies what *class* of problem; the stable string `code` lets programs branch
without parsing English messages, and lets Stripe reword messages freely.

**8. Response conventions.**
Responses include `id`, `object`, `created` (ISO 8601 timestamp), `livemode` (test vs live), and a free-form `metadata` map.
*Why:* `livemode` prevents mixing test and production data; `metadata` lets customers attach their own IDs without schema changes; consistent top-level
fields let one client library handle every resource.

**9. A list envelope instead of a bare array.**
`{ "data": [...] , "next_page_url": ... }` rather than `[...]`.
*Why:* you can add pagination metadata (and later, other fields) without a breaking change; a bare array can never be extended.

### 3.3 Takeaways you can reuse in an interview

- Path = **which thing**. Query = **how to filter/shape/page the collection**. Body = **the data you are sending**.
- Don't force every operation into CRUD; use `POST /resource/{id}/{action}` for real state transitions.
- Always design pagination, idempotency, versioning, and an error contract **on day one**; they are painful to retrofit.

---

## 4. Query Parameter vs Path Parameter

### 4.1 The rule of thumb

| Use a **path parameter** when... | Use a **query parameter** when... |
|---|---|
| It **identifies** a specific resource (or a position in the resource hierarchy) | It **filters, searches, sorts, paginates, or shapes** the response |
| It is **required**: the URL makes no sense without it | It is **optional**: the URL is still valid without it |
| It forms part of the resource's canonical identity/URL (cacheable, bookmarkable) | It modifies the *view* of a collection or resource |
| Example: `/accounts/{id}` | Example: `/accounts?closed=true&limit=20` |

**Simple test:** "If I remove this parameter, do I get a *different resource* (path) or the *same resource, differently presented* (query)?"
Removing `{id}` from `/accounts/{id}` gives you a different thing (the collection). Removing `?limit=20` still gives you the same collection.

### 4.2 Decision checklist

1. Identifies one resource or a parent/child relationship? **Path.**
2. Optional? **Query.**
3. Filtering, searching, sorting, pagination, field selection, expand/include? **Query.**
4. Multiple combinable criteria? **Query** (paths can't express optional combinations cleanly).
5. Sensitive data (tokens, passwords, PII)? **Neither**: use headers or the body, because URLs end up in logs, browser history and proxies.
6. Large or complex input (long lists, nested filters)? **Request body** (e.g. `POST /search`), because URLs have practical length limits.
7. State-changing action? **Not** a query param (`GET /accounts/1?delete=true` is wrong); use the right method or an action sub-path.

### 4.3 Practical consequences (why this convention matters)

- **Caching:** a path-based URL is the cache key for a resource; query strings may be treated differently by CDNs (some strip or include them), so use a query string only for variations of a view.
- **Routing:** frameworks and gateways route on the path, so path params are required for route matching, while query params are optional inputs.
- **Documentation/discoverability:** hierarchical paths read like a tree and are self-explanatory.
- **Backwards compatibility:** adding an *optional* query param is non-breaking; adding a required path segment is breaking.
- **Security/logging:** both appear in access logs, so never put secrets in either.

### 4.4 Common mistakes

| Mistake | Better |
|---|---|
| `GET /getUser?id=5` | `GET /users/5` |
| `GET /users/active` (filter as a path) | `GET /users?status=active` |
| `GET /accounts/5?action=close` | `POST /accounts/5/close` |
| `GET /orders/page/2/size/50` | `GET /orders?page=2&limit=50` |
| Deep nesting `/a/1/b/2/c/3/d/4` | Expose `/d/4` at top level, or `/d?c_id=3` |
| `GET /users?token=SECRET` | `Authorization` header |

---

## 5. Real-World Examples and Why They Do It That Way

> The Stripe rows come from the pages I fetched. The GitHub and Google examples reflect their publicly documented
> conventions (links in references); verify exact parameter names against their current docs before quoting them in an interview.

### 5.1 Stripe (payments)

| Request | Why |
|---|---|
| `GET /v2/core/accounts/{id}` | Path param identifies exactly one account. |
| `GET /v2/core/accounts?applied_configurations[0]=customer&closed=false&limit=2` | Query params filter and page the collection; all optional; default excludes closed accounts. |
| `POST /v2/core/accounts/{id}/close` + body `{"applied_configurations":["merchant"]}` | Path = which account; **body** = the data that governs the action (a confirmation set); `POST` because it's a state transition, not a delete. |
| `POST /v1/customers` + `Idempotency-Key: <uuid>` | Key in a **header**, not the URL: it is metadata about the request, not part of the resource identity. |

### 5.2 GitHub REST API (developer platform)

| Request | Why |
|---|---|
| `GET /repos/{owner}/{repo}` | Two path params together form the repository's identity (`owner/repo` is unique); hierarchical and human-readable. |
| `GET /repos/{owner}/{repo}/issues?state=open&labels=bug&sort=created&direction=desc&per_page=30&page=2` | Path = the collection's parent; query = state filter, label filter, sort, and pagination. Every query param is optional with a default. |
| `POST /repos/{owner}/{repo}/issues` + JSON body (`title`, `body`, `labels`) | Create is `POST` to the collection; data in the body. |
| `PATCH /repos/{owner}/{repo}/issues/{issue_number}` | Partial update uses `PATCH` on the item URL. |
| `PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge` | A verb-like operation modelled as a sub-resource. |

*Why they do it this way:* the path mirrors the domain hierarchy (owner > repo > issue), so URLs are guessable and permissions can map onto path prefixes;
pagination is page-number based (`page`, `per_page`) and exposed through `Link` response headers, which suits browsing UIs where jumping to a page is common.

### 5.3 Google API design guide (AIP)

Google's resource-oriented design (AIPs) standardises these patterns across its APIs:

| Pattern | Example | Why |
|---|---|---|
| Resource names in the path | `GET /v1/projects/{project}/topics/{topic}` | Full hierarchical resource name = unique identity. |
| List with `page_size` + `page_token` | `GET /v1/projects/{p}/topics?page_size=50&page_token=...` | Opaque tokens enable stable pagination and let the backend change internals. |
| Filtering/ordering as query params | `?filter=...&order_by=create_time desc` | Optional view modifiers. |
| Custom methods use `:verb` | `POST /v1/{name}:cancel` | Keeps non-CRUD actions explicit and distinct from child resource names. |

### 5.4 Generic e-commerce illustration (design from first principles)

| Need | Endpoint | Param type and reason |
|---|---|---|
| Get one order | `GET /orders/{orderId}` | Path: identity. |
| List a customer's orders | `GET /customers/{customerId}/orders?status=shipped&limit=20&cursor=...` | Path: ownership hierarchy. Query: filter and page. |
| Search products | `GET /products?q=shoes&min_price=50&sort=-price` | Query: all optional, combinable criteria. |
| Place an order safely | `POST /orders` + `Idempotency-Key` header | Body carries items; header protects against double submit. |
| Cancel an order | `POST /orders/{orderId}/cancel` | Action sub-path; it's a state change with rules (can't cancel after shipping). |
| Big filter set | `POST /orders/search` + JSON body | Body: input too complex or long for a URL. |

---

## 6. API Design Interview Template

Use this order when asked "Design the API for X":

1. **Clarify:** clients, scale, read/write ratio, consistency needs, auth model, rate limits, global or regional.
2. **Identify resources (nouns)** and relationships (draw a small ER sketch).
3. **Define endpoints** (method + path + params + body + success/error codes) for the core use cases first.
4. **Specify request/response schemas** with an example JSON for the main endpoints.
5. **Cross-cutting concerns:** auth, versioning, pagination, filtering, idempotency, rate limiting, error format, async operations/webhooks.
6. **Back-end design:** data model and DB choice, caching, queues, sharding/replication, how the endpoint stays fast under load.
7. **Failure modes and trade-offs:** retries, timeouts, partial failure, consistency vs availability, what you would monitor.
8. **Security and compliance:** PII handling, audit logs, data retention, encryption.

**Mini example: "Design a Library API"**

```http
GET    /v1/books?author=orwell&available=true&limit=20&page=<token>   # search/filter (query)
GET    /v1/books/{bookId}                                              # one book (path)
POST   /v1/members/{memberId}/loans        Idempotency-Key: <uuid>     # borrow (creates a loan)
POST   /v1/loans/{loanId}/return                                       # action on a loan
GET    /v1/members/{memberId}/loans?status=overdue                     # list with filter
```

Talk through: `409 Conflict` when the book is already on loan, optimistic locking on inventory, caching for the catalogue,
strong consistency for loan state, eventual consistency for search indexing.

---

## 7. References

**Stripe (fetched and read for this guide)**
- Stripe, *Accounts v2 API*: <https://docs.stripe.com/api/v2/core/accounts>
- Stripe, *List accounts*: <https://docs.stripe.com/api/v2/core/accounts/list>
- Stripe, *Close an account*: <https://docs.stripe.com/api/v2/core/accounts/close>
- Stripe, *Idempotent requests*: <https://docs.stripe.com/api/idempotent_requests>
- Stripe, *API v2 overview* (versioning header, idempotency, page tokens): <https://docs.stripe.com/api-v2-overview>

**Your provided link (could not be fetched: LinkedIn blocks automated access)**
- Tai Chia Makris Huang, *API Design Interview Preparation*: <https://www.linkedin.com/pulse/api-design-interview-preparation-tai-chia-makris-huang/>

**Standards and design guides (cited from general knowledge; open them to confirm details)**
- RFC 9110, *HTTP Semantics* (methods, safe/idempotent, status codes): <https://www.rfc-editor.org/rfc/rfc9110>
- RFC 9457, *Problem Details for HTTP APIs*: <https://www.rfc-editor.org/rfc/rfc9457>
- GitHub REST API documentation: <https://docs.github.com/en/rest>
- Google API Improvement Proposals (resource-oriented design, pagination, custom methods): <https://google.aip.dev/>
- Microsoft REST API Guidelines: <https://github.com/microsoft/api-guidelines>
- Roy Fielding, *Architectural Styles and the Design of Network-based Software Architectures* (REST dissertation): <https://ics.uci.edu/~fielding/pubs/dissertation/top.htm>

**Interview-prep context**
- Design Gurus, *How to do an API design interview?*: <https://www.designgurus.io/answers/detail/how-to-do-an-api-design-interview>
- Educative, *The Complete Guide to Grokking the API Design Interview*: <https://educative.io/blog/grokking-the-api-design-interview>
