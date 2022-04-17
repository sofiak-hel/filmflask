
from typing import Optional

from db.db import db, sql
from db.users import BaseUser
from db.videos import VideoListing, Comment


class Role:
    def __init__(self, row: dict):
        self.role_id: int = row["role_id"]
        self.role_name: str = row["role_name"]
        self.can_delete_users: bool = row["can_delete_users"]
        self.can_delete_videos: bool = row["can_delete_videos"]
        self.can_delete_comments: bool = row["can_delete_comments"]

    @staticmethod
    def empty(role_id: int) -> 'Role':
        return Role({
            "role_id": role_id,
            "role_name": "Role fetch failed",
            "can_delete_users": False,
            "can_delete_videos": False,
            "can_delete_comments": False,
        })

    @staticmethod
    def from_id(role_id: int) -> 'Role':
        res = get_roles(role_id)
        if res is None:
            return Role.empty(role_id)
        return Role(res)


class Auth:
    def __init__(self, user: BaseUser):
        if user is None:
            self.user_id = -1
            self.roles = Role.empty(-1)
        else:
            self.user_id = user.user_id
            self.roles = Role.from_id(user.role_id)

    def can_delete_video(self, video: VideoListing) -> bool:
        if video.user_id == self.user_id or self.roles.can_delete_videos:
            return True
        return False

    def can_delete_comment(self, comment: Comment) -> bool:
        if comment.user_id == self.user_id or self.roles.can_delete_comments:
            return True
        return False


def get_roles(role_id) -> Optional[dict]:
    try:
        return db.session.execute(sql["get_roles"], {
            "role_id": role_id
        }).fetchone()
    except Exception as e:
        print(e)
        return None
