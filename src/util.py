from flask import render_template as flask_template, request, session, redirect, jsonify
from typing import Any, Callable, Optional
from functools import wraps

from db.csrf import CSRFToken
from db.users import AuthUser


def get_error() -> Optional[str]:
    err = session.get('current_error', None)
    if err is not None:
        del session['current_error']
    return err


def error(error: str, base_url: Optional[str] = None):
    me = AuthUser.from_session(session)

    accept = request.headers.get('accept', None)
    if accept == "application/json":
        err = {
            "message": error
        }
        return jsonify(err), 500
    session['current_error'] = error
    if base_url is not None:
        return redirect(base_url)
    return render_template("error.html", me=me)


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
                return redirect("/")
            return route(*args, **kwargs)
        return decorated_function
    return decorator


def render_template(template: str, **kwargs):
    csrf_token = CSRFToken.from_session(session)
    error = get_error()
    return flask_template(template, error=error, csrf_token=None if csrf_token is None else csrf_token.csrf_token, **kwargs)
