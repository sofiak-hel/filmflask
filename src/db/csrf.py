
from io import BytesIO, IOBase
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from typing import Optional
from datetime import time
from uuid import UUID

from db.db import db, sql
from db.users import AuthUser


class CSRFToken:
    def __init__(self, row: dict):
        self.csrf_token: UUID = row["csrf_token"]
        self.session_id: UUID = row["session_id"]
        self.expiration: time = row["expiration"]

    @staticmethod
    def from_session(session: dict) -> Optional['CSRFToken']:
        session_id = session.get("session_id", None)
        if session_id is None:
            return None
        res = create_csrf(session_id)
        if res is None:
            return None
        return CSRFToken(res)

    @staticmethod
    def from_csrf(csrf_token: UUID) -> Optional['CSRFToken']:
        res = get_csrf(csrf_token)
        if res is None:
            return None
        return CSRFToken(res)

    @staticmethod
    def validate_request(request, session: dict) -> bool:
        uuid: UUID = request.form.get("csrf_token", None)
        session_id = session.get("session_id", None)
        print(uuid)
        print(session_id)
        if uuid is None or session_id is None:
            return False
        csrf_token = CSRFToken.from_csrf(uuid)
        if csrf_token is None:
            return False
        print(csrf_token)
        return csrf_token.session_id == session_id


def create_csrf(session_id: UUID) -> Optional[dict]:
    try:
        res = db.session.execute(sql["create_csrf_token"], {
            "session_id": session_id,
        })
        db.session.commit()
        clear_old_csrf()
        return res.fetchone()
    except Exception as e:
        print(e)
        return None


def get_csrf(csrf_token: UUID) -> Optional[dict]:
    try:
        clear_old_csrf()
        res = db.session.execute(sql["get_csrf_token"], {
            "csrf_token": csrf_token,
        })
        return res.fetchone()
    except Exception as e:
        print(e)
        return None


def clear_old_csrf():
    try:
        res = db.session.execute(sql["clear_csrf_tokens"])
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False
