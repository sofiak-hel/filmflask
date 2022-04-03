from flask import Flask, render_template, redirect, request, session
import json
from os import getenv

from pages.login import login_bp
from pages.image import image_bp
from pages.index import index_bp
from pages.user import user_bp
from pages.video import video_bp
from db.db import init_db


app = Flask(__name__)
app.config.from_file("../config.json", load=json.load)
app.config.from_prefixed_env("FILMFLASK")

app.secret_key = app.config["SECRET_KEY"]

# Workaround for Heroku
HEROKU_DB_URL = getenv("DATABASE_URL")

if HEROKU_DB_URL is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = HEROKU_DB_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://"\
        f"{app.config['PG_USER']}:{app.config['PG_PASS']}"\
        f"@{app.config['PG_HOST']}:{app.config['PG_PORT']}"\
        f"/{app.config['PG_DB']}"

app.register_blueprint(login_bp)
app.register_blueprint(image_bp)
app.register_blueprint(index_bp)
app.register_blueprint(user_bp)
app.register_blueprint(video_bp)

init_db(app)
