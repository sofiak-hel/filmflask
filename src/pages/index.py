from flask import Blueprint, session, render_template, redirect

from db.users import User

index_bp = Blueprint('home_page', __name__,
                     template_folder='templates')


@index_bp.route("/")
def index():
    user = User.from_session(session)
    if user is None:
        return redirect("/login")
    return render_template("index.html", user=user)
