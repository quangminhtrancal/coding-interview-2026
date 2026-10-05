from sortedcontainers import SortedSet
import uuid

class Token:
    def __init__(self, token_id: uuid, created_time: int, ttl: int):
        self.token_id = token_id
        self.created_time = created_time
        self.expiry_time = self.created_time + ttl

    def __lt__(self, other: "Token") -> bool:
        if self.created_time == other.created_time:
            return self.token_id < other.token_id
        return self.created_time < other.created_time

    def __repr__(self):
        return f'Toekn({self.token_id}, creaate={self.created_time}, expiry={self.expiry_time})'

class TokenManager:
    def __init__(self, default_ttl: int):
        self.default_ttl = default_ttl
        self.tokens: dict[str, Token] = {}
        self.active_tokens: SortedSet[Token] = SortedSet()

        