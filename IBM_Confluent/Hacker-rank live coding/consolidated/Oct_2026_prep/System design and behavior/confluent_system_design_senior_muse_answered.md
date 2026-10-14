# Confluent Senior/Staff System Design Prep

Source of truth: `~/workspace/user/files/system_design.md` (Henry's curated questions, incl. Jack's streaming/Kafka set).
Companion: `~/workspace/confluent_solutions.md` (SD1–SD3 + briefs — this file goes deeper and covers what that file doesn't).

**How to use this in the interview:** for every problem, open with 3–5 clarifying questions, state NFRs with numbers, sketch HLD, then go deep on ONE hard sub-problem (that's the senior signal — juniors stay broad, seniors pick the crux and go deep). Narrate trade-offs out loud. Always name what you'd do differently at 10x scale.

**Universal path-parameter vs query-parameter rule** (applied per-endpoint below):
- **Path param** = resource identity / hierarchy. `GET /channels/{channelId}`. The param identifies *which thing*. Path params are required, ordered, and part of the cache key — good for CDN/edge caching.
- **Query param** = filtering, sorting, pagination, optional modifiers, search. `GET /channels?genre=comedy&sort=followers`. Optional, unordered, omittable — changing them doesn't change *which* resource, only the *view* of it.
- Corollary: never put secrets or PII in either (they land in logs); use headers/body. Prefer `POST` for non-idempotent creates, `PUT` for idempotent full replace, `PATCH` for partial. Version in the path (`/v1/...`) when the API is public and long-lived; version in a header for internal services.

---

## 1. Temp Email Generator (HLD, API, entities, DB choices, NFRs)

*Asked as: temp email HLD + API + entities + DB choices + NFRs. The crux is expiry lifecycle and inbound mail ingestion.*

### Requirements
**Functional:**
- Generate a disposable address on demand (no signup), e.g. `abc123@tempmail.example.com`
- Receive emails to that address; user views inbox + message bodies via API/UI
- Addresses auto-expire after a configurable TTL (default 5 hours, per the Confluent report); user can delete early or extend once
- Optional: reply/forward disabled (keeps abuse surface small — say this explicitly)

**NFRs (concrete):**
- 100k active addresses at a time; 1M emails/day inbound (~12/sec avg, 100/sec peak)
- p99 inbox-read latency < 200 ms; email visible within 30 s of arrival (not real-time — say why: SMTP store-and-forward)
- Durability: once ACKed by our MX, email must survive single-node loss (RPO ≈ 0 for accepted mail)
- TTL enforcement: expired data actually deleted within ~1 h of expiry (privacy promise — this is the senior talking point)
- Abuse: rate-limit generation (10/hr/IP), blocklist known throwaway-abuse domains downstream is out of scope

### REST API design
| Method & path | Purpose | Param rationale |
|---|---|---|
| `POST /v1/addresses` | Create address. Body: `{"ttl_hours": 5}` | No params at all — creation takes a body. Returns `201` + `Location: /v1/addresses/{id}`. Idempotency: accept `Idempotency-Key` header (safe retry on flaky mobile networks). |
| `GET /v1/addresses/{addressId}` | Address metadata (created_at, expires_at) | **Path param**: identity of the resource. |
| `DELETE /v1/addresses/{addressId}` | Early delete (burn it) | **Path param**: identity; DELETE is idempotent — deleting twice returns 204 both times (say this). |
| `POST /v1/addresses/{addressId}:extend` | Extend TTL once | **Path param** for identity + custom verb `:extend` (Google API style) because "extend" isn't a resource — it's an action. Alternative `PATCH /v1/addresses/{id}` with body — mention both, pick the verb form and justify: clearer intent, avoids PATCH partial-update semantics debates. |
| `GET /v1/addresses/{addressId}/messages` | List inbox messages | **Path param** for the parent identity (hierarchy: address → messages); pagination/filter as **query params**: `?limit=20&cursor=...&unread_only=true`. Rationale: cursor/limit are a *view* of the collection, optional and unordered. |
| `GET /v1/addresses/{addressId}/messages/{messageId}` | Full message (headers + body) | **Path params** all the way down the hierarchy. Cacheable GET — good. |
| `DELETE /v1/addresses/{addressId}/messages/{messageId}` | Delete one message | Path params (identity). |

**Why query params for pagination, not path:** `/messages/page/2` bakes presentation into identity — breaks if you change page size, and each page becomes a "different resource" to caches. Cursor in query string keeps one resource (`messages` collection) with many views.

### HLD
```
[Internet] --SMTP--> [MX receivers (stateless, N nodes)] --enqueue--> [Kafka: inbound-mail]
                                                                              |
[API gateway] <--HTTPS-- [API service (stateless)] <--read/write--> [Postgres: addresses, messages meta]
      |                                                        \
[WebSocket/SSE: inbox push]                              [Object store (S3): raw MIME bodies]
                                                                              |
[Expiry sweeper (cron/leader)] --delete--> [Postgres + S3]   [Kafka consumer: mail-processor]
```
**Flow:**
1. `POST /v1/addresses` → API service generates `addressId` (ULID — time-ordered, no coordination), inserts row with `expires_at = now + ttl`, returns address string.
2. Inbound SMTP: MX receivers accept mail, do cheap validation (is local-part a known active address? — Bloom filter in memory, backed by Postgres), publish raw MIME to Kafka `inbound-mail`. **Why Kafka here:** SMTP delivery is bursty and parsing can be slow; the queue decouples acceptance (must be fast, sender retries otherwise) from processing. Also gives replay if the processor has a bug.
3. Mail processor: parses MIME, extracts headers/body/attachments metadata, writes metadata row to Postgres, raw body to S3, marks message visible. Emits event for SSE push.
4. Expiry: sweeper runs every 5 min, `DELETE ... WHERE expires_at < now()` in batches (with `LIMIT`, to avoid long locks), then deletes S3 objects. **Senior point:** soft-delete first (tombstone), hard-delete async — so a slightly-late read doesn't 500, and S3 deletes (eventual) don't block.

### LLD — key modules
- `AddressService`: `create(ttl)` → ULID gen + insert; `extend(id)` → check `extended_once` flag, single `UPDATE ... WHERE id=? AND extended_once=false` (atomic compare-and-set in SQL — no distributed lock needed).
- `MailProcessor`: streaming MIME parser (don't load 25 MB attachments into heap — parse to S3 with bounded buffers); idempotency key = `Message-ID` header + recipient → dedupe re-deliveries (SMTP retries!).
- `ExpirySweeper`: batch deletes with `LIMIT 1000`, ordered by `expires_at` index; emits metrics (deleted_rows) for the privacy SLA.
- Concurrency: API nodes stateless; all coordination via DB constraints (unique address, idempotency keys). No in-process state that breaks on scale-out.

### DB choices — every one justified
| Store | Holds | WHY |
|---|---|---|
| **PostgreSQL** | addresses, message metadata, idempotency keys | Access pattern is relational + transactional: "address + its messages" joins, atomic extend-once via `UPDATE..WHERE`, unique constraints for dedupe. ACID here is worth the cost — this is CP-leaning metadata. **Rejected:** DynamoDB — conditional writes could work, but joins/pagination over inbox are awkward and GSIs multiply cost; **Rejected:** pure Redis — durability story for accepted mail is weak. |
| **S3 / object store** | raw MIME bodies | Immutable blobs, 10 KB–25 MB, write-once/read-rarely. Object store is 10x cheaper than DB BLOBs and doesn't bloat Postgres (keeps autovacuum sane). Lifecycle policy as backstop for the sweeper. **Rejected:** storing bodies in Postgres `bytea` — table bloat kills index performance and backups balloon. |
| **Kafka** | inbound-mail topic | Durable buffer between SMTP acceptance and processing; replay on processor bugs; absorbs bursts. **Rejected:** direct HTTP handoff MX→API — one slow parse = SMTP timeout = sender retry storm. |
| **Redis (optional)** | active-address Bloom filter + rate-limit counters | Hot-path check "is this local-part live?" without hitting Postgres per RCPT TO. Loss-tolerant (rebuild from DB). |

**CAP/PACELC:** metadata path is PC/EC — on a partition, prefer refusing new mail (correctness of the expiry/privacy promise) over accepting mail we might lose. Inbox reads are PA/EL — serve slightly stale inbox rather than fail.

### Senior signals
- **Trade-offs to state:** soft-delete + async hard delete (privacy SLA vs. simplicity); Kafka between MX and processor (latency + ops cost vs. resilience to bursts/retries); ULID vs. UUID (time-ordered → index-friendly inserts, but leaks creation time — fine here).
- **Failure modes:** MX node dies mid-SMTP → sender retries (SMTP is at-least-once — that's why idempotency on `Message-ID` matters); processor poison message → DLQ + alert, don't block the partition; sweeper falls behind → metric + page (privacy SLA breach).
- **Talking points:** "Expiry isn't a cron nicety, it's the product promise — I measure deletion lag as an SLI." "SMTP gives at-least-once delivery, so the whole inbound path must be idempotent."
- **Likely follow-ups:** "How do you prevent someone from reading *my* temp address?" → unguessable 128-bit local-part, no listing API, rate-limit reads. "10x inbound burst?" → add MX nodes (stateless) + Kafka absorbs; processor scales on consumer lag.

---

## 2. Podcast Service with Feed Generation

*Asked as: podcast service, focus on feed generation. The crux is fan-out for feed reads.*

### Requirements
**Functional:**
- Creators: create channel, publish episodes (audio file + metadata)
- Users: subscribe/unsubscribe, home feed (latest episodes from subscriptions, ranked by recency), top-N episodes per channel, search
- Feed generation: the hard part — materialize or compute per-user feed

**NFRs:**
- 10M users, 500k channels, 5M episodes; avg 50 subs/user
- Feed read p99 < 300 ms; new episode visible in follower feeds within 60 s (say: not instant — justify)
- Write: 10k episode publishes/day (low); reads: 50k feed reads/sec peak (high) → read-heavy, cache-friendly

### REST API design
| Method & path | Purpose | Param rationale |
|---|---|---|
| `POST /v1/channels` | Create channel (creator) | Body. Returns `201` + Location. |
| `GET /v1/channels/{channelId}` | Channel metadata | **Path param**: identity. Heavily cacheable (CDN, long TTL — metadata changes rarely). |
| `GET /v1/channels/{channelId}/episodes` | Episodes of a channel | **Path param** for hierarchy; `?limit&cursor&sort=newest` as **query params** (pagination/sort = view modifiers). |
| `GET /v1/channels/{channelId}/episodes/{episodeId}` | Episode detail | Path params down the hierarchy. |
| `POST /v1/channels/{channelId}/episodes` | Publish episode (multipart upload or upload-then-attach pattern) | Path param = parent identity. For the audio bytes: prefer `POST /v1/uploads` → returns upload URL/ID, then attach `upload_id` in the episode body — keeps the API JSON-clean and lets uploads go direct-to-S3 (presigned URLs). |
| `POST /v1/subscriptions` body `{"channel_id": ...}` | Subscribe | Hmm — or `PUT /v1/users/{userId}/subscriptions/{channelId}` (idempotent put = natural for subscribe; repeat subscribe is a no-op → 200). **Mention both; pick PUT** and justify: subscribe is idempotent state-set, and path params express the (user, channel) identity. |
| `DELETE /v1/users/{userId}/subscriptions/{channelId}` | Unsubscribe | Path params; idempotent. |
| `GET /v1/feed` | Home feed | **Query params**: `?cursor=&limit=20`. No path param — the feed is scoped to the auth'd user (from the auth token, not the URL — never put userId in the path for "me" resources; it leaks identity and breaks caching). |
| `GET /v1/episodes/top` | Top-N episodes | **Query params**: `?n=10&window=7d&genre=tech`. Top-N is a computed view with modifiers → query params. |
| `GET /v1/search?q=...&type=channel,episode` | Search | **Query param**: `q` is a filter, not identity. |

### HLD
```
[Clients] -> [API GW + auth] -> [API service (stateless)]
      |-> [Postgres: users, channels, episodes, subscriptions]
      |-> [S3: audio files]  (CDN in front for playback)
      |-> [Feed path] --> [Redis: materialized feeds] <-- [Feed fan-out workers] <-- [Kafka: episode-published]
      |-> [Search: OpenSearch/Elasticsearch] <-- [Kafka: metadata-changes]
```
**Flow — the feed decision (go deep here, it's the asked focus):**
- **Push (fan-out-on-write):** on `episode-published`, worker appends episode ID to each subscriber's Redis list (trim to last ~500). Feed read = single `LRANGE` → O(1), p99 trivially met.
- **Pull (fan-out-on-read):** on feed read, gather latest episodes from all subscribed channels and merge. No write amplification, but read does N channel lookups — dies at "user subscribed to 2,000 channels."
- **Senior answer: hybrid.** Push for normal channels; for "celebrity" channels (>100k subs), *don't* fan out (write amplification = 100k Redis writes per episode) — mark them and merge at read time (pull). Threshold is a config, measured. This is exactly the Twitter-style answer; say the threshold explicitly and how you'd tune it (p99 write latency on publish vs. p99 feed read).
- New episode visibility ≤ 60 s: Kafka consumer lag + fan-out time; monitor consumer lag as the SLI.

### Back-of-envelope
- Feed reads: 50k/sec × 20 episode IDs × ~100 bytes = 100 MB/sec from Redis — needs Redis Cluster (~10 shards with headroom), or accept Postgres? No — Postgres at 50k point-reads/sec needs heavy read replicas; Redis is the right call, say why.
- Storage: 5M episodes × metadata 2 KB = 10 GB Postgres (trivial); audio 5M × 50 MB = 250 TB S3 (dominant cost — say it).
- Fan-out writes: 10k publishes/day × avg 1k subs = 10M Redis writes/day ≈ 115/sec avg — trivial; celebrity publishes are the tail risk.

### LLD — key pieces
- `FeedService.getFeed(userId, cursor, limit)`: `ZREVRANGE`-style read from Redis sorted set (score = publish_ts) → batch-fetch episode metadata from Postgres/Redis cache → merge celebrity-channel pull results → cursor = last score+id (cursor must be opaque & stable — never expose offsets).
- `FanoutWorker.onEpisodePublished`: fetch subscriber IDs in pages (don't load 100k IDs into memory — **stream** them), pipeline `ZADD`s, trim with `ZREMTBYRANK`. Idempotency: episode ID in the ZSET member — replays are naturally deduped.
- `SubscriptionService`: `subscriptions(user_id, channel_id)` PK — both subscribe-state check and fan-out source in one table.

### DB choices
| Store | Holds | WHY |
|---|---|---|
| **PostgreSQL** | users, channels, episodes, subscriptions | Relational core: joins (my subscriptions × episode metadata), ACID for publish (episode row + S3 key must be consistent — use transactional outbox to Kafka), pagination. **Rejected:** Mongo — joins across subscriptions/episodes get painful; **Rejected:** Cassandra — subscriptions are relational, not time-series. |
| **Redis (Cluster)** | materialized feeds (ZSET per user), episode metadata cache | ZSET gives ordered feed with O(log n) insert + O(1)-ish range reads; sub-ms p99. Ephemeral-ish (rebuildable from Postgres+Kafka replay). **Rejected:** doing fan-out in Postgres — 50k reads/sec of merged feeds would need an army of replicas. |
| **S3 + CDN** | audio | Immutable large blobs; CDN handles the actual bandwidth (playback is the real scale, not the API). |
| **Kafka** | episode-published, metadata-changes | Decouples publish from fan-out/search indexing; replay for new consumers. |
| **OpenSearch** | search index | Full-text over titles/descriptions — Postgres `tsvector` works to a point; say you'd start with Postgres FTS and move to OpenSearch when relevance tuning matters (senior: don't introduce infra prematurely). |

**CAP/PACELC:** feed reads PA/EL (stale feed OK); subscriptions/publish PC/EC (don't lose a subscribe).

### Senior signals
- **The crux:** hybrid fan-out with explicit celebrity threshold — name the number, name how you tune it.
- **Failure modes:** fan-out worker crash mid-publish → some feeds missing the episode → make fan-out idempotent (ZADD by episode ID) and add a reconciler that replays recent publishes; Redis shard loss → rebuild from Postgres (feeds are a cache, say it).
- **Talking points:** "Feed generation is a write-vs-read trade-off; I push the cost to write time because reads outnumber writes 5000:1 here." "Cursor, not offset — offsets break when the feed mutates between pages."
- **Follow-ups:** "User with 50k subscriptions opens the app" → cap pull-merge with timeout + degrade to top channels; "exactly-once fan-out" → idempotent ZADD makes at-least-once delivery fine.

---

## 3. TinyURL / URL Shortener (read-heavy)

*Asked with the constraint: optimize for high read volume; keep it simple — singleton-ish service, range-sharded DB, edge caching. The senior move is to honor the constraint instead of over-engineering.*

### Requirements
**Functional:** shorten long URL → short code; resolve short code → 301/302 redirect; optional custom alias; optional expiry; basic click stats (defer — say so).
**NFRs:** 100:1 read:write; 10k writes/day, 1M reads/day growing to 100M/day; p99 resolve < 50 ms; short codes 7 chars; no collisions, ever.

### REST API design
| Method & path | Purpose | Param rationale |
|---|---|---|
| `POST /v1/urls` body `{"long_url": ..., "custom_alias"?: ..., "ttl_days"?: ...}` | Create short URL | Body for creation. Returns `201 {"short_url": "https://sho.rt/aB3x9Yz"}`. Idempotency-Key header for safe retry (creating twice must not mint two codes). |
| `GET /{shortCode}` | Resolve → redirect | **Path param**: the code *is* the resource identity. `302 Found` (not 301!) — **say why**: 301 is cached permanently by browsers, which (a) breaks click analytics and (b) makes changing the destination impossible. 302 keeps control server-side. This is a classic senior gotcha. |
| `GET /v1/urls/{shortCode}` | Metadata (long URL, created_at, clicks) | Path param = identity. (Separate from the redirect endpoint — one is for humans/browsers, one is for API clients.) |
| `DELETE /v1/urls/{shortCode}` | Delete/expiry | Path param; idempotent. |

No query params needed in v1 — and that's a point to make: the API surface is tiny because the problem is tiny.

### Key generation — the core decision
- **Counter + base62 (pick this):** single logical counter (or range-allocated blocks per node), encode in base62 → 7 chars ≈ 3.5T codes. **Why:** guaranteed unique, no collision handling, short codes are dense, monotonic-ish. Needs a counter service — but one ZooKeeper/etcd-backed counter or DB sequence with block preallocation (each node grabs 1k IDs) is simple and proven.
- **Rejected — hash(MD5) truncated:** collisions need handling (check-and-retry loop), codes aren't shorter, and you still need a uniqueness check against the DB — all the complexity of the counter with none of the guarantees. Hashing only wins if you need *decentralized* generation with no coordination, which the read-heavy constraint doesn't require.
- Custom aliases: check uniqueness in DB at write time (rare path, contention acceptable).

### HLD
```
[Clients] -> [CDN/edge cache] -> [LB] -> [API nodes (stateless)] -> [Redis: code->URL cache]
                                                                    |
                                                              [Postgres/MySQL sharded: urls]
```
**Flow:** resolve = edge cache → Redis → DB (cache-aside, populate on miss). Create = allocate ID → base62 → insert DB → (lazy cache fill on first resolve, not on write — writes are rare, don't pay cache-write cost upfront... actually mention both and pick lazy: simpler, and the first resolve warms it).

### Scale math
- 100M reads/day ≈ 1.2k/sec avg, 10k/sec peak. One Redis cluster handles this trivially; with 90%+ hit rate, DB sees ~1k/sec — a single primary + 2 replicas is fine. **Say the numbers** — the constraint says don't over-engineer, and the math proves a modest setup suffices.
- Storage: 1B URLs × ~500 bytes/row = 500 GB → range-shard by code prefix across ~4–8 Postgres nodes when you get there (not day one).

### DB choices
| Store | Holds | WHY |
|---|---|---|
| **PostgreSQL/MySQL (range-sharded later)** | code → long_url, created_at, owner | Simple KV-ish relational row; range sharding on the code is trivially routable (first char → shard); ACID for the uniqueness invariant. **Rejected:** Cassandra — no need for its write scale or its operational weight; tunable consistency is complexity you don't need for 10k writes/day. |
| **Redis** | hot code→URL cache, TTL 24 h | Read-heavy workload → cache hit rate is the whole game; p99 < 50 ms needs memory-speed. **Rejected:** in-process cache — breaks on multi-node (inconsistent deletes) and restarts cold. |
| **CDN/edge** | redirect responses | Redirects are perfectly cacheable (same code → same destination) — push them to the edge and origin barely sees traffic. Note the tension with 302 analytics: if you need per-click counting, edge caching must be short-TTL or bypassed — **name the trade-off**. |

**CAP:** AP-leaning reads (serve stale redirect briefly rather than fail); CP for creation (uniqueness).

### Senior signals
- **Honor the constraint:** explicitly say "given read-heavy + simple, I'm *not* building a distributed ID service or multi-region active-active on day one — here's the math showing why." Interviewers test whether you can *not* over-design.
- **302 vs 301** — say it unprompted.
- **Failure modes:** counter node dies → standby takes over with preallocated block (no duplicate IDs because blocks are disjoint); cache stampede on a viral link → request coalescing (singleflight) at the API layer.
- **Follow-ups:** "10x overnight (100M→1B reads/day)?" → edge cache absorbs most; add Redis shards; DB stays untouched. "Malicious long URLs?" → validate scheme, blocklist, rate-limit creates.

---

## 4. Spotify-like API Design (podcast channels, clips per channel, pagination)

*Asked as an API-design round: retrieve X channels at a time, X clips per channel, DB design, HLD, pagination/limit-offset/skip-tokens, versioning, back-of-napkin math, corner cases (heavy subscribers, huge channels). This is section 2's sibling — the emphasis here is API surface quality.*

### Requirements
**Functional:** browse channels (paginated), list clips per channel (paginated), clip detail, subscribe. Corner cases: user subscribed to 10k channels; channel with 100k clips.
**NFRs:** 50M users, 2M channels, 100M clips; browse p99 < 250 ms; catalog data changes slowly (cache aggressively).

### REST API design — the graded part
| Method & path | Purpose | Param rationale |
|---|---|---|
| `GET /v1/channels` | List channels | **Query params**: `?limit=20&cursor=...&genre=tech&sort=popular`. All optional view modifiers. **Cursor (opaque skip-token), NOT limit/offset** — say why: offset breaks under concurrent inserts (duplicates/skips) and is O(offset) in the DB; cursor on `(sort_key, id)` is stable and index-friendly. |
| `GET /v1/channels/{channelId}` | Channel detail | **Path param** identity. `ETag` + `Cache-Control: max-age=3600` — channel metadata is near-static. |
| `GET /v1/channels/{channelId}/clips` | Clips of a channel | **Path param** hierarchy + **query** `?limit&cursor&sort=newest`. For the 100k-clip channel: keyset pagination on `(published_at, clip_id)` keeps every page O(limit). |
| `GET /v1/channels/{channelId}/clips/{clipId}` | Clip detail | Path params. Long cache TTL. |
| `GET /v1/me/subscriptions` | My subscriptions | `/me` from auth token (not `/users/{id}` — privacy + cache-safety, as in §2). **Query** `?limit&cursor`. |
| `PUT /v1/me/subscriptions/{channelId}` | Subscribe | Idempotent PUT, path param identity of the (me, channel) relation. |
| `DELETE /v1/me/subscriptions/{channelId}` | Unsubscribe | Same. |

**Versioning:** `/v1/` in path — public API, long-lived, clients pin versions. **Say:** internal service-to-service would use header versioning or no versioning (deploy together), but public needs path versions.

**Pagination contract (say it explicitly):** response envelope `{"data": [...], "paging": {"next_cursor": "opaque", "has_more": bool}}`. Cursor is base64 of `(last_sort_key, last_id)` — never expose DB offsets. Limit clamped server-side (`min(requested, 100)`).

### Back-of-napkin (they explicitly ask)
- Users 50M → channels 2M → clips 100M (50 clips/channel avg). Metadata: clip 1 KB → 100 GB; channel 2 KB → 4 GB. Fits one Postgres comfortably on storage; the scaling question is *read QPS*, not size.
- Browse: assume 5% DAU, 10 browse req/user/day → 25M/day ≈ 300/sec avg, 3k/sec peak. CDN + Redis absorb 90% → DB sees ~300/sec — single primary + replicas fine.
- Heavy subscriber (10k subs): subscription list itself paginated; feed uses §2's hybrid fan-out — cross-reference it.

### HLD
```
[Clients] -> [CDN] -> [API GW] -> [Catalog service (read-optimized, stateless)]
                                    |-> [Postgres: channels, clips, subscriptions] (read replicas)
                                    |-> [Redis: clip/channel detail cache, TTL 1h]
                                    |-> [OpenSearch: browse/search]
[Ingest service] -> [Postgres primary] -> [Kafka: catalog-changes] -> [cache invalidator, search indexer]
```
**Flow:** writes go through ingest → Postgres primary → outbox to Kafka → async cache invalidation + search indexing. Reads never touch the primary (replicas + cache). **Why separate ingest from catalog reads:** write path needs validation/transactions; read path needs fan-out scale — different scaling axes, so different services (this is the monolith→microservices instinct applied surgically).

### LLD
- `CatalogService.listClips(channelId, cursor, limit)`: decode cursor → `WHERE channel_id=? AND (published_at, id) < (?,?) ORDER BY published_at DESC, id DESC LIMIT ?` — single index range scan, O(limit). No `OFFSET`.
- `SubscriptionService`: `subscriptions(user_id, channel_id)` composite PK; `countSubscriptions` cached in Redis with write-through on subscribe/unsubscribe (counter cache — say the invalidation strategy).
- Cache keys: `clip:{id}`, `channel:{id}`; invalidation by key on catalog-changes (not TTL-only — TTL-only gives stale clips for an hour; **say which staleness you accept where**: clip *metadata* stale 5 min OK, subscription *state* must be read-your-write → read subscriptions from DB primary or invalidate synchronously).

### DB choices
| Store | Holds | WHY |
|---|---|---|
| **PostgreSQL** | channels, clips, subscriptions | Relational + keyset pagination on composite indexes; ACID for subscribe/unsubscribe counters. **Rejected:** DynamoDB — keyset pagination across "clips by channel sorted by time" needs a GSI per access pattern and costs scale with read units; relational is cheaper here. |
| **Redis** | detail cache, subscription counters | p99 < 250 ms on hot clips; counters for "N subscribers" without `COUNT(*)`. |
| **OpenSearch** | browse/search | Faceted browse (genre, popularity) — beyond what B-tree indexes do well. Start with Postgres FTS, graduate when relevance matters (repeat the "don't prematureize" line — it's a senior marker). |
| **CDN** | channel/clip detail GETs | Near-static content — edge caching is nearly free scale. |

### Senior signals
- **Cursor > offset** — derive it from first principles (stability under mutation + index efficiency), don't just assert it.
- **Corner cases they asked about:** 10k-subscription user → paginate the subscription list, cap fan-out; 100k-clip channel → keyset pagination keeps it O(limit), plus "top clips" precomputed view.
- **Talking points:** "I version in the path because this API is public and clients pin versions." "Read-your-write for subscription state, eventual for catalog metadata — different consistency per access pattern."
- **Follow-ups:** "Change the clip schema (add chapters)?" → additive, nullable columns + API versioning; old clients ignore unknown fields (say: never rename/remove without a version bump).

---

## 5. Clicks-per-Page over Last 5 Minutes

*Jack's Interview 2/3: ingestion → processing → storage → reads. Must handle 10x traffic, late events, worker crashes. This is a streaming-systems design — Confluent's home turf. Go deep.*

### Requirements
**Functional:** dashboard shows per-page click counts over trailing 5 minutes, updating ~every few seconds. Late events (up to ~1 min late) must correct counts. (The 10-min-late variant is §8; keep 1 min here per the question.)
**NFRs:** 100k clicks/sec baseline (design for 1M/sec = 10x); read QPS 1k/sec dashboard; end-to-end freshness p99 < 10 s; exactly-once *effect* on counts (no double-count on worker crash); late events up to 60 s handled, later dropped+counted (metric).

### REST API design
| Method & path | Purpose | Param rationale |
|---|---|---|
| `POST /v1/events` body `{"page_id","ts","user_id"?}` | Ingest click | Body (event payload, not identity). Return `202 Accepted` — **say why 202 not 200**: ingestion is async; 202 means "accepted for processing," honest about the pipeline. Idempotency-Key header → dedupe at ingestion (at-least-once producers). |
| `GET /v1/stats/pages/{pageId}/clicks` | Clicks for one page | **Path param** identity + **query** `?window=5m&resolution=10s`. Window/resolution are view modifiers → query. |
| `GET /v1/stats/pages/clicks` | Top pages | **Query params**: `?window=5m&limit=100&sort=clicks_desc`. Filtering/sorting/pagination → query. (Compare: single-page stats = path identity; top-N = computed view = query.) |
| `GET /v1/stats/pages/{pageId}/clicks/series` | Time series | Path identity + query `?window=5m&bucket=10s`. |

### HLD
```
[Clients] --POST--> [Ingest API (stateless, validates, dedupes)] --append--> [Kafka: clicks (keyed by page_id)]
                                                                                    |
[Stream processor: Flink / Kafka Streams] --reads--> [Kafka] --writes--> [Cassandra/Scylla: counts]
        |                                                              [Redis: hot top-N cache]
        +--checkpointing--> [S3: checkpoints/state backend]
[Dashboard API] --reads--> [Cassandra] / [Redis]
```
**Flow:**
1. Ingest: validate schema, attach `ingest_ts`, dedupe by idempotency key (Redis SETNX with TTL), append to Kafka keyed by `page_id` (**why keyed:** same page → same partition → per-page ordering, which makes windowed aggregation deterministic).
2. Stream processor: 10-second tumbling windows (or 5-min sliding with 10-s slide — **pick tumbling 10-s windows and sum 30 of them at read time**; say why: sliding windows multiply state 30x, tumbling + read-time sum is cheaper and the dashboard buckets are 10 s anyway).
3. State: per `(page_id, window_start)` count in the processor's state store (RocksDB), checkpointed to S3 every ~10 s.
4. Sink: upsert counts to Cassandra; dashboard reads latest 30 windows per page and sums, or reads a pre-aggregated 5-min rollup.
5. **Late events:** allowed lateness 60 s — events with `event_ts` within watermark+60 s update the window (retraction/upsert); later → side output + `dropped_late_events_total` metric. Watermark = max observed event_ts − 60 s.

### Back-of-envelope
- 1M events/sec × ~100 bytes = 100 MB/sec into Kafka → ~30 partitions × 3 replicas is comfortable (Kafka does ~10s of MB/sec per partition).
- State: distinct pages ~1M × 30 windows × 16 bytes ≈ 480 MB per processor instance — fits RocksDB, checkpoint to S3 is seconds.
- Cassandra: 1M pages × 30 windows = 30M rows, each tiny; writes 1M/sec ÷ windows… actually writes are per (page, window) upserts — with 10-s windows that's ~100k upserts/sec at 1M events/sec (many events share a window). Cassandra handles this on a modest cluster; **say the dedup math** — aggregation before the DB is the whole reason the DB survives.

### LLD — stream processor internals
- `ClickAggregator`: keyed stream by `page_id` → `window(TumblingEventTimeWindows.of(10s))` → `aggregate(count)` with `allowedLateness(60s)` → sink `upsert(page_id, window_start, count)`.
- **Exactly-once effect:** Kafka transactions (EOS) from source → processor → sink, *or* idempotent upserts (`INSERT ... ` with the full key `(page_id, window_start)` — replaying the same count is a no-op overwrite). **Senior point:** prefer idempotent sinks over distributed transactions when the data model allows it — simpler, no 2PC.
- **Worker crash:** checkpoint restore from S3 → replays Kafka from last committed offset → counts recomputed, idempotent sink absorbs dupes. Say the recovery-time math: state 500 MB from S3 ≈ seconds; Kafka replay bounded by checkpoint interval.
- Out-of-order within lateness: event-time (not processing-time) windows — **say why**: processing-time windows give wrong answers the moment anything is delayed.

### DB choices
| Store | Holds | WHY |
|---|---|---|
| **Kafka** | raw clicks | Ordered, replayable, partitioned by page_id; absorbs 10x bursts (that's literally what the log is for). **Rejected:** direct HTTP to processor — no backpressure story, no replay. |
| **Cassandra / ScyllaDB** | `(page_id, window_start) → count` | Write-heavy time-series-ish upserts; partition key `page_id`, clustering `window_start` → "last 30 windows for page X" is one partition read. Tunable consistency (ONE/QUORUM). **Rejected:** Postgres — 100k upserts/sec of counters = vacuum/lock pain; **Rejected:** Redis as primary — 30M rows × persistence = expensive and RDB/AOF recovery is slower than Cassandra's SSTables. |
| **Redis** | top-N leaderboard cache, idempotency keys | Top-N over 1M pages per dashboard refresh is a full scan — precompute top-N in the processor, cache in Redis, 5-s TTL. |
| **S3** | Flink/RocksDB checkpoints | Cheap durable state backend; recovery reads sequentially (fast). |

**CAP/PACELC:** counts are PA/EL (approximate-now beats unavailable); ingestion PC/EC (don't silently drop accepted clicks — 202 means durable in Kafka).

### Senior signals
- **The crux decisions:** event-time + watermarks (not processing time); tumbling windows + read-time sum (not sliding); idempotent upserts instead of transactions; keying by page_id for deterministic aggregation.
- **10x traffic:** "nothing architectural changes — add Kafka partitions, add processor task managers (stateless scale), add Cassandra nodes. The design *is* the scale story." Backpressure: Kafka consumer lag metric → autoscale processors; ingest sheds load with 429 + client retry (say it).
- **Failure modes:** processor crash → checkpoint restore (quantify: seconds); Kafka broker loss → replication factor 3, min ISR 2; late-data spike → allowed lateness absorbs, beyond → counted + dropped (metric, not silent).
- **Talking points:** "I use event time because the dashboard answers 'what happened,' not 'what arrived.'" "Exactly-once *effect* via idempotent sinks — I avoid distributed transactions where the data model lets me."
- **Follow-ups:** "10-min late events?" → that's §8's variant: longer lateness = bigger state; answer: keep 60-s fast path, route older to a batch correction job (Lambda-ish) that rewrites windows hourly. "Per-user counts too?" → key space explodes (100M users) — state becomes the constraint; say it and propose sampling or HyperLogLog for distinct counts.

---

## 6. Distributed Persistent KV Store (high write throughput)

*The Confluent-home-turf question. High write throughput, low latency, fault-tolerant, persistent, network service. Both single-host (LevelDB-style) and distributed (Redis/Memcache-style) were mentioned — address both.*

### Requirements
**Functional:** `GET/PUT/DELETE` by key; TTL optional; range scans optional (say: include or exclude — pick exclude for v1, justify: range scans complicate partitioning).
**NFRs:** 500k writes/sec, 1M reads/sec; p99 read < 5 ms, p99 write < 10 ms; 10 TB data; survive single-AZ loss without data loss (RPO=0 for acked writes); linear scale-out.

### REST API design
| Method & path | Purpose | Param rationale |
|---|---|---|
| `PUT /v1/kv/{key}` body `{"value": ..., "ttl_seconds"?: ...}` | Write | **Path param** = key identity; PUT = idempotent (retry-safe — critical for client retries on timeout). |
| `GET /v1/kv/{key}` | Read | Path param identity. `?consistent=true` as **query param** — consistency level is an optional read modifier, not identity. Default eventual (fast); `consistent=true` → quorum read. **Say this explicitly — it's a senior touch.** |
| `DELETE /v1/kv/{key}` | Delete | Path param; idempotent. Tombstone internally (say why: deletes must replicate like writes, otherwise a slow replica resurrects the key). |

Binary protocol (custom TCP) beats REST at 1M ops/sec — **say it**: REST/JSON is for the interview sketch; production would use a binary protocol or gRPC. Naming the gap is senior.

### HLD
```
[Clients: consistent-hash ring client] -> [Storage nodes (N): LSM engine + WAL]
        |-> [Coordinator layer] (or client-side routing — pick one, justify below)
[Control plane: membership (gossip), failure detection]
```
**Components:**
- **Partitioning: consistent hashing with virtual nodes** (150–200 vnodes/node). **Why over mod-N:** adding/removing a node moves ~1/N of keys, not nearly all. Vnodes smooth hotspots from heterogeneous nodes.
- **Replication: N=3, W=2, R=2 (quorum).** Write acked when 2/3 persist (WAL fsync). **Why quorum, not primary-backup:** no failover promotion, no split-brain primary; every node is symmetric — simpler ops at 10 TB scale.
- **Storage engine per node: LSM-tree (RocksDB-style).** **Why LSM for high write throughput:** writes are sequential (WAL + memtable flush → SSTables) — 500k writes/sec would murder a B-tree with random I/O. **Rejected:** B-tree (great for reads, write-amplification heavy); **Rejected:** pure in-memory (persistence requirement).
- **Read path:** coordinate → R replicas → reconcile by timestamp/version → return newest (read repair in background).
- **Hinted handoff + anti-entropy (Merkle trees):** transient failures don't lose writes; background repair converges.

### Back-of-envelope
- 500k writes/sec × 1 KB = 500 MB/sec cluster-wide ÷ 50 nodes = 10 MB/sec/node — comfortable for SSD sequential LSM writes.
- 10 TB ÷ 50 nodes ÷ 3 replicas ≈ 70 GB/node — fits on one SSD; memtable+bCache sized for hot set.
- Quorum latency: p99 write = 2 RTTs + fsync ≈ single-digit ms — meets the NFR; **say the math**.

### LLD — node internals
- `WAL`: append-only segment files, group commit (batch fsyncs every ~1 ms — throughput vs. latency knob, **name it**).
- `MemTable`: skip list (concurrent, lock-free-ish) → flush to SSTable at 64 MB.
- `SSTable`: sorted runs + Bloom filter per table (avoid disk seeks for missing keys — at 1M reads/sec with 10% misses, Bloom filters save ~100k disk I/Os/sec; **quantify it**).
- Compaction: leveled (read-optimized) vs. tiered (write-optimized) — **pick tiered for this workload** and say why; mention the read-amplification trade-off and that Bloom filters mitigate it.
- Concurrency: per-key striped locks for read-modify-write; lock-free reads via versioned values (MVCC-lite: `(value, version, tombstone?)`).

### DB choices — "we're building the DB; justify the internals"
| Choice | WHY |
|---|---|
| **LSM-tree engine** | Sequential-write-optimized for 500k writes/sec; see above. |
| **Consistent hashing + vnodes** | Incremental scale, no global rebalancing. **Rejected:** range partitioning — hot key ranges (one customer = half the traffic, cf. Jack's question) create unfixable hotspots without manual splits; hash distributes uniformly. |
| **Quorum replication (Dynamo-style)** | Symmetric, no failover, tunable R/W per operation. **Rejected:** Raft per shard — stronger consistency but leader bottleneck + complexity; the NFRs say AP-leaning is fine. |
| **WAL + group commit** | RPO=0 for acked writes without fsync-per-write latency death. |

**CAP/PACELC:** AP/EL — on partition, keep serving (last-write-wins by version); background anti-entropy converges. If the interviewer wants CP: flip to W=R=quorum+linearizable via leader — **say the knob exists**.

### Senior signals
- **Single-host vs distributed (they asked both):** single-host = embedded RocksDB/LevelDB, no network, no quorum — right when one machine holds the data and you want simplicity; distributed = everything above. **The senior line:** "The storage engine doesn't change — LSM either way. Distribution changes *coordination*, not the write path."
- **Failure modes:** node dies → hinted handoff + vnode reassignment; network partition → quorum still makes progress on the majority side, minority side rejects writes (say which side and why); disk fills → compaction backpressure → shed writes with clear error (don't corrupt).
- **Talking points:** "Every number here is a knob: W/R trade latency vs. durability; vnode count trades rebalance granularity vs. gossip overhead; compaction strategy trades write vs. read amplification. I pick defaults from the NFRs."
- **Follow-ups:** "Hot key (celebrity key)?" → replicate hot keys to more nodes / add a look-aside cache layer (say: caching doesn't fix write-hot, only read-hot — for write-hot you need key splitting, which changes the API contract — name it). "Transactions?" → out of scope v1; single-key linearizable ops only (say why: cross-shard transactions need 2PC and kill the latency NFR).

---

## 7. Scaling / Bottlenecks Playbook

*From the Bengaluru post: detect bottlenecks + remedies, LBs + access logs, multi-region LB, slow queries, master-slave + replica lag, Terraform multi-region, monolith→microservices. They want HLD then "how you'd actually do it in cloud." This is a playbook, not one system — structure it as detect → diagnose → remedy per layer.*

### 7a. Detecting bottlenecks
**Method (say it as a loop):** define SLIs (latency p50/p99, error rate, saturation) → instrument (RED: rate/errors/duration per service; USE: utilization/saturation/errors per resource) → find the constraint (the resource at 100% while others idle *is* the bottleneck — it's always *one* thing) → fix → re-measure.
**Concretely:**
- APM traces (OpenTelemetry): p99 latency broken by span — "which span dominates?" is always the first question.
- `top`-level: CPU steal (noisy neighbor), iowait (disk), memory pressure (GC pauses — Confluent cares: JVM GC logs).
- Queue depths: thread pool queues, Kafka consumer lag, DB connection pool wait time — **a growing queue upstream of a saturated resource is the signature of the bottleneck.**
- Load test to find it *before* prod: k6/Gatling ramp, watch which SLI breaks first.

### 7b. Load balancers, access logs, multi-region
- **What to check first:** LB access logs — they show per-request latency *by target*, so a single slow AZ/node pops out immediately. Also: target health, connection reuse, TLS handshake cost.
- **Remedies:** L7 (ALB) for path-based routing + sticky sessions if needed; L4 (NLB) for raw throughput (Kafka brokers sit behind NLB — **say why**: Kafka's binary protocol doesn't need L7).
- **Multi-region:** Route53-style latency/geolocation routing → regional ALB. **Active-passive vs active-active:** active-passive (pilot light) is cheaper and simpler to reason about; active-active needs conflict resolution (see §6's AP discussion). **Say:** "Multi-region active-active is a business decision disguised as a technical one — ask about RPO/RTO and data residency first."
- **Regional routing gotcha:** cross-region calls add 50–150 ms — keep request paths region-local; replicate data async or partition by region.

### 7c. Slow queries: detection → remedies
- **Detection:** `pg_stat_statements` (top queries by total time = calls × mean), slow-query log, APM DB spans. Alert on p99 query latency, not averages.
- **Remedies in order:** (1) missing index (`EXPLAIN ANALYZE` — say you read the plan, not guess); (2) N+1 → batch/join; (3) lock contention → shorter transactions; (4) cache the hot read (Redis); (5) read replica for read-heavy; (6) denormalize/materialized view; (7) shard. **Say the order matters** — juniors jump to sharding; seniors fix the query.
- **DB load analysis:** break load by query fingerprint; the top-5 fingerprints are usually >80% of load.

### 7d. Master-slave + replica lag
- **Architecture:** 1 primary (writes) + N replicas (reads). **Replica lag** is the core hazard: async replication means a read-your-write can miss.
- **Remedies:** (1) route read-your-write to primary (session pinning — "stickiness for ~1 s after write" is the pragmatic version); (2) monitor `replica_lag_seconds` as an SLI, page on it; (3) keep replicas in the same AZ as primary for the critical ones (lag < 100 ms); (4) if lag is chronic, the primary is undersized or a replica is doing analytics — **split OLTP replicas from OLAP** (don't let a BI query starve serving traffic).
- **Failover:** automated (Patroni/Stolon) with a *tested* runbook — "untested failover is not a plan." RPO>0 with async replication — **say it**, and offer semi-sync as the knob.

### 7e. IaC / Terraform multi-region
- **How you'd actually do it:** one Terraform repo, modules per component (`network`, `eks`, `rds`, `msk`...), per-region workspaces or `for_each` over regions; state per region in S3+DynamoDB locks (never one global state file — blast radius).
- **Senior points:** immutable infra (new AMI/container, not SSH-and-patch); `terraform plan` in CI, apply on merge with approvals; drift detection (`plan` on schedule); secrets in Secrets Manager, never in state (or encrypted state).
- **Multi-region deploy:** pipeline deploys region-by-region (bake in one region, promote) — **canary across regions**, not big-bang.

### 7f. Monolith → microservices
- **How to go about it (they asked explicitly):** (1) don't start with a rewrite — modularize *inside* the monolith first (clear module boundaries, separate DB schemas per module — the DB split is the real work); (2) strangler fig: carve off one bounded context at a time behind the monolith's API; (3) extract by *volatility and scaling axis* — the thing that deploys 10x/day or scales 10x differently goes first.
- **What changes:** per-service deploy, per-service scaling, but now you own distributed transactions (sagas), network latency, and observability across hops. **Senior line:** "Microservices trade code complexity for operational complexity — only pay it where the scaling or team-ownership axis demands it."
- **Data:** each service owns its tables; cross-service reads via API or event-carried state (outbox pattern — ties back to §2/§4).

### Senior signals for the whole playbook
- **Talking point:** "There's always exactly one bottleneck — find it with data before touching anything. The most expensive fix is the one applied to the wrong layer."
- **"How in cloud" specifics they want:** name the AWS/GCP pieces (ALB/NLB, Route53, RDS read replicas, ElastiCache, MSK) — but keep them as *examples*, noting the pattern transfers.
- **Follow-ups:** "When *wouldn't* you split the monolith?" → team of 5, single deploy cadence, no scaling skew — say it proudly.

---

## 8. Streaming / Kafka Deep-Dives (Jack's questions)

*Confluent's home turf. Each is a scenario — answer with: what you check first, the mechanism, the trade-off. These are asked rapid-fire; keep each answer tight.*

### 8a. Producers outpacing consumers — what to check first, backlog control
**Check first, in order:** (1) consumer lag per partition (is it uniform or one partition? — uniform = consumers too slow, skewed = hot partition, cf. 8c); (2) consumer CPU/GC (is it actually working or stalled?); (3) downstream backpressure (is the DB the real bottleneck? — check its saturation); (4) rebalance storms (are consumers constantly rebalancing instead of processing? — check rebalance rate).
**Backlog control:** short-term — the log *is* the buffer (that's the point of Kafka; size retention for the backlog duration); add consumer instances (if partitions allow — **can't exceed partition count**, say it); medium-term — increase partitions (note: changes key→partition mapping unless you over-partition upfront — **over-partition day one**, e.g. 3x expected); shed low-priority traffic (priority topics); long-term — fix the slow stage (it's usually downstream, not Kafka).
**Say:** "Kafka being behind is not an emergency — losing data or serving stale reads is. The backlog is observable and replayable, which is the whole design."

### 8b. Rebalance with unfinished batch work + offset commits
**The problem:** consumer is mid-batch when rebalance revokes its partitions. If it commits offsets for unprocessed records → data loss. If it doesn't commit → another consumer replays → duplicates.
**Handle it:** implement `ConsumerRebalanceListener.onPartitionsRevoked` — finish in-flight work *within* `max.poll.interval.ms` if you can; if not, **don't commit** the unfinished batch and let it replay (at-least-once), relying on idempotent downstream writes (§5's principle). **The rule to state:** "Never commit offsets for records you haven't durably processed. Duplicates are fixable; loss isn't."
**Deeper levers:** static group membership (`group.instance.id`) to survive rolling restarts without rebalance; incremental cooperative rebalancing (KIP-429) to avoid stop-the-world; shrink `max.poll.records` so batches fit comfortably inside the poll interval.

### 8c. Hot-key partitioning — one customer = half the traffic
**The problem:** keying by `customer_id` puts half the traffic on one partition → one consumer does half the work, lag grows forever, adding consumers doesn't help (partition-bound).
**Options (ranked):** (1) **salting/prefixing:** key = `customer_id + "#" + (order_id % 8)` → spreads the hot customer over 8 partitions; consumer merges. Downside: per-customer ordering now spans partitions — **say it**, and whether the use case needs strict ordering (charging: maybe; analytics: no). (2) **Separate topic** for the whale customer with more partitions. (3) **Two-tier:** hot keys get dedicated consumer capacity. **What NOT to do:** just add partitions — the hot key still hashes to one.
**Say:** "Partitioning is a load-balancing decision wearing a routing disguise. The moment one key dominates, key-based partitioning has failed and you need key *splitting*."

### 8d. Exactly-once charging — consumer crashes before commit
**Scenario:** consumer charges the customer, then crashes before committing the offset → replay → double charge. **This is THE Confluent interview question.**
**Answer — layered:**
1. **Make the charge idempotent (primary defense):** idempotency key = event ID (or `(customer_id, order_id)`); the charging service keeps a dedupe table with unique constraint — second attempt hits the constraint and returns the original result. **This is the answer they want first.**
2. **Transactional outbox / Kafka transactions:** consume-transform-produce within a Kafka transaction (EOS) so offset commit and downstream write are atomic — covers consume→produce, but the *external* charge API call can't be in the transaction. **Say the boundary explicitly:** "Kafka transactions give me exactly-once *within* Kafka. The moment I call an external API, I'm back to idempotency keys — there's no distributed transaction across that boundary."
3. **State/lock (they hinted):** per-customer lock/lease so only one consumer processes that customer's events at a time — prevents concurrent double-charge during rebalances, but doesn't fix crash-before-commit alone.
**Say:** "Exactly-once is a property of the *sink*, not the transport. I design the sink to be idempotent and treat the transport as at-least-once."

### 8e. Schema evolution with staggered deploys + replay of old events
**The problem:** producers and consumers deploy at different times; old events must remain replayable after a schema change.
**Answer:** Schema Registry with compatibility modes. **Backward-compatible** changes (add optional field, delete field consumers don't require) → new producers, old consumers OK. **Forward-compatible** (old producers, new consumers) → new consumers must tolerate missing fields. **Full compatibility** when both directions happen (staggered deploys!) — default to FULL, or BACKWARD_TRANSITIVE if you control deploy order.
**Rules to state:** never rename a field (it's delete+add — breaks both directions); never change a type; only add fields with defaults/optional; bump schema version, never mutate a registered version. Old events replay through the registry by version ID — **that's why the registry stores every version immutably**.
**DB/downstream rollout:** expand-then-contract: (1) deploy consumers that read both old and new, (2) deploy producers writing new, (3) migrate/backfill, (4) drop old support. **Say the sequence — it's the senior signal.**

### 8f. Late arrivals — per-minute purchase counts, events up to 10 min late
**The problem:** counting purchases per minute, but events arrive up to 10 minutes late.
**Answer:** event-time windows (1-min tumbling) + watermark = max event time − 10 min + allowed lateness 10 min. Late-but-within-lateness events update the window via retraction/upsert (cf. §5's idempotent sink). Beyond lateness → side output for a **batch correction job** that rewrites affected minute-buckets hourly/daily (Lambda architecture's speed+batch layers — **name it**).
**Trade-off to state:** longer lateness = more state held + later finality. "I give the dashboard fast approximate counts immediately and exact corrected counts within the hour — and I tell the business which number they're looking at." **Say which is which on the dashboard** (provisional vs. finalized badge) — that's the product-minded senior touch.

---

## 9. LLD — Concurrency Classics

### 9a. Thread-safe token bucket (capacity N, refill R/sec)
**Design:**
```python
class TokenBucket:
    def __init__(self, capacity, refill_per_sec):
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()
        self.lock = threading.Lock()   # one lock; critical section is ~ns

    def allow(self) -> bool:
        now = time.monotonic()
        with self.lock:
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity,
                              self.tokens + elapsed * self.refill_per_sec)
            self.last_refill = now
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
```
**WHY this shape:** lazy refill on each request (no background thread — **say why**: a refill thread adds scheduling jitter and lifecycle complexity for zero benefit; time-based math is exact); `time.monotonic()` (immune to wall-clock jumps — **say it**, NTP adjustments breaking a rate limiter is a real prod bug); single lock because the critical section is nanoseconds — lock-free atomics would be premature (but **name** the alternative: CAS loop on an `AtomicReference<State>`, and when you'd need it: >100k rps where lock contention shows in profiles).
**Edge cases:** burst = capacity (that's the point of the bucket vs. fixed window); fractional tokens accumulate correctly; `allow_n(k)` variant for weighted requests.
**Follow-ups:** "Distributed?" → that's §11. "Per-user buckets?" → `ConcurrentHashMap<user, TokenBucket>` + eviction of idle buckets (or striping).

### 9b. Bounded multi-producer multi-consumer queue with shutdown
**Design:** ring buffer (array, power-of-2 size, mask indexing) + two semaphores (`not_full`, `not_empty`) + mutex, or in Java `ArrayBlockingQueue` — **but they want you to build it**, so:
```python
class BoundedQueue:
    def __init__(self, capacity):
        self.buf = [None] * capacity
        self.head = self.tail = self.count = 0
        self.not_full = threading.Semaphore(capacity)
        self.not_empty = threading.Semaphore(0)
        self.lock = threading.Lock()
        self.shutdown = False

    def put(self, item):
        self.not_full.acquire()
        with self.lock:
            if self.shutdown:
                self.not_full.release()
                raise ShutDownError()
            self.buf[self.tail] = item
            self.tail = (self.tail + 1) % len(self.buf)
            self.count += 1
        self.not_empty.release()

    def get(self):
        while True:
            self.not_empty.acquire()
            with self.lock:
                if self.count > 0:
                    item = self.buf[self.head]
                    self.head = (self.head + 1) % len(self.buf)
                    self.count -= 1
                    self.not_full.release()
                    return item
                if self.shutdown:          # drained + shutdown -> exit
                    self.not_empty.release()  # wake next waiter
                    raise ShutDownError()
                # spurious: shutdown released permits with empty queue
                continue

    def close(self):
        with self.lock:
            self.shutdown = True
        # release all waiters: producers get ShutDownError, consumers drain then exit
        for _ in range(MAX_WAITERS):  # or track waiter counts
            self.not_full.release()
            self.not_empty.release()
```
**Shutdown semantics (the graded part):** two-phase — (1) `shutdown=True`: producers rejected, (2) consumers **drain** remaining items before exiting (no data loss), then raise. **Say why drain-then-exit:** the queue's contract is at-least-once delivery; dropping buffered items on shutdown silently loses data. Poison-pill alternative: enqueue N pills (N = consumers) — simpler, but **say the flaw**: pills can overtake real items only if you enqueue after drain... actually pills work if producers are already stopped; the semaphore version above handles the general case — **compare both out loud**.
**WHY ring buffer over linked list:** no per-item allocation (GC pressure at high throughput — Confluent cares), cache-friendly, fixed memory bound (that's the *point* of bounded).

### 9c. Timestamped KV store — reads return latest value at or before timestamp (writes in order per key)
**Design:** `Map<Key, TreeMap<Timestamp, Value>>` (Java: `ConcurrentHashMap<String, ConcurrentSkipListMap<Long, V>>`).
```python
class TimestampedKV:
    def __init__(self):
        self.store = {}              # key -> sorted list of (ts, value)
        self.locks = {}              # per-key locks (striped in prod)
        self.global_lock = threading.Lock()

    def put(self, key, value, ts):
        with self._lock_for(key):
            self.store.setdefault(key, []).append((ts, value))  # in-order: append

    def get(self, key, ts):
        with self._lock_for(key):
            versions = self.store.get(key, [])
            # binary search: rightmost ts <= requested
            i = bisect_right(versions, ts, key=lambda x: x[0]) - 1
            return versions[i][1] if i >= 0 else None
```
**WHY:** writes arrive in order per key → append is O(1), no sort needed (**exploit the given invariant — say it**); reads are `bisect_right` → O(log n). Per-key locks (striped, e.g. 64 stripes) — **why not one global lock:** writes to different keys must not serialize; **why not lock-free:** the invariant (in-order append) plus a lock is simple and correct — CAS on a list isn't.
**Follow-ups:** "Writes out of order?" → insert-sorted (O(n) shift or tree); "Memory grows forever?" → compaction/retention (keep last K versions or window); "Range scan?" → the sorted structure already supports it.

---

## 10. (Extra) Design a Kafka-like Partitioned Commit Log

*Streaming-flavored, Confluent-obvious, not in Henry's file. The crux: the log abstraction and its trade-offs.*

### Requirements
**Functional:** topics, partitions, append-only log per partition, consumer offsets, consumer groups, retention.
**NFRs:** 1M msgs/sec/cluster, p99 produce < 10 ms, retain 7 days (~50 TB), survive broker loss without data loss (acked writes).

### REST/admin API
| Method & path | Purpose | Param rationale |
|---|---|---|
| `POST /v1/topics` body `{"name","partitions","replication_factor","retention_ms"}` | Create topic | Body — creation params are a document, not identity. |
| `GET /v1/topics/{topic}` | Topic metadata | Path param identity. |
| `POST /v1/topics/{topic}/records` body `{..., "key"?: ...}` | Produce | Path param = topic identity; key in body (routing hint, not identity). Return `202` + offsets. |
| `GET /v1/topics/{topic}/records` | Consume (long-poll) | Path param topic + **query** `?partition=3&offset=12345&max_wait_ms=500&max_bytes=1MB` — offset/partition locate *a position in* the resource (view modifiers → query). Long-poll: `max_wait_ms` is the honest API for "don't busy-spin." |
| `PUT /v1/consumer-groups/{group}/offsets` | Commit offset | Path params identity; body `{topic, partition, offset}`. PUT = idempotent (recommit same offset is a no-op — **say it**). |

### HLD
```
[Producers] -> [Brokers: partition leaders] -> [Segment files on disk (mmap'd index)]
[Consumers] -> [fetch from leaders]    [Followers replicate]
[Controller (KRaft/leader election)]   [Offset store: __consumer_offsets topic]
```
**Core design decisions (go deep — this is the interview):**
1. **Sequential disk I/O is the whole performance story.** Partitions are append-only segment files (~1 GB); writes are `O_APPEND` sequential — 600 MB/sec+ on spinning disk, GBs on SSD. **Say:** "Kafka is fast *because* it treats the disk as a log, not because of clever networking." Page cache does the read serving (consumers read what was just written → page-cache hits, ~zero disk I/O).
2. **Zero-copy transfer:** `sendfile()` — disk → page cache → socket, no user-space copies. **Name it** — it's the classic follow-up ("how does the broker serve 1M msgs/sec without melting CPU?").
3. **Batching:** producer batches by `linger.ms` + `batch.size` — throughput/latency knob (ties to Jack's batching question: measure p99 produce latency vs. MB/sec as you tune).
4. **Replication:** leader + ISR (in-sync replicas); ack=all + min ISR 2 → RPO=0 for acked writes. **Why ISR not fixed quorum:** slow follower drops out of ISR instead of blocking writes — availability-first with a durability floor.
5. **Consumer groups:** partition = unit of parallelism; one consumer per partition max (say why: ordering guarantee is per-partition, and two readers would need coordination).

### LLD
- `LogSegment`: `base_offset`, data file, offset index (sparse: every N KB), timestamp index. Fetch(offset) → binary search sparse index → positional read. **Sparse index is the senior detail** — full index of 1 GB segment doesn't fit memory; sparse does.
- `ReplicaManager`: leader appends to local log, followers `fetch` (long-poll) — **followers are just special consumers** (say it — unifies the design). High watermark = min ISR log-end → consumers only see committed data.
- `GroupCoordinator`: heartbeats, rebalance protocol (cf. §8b).

### DB choices — the log *is* the DB here
| Choice | WHY |
|---|---|
| **Filesystem as the store** | No DBMS: the access pattern (sequential append, sequential scan) is exactly what filesystems + page cache do best. **Rejected:** putting the log in Postgres/Cassandra — random-I/O engines fighting a sequential workload, plus double write-ahead. |
| **Sparse in-memory indexes** | O(log n) offset lookup with bounded memory. |
| **Separate `__consumer_offsets` topic** | Offsets are just another log — dogfooding; compacted topic (log compaction keeps latest per key — **name compaction** as the mechanism). |

### Senior signals
- **Talking points:** "The log is the unifying abstraction — messaging, storage, and stream processing are all the same primitive." "Every knob is a durability/availability/latency trade: acks, min ISR, retention."
- **Failure modes:** leader dies → ISR elects new leader (no data loss for acked writes; unacked may be lost — **say the boundary**); all ISR die → choose: wait (unavailable, no loss) or elect out-of-ISR (available, possible loss) — `unclean.leader.election.enable` **is** that choice, name it.
- **Follow-ups:** "Exactly-once?" → idempotent producer (PID + sequence) + transactions (§8d). "Rebalance storms?" → static membership, cooperative protocol (§8b).

---

## 11. (Extra) Design a Distributed Rate Limiter

*Streaming-flavored adjacency: API gateways protecting Kafka ingest / multi-tenant Confluent Cloud. The crux: coordination cost vs. accuracy.*

### Requirements
**Functional:** per-API-key / per-user / per-endpoint limits (e.g. 1000 req/min); burst allowance; headers `X-RateLimit-Remaining`, `Retry-After` on 429.
**NFRs:** 100k decisions/sec across 20 gateway nodes; p99 decision < 2 ms (can't add latency to the hot path); accuracy: no more than ~5% over-admission; limiter failure → fail-open (say why: a down limiter must not take down the API — **availability over strictness**, but alert loudly).

### REST API (admin)
| Method & path | Purpose | Param rationale |
|---|---|---|
| `PUT /v1/limits/{apiKey}` body `{"rpm": 1000, "burst": 100}` | Set limit | Path param = whose limit (identity); body = the policy document. PUT idempotent. |
| `GET /v1/limits/{apiKey}` | Read limit | Path param identity. |
| `DELETE /v1/limits/{apiKey}` | Remove | Path param; idempotent. |
(The data-plane check is *not* REST — it's a library call in the gateway hot path. **Say why:** a network hop per request at 100k/sec is the bottleneck you're building the limiter to prevent.)

### HLD — the core trade-off
**Option A: centralized (Redis + Lua).** `INCR` + `EXPIRE` or sliding-window Lua script per request. Accurate, simple. Cost: 1 RTT (~0.5 ms) per request + Redis must handle 100k ops/sec (fine, but it's now a critical dependency).
**Option B: local token buckets + periodic sync (pick this for the NFRs).** Each gateway runs §9a's token bucket per key; buckets gossip/sync usage every ~1 s via Redis. **Why:** decision is local (microseconds, no hot-path RTT); accuracy bounded by sync interval (over-admission ≤ nodes × rate × interval — **quantify it**: 20 nodes × 1000/min × 1 s ≈ 333 extra requests worst case ≈ within the 5% budget at high limits; for small limits, fall back to centralized — **hybrid, say it**).
**Option C: sticky routing** (same key → same gateway via consistent hashing) — makes local buckets exact, but rebalancing on node changes redistributes keys (and a node death loses bucket state → temporary over-admission; acceptable under fail-open).

### LLD
- `LocalLimiter`: `ConcurrentHashMap<Key, TokenBucket>` (§9a) + background sync thread: every 1 s, `HINCRBY` usage to Redis, read back global usage, adjust local bucket rates (additive-increase style: `local_rate = global_limit / nodes`, corrected by actuals).
- Redis Lua for the centralized fallback path: atomic `ZREMRANGEBYSCORE` (evict old) + `ZCARD` + `ZADD` sliding-window — **one round trip, atomic** (say why Lua: no race between check and increment).
- Headers: compute `remaining` from the local bucket (approximate — **say it's approximate**).

### DB choices
| Store | Holds | WHY |
|---|---|---|
| **Redis** | global usage counters, limit policies | Atomic increments, TTLs, Lua — the coordination primitive. Not on the hot path in Option B (sync only). **Rejected:** Postgres — 100k increments/sec of counters is write-amplification misery. |
| **Local memory** | token buckets | Microseconds, no network. Ephemeral by design (fail-open on loss). |

**CAP:** AP — the limiter must never block the API; accuracy degrades gracefully under partition (buckets run on last-known rates).

### Senior signals
- **The interview is the trade-off:** centralized (accurate, slower, SPOF) vs. local (fast, approximate) — derive the choice from the p99 < 2 ms NFR.
- **Failure modes:** Redis down → local buckets continue on last-known config (fail-open, alert); clock skew → use monotonic-ish server timestamps, document the assumption.
- **Talking points:** "Rate limiting is a *coordination* problem, not a counting problem — the question is how much accuracy you buy with how much coordination." "429 + `Retry-After` is a contract with clients: honor it and retries back off instead of thundering."
- **Follow-ups:** "DDoS-level abuse from one key?" → hard block at the edge (separate denylist, not the limiter). "Multi-region?" → per-region limits with a global budget split (like §7b's region-local principle).

---

## 12. (Extra) Design a Notification Fan-out Service

*Streaming-flavored (event-driven fan-out, cf. podcast feed §2 and stock alerts in the briefs). The crux: per-user delivery preferences × channel reliability tiers.*

### Requirements
**Functional:** events in (order shipped, comment mention, price alert) → notify users via push/email/SMS per their preferences; templates per event type; quiet hours respected.
**NFRs:** 50k events/sec in, up to 10 notifications per event (500k outs/sec fan-out); p99 event→push < 30 s, email < 5 min (tiered latency — **say why different**: push is interactive, email isn't); preference changes apply within 60 s; no duplicate SMS (cost + annoyance — idempotency matters most here).

### REST API
| Method & path | Purpose | Param rationale |
|---|---|---|
| `POST /v1/events` body `{"type","user_id","payload"}` | Ingest event | Body; `202 Accepted` (async pipeline, cf. §5). |
| `GET /v1/users/{userId}/preferences` | Read prefs | Path param identity (scoped resource). |
| `PUT /v1/users/{userId}/preferences` | Set prefs | Path param; PUT idempotent full-replace (preferences are a document — **say why PUT not PATCH**: full-replace avoids merge-semantics bugs; client always sends the whole doc). |
| `GET /v1/users/{userId}/notifications` | History | Path hierarchy + **query** `?limit&cursor&type=` (view modifiers). |

### HLD
```
[Event producers] -> [Kafka: notification-events] -> [Router: enrich (prefs, templates)]
    -> [Kafka: per-channel topics: push-high, email-bulk, sms-critical]
    -> [Channel workers: push / email / sms] -> [Providers: FCM/APNS, SES, Twilio]
    -> [Cassandra: notification log (dedupe + history)]
[Preference service: Postgres] -> [Redis cache] (router reads, 60-s TTL)
```
**Flow:** router resolves user → preferences (cached) → quiet-hours check → template render → route to channel topic by priority. Channel workers send via provider with retries (exponential backoff + jitter) and write the notification log.
**Why per-channel topics:** push workers scale 10x email workers independently; an SES outage must not block push (bulkhead — **name the pattern**).

### LLD
- `Router`: `prefs = prefCache.get(userId)` (miss → Postgres, 60-s TTL — **this TTL is the "preferences apply within 60 s" mechanism**, say it); `if quietHours and not critical: delay until morning` (delayed queue / scheduled Kafka record).
- **Dedupe:** notification log PK `(user_id, event_id, channel)` with INSERT-if-not-exists — retrying a send after a provider timeout hits the constraint → no double SMS. (**The money-saving line** — SMS costs per send; say it.)
- **Template rendering:** sandboxed (no user input in templates — injection), precompiled.
- Concurrency: workers idempotent; provider calls bounded by per-provider connection pools (don't melt Twilio's rate limits — **client-side throttling per provider**).

### DB choices
| Store | Holds | WHY |
|---|---|---|
| **Kafka** | events, per-channel queues | Durable fan-out buffer; per-channel topics = independent scaling + bulkheads; replay on template bug ("we sent the wrong text" → fix template, replay). |
| **PostgreSQL** | preferences, templates | Relational, low-write, strong consistency (preference change must be read-your-write — **say it**). |
| **Redis** | pref cache (60-s TTL) | Router does 50k lookups/sec — must be memory-speed; staleness bounded by TTL = the 60-s NFR. |
| **Cassandra** | notification log `(user_id, event_id, channel)` | High-write dedupe/history log; partition by user_id → "my notification history" is one partition read. **Rejected:** Postgres — 500k writes/sec of log rows; **Rejected:** Redis — history must be durable and unbounded. |

**CAP/PACELC:** router PA/EL (skip on stale prefs rather than block); dedupe log PC/EC (double-SMS is worse than a delayed notification).

### Senior signals
- **Tiered reliability by channel:** SMS = highest correctness bar (cost + intrusiveness) → dedupe + manual review for new templates; push = best effort + collapse keys (only latest matters — **say**: FCM collapse_key means 10 rapid updates → 1 push, which is a feature).
- **Failure modes:** provider outage → per-channel DLQ + replay; template bug → fix + replay from Kafka (event sourcing pays off); preference DB slow → serve from cache, alert.
- **Talking points:** "Fan-out multiplies every upstream decision by 10 — idempotency and per-channel bulkheads are load-bearing, not nice-to-haves." "Quiet hours and dedupe are product requirements disguised as infra problems — I surface them in design."
- **Follow-ups:** "User with 1M followers triggers an event?" → that's §2's celebrity problem again — **cross-reference it** (mention→fan-out, pull at read time for mega-accounts). "Exactly-once across SMS?" → §8d's answer: idempotent sink, at-least-once transport.

---

# Closing — how to open any of these in the room

1. **Clarify (2 min):** "Who are the users? What's the scale — reads/sec, writes/sec, data size? What breaks if we're briefly stale? Any compliance constraints?" Write the numbers down — interviewers grade this.
2. **NFRs with numbers (1 min):** state them even if you invent them ("assuming 10k writes/sec — correct me"). It shows you think in constraints.
3. **HLD boxes (5 min):** client → LB → stateless API → (queue?) → stores. Justify each arrow in one sentence.
4. **Go deep on ONE crux (15 min):** the fan-out threshold, the quorum math, the watermark policy, the shutdown semantics. This is where senior is won or lost.
5. **Failure modes (3 min):** "If X dies, then Y." Always end here — it signals production ownership.

**Confluent-specific seasoning:** reach for the log (Kafka) wherever ingestion, buffering, or replay appears; name exactly-once boundaries honestly (idempotent sink > distributed transaction); use event time + watermarks for anything counted over time; and when they say "keep it simple" (TinyURL), obey visibly — restraint is a senior signal too.
