https://leetcode.com/discuss/post/7687348/confluent-sse-system-design-round-what-t-z2nd/
Was asked temp email generator HLD , API , Entities , DB Choices, NFR


https://leetcode.com/discuss/post/8545763/confluent-uk-remote-interview-experience-68jv/
System Design
Building a podcast service, focus on feed generation.



https://leetcode.com/discuss/post/5634790/confluent-sse-bengaluru-remote-by-anonym-rop3/ 
questions around scaling

how to detect bottlenecks in system and how to remedy them

talked about load balancers, access logs of LB, multi region LB and regional routing
talked about slow query detection and remedies, db load analysis and master slave archi with replica lag b/w master slave
talked about IAC like terraform to maintain infra and deploy multi-region
talked about splitting monolith to microservices and how to go about it
each question focuses on hld first then followed by how to actually do it in cloud


https://leetcode.com/discuss/post/4188001/confluent-seniorstaff-software-engineer-5219u/
Design round: TinyUrl (Constraints: optimize only for high volume of reads - a simple singleton service with a sharded database(range based sharding on short url would suffice. You can add more read replicas with additional caching at the edge if needed). Do not make it complex

Design round 1(API design) - Spotify like system. Design APIs to retrieve X podcast channels at a time, X audio clips per podcast channel, Database design and high level component design [pagination, skip tokens, limit/offset, api versioning, back of the napkin calculation for number of users to number of podcast channels, podcast channel to number of audio clips per channel, corner cases[users subscribed to a lot of channels, channels with a lot of videos, etc.,]]



### Jack's question

**Interview 1**
* Resume stuff on troubleshooting prod issue / replay data
    * Patching live streaming services while maintaining service uptime
    * replaying data (to file -> then to kafka -> flink job -> db, asked how to avoid dupes or no missing data)
    * idempotent writes
* PO asks you to “make streaming pipeline faster” What would you ask/do before changing 
* Tell me about a time you chose a simpler solution over one that could scale further. Why?
    * What changes would you make now? Why?
* Batching improves throughput but adds latency. How would you choose a batch size and measure the trade off / performance changes?
* Say you are counting purchases per minute for a e-commerce service, but events can arrive up to 10 minutes late. How would you handle late arrivals and update the counts?
* Kafka / Data streaming
    * Producers are outpacing consumers. What would you check first, and how would you keep the backlog under control?
    * A Kafka consumer is processing a batch when a rebalance happens. How would you handle unfinished work and offset commits?
* Performance tuning / testing, tradeoffs on using LRU cache, what to look for for cache settings (evictions, hits, etc.)
    * What happens if metrics not available? (expose them, etc.)


**Interview 2 / 3**
* Design a service showing clicks per page over the last five minutes. Walk through ingestion, processing, storage, and reads. How would it handle 10× traffic, late events, and worker crashes?
* Kafka / Data streaming
    * How would you partition customer orders in Kafka? What if one customer produces half the traffic?
    * A consumer service charges a customer, then crashes before committing its offset. How would you prevent another charge when the event is replayed? (state/lock question)
    * Change to schema/downstream service/db while producers and consumers deploy at different times. How to roll out the changes and support replaying older events.

* Merge k sorted event lists into one sorted list. What’s the time complexity, and what changes if they don’t fit in memory?

* Given sorted event timestamps, count events in (t - W, t] for each event. For [1, 2, 4, 7] and W = 3, return [1, 2, 2, 1]. Can you do it in O(n)?

* Threading / Concurrency
    * Two threads check whether a key exists, then insert it if it’s missing. What can go wrong, and how would you fix it?
    * One thread locks A then B; another locks B then A. How can this deadlock, and how would you prevent it?
    * Implement a token bucket rate limiter with capacity N and refill rate R tokens per second. Each request consumes one token or is rejected if none are available. How would you make it thread-safe?
    * Implement a bounded queue for multiple producers and consumers. Block when it’s full or empty. How should shutdown work?

* Implement a key-value store with timestamped writes. Reads should return the latest value at or before the requested timestamp. Assume writes arrive in order for each key.

* Given bank transactions, positive for credits and negative for debits, determine whether any subset sums to a target balance. Each transaction can be used once. How would you improve on checking every subset?
    * For example, [7, -3, 5, -2] with 4 returns true because 7 + (-3) = 4.


## System Design Questions consolidated from Muse AI

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


