
import os
import sqlite3
import hashlib
import uuid

from datetime import datetime
from flask import (
    Flask, request, redirect, url_for,
    render_template, flash, send_file, abort
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "vaultguard_secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
BACKUP_FOLDER = os.path.join(BASE_DIR, "backups")
DATABASE = os.path.join(BASE_DIR, "vaultguard.db")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS backups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            checksum TEXT NOT NULL,
            backup_time TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            file_name TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            activity_time TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def get_backup_path(stored_name):
    safe_name = os.path.basename(stored_name)
    return os.path.join(BACKUP_FOLDER, safe_name)


def calculate_checksum(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def log_activity(action, file_name, status, details=""):
    conn = get_db()

    conn.execute("""
        INSERT INTO activity_logs
        (action, file_name, status, details, activity_time)
        VALUES (?, ?, ?, ?, ?)
    """, (
        action,
        file_name,
        status,
        details,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db()

    backups = conn.execute(
        "SELECT * FROM backups ORDER BY id DESC"
    ).fetchall()

    total_backups = len(backups)
    total_size = sum(item["file_size"] for item in backups)

    conn.close()

    return render_template(
        "index.html",
        backups=backups,
        total_backups=total_backups,
        total_size=total_size
    )


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file selected.")
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("Please select a file.")
        return redirect(url_for("index"))

    original_name = secure_filename(file.filename)

    if not original_name:
        flash("Invalid filename.")
        return redirect(url_for("index"))

    stored_name = f"{uuid.uuid4().hex}_{original_name}"
    backup_path = get_backup_path(stored_name)

    try:
        file.save(backup_path)

        checksum = calculate_checksum(backup_path)
        file_size = os.path.getsize(backup_path)

        conn = get_db()

        conn.execute("""
            INSERT INTO backups
            (file_name, stored_name, file_size, checksum, backup_time)
            VALUES (?, ?, ?, ?, ?)
        """, (
            original_name,
            stored_name,
            file_size,
            checksum,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        log_activity(
            "Backup",
            original_name,
            "Success",
            "New backup created successfully."
        )

        flash("File backed up successfully!")

    except Exception as error:
        if os.path.exists(backup_path):
            os.remove(backup_path)

        log_activity(
            "Backup",
            original_name,
            "Failed",
            str(error)
        )

        flash("Backup failed. Please try again.")

    return redirect(url_for("index"))


@app.route("/recovery")
def recovery():
    conn = get_db()

    backups = conn.execute(
        "SELECT * FROM backups ORDER BY id DESC"
    ).fetchall()

    conn.close()

    versions = {}
    version_counts = {}

    for backup in backups:
        name = backup["file_name"]

        version_counts[name] = version_counts.get(name, 0) + 1
        versions[backup["id"]] = version_counts[name]

    return render_template(
        "recovery.html",
        backups=backups,
        versions=versions
    )


@app.route("/verify/<int:backup_id>")
def verify(backup_id):
    conn = get_db()

    backup = conn.execute(
        "SELECT * FROM backups WHERE id = ?",
        (backup_id,)
    ).fetchone()

    conn.close()

    if backup is None:
        abort(404)

    backup_path = get_backup_path(backup["stored_name"])

    if not os.path.isfile(backup_path):
        log_activity(
            "Verification",
            backup["file_name"],
            "Failed",
            "Backup file is missing."
        )

        flash("Backup file is missing.")
        return redirect(url_for("recovery"))

    current_checksum = calculate_checksum(backup_path)

    if current_checksum == backup["checksum"]:
        log_activity(
            "Verification",
            backup["file_name"],
            "Success",
            "SHA-256 integrity check passed."
        )

        flash(f"Integrity verified: {backup['file_name']}")

    else:
        log_activity(
            "Verification",
            backup["file_name"],
            "Failed",
            "SHA-256 checksum mismatch detected."
        )

        flash(f"WARNING: Integrity check failed for {backup['file_name']}")

    return redirect(url_for("recovery"))


@app.route("/restore/<int:backup_id>")
def restore(backup_id):
    conn = get_db()

    backup = conn.execute(
        "SELECT * FROM backups WHERE id = ?",
        (backup_id,)
    ).fetchone()

    conn.close()

    if backup is None:
        abort(404)

    backup_path = get_backup_path(backup["stored_name"])

    if not os.path.isfile(backup_path):
        log_activity(
            "Restore",
            backup["file_name"],
            "Failed",
            "Backup file is missing."
        )

        flash("The requested backup file is missing.")
        return redirect(url_for("recovery"))

    current_checksum = calculate_checksum(backup_path)

    if current_checksum != backup["checksum"]:
        log_activity(
            "Restore",
            backup["file_name"],
            "Blocked",
            "Recovery blocked due to integrity mismatch."
        )

        flash("Recovery blocked: Integrity verification failed.")
        return redirect(url_for("recovery"))

    log_activity(
        "Restore",
        backup["file_name"],
        "Success",
        "Verified backup downloaded successfully."
    )

    return send_file(
        backup_path,
        as_attachment=True,
        download_name=backup["file_name"]
    )


@app.route("/activity")
def activity():
    conn = get_db()

    logs = conn.execute(
        "SELECT * FROM activity_logs ORDER BY id DESC"
    ).fetchall()

    total_activities = len(logs)

    successful = sum(
        1 for log in logs if log["status"] == "Success"
    )

    failed = sum(
        1 for log in logs
        if log["status"] in ("Failed", "Blocked")
    )

    conn.close()

    return render_template(
        "activity.html",
        logs=logs,
        total_activities=total_activities,
        successful=successful,
        failed=failed
    )


@app.route("/health")
def health():
    conn = get_db()

    backups = conn.execute(
        "SELECT * FROM backups ORDER BY id DESC"
    ).fetchall()

    conn.close()

    health_records = []

    healthy = 0
    corrupted = 0
    missing = 0

    for backup in backups:
        backup_path = get_backup_path(backup["stored_name"])

        if not os.path.isfile(backup_path):
            status = "Missing"
            missing += 1

        else:
            current_checksum = calculate_checksum(backup_path)

            if current_checksum == backup["checksum"]:
                status = "Healthy"
                healthy += 1
            else:
                status = "Corrupted"
                corrupted += 1

        health_records.append({
            "file_name": backup["file_name"],
            "file_size": backup["file_size"],
            "backup_time": backup["backup_time"],
            "status": status
        })

    return render_template(
        "health.html",
        health_records=health_records,
        healthy=healthy,
        corrupted=corrupted,
        missing=missing,
        total=len(backups)
    )


initialize_database()

if __name__ == "__main__":
    app.run(debug=True)
