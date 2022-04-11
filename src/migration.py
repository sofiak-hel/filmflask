

from db.users import BaseUser
from db.videos import Video


def ver2_migration():
    BaseUser.reprocess_all_avatars()
    Video.reprocess_all()
    print("Performing the version 2 migration python code!")


pre_migration = [None, ver2_migration]
