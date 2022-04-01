from flask import Blueprint, render_template, redirect, request, session, send_file, current_app

from db.users import AuthUser
from db.images import Image
from util import error

image_bp = Blueprint('image_page', __name__,
                     template_folder='templates')


@image_bp.route("/image", methods=["POST"])
def avatar_upload():
    user = AuthUser.from_session(session)
    if user is None:
        return redirect("/")
    f = request.files.get("avatar", None)
    if f.filename == '':
        return redirect("/user/edit")
    if not f.mimetype.startswith("image/"):
        return error("Uploaded content must be an image!")
    buff = f.read(current_app.config["MAX_IMAGE_SIZE"])
    if len(f.read(1)) > 0:
        return error("Image too big")
    image = Image.upload(buff)
    if image is not None:
        if user.avatar_id is not None:
            Image.delete(user.avatar_id)
        user.update(None, None, image.image_id)
    return redirect("/user/edit")


@image_bp.route("/image/<uuid:image_id>")
def image_get(image_id):
    image = Image.from_id(image_id)
    if image is None:
        return "Failed to get image!"
    else:
        return send_file(image.getBuffer(), image.content_type)
