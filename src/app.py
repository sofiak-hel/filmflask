from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://flasktest:securepassword@localhost/filmflask"
db = SQLAlchemy(app)

with open("src/sql/init.sql") as file:
    db.engine.execute(file.read())


@app.route("/")
def index():
    return redirect("/login")


@app.route("/login")
def loginpage():
    return render_template('index.html')


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    passowrd = request.form["password"]
    if username == 'sofia' and passowrd == 'secret!':
        return "Welcome, %s" % username
    else:
        return "fuk u, scammer"
