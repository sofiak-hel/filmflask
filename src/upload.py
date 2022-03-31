from flask import Flask, Blueprint, render_template, redirect, request, session, send_file
from flask_sqlalchemy import SQLAlchemy
import json
from io import BytesIO

from auth import User
from images import Image

upload_bp = Blueprint('upload_page', __name__,
                      template_folder='templates')


@upload_bp.route("/upload", methods=["GET", "POST"])
def upload():
    user = User.from_session(session)
    if user is None:
        return redirect("/")
    if request.method == "GET":
        return render_template('upload.html')
    if request.method == "POST":
        f = request.files.get("avatar", None)
        if f.filename == '':
            return redirect("/upload")
        if not f.mimetype.startswith("image/"):
            return render_template("error.html", error="Uploaded content must be an image!")
        buff = f.read(200 * 1024)
        if len(f.read(1)) > 0:
            return render_template("error.html", error="Image too big")
        image = Image.upload(f.mimetype, buff)
        if image is not None:
            if user.avatar_id is not None:
                Image.delete(user.avatar_id)
            user.update(None, None, image.image_id)
        return redirect("/")


@upload_bp.route("/image/<uuid:image_id>")
def image(image_id):
    image = Image.from_id(image_id)
    if image is None:
        return "Failed to get image!"
    else:
        return send_file(image.blob, image.content_type)
