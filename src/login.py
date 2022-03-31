from flask import Flask, Blueprint, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
import json

from auth import User

login_bp = Blueprint('login_page', __name__,
                     template_folder='templates')


@login_bp.route("/login")
def login_get():
    if "session_id" in session:
        return redirect("/")
    return render_template('login.html')


@login_bp.route("/login", methods=["POST"])
def login_post():
    username = request.form["username"]
    password = request.form["password"]
    user = User.from_login(username, password)
    if user is None:
        return render_template("error.html", error="No such user!")
    session["session_id"] = user.session_id
    return redirect("/")


@login_bp.route("/register")
def register_get():
    if "session_id" in session:
        return redirect("/")
    return render_template('register.html')


@login_bp.route("/register", methods=["POST"])
def register_post():
    handle = request.form["username"]
    nickname = request.form["nickname"]
    password = request.form["password"]
    password2 = request.form["password2"]
    if len(handle) > 12:
        return render_template("error.html", error="Handle is longer than 12 characters")
    if len(nickname) > 12:
        return render_template("error.html", error="Nickname is longer than 12 characters")
    if password != password2:
        return render_template("error.html", error="Passwords do not match!")

    if User.register(handle, nickname, password):
        return redirect("/")
    else:
        return render_template("error.html", error="Failed to create user! Maybe user @%s already exists?" % handle)


@ login_bp.route("/logout", methods=["POST"])
def logout():
    if "session_id" in session:
        User.logout(session["session_id"])
        del session["session_id"]
    return redirect("/")
