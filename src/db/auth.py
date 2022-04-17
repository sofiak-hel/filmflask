
from typing import Optional

from db.db import db, sql
from db.users import BaseUser
from db.videos import VideoListing, Comment
from db.roles import Roles


class Auth:
    def __init__(self, user: BaseUser):
        if user is None:
            self.user_id = -1
            self.roles = Roles.empty(-1)
        else:
            self.user_id = user.user_id
            self.roles = Roles.from_id(user.role_id)

    def can_delete_video(self, video: VideoListing) -> bool:
        if video.user_id == self.user_id or self.roles.can_delete_videos:
            return True
        return False

    def can_delete_comment(self, comment: Comment) -> bool:
        if comment.user_id == self.user_id or self.roles.can_delete_comments:
            return True
        return False
