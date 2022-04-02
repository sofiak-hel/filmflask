from flask import render_template as flask_template, request, session, redirect
import ffmpeg
import tempfile
from typing import Any, Callable
from functools import wraps

from db.csrf import CSRFToken
from db.users import AuthUser


def error(error: str):
    return render_template("error.html", error=error)


def process_image(blob: bytes):
    process = (
        ffmpeg
        .input('pipe:')
        .filter_("crop", "min(iw,ih)", "min(iw,ih)")
        .filter_('scale', 250, 250)
        .output('pipe:', format="image2pipe", vcodec="png", pix_fmt="rgba")
        .run_async(pipe_stdout=True, pipe_stdin=True)
    )
    process.stdin.write(blob)
    process.stdin.close()
    res = process.stdout.read()
    process.wait()
    return res


def process_video(blob: bytes):
    inf = tempfile.NamedTemporaryFile()
    ouf = tempfile.NamedTemporaryFile()
    inf.write(blob)

    process = (
        ffmpeg
        .input(inf.name)
        .output(ouf.name, format="mp4")
        .overwrite_output()
        .run_async(pipe_stdout=True)
    )
    process.wait()
    inf.close()

    res = ouf.read()
    ouf.close()
    return res


def create_thumbnail(blob: bytes):
    inf = tempfile.NamedTemporaryFile()
    inf.write(blob)

    process = (
        ffmpeg
        .input(inf.name)
        .filter("select", "eq(n,34)")
        .output('pipe:', format="image2pipe", vcodec="mjpeg", vframes=1)
        .run_async(pipe_stdout=True)
    )
    res = process.stdout.read()
    inf.close()
    process.wait()
    return res


def csrf_token_required() -> Callable[..., Any]:
    def decorator(route: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(route)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            if request.method == "POST" and not CSRFToken.validate_request(request, session):
                return error("Invalid or no CSRF Token")
            return route(*args, **kwargs)
        return decorated_function
    return decorator


def auth_required(methods: list[str] = ["POST", "GET", "DELETE", "PATCH"]) -> Callable[..., Any]:
    def decorator(route: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(route)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            if request.method in methods and not AuthUser.validate_session(session):
                return error("No auth!")
            return route(*args, **kwargs)
        return decorated_function
    return decorator


def render_template(template: str, **kwargs):
    csrf_token = CSRFToken.from_session(session)
    return flask_template(template, csrf_token=None if csrf_token is None else csrf_token.csrf_token, **kwargs)
