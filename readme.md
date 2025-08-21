# 🎬 Streamify - Video Streaming Platform

A simple Flask-based video streaming platform where users can **register, log in, upload videos, and watch them** with theme support (Light/Dark mode).

---

## 🚀 Features
* **User Authentication**: Register, Login, and Logout functionality.
* **Video Management**: Upload, stream, and delete your own videos.
* **Dashboard**: A dedicated page to easily manage your video library.
* **Responsive UI**: A user-friendly interface that adapts to all screen sizes.
* **Theme Toggle**: Easily switch between Light and Dark modes.
* **Video Player Controls**: Built-in forward and backward controls on the video player.
* **Stylish Frontend**: The UI is styled using Bootstrap 5.

---

## 🛠️ Tech Stack
* **Backend**: Flask, Flask-Login, Flask-SQLAlchemy.
* **Database**: SQLite (default) or MySQL (optional).
* **Storage**: Local filesystem or AWS S3 for video storage.
* **Video Processing**: FFmpeg.
* **Frontend**: Bootstrap 5.

---

## 📂 Project Structure
```text
project/
│── app.py                # Main Flask application
│── config.py             # Configuration (DB, secret key, uploads)
│── requirements.txt      # Python dependencies
│── templates/            # HTML templates (Jinja2)
│   ├── base.html         # Common layout (Navbar, Footer, Theme)
│   ├── dashboard.html    # Dashboard (video list)
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   └── upload.html       # Upload form
│── static/               # Static files (currently empty but REQUIRED)
│   ├── css/              # Custom styles (optional)
│   ├── js/               # Custom JavaScript (optional)
│   ├── images/           # Logos/Icons (optional)
│   └── uploads/          # Uploaded videos will be stored here
```

> ⚠️ Even if the `static/` folder is empty, keep it in your project.
> Flask automatically looks inside it for CSS/JS/images.
> Later you can add custom styles like `static/css/style.css`.

---

## ⚙️ Installation

1.  **Clone this repository** or download the project files:
    ```bash
    git clone [https://github.com/yourusername/streamify.git](https://github.com/yourusername/streamify.git)
    cd streamify
    ```
2.  **Create and activate a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate    # For Linux/Mac
    venv\Scripts\activate       # For Windows
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up the database**
    By default, the app is configured for MySQL in `config.py`.
    Example:
    ```python
    SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/videoplatform'
    ```
    Create the database in MySQL:
    ```sql
    CREATE DATABASE videoplatform;
    ```
    Run database migrations (if using Flask-Migrate):
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```
---

## 🚀 Running the App
Start the Flask server:
```bash
python app.py
```
Open in your browser:
`http://127.0.0.1:5000`

---

## 🖥️ How to Use Streamify
* **Register** a new account.
* **Login** with your credentials.
* **Access the Dashboard**:
    * See a list of uploaded videos.
    * Watch videos with play, forward, and backward controls.
* **Upload Videos** from the Upload page.
* **Theme Toggle**:
    * Use the 🌓 button in the navbar to switch between Light & Dark mode.
* **Logout** anytime from the navbar.

---

## 📌 Notes
* Uploaded videos are stored in `static/uploads/`.
* If `static/uploads/` doesn’t exist, create it manually:
    ```bash
    mkdir -p static/uploads
    ```
* You can later add custom CSS in:
    ```swift
    static/css/style.css
    ```
    and link it inside `base.html` for better UI customization.
