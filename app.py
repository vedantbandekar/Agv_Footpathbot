import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, jsonify

app = Flask(__name__)
IMAGE_FOLDER = "images"
DB_NAME = "database.db"


# -------------------- DB HELPERS --------------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            label TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()


init_db()


# -------------------- ROUTES --------------------
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
        WHERE date = ? AND label != ''
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


@app.route("/upload", methods=["POST"])
def upload_image():
    image = request.files.get("image")
    if not image:
        return "No image", 400

    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H-%M-%S")

    folder = os.path.join(IMAGE_FOLDER, today)
    os.makedirs(folder, exist_ok=True)

    filename = f"{time_now}.jpg"
    image.save(os.path.join(folder, filename))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO images (filename, date, time, label) VALUES (?, ?, ?, ?)",
        (filename, today, time_now, "")
    )
    conn.commit()
    conn.close()

    return "", 204


@app.route("/update_label/<int:image_id>", methods=["POST"])
def update_label(image_id):
    # ✅ Works for BOTH JSON and form-data
    data = request.get_json(silent=True)
    label = None

    if data and "label" in data:
        label = data["label"]
    else:
        label = request.form.get("label")

    if not label:
        return jsonify({"error": "No label provided"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE images SET label = ? WHERE id = ?",
        (label.strip(), image_id)
    )

    conn.commit()
    rows_updated = cur.rowcount
    conn.close()

    if rows_updated == 0:
        return jsonify({"error": "Image not found"}), 404

    return jsonify({"success": True})


@app.route("/delete/<int:image_id>", methods=["POST"])
def delete_image(image_id):
    conn = get_db_connection()
    img = conn.execute(
        "SELECT filename, date FROM images WHERE id = ?",
        (image_id,)
    ).fetchone()

    if img:
        path = os.path.join(IMAGE_FOLDER, img["date"], img["filename"])
        if os.path.exists(path):
            os.remove(path)

        conn.execute("DELETE FROM images WHERE id = ?", (image_id,))
        conn.commit()

    conn.close()
    return "", 204


@app.route("/images/<date>/<filename>")
def serve_image(date, filename):
    return send_from_directory(os.path.join(IMAGE_FOLDER, date), filename)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
