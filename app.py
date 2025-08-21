import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Video
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Ensure video upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize DB
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ---------------- Register ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)  # ✅ securely hash password
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------------- Login ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ---------------- Dashboard ----------------
@app.route('/dashboard')
@login_required
def dashboard():
    videos = Video.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', videos=videos)

# ---------------- Upload ----------------
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['video']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            # Convert to mp4 if needed
            ext = filename.rsplit('.', 1)[1].lower()
            if ext != 'mp4':
                mp4_filename = filename.rsplit('.', 1)[0] + '.mp4'
                mp4_save_path = os.path.join(app.config['UPLOAD_FOLDER'], mp4_filename)
                subprocess.run(['ffmpeg', '-i', save_path, mp4_save_path, '-y'])
                os.remove(save_path)
                filename = mp4_filename
                save_path = mp4_save_path

            video = Video(filename=filename, original_filename=file.filename, user_id=current_user.id)
            db.session.add(video)
            db.session.commit()

            flash('Video uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('File type not allowed', 'danger')

    return render_template('upload.html')

# ---------------- Stream Video ----------------
@app.route('/video/<int:video_id>')
@login_required
def stream_video(video_id):
    video = Video.query.get_or_404(video_id)
    if video.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('stream.html', video=video)

@app.route('/videos/<filename>')
@login_required
def serve_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/delete/<int:video_id>', methods=['GET'])
@login_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    if video.user_id != current_user.id:
        flash("Access denied!")
        return redirect(url_for('dashboard'))

    # remove file from storage
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(video)
    db.session.commit()
    flash("Video deleted successfully!")
    return redirect(url_for('dashboard'))



# ---------------- Run App ----------------
if __name__ == '__main__':
    app.run(debug=True)
