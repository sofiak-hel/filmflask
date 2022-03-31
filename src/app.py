from flask import Flask, render_template, redirect, request, session

from login import login_bp
from db import init_db

from auth import User

app = Flask(__name__)
app.secret_key = "so secret!"

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://flasktest:securepassword@localhost/filmflask"
app.register_blueprint(login_bp)

init_db(app)


@app.route("/")
def index():
    if "session_id" not in session:
        return redirect("/login")
    user = User.from_session(session["session_id"])
    return render_template("index.html", user=user)
