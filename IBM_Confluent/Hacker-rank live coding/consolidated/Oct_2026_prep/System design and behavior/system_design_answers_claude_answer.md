# System Design Answers: Confluent-Style Question Set

Answers to every system design question in your `system_design.md`, each in the same framework so it is easy to reproduce on a whiteboard:

**1. Functional requirements -> 2. Non-functional requirements (+ estimates) -> 3. Core entities / data model -> 4. REST API design with detailed contracts -> 5. High-level design -> 6. Low-level design (deep dives) -> 7. Trade-offs and failure modes**

## Contents

| # | Question | Frequency in your notes |
|---|---|---|
| 0 | [Shared conventions, estimation cheat sheet, interview flow](#0-shared-conventions-and-interview-flow) | |
| 1 | [Podcast / Feed Service (Spotify-like, Feedly-like)](#1-podcast--feed-service) | 6 posts |
| 2 | [URL Shortener (TinyURL)](#2-url-shortener-tinyurl) | 4 posts |
| 3 | [Distributed Key-Value Store](#3-distributed-persistent-key-value-store) | 2 posts |
| 4 | [Temp Email Generator (5-hour expiry)](#4-temp-email-generator-5-hour-expiry) | 1 post |
| 5 | [Movie Ticketing Platform](#5-movie-ticketing-platform) | 1 post |
| 6 | [Stock Alert Notification System](#6-stock-alert-notification-system) | 1 post |
| 7 | [Operations at Scale (bottlenecks, LB, DB, IaC, microservices, multi-region)](#7-operations-at-scale) | 1 post |
| 8 | [Clicks per Page over the Last 5 Minutes (streaming)](#8-clicks-per-page-in-the-last-5-minutes) | Jack's interview |
| A | [Streaming and concurrency Q&A from Jack's interview](#appendix-a-streaming-and-concurrency-qa) | Jack's interview |
| B | [Quick comparison and checklist](#appendix-b-quick-comparison-and-checklist) | |

---

# 0. Shared Conventions and Interview Flow

## 0.1 Interview flow (45-60 min)

| Step | What to say or do | Time |
|---|---|---|
| Clarify | Users, scale, read/write ratio, consistency needs, what is out of scope | 5 min |
| Requirements | Functional list, then non-functional list with numbers | 5 min |
| Estimates | QPS, storage, bandwidth, cache size (state assumptions out loud) | 3 min |
| Entities + API | Core entities, then endpoints with request/response, status codes | 10 min |
| High-level design | Boxes and arrows, trace one read and one write | 10 min |
| Deep dive | The 1-2 hard parts (the interviewer will steer you) | 15 min |
| Wrap-up | Bottlenecks, failure modes, monitoring, what you would do next | 5 min |

## 0.2 Estimation cheat sheet

| Quantity | Rule of thumb |
|---|---|
| 1 day | 86,400 s, use about 10^5 |
| Average QPS | requests per day / 10^5 |
| Peak QPS | 2-5x average (say your multiplier) |
| Storage | records x bytes per record x replication factor x retention |
| Bandwidth | QPS x payload size |
| Hot cache | 20% of daily reads often serves 80% of traffic |
| Availability | 99.9% is about 8.8 h downtime per year, 99.99% is about 53 min |

## 0.3 REST conventions used in every API below

* **Base path** `/v1`. Plural nouns. Opaque string IDs with a type prefix (`ch_12`, `ep_9f3`). JSON bodies, `snake_case` fields, timestamps in ISO-8601 UTC.
* **Path parameter** identifies a resource (`/channels/{channelId}`). **Query parameter** filters, sorts, or pages a collection (`?limit=20&cursor=...`). **Body** carries the data. Secrets go in headers, never in the URL.
* **Auth:** `Authorization: Bearer <token>`. `401` = not authenticated, `403` = authenticated but not allowed.
* **Pagination:** `limit` (default 20, max 100) and opaque `cursor`. Response envelope: `{"data": [...], "next_cursor": "..." | null}`. Cursors are keyset based, so they stay correct while data changes. Offset paging is avoided because deep offsets are slow and skip or duplicate rows.
* **Idempotency:** every `POST` that creates or charges accepts an `Idempotency-Key` header (client UUID). The server stores the first result for 24 h and replays it on retries.
* **Errors:** `application/problem+json`:

```json
{
  "type": "https://api.example.com/errors/invalid-cursor",
  "title": "Invalid cursor",
  "status": 400,
  "code": "invalid_cursor",
  "detail": "The cursor is malformed or expired.",
  "request_id": "req_8a1f"
}
```

* **Rate limiting:** `429 Too Many Requests` with `Retry-After`. Headers `X-RateLimit-Limit` and `X-RateLimit-Remaining`.
* **Caching and concurrency:** `ETag` / `If-None-Match` on reads (`304`), `If-Match` on updates (`412` on a lost update), `Cache-Control` on public data.
* **Status codes:** `200` OK, `201` created (+ `Location`), `202` accepted for async work, `204` no content, `400` bad input, `404` missing, `409` state conflict, `410` gone (expired), `422` semantically invalid, `429` throttled, `503` overloaded.
* **Versioning:** URL major version (`/v1`) for breaking changes. Adding optional fields is not breaking.

---

# 1. Podcast / Feed Service

*(Spotify-like or Feedly-like. Focus areas from your notes: API design, pagination, skip tokens, versioning, back-of-envelope numbers, edge cases such as users with many subscriptions and channels with many episodes.)*

## 1.1 Functional requirements

* Browse and search podcast **channels**.
* **Subscribe / unsubscribe** to a channel. List my subscriptions.
* Fetch **X channels at a time** and **X episodes (audio clips) per channel**, with pagination.
* **Personalized feed:** newest episodes across my subscribed channels, newest first.
* Creators or admins **add channels and episodes** (or the system ingests RSS feeds).
* Out of scope: recommendations, payments, audio transcoding, social features.

## 1.2 Non-functional requirements and estimates

| Requirement | Target |
|---|---|
| Read-heavy | Feed and catalog reads are far more frequent than writes |
| Latency | Feed p99 under 200 ms |
| Availability | 99.99% for reads |
| Consistency | Feed may be seconds to a minute stale (eventual). Subscribe must be **read-your-writes** for that user |
| Scale | 100M MAU, 20M DAU |
| Stable paging | A new episode must not duplicate or skip items while the user scrolls |
| Outliers | Users with thousands of subscriptions, channels with 10k+ episodes, channels with millions of subscribers |

**Estimates (assumptions stated):**

* Feed reads: 20M DAU x 10 opens = 200M/day, about **2.3k QPS** average, about 10k peak.
* Channels: 5M. Episodes: 5M x 200 = **1B episodes** x 1 KB metadata = about **1 TB** (audio itself is in object storage + CDN, many PB, not in the DB).
* Subscriptions: 100M users x 30 = **3B rows** x about 50 B = about **150 GB**.
* New episodes: 5M channels x 1 per week = 5M/week, about **8 per second**. Writes are tiny compared with reads, so optimize reads.

## 1.3 Core entities

| Entity | Key fields |
|---|---|
| **User** | `user_id`, `email`, `created_at` |
| **Channel** | `channel_id`, `title`, `description`, `author`, `rss_url` (unique), `category`, `subscriber_count`, `last_episode_at` |
| **Episode** | `episode_id`, `channel_id`, `title`, `audio_url`, `duration_seconds`, `published_at` |
| **Subscription** | `user_id`, `channel_id`, `subscribed_at` |
| **FeedItem** (materialized) | `user_id`, `published_at`, `episode_id`, `channel_id` |
| **PlaybackProgress** (optional) | `user_id`, `episode_id`, `position_seconds`, `updated_at` |

```sql
CREATE TABLE channels (
  channel_id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT, author TEXT,
  rss_url TEXT UNIQUE, category TEXT, subscriber_count BIGINT DEFAULT 0,
  last_episode_at TIMESTAMPTZ, created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE episodes (
  episode_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL REFERENCES channels,
  title TEXT NOT NULL, audio_url TEXT NOT NULL, duration_seconds INT, published_at TIMESTAMPTZ NOT NULL
);
-- serves "episodes of a channel, newest first" with keyset pagination
CREATE INDEX ep_channel_time ON episodes (channel_id, published_at DESC, episode_id DESC);

CREATE TABLE subscriptions (
  user_id TEXT, channel_id TEXT, subscribed_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (user_id, channel_id)            -- "my subscriptions"
);
CREATE INDEX sub_by_channel ON subscriptions (channel_id, user_id);   -- fan-out: "who subscribes to X"
```

## 1.4 REST API design

| Method + path | Purpose | Success | Errors |
|---|---|---|---|
| `GET /v1/channels?q=&category=&limit=&cursor=` | Browse / search channels | 200 | 400 |
| `GET /v1/channels/{channelId}` | Channel detail | 200 (+ ETag) / 304 | 404 |
| `POST /v1/channels` | Create channel (creator/admin) | 201 + `Location` | 400, 403, 409 (duplicate `rss_url`) |
| `GET /v1/channels/{channelId}/episodes?limit=&cursor=` | X episodes of a channel | 200 | 400, 404 |
| `POST /v1/channels/{channelId}/episodes` | Add an episode | 201 / 202 | 403, 404, 422 |
| `PUT /v1/me/subscriptions/{channelId}` | Subscribe (idempotent) | 201 first time, 200 if already | 404 |
| `DELETE /v1/me/subscriptions/{channelId}` | Unsubscribe (idempotent) | 204 | |
| `GET /v1/me/subscriptions?limit=&cursor=` | My subscriptions | 200 | 401 |
| `GET /v1/me/feed?limit=&cursor=` | Personalized feed | 200 | 400, 401 |

Why `PUT` for subscribe: the client names the resource (`channelId`), and repeating the call has the same result, so retries are safe. It also reads naturally as "my subscription to channel X".

### Detailed contract: get my feed

```http
GET /v1/me/feed?limit=20&cursor=eyJ0IjoiMjAyNi0xMC0xNFQwODowMDowMFoiLCJpZCI6ImVwXzlmMyJ9
Authorization: Bearer <token>
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: private, max-age=15

{
  "data": [
    {
      "episode_id": "ep_9f3",
      "channel": { "channel_id": "ch_12", "title": "Daily Tech" },
      "title": "Episode 482: Edge Caching",
      "published_at": "2026-10-14T08:00:00Z",
      "duration_seconds": 1820,
      "audio_url": "https://cdn.example.com/a/ep_9f3.mp3"
    }
  ],
  "next_cursor": "eyJ0IjoiMjAyNi0xMC0xM1QxNzozMDowMFoiLCJpZCI6ImVwXzdjMiJ9"
}
```

| Case | Response |
|---|---|
| `limit` outside 1-100 | `400` `limit_out_of_range` |
| Malformed cursor | `400` `invalid_cursor` |
| Missing / bad token | `401` |
| Last page | `200` with `"next_cursor": null` |
| Too many requests | `429` + `Retry-After` |

### Detailed contract: subscribe

```http
PUT /v1/me/subscriptions/ch_12
Authorization: Bearer <token>
```

```http
HTTP/1.1 201 Created
{ "channel_id": "ch_12", "subscribed_at": "2026-10-15T10:02:11Z" }
```

`200 OK` with the same body if already subscribed. `404` `channel_not_found`. `DELETE` returns `204` whether or not the subscription existed.

### Detailed contract: create channel

```http
POST /v1/channels
Idempotency-Key: 7f1c...
{ "title": "Daily Tech", "author": "A. Smith", "rss_url": "https://example.com/feed.xml", "category": "technology" }
```

`201 Created`, `Location: /v1/channels/ch_12`, body is the channel. `409` `rss_url_exists` if already registered. `403` for non-creators.

### Pagination: why a keyset cursor

| Option | Problem |
|---|---|
| `limit` + `offset` | Deep pages scan and discard rows. New episodes shift rows, so items repeat or vanish |
| Page number | Same problems as offset |
| **Opaque cursor (skip token)** | Cursor = base64url of `{"t": published_at, "id": episode_id}`. The query is `WHERE (published_at, episode_id) < (:t, :id) ORDER BY published_at DESC, episode_id DESC LIMIT :limit+1`. It uses the index, costs the same on every page, and is stable under inserts. Fetch `limit + 1` rows to know whether a next page exists |

## 1.5 High-level design

```
 Mobile / Web
     |
     v
   CDN  (audio files, public channel + episode pages)
     |
     v
 API Gateway / Load Balancer  (auth, rate limit)
     |
     +--> Catalog Service ---------> Catalog DB (channels, episodes; read replicas) + Redis cache
     |
     +--> Subscription Service ----> Subscription DB (sharded by user_id)
     |
     +--> Feed Service ------------> Feed store (Redis sorted set per user / Cassandra)
                                         ^
 Creator / RSS poller                    |
     |                                   |
     v                                   |
 Ingestion Service --> Kafka "episode.published" --> Fan-out Workers
     |
     v
 Object storage (S3) for audio  --> served through CDN
```

**Write path (new episode):** ingestion validates and stores metadata, uploads audio to S3, publishes `episode.published` to Kafka (keyed by `channel_id`). Fan-out workers look up the channel's subscribers and write the episode into each subscriber's feed.

**Read path (feed):** Feed Service reads the user's materialized feed, merges in recent episodes from "celebrity" channels (see 1.6), hydrates episode details from cache, returns one page.

**Scaling:** stateless services behind a load balancer. Catalog and subscription DBs have read replicas, with subscriptions sharded by `user_id` and episodes sharded by `channel_id`. Redis caches hot channels. CDN handles audio and public pages.

## 1.6 Low-level design

### Feed generation: pull, push, or hybrid

| Strategy | How | Pros | Cons |
|---|---|---|---|
| **Pull (fan-out on read)** | At read time, fetch the user's channels, get the latest episodes of each, merge | No write amplification, always fresh | Slow for users with many subscriptions |
| **Push (fan-out on write)** | On publish, insert into each subscriber's feed | Fast reads | A channel with 5M subscribers causes 5M writes per episode |
| **Hybrid (choose this)** | Push for channels under a threshold (say 100k subscribers). Do **not** push for celebrity channels. At read, merge the pushed feed with the latest episodes of the user's celebrity channels | Fast reads, bounded write cost | Two code paths |

**Pull-merge with a heap** (the k-way merge problem). Each channel's episodes are already sorted by time, so take the top `limit` from each channel and merge:

```python
import heapq
from itertools import islice

def merge_feed(per_channel_lists, limit):
    """per_channel_lists: list of lists of (published_at, episode_id), each newest first."""
    merged = heapq.merge(*per_channel_lists, key=lambda e: e[0], reverse=True)
    return list(islice(merged, limit))
```

Cost: O(limit x log k) after fetching k lists. For a user with 3,000 subscriptions, only consider channels active in the last 30 days, or cap the pull set (see edge cases).

**Feed store:** Redis sorted set `feed:{user_id}` with score = `published_at`, member = `episode_id`, capped to the newest 1,000 (`ZREMRANGEBYRANK`). Older pages fall back to the pull path. At larger scale use Cassandra: partition key `user_id`, clustering `published_at DESC, episode_id DESC`.

**Fan-out worker:** idempotent, because Kafka delivers at least once. Write key is `(user_id, episode_id)` so a replay overwrites itself. Process subscribers in batches of 1,000 with a bounded worker pool.

### Edge cases (asked in the interview)

| Case | Handling |
|---|---|
| User subscribed to thousands of channels | Cap the pull set to recently active channels, paginate `GET /me/subscriptions`, rely on the materialized feed for most reads |
| Channel with a huge number of episodes | Keyset pagination on `(channel_id, published_at, episode_id)`, so page 500 costs the same as page 1 |
| Celebrity channel with millions of subscribers | Skip push, use pull-merge at read time. Cache the channel's latest episodes (it is a very hot key) |
| Subscribe | Insert the subscription, then backfill the latest 20 episodes of that channel into the user's feed |
| Unsubscribe | Delete the subscription. Filter the feed at read time against the subscription set (lazy), and clean feed entries in the background |
| New episode appears while scrolling | Cursor is keyset, so the user never sees duplicates. New items appear on the next refresh |
| Deleted episode | Soft delete (`deleted_at`), filtered on read |

### Back-of-envelope: users to channels to clips

100M users x 30 subscriptions = 3B subscription rows. 5M channels x 200 episodes = 1B episode rows. Storage and QPS above show metadata fits in a few sharded SQL nodes plus caches, while audio is the big cost (object storage + CDN).

### Trade-offs and follow-ups

* **SQL vs NoSQL:** SQL (Postgres) for catalog and subscriptions (relations, constraints, small rows). NoSQL (Cassandra / DynamoDB) for the feed (huge write volume, access by `user_id` only).
* **Consistency:** the feed is eventually consistent. Subscribe reads its own write because the subscription service is the source of truth and the feed backfills immediately.
* **Versioning:** `/v1` in the path. Add fields without a version bump. Deprecate with `Sunset` and `Deprecation` headers.
* **Monitoring:** feed latency p99, fan-out lag (Kafka consumer lag), cache hit rate, replica lag.

---

# 2. URL Shortener (TinyURL)

*(Interviewer hint from your notes: optimize only for a high volume of reads. A simple singleton service with a range-sharded database is enough. Add read replicas and edge caching if needed. Do not make it complex.)*

## 2.1 Functional requirements

* Create a **short URL** from a long URL (optional custom alias and expiry).
* **Redirect** from the short URL to the long URL.
* Delete a short URL. (Optional: click analytics.)
* Out of scope: user accounts beyond an API key, link previews, spam scanning.

## 2.2 Non-functional requirements and estimates

| Requirement | Target |
|---|---|
| Read-heavy | Reads : writes about 100 : 1 |
| Redirect latency | p99 under 50 ms (under 10 ms from cache or edge) |
| Availability | 99.99% for redirects |
| Uniqueness | No two long URLs share a code |
| Durability | A created link must never be lost |
| Short code | 7 characters, base62 |

**Estimates:**

* 100M new URLs per month = about **40 writes/s**.
* Reads: 100x = about **4k reads/s**, peak about 12k.
* 5 years: 6B URLs x 500 B = about **3 TB**.
* Code space: 62^7 = about **3.5 trillion**, plenty.
* Cache: 345M reads/day, hot 20% x 500 B = about **35 GB**, fits one Redis.

## 2.3 Core entities

| Entity | Fields |
|---|---|
| **UrlMapping** | `short_code` (PK), `long_url`, `user_id`, `created_at`, `expires_at` |
| **User** (optional) | `user_id`, `api_key_hash` |
| **ClickEvent** (async) | `short_code`, `ts`, `referrer`, `country` |

```sql
CREATE TABLE url_mappings (
  short_code  VARCHAR(10) PRIMARY KEY,
  long_url    TEXT NOT NULL,
  user_id     TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at  TIMESTAMPTZ
);
```

## 2.4 REST API design

| Method + path | Purpose | Success | Errors |
|---|---|---|---|
| `POST /v1/urls` | Create a short URL | 201 + `Location` | 400, 409 (alias taken), 422, 429 |
| `GET /{shortCode}` | **Redirect** | 301 or 302 + `Location` | 404, 410 (expired) |
| `GET /v1/urls/{shortCode}` | Metadata | 200 | 404 |
| `DELETE /v1/urls/{shortCode}` | Delete | 204 | 403, 404 |

### Detailed contract: create

```http
POST /v1/urls
Authorization: Bearer <api_key>
Idempotency-Key: 5c2e...
Content-Type: application/json

{ "long_url": "https://example.com/some/very/long/path?x=1",
  "custom_alias": "my-link",            // optional
  "expires_at": "2027-01-01T00:00:00Z"  // optional
}
```

```http
HTTP/1.1 201 Created
Location: /v1/urls/aZ3k9Qx

{ "short_code": "aZ3k9Qx",
  "short_url": "https://tiny.example/aZ3k9Qx",
  "long_url": "https://example.com/some/very/long/path?x=1",
  "created_at": "2026-10-15T10:00:00Z",
  "expires_at": "2027-01-01T00:00:00Z" }
```

| Case | Response |
|---|---|
| Invalid or non-http(s) URL, URL too long | `400` / `422` |
| Alias already used | `409` `alias_taken` |
| Throttled | `429` |

### Detailed contract: redirect

```http
GET /aZ3k9Qx
```

```http
HTTP/1.1 302 Found
Location: https://example.com/some/very/long/path?x=1
Cache-Control: private, max-age=60
```

| Code | When to use |
|---|---|
| **301** (permanent) | Browsers and CDNs cache it, so far less load, but you lose click counts and cannot change or expire the link |
| **302 / 307** (temporary) | Every click reaches you (analytics, expiry, edits work). Choose this by default and add `max-age` if you want some caching |

`404` unknown code, `410 Gone` expired link.

## 2.5 High-level design

```
 Client --> CDN / Edge cache --> Load Balancer --> Redirect Service (stateless)
                                                        |  cache-aside
                                                        v
                                                     Redis  --miss--> Read replicas --> Sharded DB (range on short_code)
 Client --> Load Balancer --> Create Service --> ID block allocator --> DB primary
                                         |
                                         +--> Kafka "click" (async) --> Analytics
```

* **Redirect path (99% of traffic):** edge cache or Redis hit returns immediately. A miss reads a replica and fills the cache.
* **Create path (1%):** get a unique ID, encode to base62, insert, return.
* Keep it simple: one logical ID service, stateless app servers, a sharded DB, replicas, a cache.

## 2.6 Low-level design

### Generating the short code

| Approach | Problem |
|---|---|
| Hash (MD5) and take 7 chars | Collisions, need a retry loop |
| Random 7 chars | Collisions, need an existence check |
| **Counter + base62 (choose this)** | No collisions by construction. Codes are sequential and guessable, so shuffle or encrypt the number (e.g. a small Feistel network) if enumeration matters |

To avoid a hot single counter, each app server **leases a block of 1,000 IDs** from the central counter (one atomic `UPDATE counter SET next = next + 1000 RETURNING next - 1000`), then hands them out locally with no network call.

```python
import threading

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode(n):
    if n == 0:
        return ALPHABET[0]
    s = []
    while n:
        n, r = divmod(n, 62)
        s.append(ALPHABET[r])
    return "".join(reversed(s))

def decode(s):
    n = 0
    for ch in s:
        n = n * 62 + ALPHABET.index(ch)
    return n

class IdBlock:
    """Local ID source. `lease(size)` atomically reserves `size` IDs centrally and returns the first."""
    def __init__(self, lease, size=1000):
        self.lease, self.size, self.cur, self.end = lease, size, 0, 0
        self.lock = threading.Lock()

    def next_id(self):
        with self.lock:
            if self.cur >= self.end:
                self.cur = self.lease(self.size)
                self.end = self.cur + self.size
            v = self.cur
            self.cur += 1
            return v
```

A crashed server wastes at most one block, which is fine given 3.5 trillion codes.

### Sharding and replication

* **Range-based sharding on `short_code`** (from your notes): shard 1 owns `0-...`, and so on. Simple routing table. Writes only reach the newest range, which is fine at 40 writes/s. Reads spread across shards and are absorbed by cache.
* Add **read replicas** per shard for read scale. Replica lag is acceptable because a link is rarely read in the first milliseconds after creation. For read-your-writes, the create response can seed the cache.
* Alternative: hash-based sharding spreads writes evenly but makes range moves harder.

### Caching

* Cache-aside in Redis: key `short_code`, value `long_url + expires_at`, TTL 24 h, LRU eviction.
* **Negative caching** of 404s for a few seconds blocks scans of random codes.
* Edge/CDN caching only if you use 301 or `Cache-Control` on 302.

### Custom alias and expiry

* Custom alias: insert with the alias as the primary key. A unique-key violation returns `409`. Never "check then insert".
* Expiry: **lazy check** on read (`expires_at < now` returns `410`) plus a nightly job that deletes expired rows.

### Trade-offs and follow-ups

* Same long URL submitted twice: either return the existing code (needs an index on a hash of `long_url`) or issue a new one (simpler, my default).
* Abuse: rate limit per API key, block known-bad domains.
* Analytics must never slow a redirect, so clicks go to Kafka asynchronously.

---

# 3. Distributed, Persistent Key-Value Store

*(High throughput, low latency, fault-tolerant, persistent, network service. Compare distributed (Redis/Memcache style) vs single-host (LevelDB style).)*

## 3.1 Functional requirements

* `put(key, value)`, `get(key)`, `delete(key)` over the network.
* Optional TTL per key. Optional batch get.
* Data survives node restarts (persistent).
* Out of scope: range scans and secondary indexes (mention as extension), multi-key transactions.

## 3.2 Non-functional requirements and estimates

| Requirement | Target |
|---|---|
| Write throughput | Very high (100k+ writes/s) |
| Latency | p99 under 10 ms |
| Fault tolerance | Survive node and AZ failure with no data loss for acknowledged writes |
| Scalability | Scale horizontally by adding nodes, minimal data movement |
| Consistency | **Tunable**: eventual (AP) by default, quorum reads and writes when needed. State the CAP choice out loud |
| Limits | Key up to 256 B, value up to 1 MB (average 10 KB) |

**Estimates:** 100k writes/s, 500k reads/s, 10 TB of data, replication factor 3. 30 TB of raw storage at roughly 50% target fill means about **15-30 nodes** with 4 TB SSDs. Write bandwidth about 1 GB/s at 10 KB values.

## 3.3 Core entities

| Entity | Fields |
|---|---|
| **Record** | `key`, `value`, `version` (timestamp or vector clock), `tombstone` flag, `expires_at` |
| **Node** | `node_id`, `address`, `status`, `tokens` (virtual node positions on the ring) |
| **Partition / token range** | `range_start`, `range_end`, `replica_nodes[]` |

## 3.4 REST API design

Namespaced by table so tenants are isolated:

| Method + path | Purpose | Success | Errors |
|---|---|---|---|
| `PUT /v1/tables/{table}/items/{key}` | Put (create or replace) | 201 created / 200 replaced | 400, 412, 413 (value too large), 503 |
| `GET /v1/tables/{table}/items/{key}` | Get | 200 | 404 |
| `DELETE /v1/tables/{table}/items/{key}` | Delete | 204 | |
| `POST /v1/tables/{table}/items:batchGet` | Batch get (keys in body, avoids long URLs) | 200 | 400 |

### Detailed contract: put with tunable consistency and optimistic concurrency

```http
PUT /v1/tables/sessions/items/user%3A42
Content-Type: application/octet-stream
X-Consistency: quorum            // one | quorum | all  (write quorum W)
X-TTL-Seconds: 3600              // optional
If-Match: "v17"                  // optional: only write if current version is v17

<value bytes>
```

```http
HTTP/1.1 200 OK
ETag: "v18"
```

| Case | Response |
|---|---|
| `If-Match` does not match the current version | `412 Precondition Failed` |
| Not enough replicas reachable for the requested consistency | `503` with `Retry-After` |
| Value larger than 1 MB | `413` |

```http
GET /v1/tables/sessions/items/user%3A42
X-Consistency: quorum

HTTP/1.1 200 OK
ETag: "v18"
Content-Type: application/octet-stream

<value bytes>
```

`404` if absent or expired. Keys are URL-encoded. If keys are arbitrary binary, use `POST .../items:get` with the key in the body.

## 3.5 High-level design

Two designs to compare (this is the core of the question):

| | **Single host (LevelDB / RocksDB style)** | **Distributed (Dynamo / Cassandra style)** |
|---|---|---|
| Where data lives | One machine's disk | Partitioned across many nodes, replicated 3x |
| Throughput | Limited by one machine | Scales with nodes |
| Fault tolerance | Machine dies, data unavailable until restored | Survives node and AZ loss |
| Consistency | Trivially strong | Tunable (quorum) |
| Complexity | Low | High (membership, repair, rebalancing) |
| Use when | Data fits one box, a failure is tolerable | Large data, high availability needed |

**Chosen design: leaderless, Dynamo-style**

```
 Client
   |
   v
 Load Balancer ---> any node acts as COORDINATOR for the request
                        |
                        | hash(key) -> position on the consistent-hash ring
                        v
        +-------------------------------------------+
        |  Ring of nodes (each with virtual nodes)  |
        |  Replicas = next N=3 distinct nodes       |
        +-------------------------------------------+
            |            |             |
          Node A       Node B        Node C        (each: commit log + memtable + SSTables)
```

* **Partitioning:** consistent hashing with virtual nodes, so adding or removing a node moves about 1/N of keys.
* **Replication:** N = 3 replicas on distinct nodes (and distinct AZs).
* **Quorum:** write to W replicas, read from R replicas. If **R + W > N** (for example 2 + 2 > 3), a read overlaps the latest write.
* **Storage engine:** an LSM tree per node, because it turns random writes into sequential appends.
* **Membership:** gossip protocol. **Repair:** hinted handoff, read repair, Merkle-tree anti-entropy.

## 3.6 Low-level design

### Write path

1. Client sends `PUT` to any node, which becomes the coordinator.
2. Coordinator hashes the key, finds the **preference list** (the N replica nodes).
3. It sends the write to all N replicas in parallel and acknowledges the client after **W** acks.
4. Each replica: append to the **write-ahead log** (sequential, fsync in small batches), update the in-memory **memtable**, ack.
5. When the memtable is full, flush it to an immutable **SSTable** on disk. Background **compaction** merges SSTables and drops tombstones and expired keys.

### Read path

1. Coordinator asks R replicas (or one, plus digests, for speed).
2. Each replica checks the memtable, then SSTables, newest first, skipping files with a **Bloom filter** that says the key is absent.
3. Coordinator picks the newest version. If replicas disagree, it returns the newest and writes it back to the stale replicas (**read repair**).

### Consistent hash ring

```python
import bisect, hashlib

class HashRing:
    def __init__(self, nodes=(), vnodes=100):
        self.vnodes, self.ring, self.owner = vnodes, [], {}
        for n in nodes:
            self.add(n)

    @staticmethod
    def _h(s):
        return int(hashlib.md5(s.encode()).hexdigest(), 16)

    def add(self, node):
        for i in range(self.vnodes):
            h = self._h(f"{node}#{i}")
            self.owner[h] = node
            bisect.insort(self.ring, h)

    def remove(self, node):
        for i in range(self.vnodes):
            h = self._h(f"{node}#{i}")
            del self.owner[h]
            self.ring.remove(h)

    def preference_list(self, key, n=3):
        """The n distinct physical nodes that hold `key` (walk clockwise from its hash)."""
        i = bisect.bisect(self.ring, self._h(key))
        out = []
        for k in range(len(self.ring)):
            node = self.owner[self.ring[(i + k) % len(self.ring)]]
            if node not in out:
                out.append(node)
                if len(out) == n:
                    break
        return out
```

### Failure handling

| Failure | Mechanism |
|---|---|
| A replica is down during a write | **Sloppy quorum + hinted handoff**: another node stores the write with a hint and replays it when the replica returns |
| Replicas drift apart | **Read repair** on reads, **Merkle-tree anti-entropy** in the background |
| Concurrent writes to the same key | Last-write-wins by timestamp (simple, can lose a write) or **vector clocks** and let the client merge |
| Node added or removed | Virtual nodes mean only about 1/N of keys stream to or from the new node |
| Datacenter or AZ loss | Place replicas across AZs so a quorum survives |
| Node crash | The commit log is replayed to rebuild the memtable |

### Alternative for strong consistency (CP)

Use **Raft per partition**: one leader per range, writes go through the leader and commit after a majority replicate. Reads go to the leader. You get linearizability at the cost of availability during a partition and slightly higher write latency. Say this is the right choice for configuration or metadata stores, while Dynamo-style is right for session and cache data.

### Trade-offs and follow-ups

* **CAP:** default AP with tunable quorums. With `quorum` reads and writes you get strong-ish reads while a majority is reachable.
* **Hot keys:** replicate hot keys to more nodes or put a cache in front.
* **Redis / Memcache:** in-memory, fastest, but persistence and durability are weaker. Use them as a cache in front of the persistent store.
* **Large values:** store a pointer and keep the blob in object storage.
* **Monitoring:** p99 latency per node, compaction backlog, hinted-handoff queue size, disk usage, repair lag.

---

# 4. Temp Email Generator (5-hour expiry)

## 4.1 Functional requirements

* Generate a random, disposable email address (an **inbox**) on demand, with no sign-up.
* **Receive** emails sent to that address (inbound SMTP).
* List messages, read one message, download attachments, delete a message.
* Everything **expires 5 hours** after the inbox is created (inbox, messages, attachments).
* Access control: only the person who created the inbox can read it.
* Optional: custom prefix, real-time push of new mail.
* Out of scope: sending email, long-term storage.

## 4.2 Non-functional requirements and estimates

| Requirement | Target |
|---|---|
| Inbound availability | High. Sending servers retry for days, but fast acceptance is still expected |
| Read latency | Message list p99 under 200 ms |
| Consistency | Eventual is fine for the list (new mail appears within seconds) |
| Bounded storage | TTL keeps data small, deletion must really happen (privacy) |
| Security / privacy | Unguessable inbox access, no cross-inbox reads, sanitized HTML, malware scanning |
| Abuse resistance | Spam floods, huge attachments, inbox-creation scripts |

**Estimates:** 1M inboxes/day x 5 emails = 5M emails/day = about **58/s** average, peak about 500/s. 50 KB average = **250 GB/day** ingested, but with a 5-hour retention only about 250 x 5/24 = **52 GB live** at any moment. The TTL is what makes this cheap.

## 4.3 Core entities

| Entity | Fields |
|---|---|
| **Inbox** | `inbox_id`, `address` (unique), `access_token_hash`, `created_at`, `expires_at` |
| **Message** | `message_id`, `inbox_id`, `from`, `subject`, `received_at`, `size_bytes`, `body_ref` (object key), `attachments[]`, `expires_at` |
| **Attachment** | `attachment_id`, `message_id`, `filename`, `content_type`, `size_bytes`, `blob_ref` |

## 4.4 REST API design

| Method + path | Purpose | Success | Errors |
|---|---|---|---|
| `POST /v1/inboxes` | Create an inbox | 201 | 400, 429 |
| `GET /v1/inboxes/{inboxId}` | Inbox info and remaining TTL | 200 | 401, 404, 410 |
| `GET /v1/inboxes/{inboxId}/messages?limit=&cursor=` | List messages | 200 | 401, 404, 410 |
| `GET /v1/inboxes/{inboxId}/messages/{messageId}` | Read one message | 200 | 401, 404, 410 |
| `GET /v1/inboxes/{inboxId}/messages/{messageId}/raw` | Raw `.eml` | 200 | |
| `GET /v1/inboxes/{inboxId}/messages/{messageId}/attachments/{attachmentId}` | Download attachment | 200 | |
| `DELETE /v1/inboxes/{inboxId}/messages/{messageId}` | Delete one message | 204 | |
| `DELETE /v1/inboxes/{inboxId}` | Delete the inbox now | 204 | |
| `GET /v1/inboxes/{inboxId}/events` | Server-Sent Events stream of new mail | 200 (stream) | |

### Detailed contract: create inbox

```http
POST /v1/inboxes
Content-Type: application/json

{ "prefix": "shopping" }        // optional, otherwise random
```

```http
HTTP/1.1 201 Created
Location: /v1/inboxes/ib_7Kq2

{
  "inbox_id": "ib_7Kq2",
  "address": "shopping-x8k2p@tempmail.example",
  "access_token": "tm_5f1c0e...c9",      // shown ONCE, only a hash is stored
  "created_at": "2026-10-15T10:00:00Z",
  "expires_at": "2026-10-15T15:00:00Z"
}
```

All later calls send `Authorization: Bearer tm_5f1c0e...c9`.

### Detailed contract: list messages

```http
GET /v1/inboxes/ib_7Kq2/messages?limit=20
Authorization: Bearer tm_5f1c0e...c9
```

```http
HTTP/1.1 200 OK
{
  "data": [
    { "message_id": "msg_01", "from": "no-reply@shop.com", "subject": "Verify your email",
      "received_at": "2026-10-15T10:03:10Z", "size_bytes": 20480, "has_attachments": false }
  ],
  "next_cursor": null,
  "inbox_expires_at": "2026-10-15T15:00:00Z"
}
```

| Case | Response |
|---|---|
| Missing or wrong token | `401` (use `404` for a wrong inbox id to avoid revealing which inboxes exist) |
| Inbox expired | `410 Gone` `inbox_expired` |
| Over inbox-creation rate limit (per IP) | `429` |

## 4.5 High-level design

```
 Sender's mail server
        |  (MX record -> our SMTP fleet)
        v
 Network LB --> SMTP Gateway fleet
                   | 1. RCPT TO check: does the inbox exist? (Redis lookup)  -> reject unknown (550)
                   | 2. size limit, spam / virus scan, parse MIME
                   v
            Object store (bodies + attachments, grouped by expiry hour)
                   +
            Metadata store (messages by inbox, TTL)
                   |
                   +--> Event bus --> Push service (SSE) --> browser

 Browser --> API Gateway (rate limit) --> Inbox API --> Redis (inbox + token) / Metadata store / Object store

 Expiry: lazy check on every read + hourly cleanup worker
```

* **Inbound:** `MX` records point to the SMTP gateways. Reject mail for unknown inboxes **at `RCPT TO`**, so spam to random addresses never costs storage.
* **Outbound to the user:** the web client calls the API, or listens on the SSE stream for new mail.

## 4.6 Low-level design

### Address and token generation

* Address: `<prefix or random 10 base36>@<domain from a pool>`. Reserve atomically with a single command, which also sets the TTL: `SET inbox:addr:{address} {inbox_id} NX EX 18300` (5 h plus a small grace). `NX` guarantees uniqueness without a read-then-write race.
* Token: 128 random bits. Store only its hash (SHA-256). Anyone with the token has access, so treat it like a password.

### Storage choices

| Data | Store | Why |
|---|---|---|
| Inbox and address lookup | Redis (with TTL) backed by the DB | Fast `RCPT TO` check, expires itself |
| Message metadata | Cassandra / DynamoDB with TTL. Key: partition `inbox_id`, clustering `received_at DESC` | The only query is "messages of an inbox, newest first". Native TTL |
| Bodies, attachments | Object storage (S3) | Cheap, large blobs |

### Making the expiry really happen

Two layers, because each alone is not enough:

1. **Lazy enforcement:** every read checks `expires_at < now` and returns `410`. Correctness never depends on the cleanup job.
2. **Physical deletion:**
   * Metadata: the database TTL (Cassandra `USING TTL 18300`, DynamoDB TTL attribute).
   * Blobs: S3 lifecycle rules work in **whole days**, which is too coarse. Store blobs under an hour prefix `expire/2026101515/...` and have a cleanup worker delete the whole prefix once that hour has passed. A message's blob goes under the hour in which its inbox expires.

### SMTP gateway flow

1. `RCPT TO:<addr>` -> look up `inbox:addr:{addr}` in Redis. Missing means reply `550 no such user`.
2. `DATA` -> stream the message, enforce a size cap (for example 10 MB), abort if exceeded.
3. Parse MIME, run spam and virus scan, strip dangerous content.
4. Write blobs to S3, write metadata, publish `message.received` for push.
5. Reply `250 OK` only after the durable write, so a crash makes the sender retry (no loss, possible duplicate, which is why `message_id` is derived from the SMTP `Message-ID` header).

### Security and abuse

* Render HTML mail in a sandboxed iframe or sanitize it, block remote images by default (tracking pixels).
* Rate limit inbox creation per IP, cap messages per inbox and total size per inbox.
* Block attachment types such as executables, scan the rest.
* Do not log message contents. Hard-delete means the data is really gone.

### Trade-offs and follow-ups

* Redis as the source of truth for inboxes: acceptable because losing an inbox on a Redis failure only loses a disposable inbox. Keep a DB copy if you need stronger guarantees.
* Extending the TTL: allow only a bounded number of extensions so storage stays bounded.
* Real-time push: SSE is simpler than WebSockets since traffic is one way. Fall back to polling.

---

# 5. Movie Ticketing Platform

## 5.1 Functional requirements

* Browse **cities, theaters, movies, and showtimes**. Search.
* View the **seat map** for a show with live availability.
* **Select and hold seats** for a short time (for example 10 minutes).
* **Pay and book**. Get a confirmation and ticket.
* Cancel a booking (with refund rules).
* Admin or theater partners add shows.
* Out of scope: food orders, loyalty programs, dynamic pricing.

## 5.2 Non-functional requirements and estimates

| Requirement | Target |
|---|---|
| **No double booking** | Strong consistency for seat inventory (the central requirement) |
| Browse availability | High, read-heavy, cacheable |
| Flash crowds | A blockbuster release: 100k users chasing a few hundred seats in a minute |
| Latency | Browse p99 under 300 ms. Seat hold under 500 ms |
| Payment safety | Never charge twice, never charge without a seat |
| Holds expire automatically | Seats return to the pool if the user walks away |

**Estimates:** 1M bookings/day = about **12 per second** average. Hot shows spike to thousands of requests per second **on a small set of rows**, so contention, not throughput, is the problem. Catalog data is small and cacheable.

## 5.3 Core entities

| Entity | Key fields |
|---|---|
| **Movie** | `movie_id`, `title`, `duration`, `language`, `rating` |
| **Theater** | `theater_id`, `city_id`, `name`, `address` |
| **Screen** | `screen_id`, `theater_id`, `seat_layout` |
| **Seat** | `seat_id`, `screen_id`, `row`, `number`, `category` |
| **Show** | `show_id`, `movie_id`, `screen_id`, `start_time`, `base_price` |
| **ShowSeat** | `show_id`, `seat_id`, `status` (AVAILABLE / HELD / BOOKED), `held_by`, `hold_expires_at`, `booking_id` |
| **Booking** | `booking_id`, `user_id`, `show_id`, `status` (PENDING / CONFIRMED / CANCELLED / EXPIRED), `total_amount`, `idempotency_key` |
| **Payment** | `payment_id`, `booking_id`, `provider_ref`, `status`, `amount` |

```sql
CREATE TABLE show_seats (
  show_id TEXT, seat_id TEXT,
  status TEXT NOT NULL DEFAULT 'AVAILABLE',     -- AVAILABLE | HELD | BOOKED
  held_by TEXT, hold_expires_at TIMESTAMPTZ, booking_id TEXT,
  PRIMARY KEY (show_id, seat_id)
);
```

## 5.4 REST API design

| Method + path | Purpose | Success | Errors |
|---|---|---|---|
| `GET /v1/movies?city_id=&date=&limit=&cursor=` | Movies playing | 200 | |
| `GET /v1/shows?movie_id=&city_id=&date=` | Showtimes | 200 | |
| `GET /v1/shows/{showId}/seats` | Seat map with status | 200 | 404 |
| `POST /v1/shows/{showId}/seat-holds` | **Hold** seats | 201 | 409, 422 |
| `DELETE /v1/seat-holds/{holdId}` | Release a hold | 204 | 404 |
| `POST /v1/bookings` | Book using a hold (starts payment) | 201 / 202 | 409, 410, 402 |
| `GET /v1/bookings/{bookingId}` | Booking status | 200 | 404 |
| `POST /v1/bookings/{bookingId}/cancel` | Cancel | 200 | 409 |

The hold is its own resource, so it can be released or expire independently of the booking.

### Detailed contract: hold seats

```http
POST /v1/shows/sh_88/seat-holds
Authorization: Bearer <token>
Idempotency-Key: 3b9d...
Content-Type: application/json

{ "seat_ids": ["A7", "A8"] }
```

```http
HTTP/1.1 201 Created
{
  "hold_id": "hd_42",
  "show_id": "sh_88",
  "seat_ids": ["A7", "A8"],
  "expires_at": "2026-10-15T10:12:00Z"
}
```

```http
HTTP/1.1 409 Conflict
{ "type": ".../errors/seats-unavailable", "status": 409, "code": "seats_unavailable",
  "detail": "One or more seats are no longer available.", "unavailable_seat_ids": ["A8"] }
```

The hold is **all or nothing**: if any seat is taken, none are held.

### Detailed contract: create booking

```http
POST /v1/bookings
Idempotency-Key: 91ac...
{ "hold_id": "hd_42", "payment_method_token": "pm_tok_123" }
```

```http
HTTP/1.1 201 Created
{ "booking_id": "bk_9", "status": "CONFIRMED", "show_id": "sh_88", "seat_ids": ["A7","A8"],
  "total_amount": { "currency": "USD", "value": "28.00" } }
```

| Case | Response |
|---|---|
| Hold expired before payment | `410` `hold_expired` |
| Payment declined | `402` `payment_failed`, seats stay held until the hold expires |
| Payment provider slow | `202 Accepted` with `status: PENDING`, client polls `GET /bookings/{id}` or gets a webhook |
| Same `Idempotency-Key` retried | The original response is replayed, no second charge |

## 5.5 High-level design

```
 Client --> CDN --> API Gateway
                      |
      +---------------+----------------+---------------------+
      v               v                v                     v
 Catalog Service   Inventory/Booking   Payment Service    Notification Service
 (movies, shows)   Service             (talks to PSP)     (email/SMS/push)
      |               |                    |                    ^
 Catalog DB +      SQL DB (primary,        PSP webhook          |
 cache + search    sharded by show_id)        |                 |
                      ^                       v                 |
                      +------ Kafka: booking events ------------+
 Seat-hold expiry worker --> releases expired holds
 Virtual waiting room (queue) in front of hot shows
```

* **Catalog** is read-heavy and cacheable (CDN, Redis, read replicas, search index).
* **Inventory/Booking** is the strongly consistent core. One SQL primary per shard, sharded by `show_id`, so contention on a show stays on one node.
* **Payment** goes through an external payment provider.

## 5.6 Low-level design

### Preventing double booking: atomic conditional update

Do the hold in one transaction with a conditional update. Check the number of rows changed, and roll back unless it equals the number of seats requested:

```sql
BEGIN;
UPDATE show_seats
   SET status = 'HELD', held_by = :user, hold_expires_at = now() + interval '10 minutes'
 WHERE show_id = :show
   AND seat_id IN (:seat_ids)                         -- sorted order, avoids deadlocks
   AND (status = 'AVAILABLE'
        OR (status = 'HELD' AND hold_expires_at < now()));   -- expired holds are reusable
-- if rows_updated <> number_of_seats: ROLLBACK and return 409
COMMIT;
```

* The database row lock makes the check and the change atomic, so two users cannot both get the same seat.
* The **expiry predicate** means expired holds are reclaimable immediately, with no dependency on the sweeper being on time. A background sweeper still resets them for tidy seat maps.
* **Always lock seats in sorted order** so two overlapping requests cannot deadlock.

| Option | Verdict |
|---|---|
| `SELECT ... FOR UPDATE` then update | Correct but holds locks longer |
| **Conditional `UPDATE` (above)** | Short lock, single statement. Preferred |
| Optimistic version column | Fine at low contention, retries under heavy contention |
| Redis `SET seat NX EX 600` | Fast path for holds, but the DB must stay the source of truth |

### Booking as a saga

State machine: `HOLD -> PENDING -> CONFIRMED`, or `-> EXPIRED / CANCELLED`.

1. Hold seats (above).
2. Create the booking `PENDING` with the idempotency key (unique constraint on the key).
3. Charge the payment provider using the same idempotency key.
4. On success, in one transaction set the seats to `BOOKED` and the booking to `CONFIRMED`, then publish `booking.confirmed`.
5. On failure or timeout, the hold expires and the seats return to the pool.
6. **Payment succeeded after the hold expired** (race): attempt the conditional update again. If the seats are still free, confirm. Otherwise **refund automatically**.

### Flash-crowd handling

* **Virtual waiting room:** admit users in batches (token bucket on entry) so the booking service sees a bounded rate.
* Serve the seat map from cache with a few seconds of staleness. Only the hold call hits the primary, and a stale map just leads to a `409` the client handles.
* Limit holds per user and per show to prevent seat-hoarding bots.

### Trade-offs and follow-ups

* Hold duration: short (5-10 min) to keep inventory moving, long enough to pay.
* Search: Elasticsearch for movie and theater search, kept in sync from the catalog DB.
* Multi-region: keep each show's inventory in a **single home region** to avoid cross-region write conflicts.

---

# 6. Stock Alert Notification System

## 6.1 Functional requirements

* Users create **alert rules**: symbol plus condition (price rises to or above X, falls to or below X, optionally percent change), with channels (push, email, SMS).
* List, update, pause, delete alerts.
* When a rule's condition is met, **notify the user within a minute**.
* One-shot or repeating alerts (with a cooldown).
* Out of scope: trading, price charts, news.

## 6.2 Non-functional requirements and estimates

| Requirement | Target |
|---|---|
| Scale | **1M+ rules** (design for 10M), about 8k symbols |
| Timeliness | Notify within **60 s** of the condition being true |
| Reliability | Never miss an alert. At-least-once delivery with dedupe so the user is not spammed |
| Throughput | Price updates about 50k per second across all symbols (assumption) |
| Availability | Rules survive failures, workers recover quickly |

**Estimates:** a **naive full scan** of 10M rules once per minute is 10M / 60 = about **167k rule checks per second**, which is manageable when partitioned across workers. That is a valid baseline to mention first. The event-driven design below cuts the work to only the rules that can actually fire and gives sub-second latency.

## 6.3 Core entities

| Entity | Fields |
|---|---|
| **User** | `user_id`, contact info, channel preferences |
| **Alert** | `alert_id`, `user_id`, `symbol`, `type` (PRICE_ABOVE / PRICE_BELOW / PCT_CHANGE), `threshold`, `status` (ACTIVE / TRIGGERED / PAUSED / EXPIRED), `recurrence` (ONCE / REPEATING), `cooldown_seconds`, `channels[]`, `last_triggered_at` |
| **PriceTick** (stream only) | `symbol`, `price`, `ts` |
| **Notification** | `notification_id`, `alert_id`, `user_id`, `channel`, `status`, `sent_at`, `dedupe_key` |

```sql
CREATE TABLE alerts (
  alert_id TEXT PRIMARY KEY, user_id TEXT NOT NULL, symbol TEXT NOT NULL,
  type TEXT NOT NULL, threshold NUMERIC NOT NULL, status TEXT NOT NULL DEFAULT 'ACTIVE',
  recurrence TEXT NOT NULL DEFAULT 'ONCE', cooldown_seconds INT DEFAULT 0,
  channels TEXT[] NOT NULL, last_triggered_at TIMESTAMPTZ, created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX alerts_by_user   ON alerts (user_id, created_at DESC);
CREATE INDEX alerts_by_symbol ON alerts (symbol) WHERE status = 'ACTIVE';   -- worker loading
```

## 6.4 REST API design

| Method + path | Purpose | Success | Errors |
|---|---|---|---|
| `POST /v1/alerts` | Create an alert | 201 | 400, 422, 429 |
| `GET /v1/alerts?status=&symbol=&limit=&cursor=` | List my alerts | 200 | |
| `GET /v1/alerts/{alertId}` | One alert | 200 | 404 |
| `PATCH /v1/alerts/{alertId}` | Update threshold, pause, resume | 200 | 404, 409, 412 |
| `DELETE /v1/alerts/{alertId}` | Delete | 204 | 404 |
| `GET /v1/notifications?limit=&cursor=` | Notification history | 200 | |
| `PUT /v1/me/notification-channels/{type}` | Register a push token, email, or phone | 200 / 201 | 422 |

### Detailed contract: create alert

```http
POST /v1/alerts
Authorization: Bearer <token>
Idempotency-Key: c7e1...
Content-Type: application/json

{ "symbol": "AAPL", "type": "PRICE_ABOVE", "threshold": "250.00",
  "recurrence": "ONCE", "channels": ["push", "email"] }
```

```http
HTTP/1.1 201 Created
Location: /v1/alerts/al_31

{ "alert_id": "al_31", "symbol": "AAPL", "type": "PRICE_ABOVE", "threshold": "250.00",
  "status": "ACTIVE", "recurrence": "ONCE", "channels": ["push","email"],
  "created_at": "2026-10-15T10:00:00Z" }
```

| Case | Response |
|---|---|
| Unknown symbol | `422` `unknown_symbol` |
| Threshold not a positive number | `400` |
| Per-user alert limit exceeded (for example 100) | `429` or `422` `alert_limit_reached` |

`PATCH` uses `If-Match` (the alert's ETag) so two devices editing the same alert do not overwrite each other (`412`).

## 6.5 High-level design

```
 Market data feed --> Ingest --> Kafka "ticks" (partitioned by symbol)
                                       |
                                       v
                          Alert Evaluators (each owns a set of symbols)
                          in-memory rule index per symbol
                                       |  rule fires
                                       v
                      DB: atomic status update (ACTIVE -> TRIGGERED), dedupe
                                       |
                                       v
                          Kafka "notifications" --> Notification workers
                                       |              (push / email / SMS, retries, DLQ)
                                       v
                                  Notification log

 Alert API --> Alerts DB --(change events: create / update / delete)--> Kafka "rule-changes"
                                                                          |
                                                      consumed by the evaluator that owns the symbol
```

* **Partition by symbol:** all ticks and all rules for one symbol land on the same evaluator, which keeps that symbol's rules in memory.
* Rule changes flow to evaluators through a change topic, so no per-tick DB reads.

## 6.6 Low-level design

### The key data structure: two heaps per symbol

For one symbol, "price >= threshold" rules and "price <= threshold" rules can be kept in heaps. On a tick, only the rules whose thresholds are crossed come off the top, so the cost is proportional to the number of alerts that fire, not the number of rules:

```python
import heapq

class SymbolIndex:
    """All active rules for ONE symbol."""
    def __init__(self):
        self.above = []              # min-heap of (threshold, alert_id): fires when price >= threshold
        self.below = []              # max-heap via negation: fires when price <= threshold
        self.cancelled = set()       # lazy deletion for deleted or paused alerts

    def add(self, alert_id, kind, threshold):
        if kind == "ABOVE":
            heapq.heappush(self.above, (threshold, alert_id))
        else:
            heapq.heappush(self.below, (-threshold, alert_id))

    def cancel(self, alert_id):
        self.cancelled.add(alert_id)

    def on_price(self, price):
        fired = []
        while self.above and self.above[0][0] <= price:
            _, a = heapq.heappop(self.above)
            if a in self.cancelled:
                self.cancelled.discard(a)
            else:
                fired.append(a)
        while self.below and -self.below[0][0] >= price:
            _, a = heapq.heappop(self.below)
            if a in self.cancelled:
                self.cancelled.discard(a)
            else:
                fired.append(a)
        return fired
```

Each tick costs O(1) when nothing fires, and O(k log n) when k rules fire. Percent-change rules are converted to absolute thresholds from a reference price (for example the previous close), then indexed the same way. Rebuild the heaps periodically to clear the cancelled entries.

### Exactly-once trigger (even with at-least-once processing)

When a rule fires, do an atomic compare-and-set in the database before notifying:

```sql
UPDATE alerts SET status = 'TRIGGERED', last_triggered_at = now()
 WHERE alert_id = :id AND status = 'ACTIVE';
-- rows_updated = 1  -> this worker owns the trigger, enqueue the notification
-- rows_updated = 0  -> someone else already fired it (replay or duplicate), do nothing
```

For repeating alerts, the condition is `status='ACTIVE' AND (last_triggered_at IS NULL OR last_triggered_at < now() - cooldown)`. The notification record carries `dedupe_key = alert_id + trigger_time_bucket`, so channel workers retrying cannot send twice.

### Failure handling

| Failure | Handling |
|---|---|
| Evaluator crashes | Another worker takes the symbol's partition, loads its ACTIVE rules from the DB (`alerts_by_symbol`), and resumes from the last committed offset. Replayed ticks are harmless because of the compare-and-set |
| Duplicate tick | Idempotent as above |
| Notification channel is down | Retry with exponential backoff, then dead-letter queue. Fall back to another channel |
| Stale or missing ticks | Alert if no ticks arrive for a symbol during market hours |
| Late tick | Evaluate on arrival. The rule is level-based (a price at or above X), so a late tick still fires correctly |

### Scaling

* 8k symbols across, say, 64 partitions, with hot symbols (AAPL, TSLA) possibly pinned to their own partitions.
* 10M rules x about 100 B in memory = about 1 GB total, so it fits easily in memory across evaluators.
* Notification sending scales independently via its own topic.

### Trade-offs and follow-ups

* **Event-driven (above)** vs **periodic batch scan**: batch is simpler and good enough for a one-minute SLA, event-driven is sub-second and cheaper at scale.
* Avoid alert storms (a market crash fires many alerts at once) with a per-user rate cap and batching ("5 of your alerts fired").
* Trading halts and price corrections: define whether a corrected tick can re-arm an alert.

---

# 7. Operations at Scale

*(Topics from your notes: finding bottlenecks and fixing them, load balancers and access logs, multi-region load balancing and regional routing, slow-query detection, database load analysis, primary/replica architecture with replica lag, Terraform for infrastructure and multi-region deploys, splitting a monolith into microservices. Each question starts with the high-level design, then asks how to do it in the cloud.)*

This is a discussion round rather than one product, so the framework is adapted: requirements are operational targets, "entities" are the things you operate, "API" is the operational surface, and the deep dives are the answers to the question list.

## 7.1 Functional requirements (what the platform must let you do)

* **Detect** that something is slow or failing and find **where**.
* **Remediate** common bottlenecks (compute, database, network, dependencies).
* **Route** traffic across instances and regions, and fail over.
* **Provision and deploy** infrastructure repeatably, in multiple regions.
* **Evolve** the architecture (monolith to services) without downtime.

## 7.2 Non-functional requirements

| Requirement | Example target |
|---|---|
| Availability | 99.99% (about 53 min downtime per year) |
| Latency | p99 API under 300 ms |
| Recovery | RTO (time to recover) 15 min, RPO (data loss allowed) under 1 min for the primary database |
| Scalability | Horizontal scale of stateless tiers, 10x traffic headroom |
| Repeatability | All infrastructure in code, reviewed, and auditable |

## 7.3 Core entities (what you operate and measure)

| Entity | Notes |
|---|---|
| **Service / deployment** | Version, replicas, health, owner |
| **Region / AZ** | Failure domains |
| **SLI / SLO** | Latency, error rate, availability, with an error budget |
| **Alert + runbook** | Symptom-based alert pointing to a fix procedure |
| **Infra module (Terraform)** | VPC, cluster, database, load balancer |
| **Database topology** | Primary, replicas, replica lag |

## 7.4 Operational API surface (contracts)

Every service exposes these, and the load balancer and orchestrator depend on them:

| Endpoint | Purpose | Contract |
|---|---|---|
| `GET /healthz` (liveness) | Is the process alive? Failing means restart it | `200 {"status":"ok"}`. Cheap, no dependency calls |
| `GET /readyz` (readiness) | Can it take traffic? Failing means remove from the load balancer | `200` or `503` `{"checks":{"db":"ok","cache":"ok"}}` |
| `GET /metrics` | Prometheus metrics | Request rate, errors, latency histogram, saturation |

Every request carries `X-Request-Id` (generated at the edge, propagated and logged everywhere) plus a trace context (`traceparent`) so one request can be followed across services.

## 7.5 High-level design (multi-region on the cloud)

```
                       Global DNS / Anycast (latency-based or geo routing + health checks)
                         |                                       |
                 Region A (us-east)                        Region B (eu-west)
                         |                                       |
                  Regional L7 load balancer               Regional L7 load balancer
                  (access logs -> object storage)         (access logs -> object storage)
                         |                                       |
                 Stateless services (autoscaled, multi-AZ)  Stateless services
                         |                                       |
              Cache  |  Primary DB + replicas (multi-AZ)   <--async replication-->  Replica / second primary
                         |
                     Message bus
 Observability: metrics + logs + traces -> dashboards + alerts      Infra: Terraform per region
```

| Concern | AWS example | GCP / Azure equivalents |
|---|---|---|
| Global routing | Route 53 (latency, failover), Global Accelerator, CloudFront | Cloud DNS + Global LB, Traffic Manager / Front Door |
| Load balancing | ALB (L7), NLB (L4) | Cloud Load Balancing, Azure LB / App Gateway |
| Compute autoscale | Auto Scaling groups, EKS/ECS | MIG / GKE, VMSS / AKS |
| Database | RDS or Aurora Multi-AZ, read replicas, Global Database | Cloud SQL / Spanner, Azure SQL |
| Cache | ElastiCache | Memorystore, Azure Cache |
| Messaging | MSK / SQS / SNS | Pub/Sub, Event Hubs |
| Observability | CloudWatch, X-Ray, Managed Prometheus/Grafana | Cloud Monitoring, Azure Monitor |
| IaC | Terraform (any cloud), CloudFormation | Terraform, Bicep |

## 7.6 Low-level design: answers to the question list

### A. How do you detect bottlenecks in a system?

Use the **golden signals** per service and **USE** per resource:

* **RED** for services: **R**ate (requests per second), **E**rrors (percent), **D**uration (p50, p95, p99 latency, never only the average).
* **USE** for resources (CPU, memory, disk, network, connection pools): **U**tilization, **S**aturation (queue length, waits), **E**rrors.

Method: start from the user symptom (p99 up) -> find the service whose latency grew (distributed **trace**, or per-service dashboard) -> check its resources and its dependencies -> confirm with a profile or query plan -> fix -> verify with the same metric.

| Bottleneck | How to spot it | Typical remedy |
|---|---|---|
| CPU-bound service | High CPU, run queue grows, latency rises with load | Profile hot code, scale out, cache results |
| Memory / GC | Frequent GC pauses, OOM kills | Fix leaks, tune heap, bigger instances |
| Slow database | Slow query log, high DB CPU or IO, connection pool waits | Index, rewrite query, cache, replicas (section D) |
| Connection pool exhaustion | Threads waiting for a connection, latency cliff | Size pools correctly, add pooling proxy, cap concurrency |
| Slow dependency | Trace shows time in one downstream call | Timeouts, retries with backoff and jitter, **circuit breaker**, cache, async |
| Hot key / hot partition | One shard or cache node much busier | Better shard key, replicate hot keys, local cache |
| Network | High retransmits or bandwidth near limit | Compression, CDN, keep traffic in-AZ |
| Queue backlog | Consumer lag growing | Scale consumers, batch, fix slow handler |
| Thundering herd | Spike after cache expiry or restart | Request coalescing, jittered TTLs, warm caches |

### B. Load balancers and access logs

* **L4 (TCP) vs L7 (HTTP):** L4 is fast and protocol-agnostic. L7 can route by path or header, terminate TLS, retry, and rate limit. Use L7 for web APIs.
* **Algorithms:** round robin (default), least connections (uneven request cost), consistent hashing (cache affinity, sticky behavior).
* **Health checks:** the LB calls `/readyz` and removes failing instances. Connection **draining** lets in-flight requests finish during deploys.
* **Access logs** answer: status code distribution (spike in 5xx), latency per path (`request_time`, `target_response_time`), slowest endpoints, error rates per upstream instance, top clients (abuse). Ship to object storage and query with SQL (for example Athena or BigQuery), or stream into a log platform.
* **Reading them:** high LB-to-target latency means the backend is slow. High total time with low target time means client or network. 502/504 from one target means that instance is unhealthy.

### C. Multi-region load balancing and regional routing

| Strategy | How | Notes |
|---|---|---|
| **Geo / latency routing** | Global DNS or Anycast sends each user to the nearest healthy region | Default for user-facing APIs |
| **Active-active** | Every region serves traffic, data replicated across regions | Best latency and availability, hardest data consistency |
| **Active-passive** | One region serves, another is warm standby | Simpler, failover takes minutes |
| **Regional pinning** | Route a user or tenant to its home region (data residency, single writer) | Avoids multi-writer conflicts |

* **Failover:** health checks at the global layer pull a region out of DNS when it fails. Keep DNS TTLs short (30-60 s). Anycast reroutes faster than DNS.
* **Data:** async cross-region replication means a failover can lose the last seconds of writes (RPO > 0). Decide per dataset: single-writer-per-key with a home region, or conflict-free / last-write-wins merges.
* **Test it:** run regular failover game days.

### D. Slow-query detection and remedies, database load analysis

**Detect:** enable the slow query log (`log_min_duration_statement` in Postgres, `slow_query_log` in MySQL), and use `pg_stat_statements` or Performance Insights to rank queries by **total time** (calls x average time), not just the slowest single call. Watch DB CPU, IOPS, lock waits, connection count, buffer cache hit rate.

**Diagnose:** run `EXPLAIN (ANALYZE, BUFFERS)`. Look for sequential scans on big tables, wrong join order, sorts spilling to disk, estimates far from actual rows (stale statistics, run `ANALYZE`).

| Cause | Remedy |
|---|---|
| Missing index | Add an index matching the `WHERE` and `ORDER BY` (column order matters, leftmost prefix) |
| N+1 queries from the app | Batch with `IN (...)` or a join |
| `SELECT *` and big payloads | Select only needed columns |
| Deep `OFFSET` paging | Keyset pagination |
| Hot read query | Cache (cache-aside), or route to a read replica |
| Heavy report on the primary | Move to a replica or a warehouse |
| Lock contention | Shorter transactions, consistent lock order, smaller batches |
| Table too big | Partitioning, archiving, eventually sharding |
| Too many connections | Connection pooler (for example PgBouncer), smaller app pools |

### E. Primary / replica architecture and replica lag

* One **primary** takes writes. **Replicas** serve reads and provide failover candidates. Replication is usually asynchronous, so replicas can lag.
* **Measure lag:** `seconds_behind_master` (MySQL), replay lag or LSN difference (Postgres), cloud metrics such as `ReplicaLag`. Alert above a threshold (for example 5 s).
* **Why it lags:** a write burst, a long-running query on the replica blocking replay, an under-sized replica, a big transaction, network issues.
* **Why it matters:** read-after-write anomalies (a user saves, then reads from a lagging replica and sees old data).

| Technique | Effect |
|---|---|
| **Read-your-writes routing** | After a write, send that user's reads to the primary for a short window (a few seconds), or until the replica reaches the write's LSN |
| Lag-aware load balancing | Remove replicas above the lag threshold from the read pool |
| Semi-synchronous replication | Primary waits for at least one replica to acknowledge. Less data loss on failover, higher write latency |
| Split read traffic by need | Tolerant reads (feeds, search) to replicas, critical reads (balances) to the primary |
| Fix the cause | Faster replica, smaller transactions, avoid long replica queries |
| **Failover** | Promote the most caught-up replica. Async replication can lose the unreplicated tail (RPO) |

### F. Infrastructure as code (Terraform), multi-region deploy

* Everything (network, clusters, databases, load balancers, DNS, IAM) is declared in code, reviewed in pull requests, and applied from CI.
* **Layout:** reusable **modules** (`network`, `service`, `database`) called by per-environment, per-region configurations.
* **State:** remote backend (object storage) with **locking**, one state per environment and region so a failed apply has a small blast radius. Never commit state (it contains secrets).
* **Multi-region:** the same module instantiated once per region using provider aliases:

```hcl
provider "aws" {
  alias  = "use1"
  region = "us-east-1"
}
provider "aws" {
  alias  = "euw1"
  region = "eu-west-1"
}

module "app_use1" {
  source    = "./modules/app"
  providers = { aws = aws.use1 }
  env       = "prod"
}
module "app_euw1" {
  source    = "./modules/app"
  providers = { aws = aws.euw1 }
  env       = "prod"
}
```

* **Pipeline:** `fmt` and `validate`, then `plan` posted on the pull request, reviewed, then `apply` on merge. Roll out region by region (canary region first). Run drift detection on a schedule. Keep secrets in a secrets manager, not in variables files.

### G. Splitting a monolith into microservices

Do it incrementally (the **strangler fig** pattern), never as a big-bang rewrite:

1. **Why first:** only split for a real reason (independent scaling, team autonomy, deploy frequency, fault isolation). A modular monolith may be enough.
2. **Observability first:** metrics, logs, and tracing must exist before you add network hops.
3. **Find seams:** use business capabilities (bounded contexts), modules with low coupling and a clear data owner. Start with an edge capability (notifications, search) rather than the core.
4. **Put a facade in front:** the gateway routes a path to the new service while everything else still hits the monolith. Move traffic gradually (feature flag, percentage rollout), with an instant rollback.
5. **Separate the data:** the hardest part. Give each service its own database. Move data with **change data capture** or dual writes during migration, and use the **outbox pattern** to publish events atomically with the write.
6. **Anti-corruption layer:** the new service has its own clean model and translates at the boundary.
7. **Avoid a distributed monolith:** no shared database, no synchronous call chains that must all succeed, no lockstep deploys. Use async events where possible, with timeouts and circuit breakers on sync calls.
8. **Finish:** delete the old code path once traffic is fully moved.

### Trade-offs to mention

* More regions mean better latency and resilience but harder consistency and higher cost.
* More services mean team independence but more operational overhead and latency.
* More replicas mean read scale but more lag to handle.

---

# 8. Clicks per Page in the Last 5 Minutes

*(Jack's interview: walk through ingestion, processing, storage, and reads. How does it handle 10x traffic, late events, and worker crashes?)*

## 8.1 Functional requirements

* **Ingest** click events from web and mobile clients.
* **Query** the number of clicks for a page over the **last 5 minutes** (a sliding window), and the top N pages.
* Results are near real-time (within a few seconds).
* Out of scope: per-user analytics, long-term historical reports (these go to a batch pipeline).

## 8.2 Non-functional requirements and estimates

| Requirement | Target |
|---|---|
| Throughput | 50k events/s baseline, **500k/s at 10x** |
| Freshness | Counts visible within about 5 s |
| Read latency | p99 under 50 ms |
| Correctness | Close to exactly-once: crashes and replays must not double count |
| Late events | Accept events up to a stated lateness (for example 1 minute in the live path) |
| Availability | Ingestion must never block clients |

**Estimates:** 200 B per event, so 10 MB/s baseline and **100 MB/s at 10x**. Using 10-second buckets, 30 buckets cover 5 minutes. If 1M pages are active, that is about 30M live counters, small enough for Redis.

## 8.3 Core entities

| Entity | Fields |
|---|---|
| **ClickEvent** | `event_id` (UUID, for dedupe), `page_id`, `user_id`, `event_time` (client time), `ingest_time` |
| **WindowCount** | `page_id`, `bucket_start` (10 s aligned), `count` |

## 8.4 REST API design

| Method + path | Purpose | Success | Errors |
|---|---|---|---|
| `POST /v1/events/clicks` | Ingest a batch of clicks | **202 Accepted** | 400, 413, 429 |
| `GET /v1/pages/{pageId}/clicks?window=5m` | Clicks for one page | 200 | 400, 404 |
| `GET /v1/pages/clicks/top?window=5m&limit=10` | Top pages | 200 | 400 |

### Detailed contract: ingest

```http
POST /v1/events/clicks
Content-Type: application/json
Authorization: Bearer <sdk_key>

{ "events": [
    { "event_id": "e6f1...", "page_id": "pg_home", "user_id": "u_42", "event_time": "2026-10-15T10:00:03.120Z" },
    { "event_id": "a91c...", "page_id": "pg_cart", "user_id": "u_17", "event_time": "2026-10-15T10:00:03.480Z" }
] }
```

```http
HTTP/1.1 202 Accepted
{ "accepted": 2 }
```

`202` because the event is only queued, not yet counted. Batches up to 500 events. `413` if larger, `429` if throttled (SDK retries with backoff, and `event_id` makes retries safe).

### Detailed contract: read

```http
GET /v1/pages/pg_home/clicks?window=5m
```

```http
HTTP/1.1 200 OK
{ "page_id": "pg_home", "window_seconds": 300, "count": 18452, "as_of": "2026-10-15T10:05:00Z" }
```

Allowed `window` values are fixed (`1m`, `5m`, `15m`) so they map to whole numbers of buckets.

## 8.5 High-level design

```
 Browser / App SDK  (batches events, retries with the same event_id)
        |
        v
 Load Balancer --> Collector service (stateless: validate, enrich, append to Kafka, reply 202)
                          |  local pre-aggregation not needed here; the collector only forwards
                          v
                   Kafka topic "clicks"  (partitioned by page_id, hot pages salted)
                          |
                          v
          Stream processor (Flink / Kafka Streams)
          * event-time tumbling windows of 10 s
          * watermark + allowed lateness
          * keyed state with checkpointing (RocksDB)
                          |  upsert (page_id, bucket_start) = count
                          v
                 Serving store: Redis (hash per page) or Cassandra / Druid
                          ^
 Query API ---------------+   sum the last 30 buckets (or 5 x 1-minute buckets)

 Late-late events --> side output --> batch job corrects history (and long-term storage in a warehouse)
```

**Flow:** clients send batches. The collector validates and writes to Kafka, then returns `202`. The stream processor counts per page per 10-second event-time bucket and writes the result to the serving store. The query API sums the buckets inside the window.

## 8.6 Low-level design

### Why buckets: the sliding window

A true per-event sliding window is expensive. Instead keep fixed **10-second buckets** and sum the 30 most recent. The window is accurate to within one bucket, which is fine for a dashboard. Bucket id = `floor(timestamp / 10)`.

```python
class SlidingCounter:
    """In-memory model of the same idea: a ring buffer of buckets (used per page in the stream state)."""
    def __init__(self, bucket_sec=10, window_sec=300):
        self.b, self.n = bucket_sec, window_sec // bucket_sec
        self.ids = [None] * self.n          # bucket id stored in each slot
        self.cnt = [0] * self.n
        self.latest = -1                    # newest bucket id seen

    def add(self, ts, k=1):
        bid = int(ts) // self.b
        if bid <= self.latest - self.n:     # too late: older than the whole window
            return False
        self.latest = max(self.latest, bid)
        i = bid % self.n
        if self.ids[i] != bid:              # slot still holds an expired bucket: reuse it
            self.ids[i], self.cnt[i] = bid, 0
        self.cnt[i] += k
        return True

    def total(self, now):
        cur = int(now) // self.b
        return sum(c for bid, c in zip(self.ids, self.cnt)
                   if bid is not None and cur - self.n < bid <= cur)
```

### Partitioning and hot pages

* Key Kafka messages by `page_id` so one page's events are ordered and land on one partition.
* **Hot page** (a viral page gets half the traffic): one partition cannot keep up. Use **two-stage aggregation**: key by `page_id + random salt (0..7)`, pre-aggregate per salt, then a second stage merges the 8 partial counts per page. Counting is commutative, so no ordering is lost.

### Late events

| Lateness | Handling |
|---|---|
| Within **allowed lateness** (for example 1 minute) | Window stays open until `watermark > window end + lateness`. The event updates its bucket and the result is **upserted** again |
| Later than that | Sent to a **side output** and applied by a periodic batch correction job, or dropped for the live view (counts are for the live dashboard only) |

Use **event time**, not arrival time, for bucketing. The watermark is "the max event time seen minus a delay".

### Worker crashes (no double counting)

* The processor takes **checkpoints** (state plus Kafka offsets together). After a crash it restores the last checkpoint and replays from those offsets, so state is consistent.
* The sink is **idempotent**: it writes `(page_id, bucket_start) = full bucket count` (an overwrite), not `count += 1`. Replaying the same events rewrites the same number.
* If increments are unavoidable, dedupe by `event_id` (for example a short-lived set per bucket).
* Kafka producer in the collector uses idempotent producer settings, so retries do not duplicate in the log.

### 10x traffic

| Layer | Action |
|---|---|
| Collectors | Stateless, autoscale on CPU and request rate. Return `202` quickly |
| Kafka | Add partitions and brokers. Batch and compress |
| Processor | Raise parallelism up to the partition count. **Autoscale on consumer lag** |
| Hot keys | Salting (above) |
| Serving store | Shard by `page_id`, add Redis nodes, cache top-N results for a few seconds |
| Protection | Backpressure, per-key rate limits, shed non-critical events if overloaded |

### Reads

* Single page: `HGETALL clicks:{page_id}` (30 buckets), sum those with `bucket_start > now - 300 s`. Set a TTL of 10 minutes so old buckets expire on their own.
* Top N: maintain a sorted set per window refreshed by the processor every few seconds (`ZADD top5m {count} {page_id}`), so the read is `ZREVRANGE` and costs O(log n + N).

### Trade-offs and follow-ups

* **Accuracy vs cost:** exact sliding window versus 10-second buckets, which are cheaper and good enough.
* **Exactly-once:** achieved by idempotent sinks plus checkpoints, not by magic delivery guarantees.
* **Alternative stack:** write straight to a real-time OLAP store (Druid or ClickHouse) and query with SQL, simpler to operate with slightly higher read cost.
* **Monitoring:** consumer lag, end-to-end freshness (now minus latest processed event time), watermark delay, drop count for late events.

---

# Appendix A: Streaming and Concurrency Q&A

Short answers to the follow-up questions in "Jack's question" in your notes. Coding questions already covered in `coding_interview_questions_python.md` are cross-referenced.

## A.1 Streaming pipelines and Kafka

| Question | Answer |
|---|---|
| **Replay data without duplicates or gaps** (file -> Kafka -> Flink -> DB) | Give every event a deterministic ID. Make DB writes **idempotent** (upsert by that ID or a primary key). Replay from known offsets or checkpoints. Verify with counts and checksums per partition or time range, comparing source and sink. Replay into a staging table or topic first for large fixes |
| **"Make the pipeline faster": what do you ask before changing anything?** | Faster at what: throughput or latency? What is the target and current baseline? Where is the time spent (per-stage lag, CPU, I/O, downstream DB)? What is the cost and risk budget? Measure first, change one thing at a time, and compare against the baseline |
| **Batching: improves throughput, adds latency. How to pick a size?** | Define the latency SLO. Sweep batch size (and linger time, for example Kafka `batch.size` and `linger.ms`) while measuring throughput and p99 latency. Choose the knee of the curve that still meets the SLO. Re-check under realistic load |
| **Counting purchases per minute with events up to 10 minutes late** | Window by **event time**, with a watermark and **allowed lateness of 10 minutes**. Late events update the earlier window and **upsert** the new count to the serving store. Consumers read the latest value. Reconcile with a batch job. Tell users that recent minutes can still change |
| **Producers outpace consumers: what to check first? How to control the backlog?** | Check consumer lag per partition (skew means a hot key), processing time per message, and downstream DB or API latency. Then: scale consumers up to the partition count, add partitions, batch work, remove the slow dependency, and apply backpressure or rate-limit producers. Ensure retention is longer than the worst expected backlog |
| **Rebalance happens mid-batch: unfinished work and offsets?** | Commit offsets only **after** processing succeeds. Use a rebalance listener to finish or abandon the batch and commit what is done when partitions are revoked. Use the cooperative sticky assignor to reduce disruption. Because uncommitted work will be redelivered, processing must be **idempotent** |
| **Partition customer orders: what if one customer is half the traffic?** | Key by the entity that needs ordering (usually `order_id`, not `customer_id`), which spreads load. If per-customer order is truly needed, give the huge customer dedicated partitions or a salted key and accept ordering only within each salt |
| **Charge then crash before committing the offset: avoid a second charge on replay** | Make the charge idempotent. Use `order_id` (or event ID) as the idempotency key to the payment provider, and a unique constraint on `payments(order_id)` written with the result. On replay, look up the state (`CHARGED`), skip the call, then commit. Never rely on the offset commit for correctness |
| **Schema or database change while producers and consumers deploy at different times** | Make changes backward and forward compatible: add optional fields, never rename or repurpose. Use a schema registry. Roll out with **expand and contract**: add the new column or field, deploy readers that understand both, then writers, then remove the old one. Version events and **upcast** old events when replaying |
| **Latency and throughput of Kafka producers** | `acks=all` plus idempotent producer for safety. Batching and compression for throughput. Partition count sets maximum consumer parallelism |
| **Cache tuning (LRU)** | Watch hit ratio, evictions, memory, and latency. A low hit ratio with many evictions means too little memory or a poor key design. If metrics are missing, **expose them first** (hits, misses, evictions, size), then tune |

## A.2 Coding questions in that interview

| Question | Where |
|---|---|
| Merge k sorted event lists. Complexity? Not in memory? | Heap merge, O(N log k) time, O(k) space (`heapq.merge`). If the lists do not fit in memory, stream each from disk through buffered readers (external k-way merge). See the Merge k Sorted Lists entry in `coding_interview_questions_python.md` |
| Count events in (t - W, t] for each event, in O(n) | Two pointers, see "Count Events in the Window" in `coding_interview_questions_python.md` |
| Key-value store with timestamped writes | See "Time Based Key-Value Store" in `coding_interview_questions_python.md` |
| Subset sum of bank transactions equals target | See "Warehouse Loading / Bank Transactions" in `coding_interview_questions_python.md` |

## A.3 Threading and concurrency

**Two threads check "does the key exist?" then insert if missing: what goes wrong?** A race (check-then-act): both see "missing" and both insert, so one overwrites the other or you get duplicates. Fix by making the check and the insert **one atomic step**: hold a lock around both, use an atomic primitive (`dict.setdefault`, `putIfAbsent`), or in a database use a **unique constraint** and handle the conflict.

```python
import threading
lock = threading.Lock()
store = {}

def insert_if_absent(key, value):
    with lock:                      # check and insert as one atomic step
        if key in store:
            return False
        store[key] = value
        return True
```

**Thread 1 locks A then B, thread 2 locks B then A: how can it deadlock? How to prevent?** Each holds one lock and waits forever for the other. Prevent with a **global lock order** (always acquire in the same order, for example by lock id), acquire with a **timeout** and back off, hold fewer locks or use one coarse lock, or avoid nested locking.

```python
def lock_both(a, b):
    first, second = sorted((a, b), key=id)      # same global order for every caller
    with first:
        with second:
            ...                                  # critical section
```

**Token bucket rate limiter (capacity N, refill R per second), thread-safe.** Refill lazily when a request arrives, based on elapsed time, so no background thread is needed. A lock protects the read-modify-write.

```python
import time, threading

class TokenBucket:
    def __init__(self, capacity, refill_rate, clock=time.monotonic):
        self.cap, self.rate, self.clock = capacity, refill_rate, clock
        self.tokens, self.last = float(capacity), clock()
        self.lock = threading.Lock()

    def allow(self, n=1):
        with self.lock:
            now = self.clock()
            self.tokens = min(self.cap, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens >= n:
                self.tokens -= n
                return True
            return False
```

Complexity O(1) per call. For a distributed limiter, keep the same state in Redis and update it with a Lua script so the read-modify-write is atomic.

**Bounded queue for many producers and consumers. Block when full or empty. How does shutdown work?** Use one lock with two condition variables (`not_full`, `not_empty`). Always wait in a `while` loop (not `if`) to handle spurious wakeups. For shutdown, add a `close()` that sets a flag and wakes everyone: producers then raise an error, consumers drain the remaining items and then see "closed".

```python
import threading
from collections import deque

class Closed(Exception):
    pass

class BoundedQueue:
    def __init__(self, cap):
        self.q, self.cap, self.closed = deque(), cap, False
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)

    def put(self, x):
        with self.lock:
            while len(self.q) >= self.cap and not self.closed:
                self.not_full.wait()
            if self.closed:
                raise Closed
            self.q.append(x)
            self.not_empty.notify()

    def get(self):
        with self.lock:
            while not self.q and not self.closed:
                self.not_empty.wait()
            if not self.q:
                raise Closed              # closed and fully drained
            x = self.q.popleft()
            self.not_full.notify()
            return x

    def close(self):
        with self.lock:
            self.closed = True
            self.not_full.notify_all()
            self.not_empty.notify_all()
```

---

# Appendix B: Quick Comparison and Checklist

| Problem | The one idea to remember |
|---|---|
| Podcast feed | Hybrid fan-out: push for normal channels, pull for celebrities. Keyset cursor pagination |
| TinyURL | Counter in blocks + base62, range-sharded DB, cache, 302 for analytics |
| Key-value store | Consistent hashing + N replicas + quorum (R + W > N) + LSM tree |
| Temp email | Reject unknown recipients at SMTP, lazy expiry + hourly physical cleanup, token-per-inbox |
| Movie tickets | Atomic conditional `UPDATE` with hold expiry, saga for payment, waiting room for flash crowds |
| Stock alerts | Per-symbol heaps, partition by symbol, compare-and-set so an alert fires once |
| Ops at scale | RED + USE, trace to the slow hop, replica lag with read-your-writes, Terraform modules per region, strangler fig |
| Clicks per page | Event-time 10 s buckets, watermark + lateness, idempotent upserts, salted hot keys |

**Always finish with:** the main bottleneck, the failure modes you handled, what you would monitor, and what you would do next with more time.
