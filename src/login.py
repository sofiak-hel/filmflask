from flask import Flask, Blueprint, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
import json

from auth import User

login_bp = Blueprint('login_page', __name__,
                     template_folder='templates')


@login_bp.route("/login")
def login_page():
    if "session_id" in session:
        return redirect("/")
    return render_template('login.html')


@login_bp.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = User.from_login(username, password)
    session["session_id"] = user.session_id
    return redirect("/")


@login_bp.route("/logout", methods=["POST"])
def logout():
    if "session_id" in session:
        User.logout(session["session_id"])
        del session["session_id"]
    return redirect("/")
