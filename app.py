from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
app.secret_key = "memories_secret_key"
# Google Drive Setup
SCOPES = ['https://www.googleapis.com/auth/drive']
SSCOPES = ['https://www.googleapis.com/auth/drive.file']

SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")

import os
import json
from google.oauth2 import service_account

credentials_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])

credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=SCOPES
)

drive_service = build('drive', 'v3', credentials=credentials)
FOLDER_ID = '1mutUPEcpcdKqKv_g5xPyHzKSx_6SWH9L'  # We will add your folder ID next


drive_service = build('drive', 'v3', credentials=credentials)

# ===== LOGIN DETAILS (YOU CAN CHANGE ANYTIME) =====
USERNAME = "MohakchiRiya"
PASSWORD = "5thAug"

# ===== GOOGLE DRIVE SETUP =====
# ----- GOOGLE DRIVE SETUP -----
import json
import os

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Load credentials from Render Environment Variable (SAFE)
credentials_dict = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))

from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_info(
    credentials_dict, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=credentials)
FOLDER_ID = '1mutUPEcpcdKqKv_g5xPyHzKSx_6SWH9L'
drive_service = build('drive', 'v3', credentials=credentials)

# 🔴 IMPORTANT: YOU WILL PUT YOUR FOLDER ID HERE
FOLDER_ID = "1mutUPEcpcdKqKv_g5xPyHzKSx_6SWH9L"

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATA_FILE = "data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def upload_to_drive(file_path, filename):
    file_metadata = {
        'name': filename,
        'parents': [FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return file.get('id')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('gallery'))
    return render_template('login.html')

@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    with open(DATA_FILE, "r") as f:
        items = json.load(f)

    if request.method == 'POST':
        file = request.files['file']
        caption = request.form['caption']

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

        return redirect(url_for('gallery'))

    return render_template('gallery.html', items=items)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)