from flask import Blueprint, session, redirect, request

from db.users import AuthUser
from db.videos import Video
from util import render_template, auth_required

index_bp = Blueprint('home_page', __name__,
                     template_folder='templates')


@index_bp.route("/")
def index():
    me = AuthUser.from_session(session)
    videos = Video.search()
    return render_template("index.html", me=me, videos=videos)


@index_bp.route("/search")
def search():
    me = AuthUser.from_session(session)
    query = request.args.get("query", "").strip()
    if len(query) == 0:
        return redirect("/")

    videos = Video.search(query)
    return render_template("index.html", me=me, videos=videos)


@index_bp.route("/subbox")
@auth_required()
def subbox():
    me = AuthUser.from_session(session)
    videos = Video.subbox(me.user_id)
    return render_template("index.html", me=me, videos=videos)
