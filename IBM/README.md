# IBM Senior Backend Developer / Architect - Coding Assessment Pack
Company: IBM
Language: Java 17+
Location: `Coding interview/IBM/`

Practice consolidation based on commonly reported IBM senior backend assessment areas. Not verbatim IBM content.

## Questions
1. RateLimiter (`IbmRateLimiter.java`) - thread-safe fixed-window rate limiter per client. `allow(clientId, nowMillis)` enforces N requests per window.
2. LRU Cache (`IbmLruCache.java`) - generic thread-safe LRU cache with O(1) get/put and eviction.
3. Idempotent Orders (`IbmIdempotentOrders.java`) - process each `idempotencyKey` exactly once under concurrency, return newest-first history.
4. Circuit Breaker (`IbmCircuitBreaker.java`) - CLOSED/OPEN/HALF_OPEN breaker with failure threshold and recovery timeout.
5. Log Analytics (`IbmLogAnalytics.java`) - parse log lines with Streams, count ERROR by service, top-K, filter by time range.
6. FIFO Hold Allocator (`IbmHoldAllocator.java`) - allocate N copies to earliest holds (createdAt, id), idempotent per hold, newest-first notifications.

## Run
```bash
cd "Coding interview/IBM"
javac *.java && java IbmRateLimiter && java IbmLruCache && java IbmIdempotentOrders && java IbmCircuitBreaker && java IbmLogAnalytics && java IbmHoldAllocator
```
