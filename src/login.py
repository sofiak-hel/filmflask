from flask import Flask, Blueprint, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
import json

from auth import User

login_bp = Blueprint('login_page', __name__,
                     template_folder='templates')


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    user = User.from_session(session)
    if request.method == "GET":
        if user is not None:
            return redirect("/")
        return render_template('login.html')
    elif request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        if username is None or password is None:
            return render("error.html", error="No username of password part")
        user = User.from_login(username, password)
        if user is None:
            return render_template("error.html", error="No such user!")
        session["session_id"] = user.session_id
        return redirect("/")


@login_bp.route("/register", methods=["GET", "POST"])
def register():
    user = User.from_session(session)
    if user is not None:
        return redirect("/")
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        handle = request.form.get("username", None)
        nickname = request.form.get("nickname", None)
        password = request.form.get("password", None)
        password2 = request.form.get("password2", None)
        if handle is None or len(handle) > 12:
            return render_template("error.html", error="Handle is longer than 12 characters")
        if nickname is None or len(nickname) > 12:
            return render_template("error.html", error="Nickname is longer than 12 characters")
        if password is None or password2 is None or password != password2:
            return render_template("error.html", error="Passwords do not match!")

        if User.register(handle, nickname, password):
            return redirect("/")
        else:
            return render_template("error.html", error="Failed to create user! Maybe user @%s already exists?" % handle)


@ login_bp.route("/logout", methods=["POST"])
def logout():
    user = User.from_session(session)
    if user is not None:
        user.logout()
        del session["session_id"]
    return redirect("/")
