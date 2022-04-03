
from io import BytesIO, IOBase
from argon2 import PasswordHasher
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from datetime import time
from typing import Optional, Tuple
from psycopg2 import Binary
from uuid import UUID
from datetime import time

from db.db import db, sql
from db.users import BaseUser, AuthUser
from db.images import Image
from util import process_video, create_thumbnail


class VideoListing:
    def __init__(self, row: dict):
        self.video_id: UUID = row["video_id"]
        self.user_id: int = row["user_id"]
        self.content_type: str = row["content_type"]
        self.title: str = row["title"]
        self.description: str = row["description"]
        self.thumbnail_id: UUID = row["thumbnail_id"]
        self.upload_time: time = row["upload_time"]
        self.download_counter: int = row["download_counter"]
        self.uploader: BaseUser = BaseUser(row)

    @staticmethod
    def search(search: Optional[str] = None) -> list['VideoListing']:
        if search is not None:
            res = search_videos(search) or []
        else:
            res = all_videos() or []

        videos = []
        for row in res:
            videos.append(VideoListing(row))
        return videos

    @staticmethod
    def by_uploaders(uploader_ids: list[int]) -> list['VideoListing']:
        res = get_videos(uploader_ids) or []
        videos = []
        for row in res:
            videos.append(VideoListing(row))
        return videos

    @staticmethod
    def subbox(user_id: int) -> list['VideoListing']:
        res = get_subbox(user_id) or []
        videos: list['VideoListing'] = []
        for row in res:
            videos.append(VideoListing(row))
        return videos

    def add_download(self) -> bool:
        self.download_counter += 1
        return add_download(self.video_id)

    def add_comment(self, user_id: int, content: str) -> bool:
        return add_comment(self.video_id, user_id, content)

    def get_comments(self) -> list['Comment']:
        res = get_comments(self.video_id) or []
        comments: list['Comment'] = []
        for row in res:
            comments.append(Comment(row))

        return comments

    def get_ratings(self) -> Tuple[int, int]:
        res: list[dict] = get_ratings(self.video_id) or []
        ratings: list[int] = []
        for row in res:
            ratings.append(row["rating"])

        likes = len([r for r in ratings if r == 1])
        dislikes = len([r for r in ratings if r == -1])

        return (likes, dislikes)


class Comment:
    def __init__(self, row: dict):
        self.comment_id: int = row["comment_id"]
        self.video_id: UUID = row["video_id"]
        self.user_id: int = row["user_id"]
        self.timestamp: time = row["timestamp"]
        self.content: str = row["content"]
        self.user = BaseUser(row)


class Video(VideoListing):
    def __init__(self, row: dict):
        VideoListing.__init__(self, row)
        self.blob: bytes = row["blob"]

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
    def reprocess_all():
        videos = Video.search()

        for video in videos:
            new_blob = process_video(video.blob)
            update_video(video.video_id, new_blob)

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
        res = db.session.execute(sql["reupload_video"], {
            "video_id": video_id,
            "blob": blob
        })
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def get_subbox(user_id: int) -> Optional[list[dict]]:
    try:
        res = db.session.execute(sql["get_subbox"], {
            "user_id": user_id,
        })
        if res is None:
            return None
        return res.fetchall()
    except Exception as e:
        print(e)
        return None


def add_comment(video_id: UUID, user_id: int, content: str) -> bool:
    try:
        db.session.execute(sql["add_comment"], {
            "video_id": video_id,
            "user_id": user_id,
            "content": content,
        })
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def get_comments(video_id) -> Optional[list[dict]]:
    try:
        res = db.session.execute(sql["get_comments"], {
            "video_id": video_id,
        })
        if res is None:
            return None
        return res.fetchall()
    except Exception as e:
        print(e)
        return None


def get_ratings(video_id: UUID) -> Optional[list[dict]]:
    try:
        res = db.session.execute(sql["get_ratings"], {
            "video_id": video_id,
        })
        if res is None:
            return None
        return res.fetchall()
    except Exception as e:
        print(e)
        return None
