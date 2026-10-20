import io
import os
import sys

import cv2
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from app.detector import detect, load_slots  # noqa: E402
from app.main import app  # noqa: E402
from make_sample import make_image  # noqa: E402

SLOTS = load_slots(os.path.join(ROOT, "app", "slots.json"))


def test_all_free():
    result = detect(make_image(set()), SLOTS)
    assert result["total"] == 8
    assert result["free"] == 8


def test_some_occupied():
    result = detect(make_image({1, 3, 4, 6}), SLOTS)
    assert result["occupied"] == 4
    occupied_ids = {s["id"] for s in result["slots"] if s["occupied"]}
    assert occupied_ids == {1, 3, 4, 6}


def test_all_occupied():
    result = detect(make_image({1, 2, 3, 4, 5, 6, 7, 8}), SLOTS)
    assert result["occupied"] == 8


def test_empty_image_raises():
    try:
        detect(np.zeros((0, 0, 3), np.uint8), SLOTS)
    except ValueError:
        return
    raise AssertionError("ValueError expected")


def test_health_endpoint():
    resp = app.test_client().get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_api_detect():
    _, buf = cv2.imencode(".png", make_image({2, 5}))
    resp = app.test_client().post(
        "/api/detect",
        data={"image": (io.BytesIO(buf.tobytes()), "lot.png")},
        content_type="multipart/form-data")
    assert resp.status_code == 200
    assert resp.get_json()["occupied"] == 2


def test_api_detect_without_image():
    resp = app.test_client().post("/api/detect")
    assert resp.status_code == 400
