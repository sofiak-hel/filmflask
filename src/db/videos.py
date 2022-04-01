
from io import BytesIO, IOBase
from argon2 import PasswordHasher
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from datetime import time
from typing import Optional
from psycopg2 import Binary
from uuid import UUID
from datetime import time

from db.db import db, sql
from db.users import User


class Video:
    def __init__(self, row: dict):
        self.video_id: UUID = row["video_id"]
        self.user_id: int = row["user_id"]
        self.content_type: str = row["video_id"]
        self.blob: bytes = row["blob"]
        self.title: str = row["title"]
        self.description: str = row["description"]
        self.thumbnail_id: UUID = row["thumbnail_id"]
        self.upload_time: time = row["upload_time"]

    @staticmethod
    def upload(user: User, title: str, description: str, blob: bytes, content_type: str, thumbnail_id: UUID) -> Optional['Video']:
        res = create_video(user.user_id, content_type, Binary(blob), title,
                           description, thumbnail_id)
        if res is None:
            return None
        return Video(res)

    @staticmethod
    def from_id(video_id: str | UUID) -> Optional['Video']:
        try:
            if isinstance(video_id, str):
                video_id = UUID(video_id)
        except:
            return None

        res = get_video(video_id)
        if res is None:
            return None
        return Video(res)

    def getBuffer(self) -> IOBase:
        return BytesIO(self.blob)


def create_video(user_id: UUID, title: str, description: str, blob: Binary, content_type: str, thumbnail_id: UUID) -> Optional[dict]:
    # :user_id, :blob, :content_type, :title, :description, :thumbnail_id
    try:
        res = db.session.execute(sql["create_video"], {
            "user_id": user_id,
            "content_type": content_type,
            "blob": blob,
            "thumbnail_id": thumbnail_id,
            "title": title,
            "description": description,
        })
        db.session.commit()
        return res.fetchone()
    except Exception as e:
        print(e)
        return None


def get_video(video_id: UUID) -> Optional[dict]:
    try:
        res = db.session.execute(sql["get_video"], {
            "video_id": video_id,
        })
        return res.fetchone()
    except Exception as e:
        print(e)
        return None
