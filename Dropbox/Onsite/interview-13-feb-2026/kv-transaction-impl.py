'''
Key-Value Store with Transaction Support

Implements single-threaded transactions with conflict detection.
Uses optimistic concurrency control - conflicts are detected at commit time.
'''

class Transaction:
    def __init__(self, txid):
        self.txid = txid
        self.local_writes = {}      # key -> value (None means delete)
        self.local_reads = {}       # key -> value_read_at_begin
        self.deleted_keys = set()   # keys marked for deletion
        
    def get_local(self, key):
        '''Get value from local transaction writes'''
        if key in self.local_writes:
            return self.local_writes[key]
        return None
        
    def has_local_write(self, key):
        '''Check if key was written in this transaction'''
        return key in self.local_writes


class KV:
    _txid_counter = 0
    
    def __init__(self):
        self.stores = {}           # permanent key-value store: key -> value
        self.transactions = {}     # txid -> Transaction
        self.key_versions = {}     # key -> version (for conflict detection)
        
    @classmethod
    def _get_next_txid(cls):
        cls._txid_counter += 1
        return cls._txid_counter
    
    def begin(self):
        '''Start a new transaction'''
        txid = KV._get_next_txid()
        tx = Transaction(txid)
        self.transactions[txid] = tx
        return txid
    
    def get(self, txid, key):
        '''
        Get value for key within transaction context.
        Returns local writes first, then falls back to committed store.
        '''
        if txid is None:
            # Direct read without transaction
            return self.stores.get(key)
            
        if txid not in self.transactions:
            raise ValueError(f"Transaction {txid} does not exist")
            
        tx = self.transactions[txid]
        
        # Check local writes first (including deletes)
        if key in tx.local_writes:
            return tx.local_writes[key]  # Could be None (deleted)
        
        # Track read for conflict detection
        if key not in tx.local_reads:
            tx.local_reads[key] = self.stores.get(key)
        
        return self.stores.get(key)
    
    def put(self, key, value, txid):
        '''Write key-value pair within transaction context'''
        if txid is None:
            # Direct write without transaction
            self.stores[key] = value
            self.key_versions[key] = self.key_versions.get(key, 0) + 1
            return
            
        if txid not in self.transactions:
            raise ValueError(f"Transaction {txid} does not exist")
            
        tx = self.transactions[txid]
        tx.local_writes[key] = value
        if key in tx.deleted_keys:
            tx.deleted_keys.remove(key)
    
    def delete(self, key, txid):
        '''Mark key for deletion within transaction'''
        if txid is None:
            # Direct delete without transaction
            if key in self.stores:
                del self.stores[key]
                self.key_versions[key] = self.key_versions.get(key, 0) + 1
            return
            
        if txid not in self.transactions:
            raise ValueError(f"Transaction {txid} does not exist")
            
        tx = self.transactions[txid]
        tx.local_writes[key] = None  # None indicates deletion
        tx.deleted_keys.add(key)
    
    def commit(self, txid):
        '''
        Commit transaction with conflict detection.
        
        Conflict detection: If a key was read by this transaction and
        was modified by another committed transaction, this commit fails.
        
        Returns True if commit succeeded, False if conflict detected.
        '''
        if txid not in self.transactions:
            raise ValueError(f"Transaction {txid} does not exist")
            
        tx = self.transactions[txid]
        
        # Check for conflicts: for each key we read, check if it was modified
        for key, value_at_read in tx.local_reads.items():
            # Skip keys we wrote to ourselves
            if key in tx.local_writes:
                continue
                
            # Check if the current value in store differs from what we read
            current_value = self.stores.get(key)
            if current_value != value_at_read:
                # Conflict detected - another transaction modified this key
                del self.transactions[txid]
                return False
        
        # No conflicts - apply all writes to permanent store
        for key, value in tx.local_writes.items():
            if value is None:  # Delete operation
                if key in self.stores:
                    del self.stores[key]
                    self.key_versions[key] = self.key_versions.get(key, 0) + 1
            else:
                self.stores[key] = value
                self.key_versions[key] = self.key_versions.get(key, 0) + 1
        
        del self.transactions[txid]
        return True
    
    def rollback(self, txid):
        '''Rollback transaction - discard all local changes'''
        if txid not in self.transactions:
            raise ValueError(f"Transaction {txid} does not exist")
            
        del self.transactions[txid]
        return True


# Test cases
if __name__ == "__main__":
    print("=== Test Case 1: Basic Operations ===")
    kv = KV()
    
    # Direct operations (no transaction)
    kv.put("k1", "v1", None)
    kv.put("k2", "v2", None)
    print(f"get(k1) = {kv.get(None, 'k1')}")  # v1
    print(f"get(k2) = {kv.get(None, 'k2')}")  # v2
    
    print("\n=== Test Case 2: Transaction Commit ===")
    tx1 = kv.begin()
    kv.put("k3", "v3", tx1)
    print(f"get(k3) before commit = {kv.get(tx1, 'k3')}")  # v3 (from local)
    print(f"get(k3) global before commit = {kv.get(None, 'k3')}")  # None
    
    result = kv.commit(tx1)
    print(f"commit result = {result}")  # True
    print(f"get(k3) after commit = {kv.get(None, 'k3')}")  # v3
    
    print("\n=== Test Case 3: Transaction Rollback ===")
    tx2 = kv.begin()
    kv.put("k3", "v3_modified", tx2)
    print(f"get(k3) in tx2 = {kv.get(tx2, 'k3')}")  # v3_modified
    
    kv.rollback(tx2)
    print(f"get(k3) after rollback = {kv.get(None, 'k3')}")  # v3 (unchanged)
    
    print("\n=== Test Case 4: Conflict Detection (from problem) ===")
    kv2 = KV()
    kv2.put("k1", "v1", None)
    kv2.put("k2", "v2", None)
    
    # Transaction 1: Read k1, Read k2, Write k3
    tx1 = kv2.begin()
    print(f"TX1: read k1 = {kv2.get(tx1, 'k1')}")
    print(f"TX1: read k2 = {kv2.get(tx1, 'k2')}")
    kv2.put("k3", "v3", tx1)
    
    # Transaction 2: Read k2, Write k3, Read k4, Commit
    tx2 = kv2.begin()
    print(f"TX2: read k2 = {kv2.get(tx2, 'k2')}")
    kv2.put("k3", "v4", tx2)
    print(f"TX2: read k4 = {kv2.get(tx2, 'k4')}")
    
    # Commit tx1 first - should succeed
    print(f"TX1 commit result = {kv2.commit(tx1)}")  # True
    print(f"get(k3) after TX1 commit = {kv2.get(None, 'k3')}")  # v3
    
    # Commit tx2 - should succeed (k2 wasn't modified by tx1, k3 conflict doesn't matter since tx2 wrote it)
    print(f"TX2 commit result = {kv2.commit(tx2)}")  # True
    print(f"get(k3) after TX2 commit = {kv2.get(None, 'k3')}")  # v4
    
    print("\n=== Test Case 5: Conflict Detection (actual conflict) ===")
    kv3 = KV()
    kv3.put("k1", "v1", None)
    kv3.put("k2", "v2", None)
    
    # Transaction 1: Read k1
    tx1 = kv3.begin()
    print(f"TX1: read k1 = {kv3.get(tx1, 'k1')}")
    
    # Transaction 2: Read k1, Write k1, Commit
    tx2 = kv3.begin()
    print(f"TX2: read k1 = {kv3.get(tx2, 'k1')}")
    kv3.put("k1", "v1_modified", tx2)
    print(f"TX2 commit result = {kv3.commit(tx2)}")  # True
    
    # Transaction 1 tries to commit - should fail (read k1 which was modified)
    print(f"TX1 commit result = {kv3.commit(tx1)}")  # False (conflict)
    print(f"get(k1) final = {kv3.get(None, 'k1')}")  # v1_modified
    
    print("\n=== Test Case 6: Delete Operations ===")
    kv4 = KV()
    kv4.put("k1", "v1", None)
    
    tx1 = kv4.begin()
    kv4.delete("k1", tx1)
    print(f"get(k1) in tx1 after delete = {kv4.get(tx1, 'k1')}")  # None
    print(f"get(k1) global before commit = {kv4.get(None, 'k1')}")  # v1
    
    kv4.commit(tx1)
    print(f"get(k1) after commit = {kv4.get(None, 'k1')}")  # None (deleted)
    
    print("\n=== All tests passed! ===")
