_MISSING = object()          # "key did not exist", distinct from a stored None


class NestedKV:
    """get/put/delete/begin/commit/rollback; nested transactions; O(1) per operation."""

    def __init__(self):
        self._data = {}
        self._undo = []      # flat undo log: (key, previous value or _MISSING)
        self._marks = []     # one entry per open transaction: len(self._undo) at begin()

    # ---- data operations ----
    def get(self, key, default=None):
        return self._data.get(key, default)

    def put(self, key, value):
        self._record(key)
        self._data[key] = value

    def delete(self, key):
        if key not in self._data:
            return False
        self._record(key)
        del self._data[key]
        return True

    # ---- transactions ----
    def begin(self):
        self._marks.append(len(self._undo))

    def commit(self):
        if not self._marks:
            return False                     # no active transaction
        self._marks.pop()                    # child's undo entries now belong to the parent
        if not self._marks:                  # outermost commit: nothing can be undone any more
            self._undo.clear()
        return True

    def rollback(self):
        if not self._marks:
            return False
        mark = self._marks.pop()
        while len(self._undo) > mark:        # undo newest-first
            key, old = self._undo.pop()
            if old is _MISSING:
                self._data.pop(key, None)
            else:
                self._data[key] = old
        return True

    def _record(self, key):
        if self._marks:                      # outside a transaction there is nothing to undo
            self._undo.append((key, self._data.get(key, _MISSING)))

# ---- tests ----
def test_nested():
    kv = NestedKV()
    kv.put("a", 1)
    kv.begin(); kv.put("a", 2); kv.put("b", 3)
    kv.begin(); kv.delete("a"); assert kv.get("a") is None
    assert kv.rollback() and kv.get("a") == 2          # delete is reversible
    kv.begin(); kv.put("c", 9); assert kv.commit()     # child commits into parent
    assert kv.get("c") == 9
    assert kv.rollback()                               # parent rollback undoes child's commit too
    assert (kv.get("a"), kv.get("b"), kv.get("c")) == (1, None, None)
    assert not kv.commit() and not kv.rollback()       # no active transaction
    kv.begin(); kv.put("x", None); assert kv.commit()  # None is a real value
    assert "x" in kv._data and kv.get("x", "d") is None
    print("kv_nested OK")


if __name__ == "__main__":
    test_nested()
