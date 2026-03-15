from flask import Flask, render_template, request, redirect, url_for, session
import os
import json

import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="ddnponhsu",
    api_key="169154656924871",
    api_secret="YB6b_jlZBKPjxQ8hAUDGIfn_Tvs"
)

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



# ===============================
# GOOGLE DRIVE FOLDER ID
# ===============================




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

def upload_to_cloudinary(file_path):

    result = cloudinary.uploader.upload(file_path)

    return result["secure_url"]

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

            image_url = upload_to_cloudinary(filepath)

            items.append({
                "filename": file.filename,
                "caption": caption,
                "image_url": image_url
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