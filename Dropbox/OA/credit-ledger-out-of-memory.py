'''
https://prachub.com/interview-questions/implement-credit-ledger-with-out-of-order-timestamps

You are implementing a GPU credit ledger that supports adding credits, charging credits, and querying balances. Requests can arrive in any timestamp order (timestamps are not monotonic).

Design a data structure/class that supports these operations:

addCredit(timestamp, amount)
Records that amount credits were added at time timestamp .

chargeCredit(timestamp, amount)
Records that amount credits were requested to be charged at time timestamp .

getBalance(timestamp) -> integer
Returns the effective balance at time timestamp , computed using all recorded requests whose timestamps are <= timestamp .

Rules for computing the effective balance
When computing the balance at time T, consider all recorded addCredit and chargeCredit events 
with timestamp <= T and process them in increasing timestamp order.

Start from balance 0 .
For an addCredit , increase the balance.
For a chargeCredit :
If current balance is >= amount , deduct it (the charge succeeds).
Otherwise, do not deduct it (the charge is declined/ignored).
Tie-breaking (same timestamp)
If multiple events share the same timestamp, process them in this order:

All addCredit events at that timestamp (in insertion order)
All chargeCredit events at that timestamp (in insertion order)
Notes
Requests arrive out of order; you are allowed to cache/store all requests.
There is no strict time complexity requirement ; correctness is the priority.
Deliverable
Provide the API and implement the logic so that repeated calls to getBalance(T) always return the correct value according to the rules above.
'''

