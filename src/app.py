from flask import Flask, render_template, redirect, request, session

from login import login_bp
from upload import upload_bp
from db import init_db

from auth import User

app = Flask(__name__)
app.secret_key = "so secret!"

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://flasktest:securepassword@localhost/filmflask"
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.register_blueprint(login_bp)
app.register_blueprint(upload_bp)

init_db(app)


@app.route("/")
def index():
    user = User.from_session(session)
    if user is None:
        return redirect("/login")
    return render_template("index.html", user=user)
