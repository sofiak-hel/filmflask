from flask import Blueprint, redirect, request, session, current_app
from typing import Optional

from db.users import BaseUser, AuthUser
from db.images import Image
from db.videos import Video
from util import error, csrf_token_required, auth_required, render_template

user_bp = Blueprint('user_page', __name__,
                    template_folder='templates')


@user_bp.route("/user/<handle>")
def user(handle):
    me = AuthUser.from_session(session)
    user = BaseUser.from_handle(handle)
    if user is None:
        return error("No such user!")
    videos = Video.by_uploaders([user.user_id])
    return render_template("user.html", user=user, me=me, videos=videos)


@user_bp.route("/subscribe/<handle>", methods=["POST"])
@csrf_token_required()
@auth_required()
def subscribe(handle):
    me = AuthUser.from_session(session)
    user = BaseUser.from_handle(handle)
    if not me.subscribe(user.user_id):
        return error("Failed to subscribe to %s!" % handle)
    return redirect("/user/%s" % handle)


@user_bp.route("/unsubscribe/<handle>", methods=["POST"])
@csrf_token_required()
@auth_required()
def unsubscribe(handle):
    me = AuthUser.from_session(session)
    user = BaseUser.from_handle(handle)
    if not me.unsubscribe(user.user_id):
        return error("Failed to unsubscribe to %s!" % handle)
    return redirect("/user/%s" % handle)


@user_bp.route("/user/edit", methods=["GET", "POST"])
@csrf_token_required()
@auth_required()
def edit_user():
    user = AuthUser.from_session(session)
    if request.method == "GET":
        return render_template("user_edit.html", me=user, config=current_app.config)

    elif request.method == "POST":
        nickname: str = request.form.get("nickname", "").strip()
        bio: str = request.form.get("bio", "").strip()
        if len(nickname) > current_app.config["NICKNAME_MAX_LENGTH"] or len(nickname) < current_app.config["NICKNAME_MIN_LENGTH"]:
            return error("Nickname must be between %s and %s characters long" % (current_app.config["NICKNAME_MIN_LENGTH"], current_app.config["NICKNAME_MAX_LENGTH"]))
        if len(bio) > current_app.config["BIO_MAX_LENGTH"]:
            return error("Bio is over %s characters" % current_app.config["BIO_MAX_LENGTH"])
        if not user.update(nickname, bio, None):
            return error("Failed to update user info")
        return redirect("/user/edit")
