from flask import Blueprint, render_template, redirect, request, session, send_file, current_app

from db.users import AuthUser
from db.videos import Video
from db.images import Image
from util import error

video_bp = Blueprint('video_page', __name__,
                     template_folder='templates')


@video_bp.route("/upload", methods=["GET", "POST"])
def video_upload():
    user = AuthUser.from_session(session)
    if user is None:
        return redirect("/")

    if request.method == "GET":
        return render_template("upload.html", config=current_app.config)

    elif request.method == "POST":
        title: str = request.form.get("title", "").strip()
        description: str = request.form.get("description", "").strip()
        if len(title) < current_app.config["VIDEO_TITLE_MIN_LENGTH"] or len(title) > current_app.config["VIDEO_TITLE_MAX_LENGTH"]:
            return error("Video title must be between %s and %s characters long" % (current_app.config["VIDEO_TITLE_MIN_LENGTH"], current_app.config["VIDEO_TITLE_MAX_LENGTH"]))

        f = request.files.get("video", None)
        if f.filename == '':
            return redirect("/upload")
        if not f.mimetype.startswith("video/"):
            return error("Uploaded content must be an image!")

        video = Video.upload(user, title, description, f.read())
        if video is not None:
            return redirect("/watch/%s" % video.video_id)
        return redirect("/upload")


@video_bp.route("/video/<uuid:video_id>")
def video_get(video_id):
    video = Video.from_id(video_id)
    if video is None:
        return "Failed to get video!"
    else:
        return send_file(video.getBuffer(), video.content_type)


@video_bp.route("/watch/<uuid:video_id>")
def watch(video_id):
    video = Video.from_id(video_id)
    video.add_download()
    if video is None:
        return "Failed to get video or uploader!"
    else:
        return render_template("watch.html", video=video)
