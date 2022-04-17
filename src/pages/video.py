from flask import Blueprint, redirect, request, session, send_file, current_app, jsonify
from typing import Optional, Any
from uuid import UUID

from db.users import AuthUser
from db.videos import Video, Comment
from db.images import Image
from db.csrf import CSRFToken
from util import error, csrf_token_required, auth_required, render_template

video_bp = Blueprint('video_page', __name__,
                     template_folder='templates')


def check_title_and_desc(title: str, description: str, base: str) -> Optional[Any]:
    if len(title) < current_app.config["VIDEO_TITLE_MIN_LENGTH"] or len(title) > current_app.config["VIDEO_TITLE_MAX_LENGTH"]:
        return error("Video title must be between %s and %s characters long" % (current_app.config["VIDEO_TITLE_MIN_LENGTH"], current_app.config["VIDEO_TITLE_MAX_LENGTH"]), base)
    if len(description) < 0 or len(description) > current_app.config["VIDEO_DESC_MAX_LENGTH"]:
        return error("Video description must be between %s and %s characters long" % (current_app.config["VIDEO_TITLE_MIN_LENGTH"], current_app.config["VIDEO_TITLE_MAX_LENGTH"]), base)
    return None


@video_bp.route("/upload", methods=["GET", "POST"])
@csrf_token_required()
@auth_required()
def video_upload():
    user = AuthUser.from_session(session)
    if request.method == "GET":
        return render_template("upload.html", me=user, config=current_app.config)

    elif request.method == "POST":
        title: str = request.form.get("title", "").strip()
        description: str = request.form.get("description", "").strip()
        err = check_title_and_desc(title, description, "/upload")
        if err is not None:
            return err

        f = request.files.get("video", None)
        if f.filename == '':
            return error("No video!", "/upload")
        if not f.mimetype.startswith("video/"):
            return error("Uploaded content must be a video!", "/upload")

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


@video_bp.route("/video/<uuid:video_id>", methods=["DELETE"])
@csrf_token_required()
@auth_required()
def video_delete(video_id):
    me = AuthUser.from_session(session)
    if Video.delete(video_id, me.user_id):
        return jsonify("Success")
    return error('Failed to delete video')


@video_bp.route("/video/edit/<uuid:video_id>", methods=["POST"])
@csrf_token_required()
@auth_required()
def video_edit(video_id):
    me = AuthUser.from_session(session)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    err = check_title_and_desc(
        title, description, "/watch/%s" % video_id)
    if err is not None:
        return err
    if Video.edit(title, description, video_id, me.user_id):
        return redirect("/watch/%s" % video_id)
    return error('Failed to edit video')


@video_bp.route("/watch/<uuid:video_id>")
def watch(video_id):
    me = AuthUser.from_session(session)
    video = Video.from_id(video_id)
    video.add_download()
    if video is None:
        return "Failed to get video or uploader!"
    else:
        return render_template("watch.html", me=me, video=video)


@video_bp.route("/comment", methods=["POST"])
@csrf_token_required()
@auth_required()
def comment():
    me = AuthUser.from_session(session)

    video_id: str = request.form.get("comment_video_id", "").strip()
    content: str = request.form.get("content", "").strip()
    video = Video.from_id(video_id)

    if video is None:
        return error("Invalid video id")
    if len(content) == 0:
        return error("Comment must not be empty!")

    comment_id = video.add_comment(me.user_id, content)
    if not comment_id:
        return error("Failed to add comment!")

    return jsonify({"comment_id": comment_id})


@video_bp.route("/comment", methods=["DELETE"])
@csrf_token_required()
@auth_required()
def delete_comment():
    me = AuthUser.from_session(session)

    comment_id: str = request.form.get("comment_id", None)
    if comment_id is None:
        return error("No comment id specified!")
    video_id = me.delete_comment(comment_id)
    if video_id:
        return jsonify("Success")
    else:
        return error("Failed to delete comment!")


@video_bp.route("/rate/thumbsup", methods=["POST"])
@csrf_token_required()
@auth_required()
def thumbsup():
    return rate_video(1, request.form.get("video_id", None))


@video_bp.route("/rate/thumbsdown", methods=["POST"])
@csrf_token_required()
@auth_required()
def thumbsdown():
    return rate_video(-1, request.form.get("video_id", None))


@video_bp.route("/rate", methods=["DELETE"])
@csrf_token_required()
@auth_required()
def unrate():
    me = AuthUser.from_session(session)

    video_id = request.form.get("video_id", None)
    if video_id is None:
        return error("Failed to get video id!")

    if me.unrate_video(video_id):
        return jsonify("Success")
    else:
        return error("Failed to rate video!")


@video_bp.route("/rate/get/<video_id>", methods=["GET"])
@csrf_token_required()
def get_ratings(video_id):
    if video_id is None:
        return error("Failed to get video id!")

    video = Video.from_id(video_id)
    if video is None:
        return error("No such video")
    return jsonify(video.get_ratings())


@video_bp.route("/comments/<video_id>", methods=["GET"])
def get_comments(video_id):
    me = AuthUser.from_session(session)
    if video_id is None:
        return error("Failed to get video id!")

    video = Video.from_id(video_id)
    if video is None:
        return error("No such video")

    return render_template("components/comments.html", comments=video.get_comments(), me=me)


def rate_video(rating: int, video_id: Optional[UUID]):
    me = AuthUser.from_session(session)

    if video_id is None:
        return error("Failed to get video id!")

    if me.rate_video(video_id, rating):
        return jsonify("Success")
    else:
        return error("Failed to rate video!")
