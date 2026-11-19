"""SecureGate: a small educational login application.

The application keeps authentication logic deliberately straightforward so
students can trace each security control while reading the source.
"""

import hmac
import os
import secrets
import sqlite3
from functools import wraps
from pathlib import Path

import bcrypt
from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "users.db"))

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-change-this-key"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    PERMANENT_SESSION_LIFETIME=1800,
)


def get_db():
    """Open one SQLite connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the account table if this is the first application run."""
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.commit()


def csrf_token():
    """Return the session's anti-CSRF token, creating it when needed."""
    token = session.get("_csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


@app.context_processor
def inject_csrf_token():
    return {"csrf_token": csrf_token}


@app.before_request
def protect_post_requests():
    """Reject form submissions without the token tied to this session."""
    if request.method == "POST":
        submitted = request.form.get("_csrf_token", "")
        expected = session.get("_csrf_token", "")
        if not submitted or not expected or not hmac.compare_digest(submitted, expected):
            abort(400, description="The form expired or could not be verified. Please try again.")


@app.after_request
def add_security_headers(response):
    """Set browser protections appropriate for this small server-rendered app."""
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Cache-Control", "no-store")
    return response


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "info")
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def valid_username(username):
    """Allow a short username made only from letters, digits, and underscores."""
    return (
        3 <= len(username) <= 30
        and username.replace("_", "").isalnum()
        and username.replace("_", "") != ""
    )


def valid_password(password):
    """Enforce a simple baseline and bcrypt's 72-byte input limit."""
    encoded = password.encode("utf-8")
    return (
        len(encoded) <= 72
        and len(password) >= 8
        and any(char.islower() for char in password)
        and any(char.isupper() for char in password)
        and any(char.isdigit() for char in password)
    )


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not valid_username(username):
            flash("Use 3–30 letters, numbers, or underscores for your username.", "error")
            return render_template("register.html"), 400

        if not valid_password(password):
            flash(
                "Use 8–72 UTF-8 bytes with an uppercase letter, lowercase letter, and number.",
                "error",
            )
            return render_template("register.html"), 400

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        try:
            db = get_db()
            # Placeholders keep user input separate from SQL instructions.
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("That username is already in use. Choose another one.", "error")
            return render_template("register.html"), 409

        flash("Account created. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_db().execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        password_matches = False
        if user:
            try:
                password_matches = bcrypt.checkpw(
                    password.encode("utf-8"), bytes(user["password_hash"])
                )
            except (ValueError, TypeError):
                password_matches = False

        # Use one message so the page does not reveal whether an account exists.
        if not user or not password_matches:
            flash("Invalid username or password.", "error")
            return render_template("login.html"), 401

        # Rotate the session contents after authentication to reduce session-fixation risk.
        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session.permanent = True
        csrf_token()  # Issue a new CSRF token for the authenticated session.
        flash("You are now logged in.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"])


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.errorhandler(400)
def bad_request(error):
    return render_template(
        "error.html", message=getattr(error, "description", "Bad request.")
    ), 400


if __name__ == "__main__":
    init_db()
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
