
from io import BytesIO, IOBase
from argon2 import PasswordHasher
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from datetime import time
from typing import Optional
from psycopg2 import Binary
from uuid import UUID

from db.db import db, sql
from util import process_image


class Image:
    def __init__(self, id: UUID, content_type: str, blob: bytes):
        self.image_id: UUID = id
        self.content_type: str = content_type
        self.blob: bytes = blob

    @staticmethod
    def upload(blob: bytes, content_type: str = "image/png") -> Optional['Image']:
        res = create_image(content_type, blob)
        if res is None:
            return None
        return Image(res["image_id"], content_type, blob)

    @staticmethod
    def from_id(image_id: str | UUID) -> Optional['Image']:
        try:
            if isinstance(image_id, str):
                image_id = UUID(image_id)
        except:
            return None

        res = get_image(image_id)
        if res is None:
            return None
        content_type = res["content_type"]
        blob = res["blob"]
        return Image(image_id, content_type, blob)

    @staticmethod
    def delete(image_id) -> bool:
        return delete_image(image_id)

    def getBuffer(self) -> IOBase:
        return BytesIO(self.blob)


def create_image(content_type: str, blob: bytes) -> Optional[dict]:
    try:
        blob = process_image(blob)
        res = db.session.execute(sql["create_image"], {
            "content_type": content_type,
            "blob": Binary(blob),
        })
        db.session.commit()
        return res.fetchone()
    except Exception as e:
        print(e)
        return None


def get_image(image_id: UUID) -> Optional[dict]:
    try:
        res = db.session.execute(sql["get_image"], {
            "image_id": image_id,
        })
        return res.fetchone()
    except Exception as e:
        print(e)
        return None


def delete_image(image_id: UUID) -> bool:
    try:
        db.session.execute(sql["delete_image"], {
            "image_id": image_id,
        })
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False
