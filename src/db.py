
from flask_sqlalchemy import SQLAlchemy
import json

sql = {}
with open("src/sql/shorts.json") as f:
    sql = json.load(f)

db = SQLAlchemy()


def init_db(app):
    db.app = app
    db.init_app(app)
    with open("src/sql/init.sql") as file:
        db.engine.execute(file.read())
