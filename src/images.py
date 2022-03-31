
from io import BytesIO
from argon2 import PasswordHasher
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from datetime import time
from typing import Optional
from psycopg2 import Binary
from uuid import UUID

from db import db, sql


class Image:
    def __init__(self, id: UUID, content_type: str, blob: BytesIO):
        self.image_id = id
        self.content_type = content_type
        self.blob = blob

    @staticmethod
    def upload(content_type: str, blob: bytes) -> Optional['Image']:
        res = create_image(content_type, Binary(blob))
        if res is None:
            return None
        return Image(res["image_id"], content_type, BytesIO(blob))

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
        return Image(image_id, content_type, BytesIO(blob))

    @staticmethod
    def delete(image_id) -> bool:
        return delete_image(image_id)


def create_image(content_type: str, blob: Binary) -> Optional[dict]:
    try:
        res = db.session.execute(sql["create_image"], {
            "content_type": content_type,
            "blob": blob,
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
