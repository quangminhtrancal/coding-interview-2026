**Confluent notes**

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
