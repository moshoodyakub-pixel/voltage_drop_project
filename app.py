from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "change_this_secret_key_in_production"

# ---------------------------------------------------------------------------
# Database helper
# ---------------------------------------------------------------------------

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",          # update with your MySQL password
    "database": "voltage_drop_db",
}


def get_db_connection():
    """Return a new MySQL connection using DB_CONFIG."""
    return mysql.connector.connect(**DB_CONFIG)


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
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        # --- basic validation ---
        if not username or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("signup.html")

        if len(username) < 3:
            flash("Username must be at least 3 characters long.", "danger")
            return render_template("signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("signup.html")

        # --- hash password before storing ---
        hashed_password = generate_password_hash(password)

        # --- persist to database ---
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # check for duplicate username
            cursor.execute(
                "SELECT id FROM tbl_user WHERE username = %s", (username,)
            )
            if cursor.fetchone():
                flash("Username already exists. Please choose another.", "warning")
                cursor.close()
                conn.close()
                return render_template("signup.html")

            cursor.execute(
                "INSERT INTO tbl_user (username, password) VALUES (%s, %s)",
                (username, hashed_password),
            )
            conn.commit()
            cursor.close()
            conn.close()

            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for("index"))

        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
            return render_template("signup.html")

    return render_template("signup.html")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
