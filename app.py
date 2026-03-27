import logging
import os
import secrets

import mysql.connector
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash

app = Flask(__name__)
# SECRET_KEY must be set via the environment variable in production.
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Database helper
# ---------------------------------------------------------------------------

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "voltage_drop_db"),
}


def get_db_connection():
    """Return a new MySQL connection using DB_CONFIG."""
    return mysql.connector.connect(**DB_CONFIG)


# ---------------------------------------------------------------------------
# CSRF helpers
# ---------------------------------------------------------------------------

def _new_csrf_token() -> str:
    """Generate a fresh CSRF token, store it in the session, and return it."""
    token = secrets.token_hex(32)
    session["csrf_token"] = token
    return token


def _validate_csrf_token() -> bool:
    """Return True if the submitted CSRF token matches the one in the session."""
    form_token = request.form.get("csrf_token", "")
    session_token = session.get("csrf_token", "")
    return secrets.compare_digest(form_token, session_token)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Homepage."""
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Signup page – validate form data and persist user to the database."""
    if request.method == "POST":
        # --- CSRF validation ---
        if not _validate_csrf_token():
            flash("Invalid or expired form submission. Please try again.", "danger")
            return render_template("signup.html", csrf_token=_new_csrf_token())

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        # --- basic validation ---
        if not username or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("signup.html", csrf_token=_new_csrf_token())

        if len(username) < 3:
            flash("Username must be at least 3 characters long.", "danger")
            return render_template("signup.html", csrf_token=_new_csrf_token())

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("signup.html", csrf_token=_new_csrf_token())

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("signup.html", csrf_token=_new_csrf_token())

        # --- hash password before storing (scrypt is the strongest built-in method) ---
        hashed_password = generate_password_hash(password, method="scrypt")

        # --- persist to database ---
        # The UNIQUE constraint on tbl_user.username prevents duplicate entries.
        # We rely on that constraint and catch IntegrityError to avoid a TOCTOU
        # race condition between a separate SELECT check and the INSERT.
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tbl_user (username, password) VALUES (%s, %s)",
                (username, hashed_password),
            )
            conn.commit()
            cursor.close()
            conn.close()

            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for("index"))

        except mysql.connector.IntegrityError:
            flash("Username already exists. Please choose another.", "warning")
            return render_template("signup.html", csrf_token=_new_csrf_token())
        except mysql.connector.Error as err:
            logger.error("Database error during signup: %s", err)
            flash("An unexpected error occurred. Please try again later.", "danger")
            return render_template("signup.html", csrf_token=_new_csrf_token())

    return render_template("signup.html", csrf_token=_new_csrf_token())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
