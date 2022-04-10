from flask import Blueprint, redirect, request, session, current_app

from db.users import AuthUser
from util import error, csrf_token_required, render_template

login_bp = Blueprint('login_page', __name__,
                     template_folder='templates')


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    user = AuthUser.from_session(session)
    if request.method == "GET":
        redirect_url = request.args.get('redirect', None)
        if user is not None or redirect_url is None:
            return redirect("/")
        return render_template('login.html', redirect=redirect_url)
    elif request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        redirect_url = request.form.get("redirect", None)
        if username is None or password is None:
            return error("No username of password part", "/login?redirect=%s" % redirect_url)
        if redirect_url is None:
            return error("No redirect url!", "/login?redirect=%s" % redirect_url)
        user = AuthUser.from_login(username, password)
        if user is None:
            return error("No such user!", "/login?redirect=%s" % redirect_url)
        session["session_id"] = user.session_id
        return redirect(redirect_url)


@login_bp.route("/register", methods=["GET", "POST"])
def register():
    user = AuthUser.from_session(session)
    if user is not None:
        return redirect("/")
    if request.method == "GET":
        return render_template('register.html', config=current_app.config)
    elif request.method == "POST":
        handle = request.form.get("username", None)
        nickname = request.form.get("nickname", None)
        password = request.form.get("password", None)
        password2 = request.form.get("password2", None)
        if handle is None or len(handle) > current_app.config["HANDLE_MAX_LENGTH"]:
            return error("Handle is longer than 12 characters", "/register")
        if nickname is None or len(nickname) > current_app.config["NICKNAME_MAX_LENGTH"]:
            return error("Nickname is longer than 12 characters", "/register")
        if password is None or password2 is None or password != password2:
            return error("Passwords do not match!", "/register")
        if not handle.isalnum() and handle.isascii():
            return error("Handle must only contain numbers and characters from a to z!", "/register")

        if AuthUser.register(handle, nickname, password):
            return redirect("/")
        else:
            return error("Failed to create user! Maybe user @%s already exists?" % handle)


@login_bp.route("/logout", methods=["POST"])
@csrf_token_required()
def logout():
    redirect_url = request.args.get('redirect', None)
    user = AuthUser.from_session(session)
    if user is not None:
        user.logout()
        del session["session_id"]
    if redirect_url is None:
        return redirect("/")
    else:
        return redirect(redirect_url)
