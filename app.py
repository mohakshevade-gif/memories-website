from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
import pickle

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


app = Flask(__name__)
app.secret_key = "memories_secret_key"


# ===============================
# LOGIN CREDENTIALS
# ===============================

USERNAME = "MohakchiRiya"
PASSWORD = "Brighampahije"


# ===============================
# GOOGLE DRIVE AUTHENTICATION
# ===============================

# ===============================
# GOOGLE DRIVE SETUP
# ===============================

SCOPES = ['https://www.googleapis.com/auth/drive']

credentials_dict = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))

credentials = service_account.Credentials.from_service_account_info(
    credentials_dict,
    scopes=SCOPES
)

drive_service = build('drive', 'v3', credentials=credentials)


# ===============================
# GOOGLE DRIVE FOLDER ID
# ===============================

FOLDER_ID = "1xxOEk9LwVZl4Q_qxKQJ28ftwn7ZvY8DZ"


# ===============================
# LOCAL FILE STORAGE
# ===============================

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


# ===============================
# GOOGLE DRIVE UPLOAD FUNCTION
# ===============================

def upload_to_drive(file_path, filename):

    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID]
    }

    media = MediaFileUpload(file_path, resumable=True)

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
        supportsAllDrives=True
    ).execute()

    return file.get("id")


# ===============================
# LOGIN PAGE
# ===============================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("gallery"))

        return "Login failed"

    return render_template("login.html")


# ===============================
# GALLERY PAGE
# ===============================

@app.route("/gallery", methods=["GET", "POST"])
def gallery():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    with open(DATA_FILE, "r") as f:
        items = json.load(f)

    if request.method == "POST":

        file = request.files["file"]
        caption = request.form["caption"]

        if file:

            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            drive_file_id = upload_to_drive(filepath, file.filename)

            items.append({
                "filename": file.filename,
                "caption": caption,
                "drive_id": drive_file_id
            })

            with open(DATA_FILE, "w") as f:
                json.dump(items, f)

            os.remove(filepath)

        return redirect(url_for("gallery"))

    return render_template("gallery.html", items=items)


# ===============================
# LOGOUT
# ===============================

@app.route("/logout")
def logout():

    session.clear()
    return redirect(url_for("login"))


# ===============================
# RUN APP
# ===============================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)