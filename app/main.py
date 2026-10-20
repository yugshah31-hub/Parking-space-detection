"""Flask web application exposing the parking space detector."""
import os

import cv2
import numpy as np
from flask import Flask, Response, jsonify, render_template, request

from app.detector import annotate, detect, load_slots

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SLOTS_FILE = os.path.join(BASE_DIR, "slots.json")


def _read_image():
    file = request.files.get("image")
    if file is None:
        return None, (jsonify(error="Send an image in form field 'image'"), 400)
    data = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        return None, (jsonify(error="Invalid image"), 400)
    return image, None


def create_app() -> Flask:
    app = Flask(__name__)
    slots = load_slots(SLOTS_FILE)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    @app.route("/api/detect", methods=["POST"])
    def api_detect():
        image, err = _read_image()
        if err:
            return err
        try:
            return jsonify(detect(image, slots))
        except ValueError as exc:
            return jsonify(error=str(exc)), 400

    @app.route("/api/annotate", methods=["POST"])
    def api_annotate():
        image, err = _read_image()
        if err:
            return err
        try:
            out = annotate(image, slots, detect(image, slots))
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        _, buf = cv2.imencode(".png", out)
        return Response(buf.tobytes(), mimetype="image/png")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
