from flask import current_app
from io import BytesIO, IOBase
from argon2 import PasswordHasher
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from datetime import time
from typing import Optional
from psycopg2 import Binary
from uuid import UUID
import random
import math
import itertools

from db.db import db, sql
from ffmpeg_util import process_image


class Image:
    def __init__(self, id: UUID, content_type: str, blob: bytes):
        self.image_id: UUID = id
        self.content_type: str = content_type
        self.blob: bytes = blob

    @staticmethod
    def upload(blob: bytes, content_type: str = "image/jpeg", process: bool = True) -> Optional['Image']:
        res = create_image(content_type, blob, process)
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

    @staticmethod
    def generate_avatar() -> Optional['Image']:
        size = 8

        color1 = [random.randint(0, 255) for i in range(0, 3)]
        color2 = [random.randint(0, 255) for i in range(0, 3)]

        l: list[int] = []
        for y in range(0, size):
            row = []
            for x in range(0, math.floor(size / 2)):
                if random.randint(0, 1) == 1:
                    row.append(color1)
                else:
                    row.append(color2)
            row.extend(row[::-1])
            l.extend(itertools.chain(*row))

        blob = process_image(bytes(l), flags="neighbor", format="rawvideo",
                             pix_fmt="rgb24", s="%sx%s" % (size, size))
        return Image.upload(blob)

    def getBuffer(self) -> IOBase:
        return BytesIO(self.blob)


def create_image(content_type: str, blob: bytes, process: bool) -> Optional[dict]:
    try:
        if process:
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
