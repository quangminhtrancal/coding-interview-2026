import bisect
import threading

TOMBSTONE = object()                 # marks a deleted key in a write buffer / version chain


class ConflictError(Exception):
    """commit() lost to a transaction that committed a conflicting change first. Retry."""


class TransactionError(Exception):
    """Unknown or already finished transaction id."""


class Transaction:
    __slots__ = ("txid", "start_ts", "reads", "writes")

    def __init__(self, txid, start_ts):
        self.txid = txid
        self.start_ts = start_ts     # snapshot: sees commits with commit_ts <= start_ts
        self.reads = set()           # keys read from the snapshot (for serializable mode)
        self.writes = {}             # private write buffer: key -> value | TOMBSTONE


class KV:
    """MVCC store, optimistic commit-time validation.

    isolation="snapshot":     first committer wins on write-write conflicts.
    isolation="serializable": additionally aborts if anything the transaction read was
                              committed by someone else after it started (stops write skew).
    The single RLock makes every public method atomic; in a purely single-threaded program
    you can delete the `with self._lock:` lines and nothing else changes.
    """

    def __init__(self, isolation="snapshot"):
        assert isolation in ("snapshot", "serializable")
        self.isolation = isolation
        self._stamps = {}            # key -> [commit_ts, ...] ascending
        self._values = {}            # key -> [value | TOMBSTONE, ...] parallel to _stamps
        self._clock = 0              # timestamp of the latest commit
        self._next_txid = 1
        self._active = {}            # txid -> Transaction
        self._lock = threading.RLock()

    # ---- transaction lifecycle ----
    def begin(self):
        with self._lock:
            tx = Transaction(self._next_txid, self._clock)
            self._next_txid += 1
            self._active[tx.txid] = tx
            return tx.txid

    def get(self, txid, key, default=None):
        with self._lock:
            tx = self._tx(txid)
            if key in tx.writes:                         # read-your-own-writes
                value = tx.writes[key]
            else:
                tx.reads.add(key)
                value = self._read_at(key, tx.start_ts)  # snapshot read
            return default if value is TOMBSTONE else value

    def put(self, txid, key, value):
        with self._lock:
            self._tx(txid).writes[key] = value

    def delete(self, txid, key):
        with self._lock:
            self._tx(txid).writes[key] = TOMBSTONE

    def rollback(self, txid):
        with self._lock:
            self._tx(txid)
            del self._active[txid]                       # just drop the private buffer

    def commit(self, txid):
        with self._lock:                                 # validate + apply = ONE critical section
            tx = self._tx(txid)
            del self._active[txid]                       # finished whether it succeeds or not
            to_check = set(tx.writes)
            if self.isolation == "serializable":
                to_check |= tx.reads
            for key in to_check:
                stamps = self._stamps.get(key)
                if stamps and stamps[-1] > tx.start_ts:  # someone committed it after my snapshot
                    raise ConflictError(
                        f"tx {txid}: key {key!r} committed at ts={stamps[-1]} "
                        f"after tx started at ts={tx.start_ts}")
            if tx.writes:
                self._clock += 1
                for key, value in tx.writes.items():
                    self._stamps.setdefault(key, []).append(self._clock)
                    self._values.setdefault(key, []).append(value)
            return self._clock

    # ---- helpers ----
    def get_committed(self, key, default=None):
        """Latest committed value (auto-commit read)."""
        with self._lock:
            value = self._read_at(key, self._clock)
            return default if value is TOMBSTONE else value

    def _read_at(self, key, ts):
        stamps = self._stamps.get(key)
        if not stamps:
            return TOMBSTONE
        i = bisect.bisect_right(stamps, ts)              # newest version with commit_ts <= ts
        return self._values[key][i - 1] if i else TOMBSTONE

    def _tx(self, txid):
        try:
            return self._active[txid]
        except KeyError:
            raise TransactionError(f"transaction {txid} is not active") from None

class Session:
    """Nested-transaction API. State is per thread (threading.local); the store is shared."""

    def __init__(self, kv=None):
        self.kv = kv or KV()
        self._local = threading.local()

    def _st(self):
        st = self._local
        if not hasattr(st, "txid"):
            st.txid = None           # outermost MVCC transaction, or None if no transaction
            st.frames = []           # buffers for NESTED transactions (outermost writes live in the txn)
        return st

    # ---- transactions ----
    def begin(self):
        st = self._st()
        if st.txid is None:
            st.txid = self.kv.begin()
        else:
            st.frames.append({})

    def commit(self):
        st = self._st()
        if st.txid is None:
            return False
        if st.frames:                                    # nested commit: merge into the parent
            top = st.frames.pop()
            for key, value in top.items():
                if st.frames:
                    st.frames[-1][key] = value
                else:
                    self._apply(st.txid, key, value)
            return True
        txid, st.txid = st.txid, None
        self.kv.commit(txid)                             # may raise ConflictError; txn is already closed
        return True

    def rollback(self):
        st = self._st()
        if st.txid is None:
            return False
        if st.frames:
            st.frames.pop()
        else:
            txid, st.txid = st.txid, None
            self.kv.rollback(txid)
        return True

    # ---- data operations ----
    def get(self, key, default=None):
        st = self._st()
        if st.txid is None:
            return self.kv.get_committed(key, default)
        for frame in reversed(st.frames):                # innermost savepoint first
            if key in frame:
                value = frame[key]
                return default if value is TOMBSTONE else value
        return self.kv.get(st.txid, key, default)

    def put(self, key, value):
        self._write(key, value)

    def delete(self, key):
        self._write(key, TOMBSTONE)

    def _write(self, key, value):
        st = self._st()
        if st.txid is None:                              # auto-commit single write; retry on conflict
            while True:
                txid = self.kv.begin()
                self._apply(txid, key, value)
                try:
                    self.kv.commit(txid)
                    return
                except ConflictError:
                    continue
        elif st.frames:
            st.frames[-1][key] = value
        else:
            self._apply(st.txid, key, value)

    def _apply(self, txid, key, value):
        if value is TOMBSTONE:
            self.kv.delete(txid, key)
        else:
            self.kv.put(txid, key, value)

# ---- tests ----
import time


def test_whiteboard():
    kv = KV()
    t = kv.begin()
    for k in ("k1", "k2", "k4"):
        kv.put(t, k, k.upper())
    kv.commit(t)

    a, b = kv.begin(), kv.begin()                        # both start from the same snapshot
    kv.get(a, "k1"); kv.get(a, "k2"); kv.put(a, "k3", "V3")
    kv.get(b, "k2"); kv.put(b, "k3", "V4"); assert kv.get(b, "k4") == "K4"
    kv.commit(a)                                          # left side commits first
    assert kv.get(b, "k3") == "V4"                        # b still sees its own write
    try:
        kv.commit(b)
        raise AssertionError("expected ConflictError")
    except ConflictError:
        pass
    assert kv.get_committed("k3") == "V3"                 # b's write never became visible
    try:
        kv.put(b, "x", 1)
        raise AssertionError("expected TransactionError")
    except TransactionError:
        pass


def test_snapshot_reads_and_delete():
    kv = KV()
    t = kv.begin(); kv.put(t, "a", 1); kv.commit(t)
    reader = kv.begin()
    w = kv.begin(); kv.put(w, "a", 2); kv.commit(w)
    assert kv.get(reader, "a") == 1                       # repeatable read: sees old snapshot
    assert kv.get_committed("a") == 2
    d = kv.begin(); kv.delete(d, "a"); assert kv.get(d, "a") is None
    kv.rollback(d); assert kv.get_committed("a") == 2     # rollback reverses the delete
    d = kv.begin(); kv.delete(d, "a"); kv.commit(d); assert kv.get_committed("a") is None


def test_write_skew():
    for isolation, conflicts in (("snapshot", False), ("serializable", True)):
        kv = KV(isolation)
        t = kv.begin(); kv.put(t, "x", 1); kv.put(t, "y", 1); kv.commit(t)
        a, b = kv.begin(), kv.begin()
        kv.get(a, "y"); kv.put(a, "x", 0)
        kv.get(b, "x"); kv.put(b, "y", 0)
        kv.commit(a)
        try:
            kv.commit(b); got = False
        except ConflictError:
            got = True
        assert got == conflicts, isolation


def test_session_nested():
    s = Session()
    s.put("a", 1)
    s.begin(); s.put("a", 2)
    s.begin(); s.delete("a"); assert s.get("a") is None
    assert s.rollback() and s.get("a") == 2
    s.begin(); s.put("c", 3); assert s.commit() and s.get("c") == 3
    seen = []
    t = threading.Thread(target=lambda: seen.append((s.get("a"), s.get("c"))))
    t.start(); t.join()
    assert seen == [(1, None)]                            # other threads see only committed data
    assert s.rollback()
    assert (s.get("a"), s.get("c")) == (1, None)
    assert not s.commit() and not s.rollback()


def test_threads_no_lost_updates():
    s = Session(); s.put("n", 0)
    retries = []

    def worker():
        for _ in range(200):
            while True:
                s.begin()
                v = s.get("n")
                time.sleep(0.0002)                        # widen the race window on purpose
                s.put("n", v + 1)                         # read-modify-write
                try:
                    s.commit(); break
                except ConflictError:
                    retries.append(1)                     # lost the race: redo the whole transaction
    ts = [threading.Thread(target=worker) for _ in range(8)]
    for t in ts: t.start()
    for t in ts: t.join(60)
    assert all(not t.is_alive() for t in ts)
    assert s.get("n") == 1600, s.get("n")                 # no increment lost
    print("kv_mvcc OK (conflict retries:", len(retries), ")")


if __name__ == "__main__":
    test_whiteboard(); test_snapshot_reads_and_delete(); test_write_skew()
    test_session_nested(); test_threads_no_lost_updates()
