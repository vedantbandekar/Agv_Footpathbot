import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime
from flask import send_from_directory

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            date TEXT,
            time TEXT,
            label TEXT
        )
    """)
    conn.commit()
    conn.close()



app = Flask(__name__)
init_db()
# Folder where images will be stored
IMAGE_FOLDER = "images"
# app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

@app.route("/")
def dataset():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_db_connection()

    images = conn.execute(
        "SELECT * FROM images WHERE date = ? ORDER BY time DESC",
        (today,)
    ).fetchall()

    total_count = conn.execute(
        "SELECT COUNT(*) FROM images WHERE date = ?",
        (today,)
    ).fetchone()[0]

    tag_counts = conn.execute(
        """
        SELECT label, COUNT(*) as count
        FROM images
        WHERE date = ?
        GROUP BY label
        """,
        (today,)
    ).fetchall()

    conn.close()

    return render_template(
        "dataset.html",
        images=images,
        total_count=total_count,
        tag_counts=tag_counts,
        date=today
    )

@app.route("/test-upload")
def test_upload():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return "No image found", 400

    image = request.files["image"]

    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H-%M-%S")

    save_folder = os.path.join(IMAGE_FOLDER, today)
    os.makedirs(save_folder, exist_ok=True)

    filename = f"{time_now}.jpg"
    image_path = os.path.join(save_folder, filename)
    image.save(image_path)

    # Save metadata to database
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO images (filename, date, time) VALUES (?, ?, ?)",
        (filename, today, time_now)
    )
    conn.commit()
    conn.close()

    return "Image received", 200

@app.route("/delete/<int:image_id>", methods=["POST"])
def delete_image(image_id):
    conn = get_db_connection()
    img = conn.execute(
        "SELECT * FROM images WHERE id = ?",
        (image_id,)
    ).fetchone()

    if img is None:
        conn.close()
        return "Image not found", 404

    # delete file
    image_path = os.path.join(IMAGE_FOLDER, img["date"], img["filename"])
    if os.path.exists(image_path):
        os.remove(image_path)

    # delete from db
    conn.execute("DELETE FROM images WHERE id = ?", (image_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("dataset"))

@app.route('/images/<date>/<filename>')
def serve_image(date, filename):
        return send_from_directory(os.path.join(IMAGE_FOLDER, date), filename)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

@app.route("/update-meta/<int:image_id>", methods=["POST"])
def update_meta(image_id):
    data = request.json
    tag = data.get("tag")
    label = data.get("label")

    conn = get_db_connection()

    if tag is not None:
        conn.execute(
            "UPDATE images SET tag = ? WHERE id = ?",
            (tag, image_id)
        )

    if label is not None:
        conn.execute(
            "UPDATE images SET label = ? WHERE id = ?",
            (label, image_id)
        )

    conn.commit()
    conn.close()
    return "", 204
