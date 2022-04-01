from flask import Blueprint, render_template, redirect, request, session, current_app
from typing import Optional

from db.user import User
from db.images import Image
from util import error

user_bp = Blueprint('user_page', __name__,
                    template_folder='templates')


@user_bp.route("/user/edit", methods=["GET", "POST"])
def edit_user():
    user = User.from_session(session)
    if user is None:
        return redirect("/")

    if request.method == "GET":
        return render_template("user_edit.html", user=user, config=current_app.config)

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
