from flask import render_template


def error(error: str):
    return render_template("error.html", error=error)
