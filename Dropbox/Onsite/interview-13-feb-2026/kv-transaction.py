'''
implement single threaded  transaction

resolve conflict during commit

Begin transaction:
    Read k1
    Read K2                     Begin transaction:
    Write K3, V3                    Read K2
Commit                              Write K3, V4
                                    Read K4
                                    Commit
then the right hand fail due to commit after

'''
class Transaction:
    def __init__(self):
            pass

class KV:

    txid = 0
    def __init__(self):
        self.txid = txid
        txid += 1

        self.stores = {}
        self.transactions = {}

    def put(key, value, txid):

    def get(txid, key):

    
    def commit(self, txid):

'''
https://leetcode.com/discuss/post/4985212/rippling-phonescreen-keyvalue-datastore-fi5hl/

KeyValue datastore with begin,commit and rollback.
Question is the same as discussed here. It also has some good solutions in the discussion forum.
https://leetcode.com/discuss/interview-question/279913/bloomberg-onsite-key-value-store-with-transactions
You are expected to implement and run the code with a few test cases.
Please Note-> They made it very clear at the beginning that they want the code to run or there will be a reject, so please keep that in mind when you start implementing.
My advice is to run the code after writing small logic of code in incremental way to make sure that you always have an executable code and you are not inroducing bugs and making it non-runnable as running the code without exceptions is of prime importance for this company.
The solution to this question is easily available in various discussion forums.
However in short it can be implemented as the psuedo code below.

Declare a Permament keyvalue hashmap
Decalre a Temporary keyvalue HashMap to store the temp transactions when begin is called
If rollback is called, you will delete the temporary HashMap.
If commit is called, you will copy the values from temporary HashMap to permanent hashmap
Please note, if you need to delete a value in the HashMap you need to mark it with some unique value to identify that this key needs to be deleted, otherwise if you delete it from the temphashmap, you will never know that it needs to be deleted from the permanent hashmap when commit is called.
For Nested Transactions , you will need to store the temporary hashmaps in a stack.
However, for senior candidates, I would recommend reading DDIA(Designing Data Intensive Applications) Chapter 3 as that will help you to understand the fundamentals behind this question.
This question can be also asked as a System Design Question in Onsite and the expectation from Senior/Staff would be to know the details explained in DDIA Chapter 3 Storage and Retrieval and bonus points if you can also explain the bits explained in Chapter 7 Transactions.
'''

'''
Other more advance questions

Design and implement an in-memory key–value store that supports basic operations plus transactions.

Core API
Implement the following operations:

get(key) -> value | null
Return the current value for key , or null / None if it does not exist.
put(key, value)
Set key to value .
delete(key)
Remove key if it exists.
Follow-up 1: Transactions (must support nested)
Add transactional operations:

begin() — starts a new transaction scope (transactions may be nested).
commit() -> bool — commits the current transaction.
Returns false (or throws) if there is no active transaction.
rollback() -> bool — rolls back the current transaction.
Returns false (or throws) if there is no active transaction.
After commit, changes in the committed transaction become visible in the parent transaction (or globally if committing the outermost transaction). After rollback, all changes made since the last begin() are undone.

Complexity requirement: Each operation should run in O(1) time on average (constant-time hash operations allowed). You may assume keys and values fit in memory.

Follow-up 2: Concurrency
Extend your design to support multi-threaded access:

Multiple threads may call get/put/delete/begin/commit/rollback concurrently.
Describe the thread-safety guarantees you provide (e.g., linearizability vs. weaker consistency) and what synchronization approach you would use.
Notes
Clarify how delete interacts with transactions (e.g., deleting a key inside a transaction should be reversible by rollback).
Be prepared to discuss edge cases such as committing/rolling back with no active transaction and nested transactions.
'''