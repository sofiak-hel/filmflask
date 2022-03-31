
from argon2 import PasswordHasher
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from datetime import time
from typing import Optional
from uuid import UUID

from db import db, sql

hasher = PasswordHasher()


class User:
    def __init__(self, row: dict):
        self.user_id: int = row["user_id"]
        self.session_id: str = row["session_id"]
        self.expiration: time = row["expiration"]
        self.handle: str = row["handle"]
        self.nickname: str = row["nickname"]
        self.bio: str = row["bio"]
        self.avatar_id: UUID = row["avatar_id"]

    @staticmethod
    def from_session(session: dict) -> Optional['User']:
        session_id = session.get("session_id", None)
        if session_id is None:
            return None

        current_session = find_session_and_user(session_id)
        if current_session is not None:
            return User(current_session)

        del session["session_id"]
        return None

    @staticmethod
    def from_login(username, password) -> Optional['User']:
        session = login(username, password)
        if session is not None:
            return User(session)
        return None

    @staticmethod
    def register(handle: str, nickname: str, password: str):
        return create_user(handle, nickname, password)

    def logout(self):
        delete_session(self.session_id)

    def update(self, nickname: Optional[str] = None, bio: Optional[str] = None, avatar_id: Optional[UUID] = None):
        self.nickname = nickname or self.nickname
        self.bio = bio or self.bio
        self.avatar_id = avatar_id or self.avatar_id
        update_user(self.user_id, self.nickname, self.bio, self.avatar_id)

    def __str__(self):
        return "%s (@%s)" % (self.nickname, self.handle)


def create_user(handle: str, nickname: str, password: str) -> bool:
    try:
        password_hash = hasher.hash(password)
        db.session.execute(sql["create_user"], {
            "handle": handle,
            "nickname": nickname,
            "password_hash": password_hash
        })
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def login(handle: str, password: str) -> Optional[dict]:
    try:
        password_hash = hasher.hash(password)
        result = db.session.execute(sql["find_user_handle"], {
            "handle": handle
        })
        user = result.fetchone()
        if user is None:
            return None
        elif not hasher.verify(user["password_hash"], password):
            return None
        else:
            if hasher.check_needs_rehash(user["password_hash"]):
                new_hash = hasher.hash(password)
                db.session.execute(sql["update_user_password"], {
                    "password_hash": new_hash,
                    "user_id": user["user_id"]
                })
                db.session.commit()
            return create_session(user["user_id"])
    except Exception as e:
        print(e)
        return None


def create_session(user_id: str) -> Optional[dict]:
    try:
        result = db.session.execute(
            sql["create_session"], {"user_id": user_id})
        db.session.commit()
        session = result.fetchone()
        if session is not None:
            return find_session_and_user(session["session_id"])
        return None
    except Exception as e:
        print(e)
        return None


def find_session_and_user(session_id: str) -> Optional[dict]:
    try:
        data = {"session_id": session_id}
        db.session.execute(sql["clear_old_sessions"])
        db.session.commit()
        result = db.session.execute(
            sql["find_session_and_user"], data).fetchone()
        if result is None:
            return None
        db.session.execute(sql["refresh_session"], data)
        db.session.commit()
        return result
    except Exception as e:
        print(e)
        return None


def delete_session(session_id: str) -> bool:
    try:
        db.session.execute(sql["delete_session"], {"session_id": session_id})
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def update_user(user_id: int, nickname: str, bio: str, avatar_id: UUID) -> bool:
    try:
        db.session.execute(sql["update_user"], {
            "user_id": user_id,
            "nickname": nickname,
            "bio": bio,
            "avatar_id": avatar_id
        })
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False
