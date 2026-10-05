"""
A token bucket rate limiter controls how often operations can proceed by keeping a bucket of tokens:

The bucket holds at most
capacity
tokens.
Tokens refill at
refill_rate
tokens per second.
A request for
k
tokens succeeds only if at least
k
tokens are available. On success, those tokens are deducted; on failure, the balance stays unchanged.
The bucket starts full unless the problem specifies otherwise.
What
try_acquire(k)
should do
Read the current time using a monotonic clock.
Compute the elapsed time since the previous refill update.
Add
elapsed × refill_rate
tokens, capped at
capacity
.
Update the last-refill timestamp.
If at least
k
tokens are available, deduct
k
and return
True
; otherwise return
False
.
For example, with capacity
5
and a refill rate of
1
token per second, an initially full bucket can grant five immediate one-token requests. After it’s empty, waiting about two seconds should make roughly two tokens available.

Thread-safety requirement
The refill and check-and-deduct steps must be one atomic operation. Protect them with a lock. If two threads both observe the same available token before either deducts it, both might otherwise succeed and overspend the bucket. Keep the lock around the short state update; don’t split the check and deduction into separate critical sections.

Details to clarify in an implementation
Whether
k <= 0
is invalid or treated specially.
Whether requests larger than
capacity
should always fail.
Whether tokens may be fractional. If so, retain fractional refill rather than rounding down elapsed time too early.
What should happen for invalid capacity or refill-rate values.
How the class is expected to be initialized and tested.
The main interview focus is combining correct lazy refill math with an atomic acquire operation, then testing refill limits, failed requests, and concurrent calls.


"""