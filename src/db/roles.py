
from typing import Optional

from db.db import db, sql


class Roles:
    def __init__(self, row: dict):
        self.role_id: int = row["role_id"]
        self.role_name: str = row["role_name"]
        self.can_delete_users: bool = row["can_delete_users"]
        self.can_delete_videos: bool = row["can_delete_videos"]
        self.can_delete_comments: bool = row["can_delete_comments"]

    @staticmethod
    def empty(role_id: int) -> 'Roles':
        return Roles({
            "role_id": role_id,
            "role_name": "Role fetch failed",
            "can_delete_users": False,
            "can_delete_videos": False,
            "can_delete_comments": False,
        })

    @staticmethod
    def from_id(role_id: int) -> 'Roles':
        res = get_roles(role_id)
        if res is None:
            return Roles.empty(role_id)
        return Roles(res)


def get_roles(role_id) -> Optional[dict]:
    try:
        return db.session.execute(sql["get_roles"], {
            "role_id": role_id
        }).fetchone()
    except Exception as e:
        print(e)
        return None
