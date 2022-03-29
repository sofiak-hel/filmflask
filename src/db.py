
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher
import json
from typing import Optional

hasher = PasswordHasher()
sql = {}
with open("src/sql/shorts.json") as f:
    sql = json.load(f)

db = SQLAlchemy()


def create_user(handle: str, nickname: str, password: str):
    password_hash = hasher.hash(password)
    db.session.execute(sql["create_user"], {
        "handle": handle,
        "nickname": nickname,
        "password_hash": password_hash
    })


def login(handle: str, password: str) -> Optional[dict]:
    password_hash = hasher.hash(password)
    result = db.session.execute(sql["find_user_handle"], {"handle": handle})
    user = result.fetchone()
    if user is None:
        return None
    elif not hasher.verify(user["password_hash"], password):
        return None
    else:
        return create_session(user["user_id"])


def create_session(user_id: str) -> Optional[dict]:
    result = db.session.execute(sql["create_session"], {"user_id": user_id})
    db.session.commit()
    session = result.fetchone()
    if session is not None:
        return find_session_and_user(session["session_id"])
    return None


def find_session_and_user(session_id: int) -> Optional[dict]:
    data = {"session_id": session_id}
    db.session.execute(sql["clear_old_sessions"])
    db.session.commit()
    result = db.session.execute(sql["find_session_and_user"], data).fetchone()
    if result is not None:
        db.session.execute(sql["refresh_session"], data)
        db.session.commit()
        return result
    return None


def delete_session(session_id):
    db.session.execute(sql["delete_session"], {"session_id": session_id})
    db.session.commit()
