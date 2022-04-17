from flask import Blueprint, session, redirect, request

from db.users import AuthUser
from db.videos import Video
from util import render_template, auth_required

index_bp = Blueprint('home_page', __name__,
                     template_folder='templates')


@index_bp.route("/")
def index():
    return render_template("index.html", videos=Video.search())


@index_bp.route("/search")
def search():
    query = request.args.get("query", "").strip()
    if len(query) == 0:
        return redirect("/")

    return render_template("index.html", videos=Video.search(query))


@index_bp.route("/subbox")
@auth_required()
def subbox():
    me = AuthUser.from_session(session)
    return render_template("index.html", videos=Video.subbox(me.user_id))
