"""
LMS-ML application factory.

Run (development):   flask --app app run --debug
Run (production):    gunicorn "app:create_app()"
"""
import logging

from flask import Flask, jsonify, render_template, request, session
from flask_login import LoginManager, current_user

from config import Config
from services import activity_tracker
from services.db import close_db, query_one
from services.schema import ensure_schema
from services.security import csrf_protect, csrf_token
from services.users import load_session_user


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)
    logging.basicConfig(level=logging.INFO)

    if app.config["SECRET_KEY"] == "dev-only-change-me" and not app.debug:
        app.logger.warning("SECRET_KEY is the insecure development default - set SECRET_KEY in production.")

    if not app.config.get("TESTING_SKIP_SCHEMA"):
        ensure_schema(app.config)            # create the timetable table on older databases

    # ---- authentication --------------------------------------------------------
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to continue."
    login_manager.login_message_category = "info"
    login_manager.user_loader(load_session_user)

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "Authentication required."}), 401
        from flask import redirect, url_for
        return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))

    # ---- blueprints (one per module) -------------------------------------------
    from blueprints import admin, announcements, api, auth, pages, student, teacher, videos
    for module in (auth, pages, student, teacher, admin, videos, announcements, api):
        app.register_blueprint(module.bp)

    # ---- request lifecycle -----------------------------------------------------
    app.before_request(csrf_protect)

    @app.before_request
    def record_remembered_login():
        # A student who comes back through the "keep me signed in" cookie never passes the login form,
        # so count that visit as a login here (once per browser session). The ML model uses login frequency.
        if (request.endpoint not in (None, "static") and current_user.is_authenticated
                and current_user.role == "student" and not session.get("login_log_id")):
            session["login_log_id"] = activity_tracker.log_login(current_user.id)
    app.teardown_appcontext(close_db)
    app.jinja_env.globals["csrf_token"] = csrf_token
    app.jinja_env.filters["initials"] = lambda name: "".join(w[0] for w in (name or "?").split()[:2]).upper() or "?"

    def _ago(when):
        """'3 hours ago' style text for a datetime (falls back to the date after a month)."""
        from datetime import datetime
        if when is None:
            return "never"
        secs = int((datetime.now() - when).total_seconds())
        if secs < 60:
            return "just now"
        for size, unit in ((86400, "day"), (3600, "hour"), (60, "minute")):
            if secs >= size:
                n = secs // size
                return when.strftime("%d %b %Y") if unit == "day" and n > 30 else f"{n} {unit}{'' if n == 1 else 's'} ago"
        return "just now"
    app.jinja_env.filters["ago"] = _ago
    from services.text import rich, rich_inline          # safe rendering of assignment briefs and quiz questions
    app.jinja_env.filters["rich"] = rich
    app.jinja_env.filters["rich_inline"] = rich_inline
    # One colour per SUBJECT: every section of a subject (CS302, CS302-B, ...) shares it. Cached per process.
    _tones: dict[int, str] = {}
    _bases = ["CS301", "CS302", "CS304", "CS305", "CS306", "CS307", "MA201"]

    def _tone(course_id) -> str:
        cid = int(course_id)
        if cid not in _tones:
            row = query_one("SELECT code FROM courses WHERE id = %s", (cid,))
            base = row["code"].split("-")[0] if row else ""
            _tones[cid] = f"tone-{_bases.index(base) if base in _bases else cid % 8}"
        return _tones[cid]
    app.jinja_env.filters["tone"] = _tone

    @app.context_processor
    def admin_badges():
        """Pending teacher count for the admin sidebar (one cheap query, admins only)."""
        from flask_login import current_user
        if current_user.is_authenticated and current_user.role == "admin":
            try:
                row = query_one("SELECT COUNT(*) AS n FROM users WHERE role = 'teacher' AND is_approved = 0")
                return {"pending_teachers": row["n"] if row else 0}
            except Exception:                  # never let a badge break a page
                return {"pending_teachers": 0}
        return {"pending_teachers": 0}

    @app.after_request
    def security_headers(resp):
        # Bootstrap and Chart.js are vendored under /static/vendor, so 'self' is enough
        # (and the site also works on a campus network with no internet).
        # Frames are forbidden everywhere except the one page that plays a lecture, and there only YouTube's
        # privacy-enhanced embed origin is allowed.
        frames = "https://www.youtube-nocookie.com" if request.endpoint == "videos.watch" else "'none'"
        resp.headers.setdefault("Content-Security-Policy",
                                f"default-src 'self'; img-src 'self' data:; frame-src {frames}; frame-ancestors 'none'; "
                                "base-uri 'self'; form-action 'self'")
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "same-origin")
        if request.endpoint and request.endpoint != "static":
            resp.headers.setdefault("Cache-Control", "no-store")   # never cache personal pages
        return resp

    # ---- error pages -----------------------------------------------------------
    def _error(code: int, title: str, detail: str):
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": detail}), code
        return render_template("error.html", code=code, title=title, detail=detail), code

    app.register_error_handler(400, lambda e: _error(400, "Request rejected", getattr(e, "description", "Bad request.")))
    app.register_error_handler(403, lambda e: _error(403, "Access denied", "You do not have permission to view this page."))
    app.register_error_handler(404, lambda e: _error(404, "Page not found", "We couldn't find what you were looking for."))
    app.register_error_handler(413, lambda e: _error(413, "File too large", "That upload is bigger than the 25 MB limit."))
    app.register_error_handler(500, lambda e: _error(500, "Something went wrong", "An unexpected error occurred."))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
