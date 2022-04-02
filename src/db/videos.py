
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
from db.users import BaseUser, AuthUser
from db.images import Image
from util import process_video, create_thumbnail


class Video:
    def __init__(self, row: dict):
        self.video_id: UUID = row["video_id"]
        self.user_id: int = row["user_id"]
        self.content_type: str = row["content_type"]
        self.blob: bytes = row["blob"]
        self.title: str = row["title"]
        self.description: str = row["description"]
        self.thumbnail_id: UUID = row["thumbnail_id"]
        self.upload_time: time = row["upload_time"]
        self.download_counter: int = row["download_counter"]
        self.uploader: BaseUser = BaseUser(row)

    @staticmethod
    def upload(user: AuthUser, title: str, description: str, blob: bytes) -> Optional['Image']:
        blob = process_video(blob)
        thumbnail_blob = create_thumbnail(blob)
        thumbnail = Image.upload(thumbnail_blob, "image/jpeg")
        res = create_video(user.user_id,  title, description, Binary(blob),
                           "video/mp4", thumbnail.image_id)
        if res is not None:
            get = get_video(res["video_id"])
            if get is not None:
                return Video(get)
        return None

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

    @staticmethod
    def search(search: Optional[str] = None) -> list['Video']:
        if search is not None:
            res = search_videos(search)
        else:
            res = all_videos()

        if res is None:
            return []
        videos = []
        for row in res:
            videos.append(Video(row))
        return videos

    @staticmethod
    def by_uploaders(uploader_ids: list[int]) -> list['Video']:
        res = get_videos(uploader_ids)

        if res is None:
            return []
        videos = []
        for row in res:
            videos.append(Video(row))
        return videos

    @staticmethod
    def reprocess_all():
        videos = Video.search()

        for video in videos:
            new_blob = process_video(video.blob)
            update_video(video.video_id, new_blob)

    def add_download(self) -> bool:
        self.download_counter += 1
        return add_download(self.video_id)

    def getBuffer(self) -> IOBase:
        return BytesIO(self.blob)


def create_video(user_id: int, title: str, description: str, blob: bytes, content_type: str, thumbnail_id: UUID) -> Optional[dict]:
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


def all_videos() -> Optional[list[dict]]:
    try:
        return db.session.execute(sql["all_videos"]).fetchall()
    except Exception as e:
        print(e)
        return None


def get_videos(uploader_ids: list[int]) -> Optional[list[dict]]:
    try:
        return db.session.execute(sql["get_videos_by_uploader"], {
            "user_ids": tuple(uploader_ids)
        }).fetchall()
    except Exception as e:
        print(e)
        return None


def search_videos(search: str) -> Optional[list[dict]]:
    try:
        res = db.session.execute(sql["search_videos"], {
                                 "search": search}).fetchall()
        if res is None or len(res) == 0:
            res = db.session.execute(sql["search_videos_substr"], {
                "search": f"%{search}%"}).fetchall()
        return res
    except Exception as e:
        print(e)
        return None


def get_video(video_id: UUID) -> Optional[dict]:
    try:
        res = db.session.execute(sql["get_video_and_uploader"], {
            "video_id": video_id,
        })
        return res.fetchone()
    except Exception as e:
        print(e)
        return None


def add_download(video_id: UUID) -> bool:
    try:
        res = db.session.execute(sql["inc_video_counter"], {
            "video_id": video_id,
        })
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def update_video(video_id: UUID, blob: bytes) -> bool:
    try:
        res = db.session.execute(sql["update_video"], {
            "video_id": video_id,
            "blob": blob
        })
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False
