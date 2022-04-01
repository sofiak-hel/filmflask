from flask import Blueprint, session, render_template, redirect, request

from db.users import AuthUser
from db.videos import Video

index_bp = Blueprint('home_page', __name__,
                     template_folder='templates')


@index_bp.route("/")
def index():
    user = AuthUser.from_session(session)
    if user is None:
        return redirect("/login")
    videos = Video.search()
    return render_template("index.html", user=user, videos=videos)


@index_bp.route("/search")
def search():
    user = AuthUser.from_session(session)
    if user is None:
        return redirect("/login")

    query = request.args.get("query", "").strip()
    if len(query) == 0:
        return redirect("/")

    videos = Video.search(query)
    return render_template("index.html", user=user, videos=videos)
