'''

Questions from: https://prachub.com/interview-questions/implement-an-in-memory-database-with-ttl-and-backup

QUESTION 1 (Level 1): Implement basic CRUD operations
- set(key, field, value): Insert or overwrite field-value pair for a key
- get(key, field) -> string: Return value or "" if absent
- delete(key, field) -> bool: Remove field, return true if deleted

QUESTION 2 (Level 2): Implement read-only listing operations
- scan(key) -> list[string]: Return all fields as "field(value)" sorted lexicographically
- scan_by_prefix(key, prefix) -> list[string]: Return only fields starting with prefix

QUESTION 3 (Level 3): Add timestamped operations with TTL support
- set_at(key, field, value, timestamp): Set with timestamp
- set_at_with_ttl(key, field, value, timestamp, ttl): Set with expiration [timestamp, timestamp+ttl)
- get_at, delete_at, scan_at, scan_by_prefix_at: Timestamped variants that respect TTL
- TTL semantics: Fields expire when timestamp >= timestamp_created + ttl

QUESTION 4 (Level 4): Implement backup and restore with TTL recalculation
- backup(timestamp): Save snapshot with remaining TTL for each field
- restore(now, timestamp_to_restore): Restore from latest backup <= timestamp_to_restore
  and recalculate expiry times based on remaining TTL at 'now'

========================
https://www.reddit.com/r/leetcode/comments/1lb1him/comment/myec2eo/?force-legacy-sct=1

The question had 4 stages. The base problem was to design an in memory database - by adding implementation for a few interface methods. More methods were added in each stage. You unlock the next stage by completing the current stage but you have an overview of each stage at the very beginning of the round.

The overview mentioned that stage 1 will be about implementing a database in-memory and have the basic get/set functionality. The next stage will have the introduction of a TTL and then next will require fetching point-in-time records from the database. (I don't remember stage 2).

When you reach the actual stage, the exact method signatures and more details about the expectation from the methods is added.

There are unit tests that your code needs to pass and then you proceed to the next round. These unit tests are viewable but not editable. There is a separate unit test file where you could make changes and try your code by adding debug logs. The code is not required to be super optimized though the limits of the environment were mentioned at the bottom.

I ran out of time and hence could not fix the deletion method in stage 4 and hence 4 test cases in the last stage could not pass. Result awaited.

=============================

https://github.com/MayukhSobo/in-memory-db
Level 1
Set(key, field, value string) - Should insert a field-value pair to the record associated with key. If the field in the record already exists, replace the existing value with the specified value. If record doesn't exist, create a new one.

Get(key, field string) *string - Should return the value contained within field of record associated with key. If record or field doesn't exist, should return nil

Delete(key, field string) bool - Should remove the field from the record associated with key. Returns true if the field was successfully deleted, and false if the key or the field do not exist in the database

Level 2
Scan(key string) []string - Should return a list of strings representing the fields of a record associated with the key. The returned list should be in the following format ["<field1>(<value1>)" , "<field2>(<value2>)", ...] where the fields are lexicographically sorted. If specified record doesn't exist, return empty list.

ScanByPrefix(key, prefix string) []string - Should return a list of strings representing some fields of a records associated with the key. Specifically, only fields that starts with the prefix should be included. The returned list should be the same format as the Scan operation with the fields sorted in lexicographical order.

Level 3
SetAt(key, field, value string, timestamp int) []string - Should insert a field-value pair or update the value of the field in the record associated with key

SetAtWithTtl(key, field, value string, timestamp, ttl int) []string - Should insert a field-value pair or update the value of the field in the record associated with key. Also sets its Time-to-Live starting at timestamp to be ttl. The ttl is the amount of time that this field-value pair should exist in the database, meaning it will be avaialble during the interval: [timestamp, timestamp + ttl]

DeleteAt(key, field string, timestamp int) bool The same as Delete, but with timestamp of the operation specified. Should return true if the field existed and was successfully deleted and false if the key didn't exist.

GetAt(key, field string, timestamp int) *string The same as Get, but with timestamp of the operation specified

ScanAt(key string, timestamp int) []string The same Scan but with the timestamp of the operation specified

ScanPrefixAt(key, prefix string, timestamp int) []string The same as ScanPrefix but with the timestamp of the operation specified.

=============================

https://prachub.com/interview-questions/implement-an-in-memory-database-with-ttl-and-backup
In-Memory Database (Levels 1–4: TTL and Backup/Restore)
Implement an in-memory database that stores records identified by a string key. Each record contains multiple string field → string value pairs.

You must support a set of operations that progressively add features.

Data model
key is a string.
Each key maps to a set of fields.
Each field maps to a value (both strings).
If an operation refers to a missing key or field, treat it as absent.

Assumption to make outputs well-defined (typical for OAs):

get* returns "" (empty string) when absent.
delete* returns true if something was deleted, else false .
scan* returns an empty list when nothing matches.
Level 1: Basic CRUD on fields
Implement:

set(key, field, value)
get(key, field) -> string
delete(key, field) -> bool
set inserts or overwrites the field’s value.

Level 2: Read-only listing
Implement:

scan(key) -> list[string]
scan_by_prefix(key, prefix) -> list[string]
Return format:

Each returned element is formatted as "field(value)" .
Results are sorted lexicographically by field .
scan_by_prefix returns only fields whose name starts with prefix .
Level 3: Timestamped operations + TTL
Add timestamped variants of the above operations. Tests will use either timestamped APIs or non-timestamped APIs, but never mix them.

All timestamped operations accept an integer timestamp.

Implement:

set_at(key, field, value, timestamp)
set_at_with_ttl(key, field, value, timestamp, ttl)
get_at(key, field, timestamp) -> string
delete_at(key, field, timestamp) -> bool
scan_at(key, timestamp) -> list[string]
scan_by_prefix_at(key, prefix, timestamp) -> list[string]
TTL semantics:

set_at_with_ttl makes the field valid over the half-open interval:
valid in [timestamp, timestamp + ttl)
Expired fields must not appear in get_at , scan_at , or prefix scans.
Time always moves forward: timestamps provided to operations are non-decreasing .
Level 4: Backup and restore
Implement:

backup(timestamp)
restore(timestamp, timestamp_to_restore)
Backup requirements:

backup(t) stores a snapshot of the database state at time t .
For fields with TTL, the backup must capture remaining TTL at backup time (i.e., how much lifetime is left at t ).
Restore requirements:

restore(now, timestamp_to_restore) restores the database from the latest backup whose backup time is ≤ timestamp_to_restore .
After restoring at current time now , TTL expiration must be recalculated based on remaining TTL stored in the backup:
If a field had remaining TTL r in the backup, then after restore at time now it should expire at now + r .
Fields that were already expired at the moment of backup should not be present in that backup.
Your implementation should correctly handle overwrites, deletions, scans, TTL expiry, and backup/restore interactions under the monotonic-time guarantee.

'''

#### GEMINI solution below ####
import collections


class FieldRecord:
    def __init__(self, value, expiry):
        self.value = value
        self.expiry = expiry

    def is_valid(self, timestamp):
        return timestamp < self.expiry

    def remaining_ttl(self, timestamp):
        return self.expiry - timestamp

class InMemoryDatabase:
    def __init__(self):
        # Data structure: { key: { field: FieldRecord } }
        self.db = collections.defaultdict(dict)
        # Backups: { backup_timestamp: deep_copy_of_db_state }
        self.backups = {}

    # --- Level 1 & 3: CRUD with Timestamps/TTL ---
    
    def set_at(self, key, field, value, timestamp, ttl=None):
        expiry = (timestamp + ttl) if ttl is not None else float('inf')
        self.db[key][field] = FieldRecord(value, expiry)
        return "OK"

    def set_and_compare(self, key, field, value, timestamp, expected_value):
        if key in self.db and field in self.db[key]:
            record = self.db[key][field]
            if record.is_valid(timestamp):
                if record.value != expected_value:
                    return False
                
        self.set_at(key, field, value, timestamp)
        return True

    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        return self.set_at(key, field, value, timestamp, ttl)

    def set_and_compare_with_ttl(self, key, field, value, timestamp, expected_value, ttl):
        if key in self.db and field in self.db[key]:
            record = self.db[key][field]
            if record.is_valid(timestamp):
                if record.value != expected_value:
                    return False
        self.set_at_with_ttl(key, field, value, timestamp, ttl)
        return True

    def get_at(self, key, field, timestamp):
        if key not in self.db or field not in self.db[key]:
            return ""
        record = self.db[key][field]
        if record.is_valid(timestamp):
            return record.value
        # Lazy cleanup (optional, but good for memory)
        # del self.db[key][field]
        return ""

    def delete_at(self, key, field, timestamp):
        if key in self.db and field in self.db[key]:
            record = self.db[key][field]
            if record.is_valid(timestamp):
                del self.db[key][field]
                return True
        return False

    # --- Level 2: Scanning ---

    def scan_at(self, key, timestamp):
        return self.scan_by_prefix_at(key, "", timestamp)

    def scan_by_prefix_at(self, key, prefix, timestamp):
        if key not in self.db:
            return []
        results = []
        # Sort fields lexicographically
        sorted_fields = sorted(self.db[key].keys())
        for field in sorted_fields:
            if field.startswith(prefix):
                record = self.db[key][field]
                if record.is_valid(timestamp):
                    results.append(f"{field}({record.value})")
        return results

    # --- Level 4: Backup and Restore ---

    def backup(self, timestamp):
        # Create a snapshot of all non-expired fields
        snapshot = {}
        for key, fields in self.db.items():
            key_snapshot = {}
            for field, record in fields.items():
                if record.is_valid(timestamp):
                    # Store remaining TTL: expiry - backup_time
                    remaining_ttl = record.remaining_ttl(timestamp)
                    key_snapshot[field] = {
                        'value': record.value,
                        'remaining_ttl': remaining_ttl
                    }
            if key_snapshot:
                snapshot[key] = key_snapshot
        self.backups[timestamp] = snapshot
        return len(snapshot) # Often returns count of keys or fields

    def restore(self, now, timestamp_to_restore):
        # Find latest backup at or before timestamp_to_restore
        available_backups = [t for t in self.backups if t <= timestamp_to_restore]
        if not available_backups:
            return False
        latest_backup_ts = max(available_backups)
        snapshot = self.backups[latest_backup_ts]
        # Reset DB state
        self.db = collections.defaultdict(dict)
        # Recalculate expiry based on 'now'
        for key, fields in snapshot.items():
            for field, data in fields.items():
                new_expiry = now + data['remaining_ttl']
                self.db[key][field] = FieldRecord(data['value'], new_expiry)
        return True
	
def run_tests():
    db = InMemoryDatabase()

    print("--- Level 1 & 2: Basic CRUD & Scans ---")
    db.set_at("user1", "name", "Alice", 0)
    db.set_at("user1", "email", "a@test.com", 0)
    db.set_at("user1", "age", "25", 0)
    
    print("Get name:", db.get_at("user1", "name", 1))           # "Alice"
    print("Scan user1:", db.scan_at("user1", 1))               # ['age(25)', 'email(a@test.com)', 'name(Alice)']
    print("Scan prefix 'e':", db.scan_by_prefix_at("user1", "e", 1)) # ['email(a@test.com)']

    print("\n--- Level 3: TTL ---")
    # Set with 5s TTL (expires at T15)
    db.set_at("user1", "session", "active", 10, ttl=5)
    print("Session at T12:", db.get_at("user1", "session", 12)) # "active"
    print("Session at T15:", db.get_at("user1", "session", 15)) # "" (Expired)

    print("\n--- Level 4: Backup & Restore ---")
    # Current State: name, email, age (no TTL), session (expired)
    db.set_at("user2", "temp", "val", 20, ttl=10) # Expires at T30
    
    print("Backup at T25...")
    db.backup(25) # temp has 5s left (30-25)
    
    # Modify data after backup
    db.delete_at("user1", "name", 26)
    print("Name after delete:", db.get_at("user1", "name", 27)) # ""
    
    print("Restore at T40 from backup at T25...")
    db.restore(40, 25)
    
    # user1.name should be back
    print("Name after restore:", db.get_at("user1", "name", 41)) # "Alice"
    # user2.temp had 5s left at backup, so it should expire at 40 + 5 = 45
    print("Temp at T44:", db.get_at("user2", "temp", 44))        # "val"
    print("Temp at T46:", db.get_at("user2", "temp", 46))        # "" (Expired)


def test_claude_solution():
    """Test all 4 levels of the in-memory database implementation."""
    db = InMemoryDatabaseClaude()

    print("=" * 60)
    print("LEVEL 1 & 2 TESTS: Basic CRUD and Scanning")
    print("=" * 60)

    # Level 1: Basic operations
    db.set("user1", "name", "Alice")
    db.set("user1", "email", "alice@example.com")
    db.set("user1", "age", "30")

    print(f"get(user1, name): {db.get('user1', 'name')}")  # Alice
    print(f"get(user1, email): {db.get('user1', 'email')}")  # alice@example.com
    print(f"get(user1, missing): '{db.get('user1', 'missing')}'")  # ""

    # Level 2: Scanning
    print(f"scan(user1): {db.scan('user1')}")  # ['age(30)', 'email(alice@example.com)', 'name(Alice)']
    print(f"scan_by_prefix(user1, 'e'): {db.scan_by_prefix('user1', 'e')}")  # ['email(alice@example.com)']
    print(f"scan_by_prefix(user1, 'na'): {db.scan_by_prefix('user1', 'na')}")  # ['name(Alice)']

    # Delete
    print(f"delete(user1, age): {db.delete('user1', 'age')}")  # True
    print(f"delete(user1, age) again: {db.delete('user1', 'age')}")  # False
    print(f"scan(user1) after delete: {db.scan('user1')}")  # ['email(alice@example.com)', 'name(Alice)']

    print("\n" + "=" * 60)
    print("LEVEL 3 TESTS: Timestamped Operations + TTL")
    print("=" * 60)

    db2 = InMemoryDatabaseClaude()

    # Set with timestamp
    db2.set_at("session", "token", "abc123", 100)
    print(f"get_at(session, token, 150): {db2.get_at('session', 'token', 150)}")  # abc123

    # Set with TTL (valid from 200 to 210)
    db2.set_at_with_ttl("session", "temp_token", "xyz789", 200, 10)
    print(f"get_at(session, temp_token, 205): {db2.get_at('session', 'temp_token', 205)}")  # xyz789
    print(f"get_at(session, temp_token, 209): {db2.get_at('session', 'temp_token', 209)}")  # xyz789
    print(f"get_at(session, temp_token, 210): '{db2.get_at('session', 'temp_token', 210)}'")  # "" (expired)
    print(f"get_at(session, temp_token, 215): '{db2.get_at('session', 'temp_token', 215)}'")  # ""

    # Scan with TTL
    db2.set_at("user2", "field1", "val1", 300)
    db2.set_at_with_ttl("user2", "field2", "val2", 300, 20)  # Expires at 320
    db2.set_at_with_ttl("user2", "field3", "val3", 300, 10)  # Expires at 310

    print(f"scan_at(user2, 305): {db2.scan_at('user2', 305)}")  # All 3 fields
    print(f"scan_at(user2, 315): {db2.scan_at('user2', 315)}")  # field1, field2 (field3 expired)
    print(f"scan_at(user2, 325): {db2.scan_at('user2', 325)}")  # Only field1

    print("\n" + "=" * 60)
    print("LEVEL 4 TESTS: Backup and Restore")
    print("=" * 60)

    db3 = InMemoryDatabaseClaude()

    # Create data with various TTLs
    db3.set_at("user", "name", "Bob", 100)
    db3.set_at_with_ttl("user", "session", "active", 100, 50)  # Expires at 150
    db3.set_at_with_ttl("user", "temp", "data", 100, 20)  # Expires at 120

    print(f"Before backup - scan_at(user, 110): {db3.scan_at('user', 110)}")

    # Backup at time 110 (temp has 10s left, session has 40s left)
    db3.backup(110)
    print("Backup created at timestamp 110")

    # Modify data after backup
    db3.delete_at("user", "name", 115)
    db3.set_at("user", "newfield", "newval", 115)
    print(f"After changes - scan_at(user, 115): {db3.scan_at('user', 115)}")

    # Restore at time 200 from backup at 110
    db3.restore(200, 110)
    print("Restored to backup from timestamp 110, now at timestamp 200")

    # Check restored state: name should be back, session expires at 200+40=240, temp at 200+10=210
    print(f"After restore - scan_at(user, 200): {db3.scan_at('user', 200)}")  # All fields
    print(f"get_at(user, name, 200): {db3.get_at('user', 'name', 200)}")  # Bob
    print(f"get_at(user, temp, 209): {db3.get_at('user', 'temp', 209)}")  # data
    print(f"get_at(user, temp, 210): '{db3.get_at('user', 'temp', 210)}'")  # "" (expired)
    print(f"get_at(user, session, 239): {db3.get_at('user', 'session', 239)}")  # active
    print(f"get_at(user, session, 240): '{db3.get_at('user', 'session', 240)}'")  # "" (expired)
    print(f"get_at(user, newfield, 200): '{db3.get_at('user', 'newfield', 200)}'")  # "" (not in backup)

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
    print("\n" * 2)
    test_claude_solution()
	

