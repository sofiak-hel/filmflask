
from argon2 import PasswordHasher
from typing import Optional
from datetime import time

from db import login, find_session_and_user, delete_session


class User:
    def __init__(self, row: dict):
        self.user_id: int = row["user_id"]
        self.session_id: str = row["session_id"]
        self.expiration: time = row["expiration"]
        self.handle: str = row["handle"]
        self.nickname: str = row["nickname"]

    @staticmethod
    def from_session(session_id: int) -> Optional['User']:
        session = find_session_and_user(session_id)
        if session is not None:
            return User(session)
        return None

    @staticmethod
    def from_login(username, password) -> Optional['User']:
        session = login(username, password)
        if session is not None:
            return User(session)
        return None

    @staticmethod
    def logout(session_id: int):
        delete_session(session_id)

    def __str__(self):
        return "%s (@%s)" % (self.nickname, self.handle)
