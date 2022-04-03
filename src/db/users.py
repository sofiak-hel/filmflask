
from argon2 import PasswordHasher
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from datetime import time
from typing import Optional
from uuid import UUID

from db.db import db, sql

hasher = PasswordHasher()


class BaseUser:
    def __init__(self, row: dict):
        self.user_id: int = row["user_id"]
        self.handle: str = row["handle"]
        self.nickname: str = row["nickname"]
        self.bio: str = row["bio"]
        self.avatar_id: UUID = row["avatar_id"]

    @staticmethod
    def from_id(user_id: int) -> Optional['BaseUser']:
        res = find_user(user_id)
        if res is None:
            return None
        return BaseUser(res)

    @staticmethod
    def from_handle(handle: str) -> Optional['BaseUser']:
        res = find_user_by_handle(handle)
        if res is None:
            return None
        return BaseUser(res)

    def update(self, nickname: Optional[str] = None, bio: Optional[str] = None, avatar_id: Optional[UUID] = None):
        self.nickname = nickname or self.nickname
        self.bio = self.bio if bio is None else bio
        self.avatar_id = avatar_id or self.avatar_id
        return update_user(self.user_id, self.nickname, self.bio, self.avatar_id)

    def list_subscriptions(self) -> list[int]:
        res = list_subscriptions(self.user_id)
        subs: list[int] = []
        if res is None:
            return subs

        for row in res:
            subs.append(row["subscribed_id"])
        return subs

    def get_subscribers(self) -> list[int]:
        res = get_subscribers(self.user_id)
        subs: list[int] = []
        if res is None:
            return subs

        for row in res:
            subs.append(row["user_id"])
        return subs


class AuthUser(BaseUser):
    def __init__(self, row: dict):
        BaseUser.__init__(self, row)
        self.session_id: str = row["session_id"]
        self.expiration: time = row["expiration"]

    @staticmethod
    def from_session(session: dict) -> Optional['AuthUser']:
        session_id = session.get("session_id", None)
        if session_id is None:
            return None

        current_session = find_session_and_user(session_id)
        if current_session is not None:
            return AuthUser(current_session)

        del session["session_id"]
        return None

    @staticmethod
    def from_login(username, password) -> Optional['AuthUser']:
        session = login(username, password)
        if session is not None:
            return AuthUser(session)
        return None

    @staticmethod
    def register(handle: str, nickname: str, password: str):
        return create_user(handle, nickname, password)

    @staticmethod
    def validate_session(session: dict) -> bool:
        if "session_id" not in session:
            return False
        return find_session(session["session_id"]) is not None

    def logout(self):
        delete_session(self.session_id)

    def subscribe(self, other_id: int) -> bool:
        return subscribe(self.user_id, other_id)

    def unsubscribe(self, other_id: int) -> bool:
        return unsubscribe(self.user_id, other_id)

    def check_subscription(self, other_id: int) -> bool:
        return check_subscription(self.user_id, other_id)

    def delete_comment(self, comment_id: int) -> Optional[UUID]:
        res = delete_comment_safe(comment_id, self.user_id)
        if res is None:
            return None
        return res["video_id"]

    def rate_video(self, video_id: UUID, rating: int) -> bool:
        return rate_video(self.user_id, video_id, rating)

    def unrate_video(self, video_id: UUID) -> bool:
        return delete_rating(self.user_id, video_id)

    def get_rating(self, video_id: UUID) -> Optional[int]:
        res = get_rating(self.user_id, video_id)
        if res is None:
            return None
        return res["rating"]

    def __str__(self):
        return "%s (@%s). Bio: %s, avatar_id: %s." % (self.nickname, self.handle, self.bio, self.avatar_id)


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


def find_user(user_id: int) -> Optional[dict]:
    try:
        result = db.session.execute(sql["find_user"], {
            "user_id": user_id
        })
        return result.fetchone()
    except Exception as e:
        print(e)
        return None


def find_user_by_handle(handle: str) -> Optional[dict]:
    try:
        result = db.session.execute(sql["find_user_handle"], {
            "handle": handle
        })
        return result.fetchone()
    except Exception as e:
        print(e)
        return None


def login(handle: str, password: str) -> Optional[dict]:
    try:
        password_hash = hasher.hash(password)
        user = find_user_by_handle(handle)
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


def find_session(session_id: UUID) -> Optional[dict]:
    try:
        clear_old_sessions()
        result = db.session.execute(sql["find_session"], {
            "session_id": session_id
        })
        return result.fetchone()
    except Exception as e:
        print(e)
        return None


def find_session_and_user(session_id: str) -> Optional[dict]:
    try:
        data = {"session_id": session_id}
        clear_old_sessions()
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
        clear_old_sessions()
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


def clear_old_sessions():
    try:
        db.session.execute(sql["clear_old_sessions"])
        db.session.commit()
    except Exception as e:
        print(e)
        return None


def subscribe(user_id: int, subscribed_id: int) -> bool:
    try:
        db.session.execute(sql["subscribe"], {
            "user_id": user_id,
            "subscribed_id": subscribed_id
        })
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def unsubscribe(user_id: int, subscribed_id: int) -> bool:
    try:
        db.session.execute(sql["unsubscribe"], {
            "user_id": user_id,
            "subscribed_id": subscribed_id
        })
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def list_subscriptions(user_id: int) -> Optional[list[dict]]:
    try:
        res = db.session.execute(sql["list_subscriptions"], {
            "user_id": user_id,
        })
        if res is None:
            return None
        return res.fetchone()
    except Exception as e:
        print(e)
        return None


def check_subscription(user_id: int, subscribed_id: int) -> bool:
    try:
        res = db.session.execute(sql["check_subscription"], {
            "user_id": user_id,
            "subscribed_id": subscribed_id
        })
        if res is None:
            return False
        return res.fetchone() is not None
    except Exception as e:
        print(e)
        return False


def get_subscribers(user_id: int) -> Optional[list[dict]]:
    try:
        res = db.session.execute(sql["get_subscribers"], {
            "user_id": user_id,
        })
        if res is None:
            return None
        return res.fetchall()
    except Exception as e:
        print(e)
        return None


def delete_comment_safe(comment_id: int, user_id: int) -> Optional[dict]:
    try:
        res = db.session.execute(sql["delete_comment_safe"], {
            "comment_id": comment_id,
            "user_id": user_id,
        })
        db.session.commit()
        if res is None:
            return None
        return res.fetchone()
    except Exception as e:
        print(e)
        return None


def rate_video(user_id: int, video_id: UUID, rating: int) -> bool:
    try:
        db.session.execute(sql["rate_video"], {
            "user_id": user_id,
            "video_id": video_id,
            "rating": rating,
        })
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def delete_rating(user_id: int, video_id: UUID) -> bool:
    try:
        db.session.execute(sql["delete_rating"], {
            "user_id": user_id,
            "video_id": video_id,
        })
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def get_rating(user_id: int, video_id: UUID) -> Optional[dict]:
    try:
        res = db.session.execute(sql["get_rating"], {
            "user_id": user_id,
            "video_id": video_id,
        })
        if res is None:
            return None
        return res.fetchone()
    except Exception as e:
        print(e)
        return None
