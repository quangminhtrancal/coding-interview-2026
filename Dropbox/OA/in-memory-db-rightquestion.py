'''

https://leetcode.com/discuss/post/6866221/codesignal-coding-challenge-by-anonymous-xywa/

Design an in-memory database that stores records, where:

Each record is accessed by a unique string key.
Each record contains multiple field-value pairs:
Field: string
Value: integer
The following operations need to be implemented and each has a unique timestamp (strictly increasing).
COMPARE_AND_DELETE
COMPARE_AND_SET
COMPARE_AND_SET_WITH_TTL
GET
GET_WHEN
SCAN
SET
SET_WITH_TTL
🔹 Level 1: Basic operations

Supports basic CRUD-style field operations:
• SET <timestamp> <key> <field> <value> → Insert or update a field in a record. Create record if not exists.
• COMPARE_AND_SET <timestamp> <key> <field> <expectedValue> <newValue> → Update if current value equals expectedValue.
• COMPARE_AND_DELETE <timestamp> <key> <field> <expectedValue> → Delete if current value equals expectedValue.
• GET <timestamp> <key> <field> → Return the field’s value, or empty string if not found.

  ["SET", "0", "A", "B", "4"],           // A = { B: 4 }
  ["SET", "1", "A", "C", "6"],           // A = { B: 4, C: 6 }
  ["COMPARE_AND_SET", "2", "A", "B", "4", "9"],   // A = { B: 9, C: 6 }
  ["COMPARE_AND_SET", "3", "A", "C", "4", "9"],   // fail, C is 6
  ["COMPARE_AND_DELETE", "4", "A", "C", "6"],     // A = { B: 9 }
  ["GET", "5", "A", "C"],                // ""
  ["GET", "6", "A", "B"]                 // "9"
🔹 Level 2: Scan and filter

add querying capabilities:
• SCAN <timestamp> <key> → Return all fields of a record, sorted lexicographically:
"<field1>(<value1>), <field2>(<value2>)".
• SCAN_BY_PREFIX <timestamp> <key> <prefix> → Return fields starting with prefix in same format.

  ["SET", "0", "A", "apple", "1"],       // A = { apple: 1 }
  ["SET", "1", "A", "banana", "2"],      // A = { apple: 1, banana: 2 }
  ["SCAN", "2", "A"],                    // "apple(1), banana(2)"
  ["SCAN_BY_PREFIX", "3", "A", "a"]      // "apple(1)"
🔹 Level 3: TTL (Time-To-Live)

Support expiring fields:
• SET_WITH_TTL <timestamp> <key> <field> <value> <ttl> → Insert/update field with expiration at timestamp + ttl.
• COMPARE_AND_SET_WITH_TTL <timestamp> <key> <field> <expectedValue> <newValue> <ttl> → Like COMPARE_AND_SET, but also updates TTL.
✅ Fields are valid in [timestamp, timestamp + ttl).

  ["SET", "1", "A", "B", "4"],                        // A = { B: 4 } (no TTL)
  ["SET_WITH_TTL", "2", "X", "Y", "5", "15"],         // X = { Y: 5 } expires at 17
  ["SET_WITH_TTL", "4", "A", "D", "3", "6"],          // A = { B: 4, D: 3 } D expires at 10
  ["COMPARE_AND_SET_WITH_TTL", "6", "A", "D", "3", "5", "10"], // D = 5, expires at 16
  ["GET", "7", "A", "D"],                             // "5"
  ["SCAN", "15", "A"],                                // "B(4), D(5)"
  ["SCAN", "17", "A"]                                 // "B(4)"
🔹 Level 4: Historical lookup

Adds ability to query historical values:
• GET_WHEN <timestamp> <key> <field> <atTimestamp> → Return the field’s value at atTimestamp.
✅ If atTimestamp = 0, behaves like normal GET.

  ["SET_WITH_TTL", "1", "A", "B", "3", "10"],         // B = 3, expires at 11
  ["COMPARE_AND_SET_WITH_TTL", "4", "A", "B", "3", "7", "9"], // B = 7, expires at 13
  ["GET", "10", "A", "B"],                            // "7"
  ["GET_WHEN", "13", "A", "B", "3"],                  // "3"
  ["GET_WHEN", "15", "A", "B", "13"]                  // ""

'''

import bisect

class InMemoryDatabase:
    def __init__(self):
        # Structure: { key: { field: [ (timestamp, value, expiry), ... ] } }
        self.db = {}

    def _get_active_version(self, key, field, query_ts):
        """
        Helper to find the valid value for a field at a specific point in time.
        query_ts: The point in time we are looking at.
        """
        if key not in self.db or field not in self.db[key]:
            return None
        
        history = self.db[key][field]
        # Binary search to find the latest version recorded at or before query_ts
        # We search for query_ts + 1 to find the rightmost insertion point
# the tuple (int(query_ts), float('inf'), float('inf')) is used as the search key for bisect_right. Here’s why both extra float('inf') values are needed:

# Each entry in history is a tuple: (timestamp, value, expiry).
# bisect_right compares tuples element-wise.
# You want to find the rightmost entry where timestamp <= query_ts.
# By using (int(query_ts), float('inf'), float('inf')), you ensure that if there are multiple entries with the same timestamp, the search will go past all of them (since float('inf') is greater than any possible value or expiry).
# This guarantees you get the latest version at or before query_ts, even if there are multiple updates at the same timestamp.


        idx = bisect.bisect_right(history, (int(query_ts), float('inf'), float('inf')))
        
        if idx == 0:
            return None
        
        ts, val, expiry = history[idx - 1]
        
        # 1. If val is None, it represents a deleted record
        # 2. If expiry exists, check if query_ts is within the valid range [ts, expiry)
        if val is None:
            return None
        if expiry is not None and int(query_ts) >= expiry:
            return None
            
        return val

    # --- LEVEL 1 & 2: Basic Ops & Scan ---

    def SET(self, timestamp, key, field, value):
        if key not in self.db:
            self.db[key] = {}
        if field not in self.db[key]:
            self.db[key][field] = []
        # expiry = None means it lasts forever
        self.db[key][field].append((int(timestamp), str(value), None))
        return ""

    def GET(self, timestamp, key, field):
        val = self._get_active_version(key, field, timestamp)
        return val if val is not None else ""

    def COMPARE_AND_SET(self, timestamp, key, field, expected, new_val):
        current = self._get_active_version(key, field, timestamp)
        if current == str(expected):
            self.SET(timestamp, key, field, new_val)
            return "true"
        return "false"

    def COMPARE_AND_DELETE(self, timestamp, key, field, expected):
        current = self._get_active_version(key, field, timestamp)
        if current == str(expected):
            # We "delete" by appending a None value with an immediate expiry
            if key in self.db and field in self.db[key]:
                self.db[key][field].append((int(timestamp), None, int(timestamp)))
                return "true"
        return "false"

    def SCAN(self, timestamp, key, prefix=None):
        if key not in self.db:
            return ""
        
        results = []
        # Sort fields lexicographically
        sorted_fields = sorted(self.db[key].keys())
        
        for f in sorted_fields:
            if prefix and not f.startswith(prefix):
                continue
            val = self._get_active_version(key, f, timestamp)
            if val is not None:
                results.append(f"{f}({val})")
        
        return ", ".join(results)

    # --- LEVEL 3: TTL (Time-To-Live) ---

    def SET_WITH_TTL(self, timestamp, key, field, value, ttl):
        if key not in self.db:
            self.db[key] = {}
        if field not in self.db[key]:
            self.db[key][field] = []
        
        expiry = int(timestamp) + int(ttl)
        self.db[key][field].append((int(timestamp), str(value), expiry))
        return ""

    def COMPARE_AND_SET_WITH_TTL(self, timestamp, key, field, expected, new_val, ttl):
        current = self._get_active_version(key, field, timestamp)
        if current == str(expected):
            return self.SET_WITH_TTL(timestamp, key, field, new_val, ttl).replace("", "true")
        return "false"

    # --- LEVEL 4: Historical Lookup ---

    def GET_WHEN(self, timestamp, key, field, at_timestamp):
        # We ignore the current request 'timestamp' and query the state at 'at_timestamp'
        val = self._get_active_version(key, field, at_timestamp)
        return val if val is not None else ""

def solution(queries):
    db = InMemoryDatabase()
    results = []
    
    for q in queries:
        op = q[0]
        if op == "SET":
            results.append(db.SET(q[1], q[2], q[3], q[4]))
        elif op == "GET":
            results.append(db.GET(q[1], q[2], q[3]))
        elif op == "COMPARE_AND_SET":
            results.append(db.COMPARE_AND_SET(q[1], q[2], q[3], q[4], q[5]))
        elif op == "COMPARE_AND_DELETE":
            results.append(db.COMPARE_AND_DELETE(q[1], q[2], q[3], q[4]))
        elif op == "SCAN":
            results.append(db.SCAN(q[1], q[2]))
        elif op == "SCAN_BY_PREFIX":
            results.append(db.SCAN(q[1], q[2], q[3]))
        elif op == "SET_WITH_TTL":
            results.append(db.SET_WITH_TTL(q[1], q[2], q[3], q[4], q[5]))
        elif op == "COMPARE_AND_SET_WITH_TTL":
            results.append(db.COMPARE_AND_SET_WITH_TTL(q[1], q[2], q[3], q[4], q[5], q[6]))
        elif op == "GET_WHEN":
            results.append(db.GET_WHEN(q[1], q[2], q[3], q[4]))
            
    return results

print(solution(
  [["SET", "0", "A", "B", "4"],
  ["SET", "1", "A", "C", "6"],
  ["COMPARE_AND_SET", "2", "A", "B", "4", "9"],
  ["COMPARE_AND_SET", "3", "A", "C", "4", "9"]]))



# import bisect

# class HistoryEntry:
#     def __init__(self, timestamp, value, expiry):
#         self.timestamp = int(timestamp)
#         self.value = value
#         self.expiry = expiry

#     def __lt__(self, other):
#         # Clean comparison: strictly object vs object
#         return self.timestamp < other.timestamp

# class InMemoryDatabase:
#     def __init__(self):
#         self.db = {}

#     def _get_active_version(self, key, field, query_ts):
#         if key not in self.db or field not in self.db[key]:
#             return None
        
#         history = self.db[key][field]
#         ts_int = int(query_ts)
        
#         # We create a dummy HistoryEntry object for comparison.
#         # We use a high value for timestamp comparison to find the right boundary.
#         # Note: value and expiry don't matter for the search logic.
#         target = HistoryEntry(ts_int, None, None)
        
#         # bisect_right finds the first index where entry.timestamp > ts_int
#         idx = bisect.bisect_right(history, target)
        
#         if idx == 0:
#             return None
        
#         entry = history[idx - 1]
        
#         # Validation Logic: check for tombstone or TTL expiration
#         if entry.value is None:
#             return None
#         if entry.expiry is not None and ts_int >= entry.expiry:
#             return None
            
#         return entry.value

#     # --- Level 1 & 2 Methods ---

#     def SET(self, timestamp, key, field, value):
#         if key not in self.db: self.db[key] = {}
#         if field not in self.db[key]: self.db[key][field] = []
#         self.db[key][field].append(HistoryEntry(timestamp, str(value), None))
#         return ""

#     def GET(self, timestamp, key, field):
#         val = self._get_active_version(key, field, timestamp)
#         return val if val is not None else ""

#     def COMPARE_AND_SET(self, timestamp, key, field, expected, new_val):
#         current = self._get_active_version(key, field, timestamp)
#         if current == str(expected):
#             self.SET(timestamp, key, field, new_val)
#             return "true"
#         return "false"

#     def COMPARE_AND_DELETE(self, timestamp, key, field, expected):
#         current = self._get_active_version(key, field, timestamp)
#         if current == str(expected):
#             ts = int(timestamp)
            
#             # Tombstone: value is None, expires immediately
#             self.db[key][field].append(HistoryEntry(ts, None, ts))
#             return "true"
#         return "false"

#     def SCAN(self, timestamp, key, prefix=None):
#         if key not in self.db: return ""
#         fields = sorted(self.db[key].keys())
#         results = []
#         for f in fields:
#             if prefix and not f.startswith(prefix): continue
#             val = self._get_active_version(key, f, timestamp)
#             if val is not None:
#                 results.append(f"{f}({val})")
#         return ", ".join(results)

#     # --- Level 3 & 4 Methods ---

#     def SET_WITH_TTL(self, timestamp, key, field, value, ttl):
#         if key not in self.db: self.db[key] = {}
#         if field not in self.db[key]: self.db[key][field] = []
#         expiry = int(timestamp) + int(ttl)
#         self.db[key][field].append(HistoryEntry(timestamp, str(value), expiry))
#         return ""

#     def COMPARE_AND_SET_WITH_TTL(self, timestamp, key, field, expected, new_val, ttl):
#         current = self._get_active_version(key, field, timestamp)
#         if current == str(expected):
#             self.SET_WITH_TTL(timestamp, key, field, new_val, ttl)
#             return "true"
#         return "false"

#     def GET_WHEN(self, timestamp, key, field, at_timestamp):
#         val = self._get_active_version(key, field, at_timestamp)
#         return val if val is not None else ""

# def solution(queries):
#     db = InMemoryDatabase()
#     res = []
#     for q in queries:
#         cmd = q[0]
#         if cmd == "SET": res.append(db.SET(q[1], q[2], q[3], q[4]))
#         elif cmd == "GET": res.append(db.GET(q[1], q[2], q[3]))
#         elif cmd == "COMPARE_AND_SET": res.append(db.COMPARE_AND_SET(q[1], q[2], q[3], q[4], q[5]))
#         elif cmd == "COMPARE_AND_DELETE": res.append(db.COMPARE_AND_DELETE(q[1], q[2], q[3], q[4]))
#         elif cmd == "SCAN": res.append(db.SCAN(q[1], q[2]))
#         elif cmd == "SCAN_BY_PREFIX": res.append(db.SCAN(q[1], q[2], q[3]))
#         elif cmd == "SET_WITH_TTL": res.append(db.SET_WITH_TTL(q[1], q[2], q[3], q[4], q[5]))
#         elif cmd == "COMPARE_AND_SET_WITH_TTL": res.append(db.COMPARE_AND_SET_WITH_TTL(q[1], q[2], q[3], q[4], q[5], q[6]))
#         elif cmd == "GET_WHEN": res.append(db.GET_WHEN(q[1], q[2], q[3], q[4]))
#     return res