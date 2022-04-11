
from flask_sqlalchemy import SQLAlchemy
import json
from os import path
from typing import Callable, Optional

sql = {}
with open("sql/shorts.json") as f:
    sql = json.load(f)

db = SQLAlchemy()


def init_db(app, pre_migration: list[Optional[Callable]]):
    db.app = app
    db.init_app(app)

    schema_version = get_schema_version() + 1
    while path.exists("sql/version_%s.sql" % schema_version):
        if len(pre_migration) < schema_version:
            raise Exception(
                "Function for version %s has not been specified!" % schema_version)
        with open("sql/version_%s.sql" % schema_version) as file:
            fn = pre_migration[schema_version - 1]
            if fn is not None:
                fn()
            print("Performing version %s migration!" % schema_version)
            db.engine.execute(file.read())
        schema_version += 1


def get_schema_version() -> int:
    try:
        row = db.session.execute(sql["get_schema_version"]).fetchone()
        if (row is None):
            return 0
        return row["version"]
    except Exception as e:
        print(e)
        return 0
