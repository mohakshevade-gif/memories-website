
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERNAME = "love"
PASSWORD = "forever"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("gallery"))
        else:
            return "Wrong username or password 💔"

    return render_template("login.html")

@app.route("/gallery", methods=["GET", "POST"])
def gallery():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files["file"]
        caption = request.form["caption"]

        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            with open(os.path.join(UPLOAD_FOLDER, file.filename + ".txt"), "w") as f:
                f.write(caption)

    files = [f for f in os.listdir(UPLOAD_FOLDER) if not f.endswith(".txt")]
    items = []

    for file in files:
        caption_file = os.path.join(UPLOAD_FOLDER, file + ".txt")
        caption = ""
        if os.path.exists(caption_file):
            with open(caption_file, "r") as f:
                caption = f.read()
        items.append({"filename": file, "caption": caption})

    return render_template("gallery.html", items=items)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/download/<filename>")
def download_file(filename):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)