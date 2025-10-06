import os
import subprocess
from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    send_from_directory, jsonify
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from models import db, User, Video
from config import Config
from dotenv import load_dotenv


# -------------------------------------------------------------------------
# App Initialization
# -------------------------------------------------------------------------
load_dotenv()  # ✅ Load environment variables from .env
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database and login manager
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------
def allowed_file(filename: str) -> bool:
    """Return True if filename has an allowed extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def _ensure_owner(video: Video):
    """Abort if the current user does not own the video."""
    if video.user_id != current_user.id:
        flash("Access denied", "danger")
        return False
    return True


# -------------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------------
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ---------------- Register ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------------- Dashboard ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    q = request.args.get("q", "", type=str).strip()
    base_query = Video.query.filter_by(user_id=current_user.id)

    if q:
        like = f"%{q}%"
        base_query = base_query.filter(
            or_(Video.title.ilike(like), Video.original_filename.ilike(like))
        )

    videos = base_query.order_by(Video.created_at.desc()).all()
    return render_template("dashboard.html", videos=videos, q=q)


# ---------------- Upload ----------------
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if "video" not in request.files:
            flash("No file part", "danger")
            return redirect(request.url)

        file = request.files["video"]
        if file.filename == "":
            flash("No selected file", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            original_name = file.filename
            filename = secure_filename(original_name)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)

            # Convert to mp4 if needed
            ext = filename.rsplit(".", 1)[1].lower()
            if ext != "mp4":
                mp4_filename = f"{os.path.splitext(filename)[0]}.mp4"
                mp4_save_path = os.path.join(app.config["UPLOAD_FOLDER"], mp4_filename)
                subprocess.run(
                    ["ffmpeg", "-i", save_path, mp4_save_path, "-y"], check=False
                )
                try:
                    os.remove(save_path)
                except OSError:
                    pass
                filename = mp4_filename
                save_path = mp4_save_path

            default_title = os.path.splitext(original_name)[0]

            video = Video(
                filename=filename,
                original_filename=original_name,
                title=default_title,
                description=None,
                user_id=current_user.id,
            )
            db.session.add(video)
            db.session.commit()

            flash("Video uploaded successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("File type not allowed", "danger")

    return render_template("upload.html")


# ---------------- Stream Video ----------------
@app.route("/video/<int:video_id>")
@login_required
def stream_video(video_id):
    video = Video.query.get_or_404(video_id)
    if not _ensure_owner(video):
        return redirect(url_for("dashboard"))
    return render_template("stream.html", video=video)


# ---------------- Edit Video ----------------
@app.route("/edit_video/<int:video_id>", methods=["POST"])
@login_required
def edit_video(video_id):
    video = Video.query.get_or_404(video_id)
    if video.user_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json()
    new_title = data.get("title", "").strip()
    if new_title:
        video.original_filename = new_title
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Invalid title"}), 400


# ---------------- Download Video ----------------
@app.route("/video/<int:video_id>/download")
@login_required
def download_video(video_id):
    video = Video.query.get_or_404(video_id)
    if not _ensure_owner(video):
        return redirect(url_for("dashboard"))
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        video.filename,
        as_attachment=True,
        download_name=video.original_filename or video.filename,
    )


# ---------------- Serve Video Inline ----------------
@app.route("/videos/<path:filename>")
@login_required
def serve_video(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------------- Delete Video ----------------
@app.route("/video/<int:video_id>/delete", methods=["POST"])
@login_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    if not _ensure_owner(video):
        return redirect(url_for("dashboard"))

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass

    db.session.delete(video)
    db.session.commit()
    flash("Video deleted successfully!", "success")
    return redirect(url_for("dashboard"))


# -------------------------------------------------------------------------
# App Runner
# -------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ✅ ensures DB tables exist before running
    app.run(host="0.0.0.0", port=5000, debug=False)
