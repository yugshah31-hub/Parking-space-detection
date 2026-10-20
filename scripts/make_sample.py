"""Generate a synthetic parking-lot image for demo and tests.

Usage: python scripts/make_sample.py sample/parking.png 1,3,4,6
(the list gives the slot ids that contain a car)
"""
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SLOTS = os.path.join(HERE, "..", "app", "slots.json")


def make_image(occupied_ids, seed=0):
    rng = np.random.default_rng(seed)
    img = np.full((360, 640, 3), 110, np.uint8)
    img = cv2.add(img, rng.integers(0, 4, img.shape, dtype=np.uint8))
    with open(SLOTS, encoding="utf-8") as f:
        slots = json.load(f)
    for s in slots:
        x, y, w, h = s["x"], s["y"], s["w"], s["h"]
        cv2.rectangle(img, (x, y), (x + w, y + h), (230, 230, 230), 2)
        if s["id"] in occupied_ids:
            body = tuple(int(c) for c in rng.integers(40, 220, 3))
            cv2.rectangle(img, (x + 15, y + 12), (x + w - 15, y + h - 12), body, -1)
            cv2.rectangle(img, (x + 28, y + 30), (x + w - 28, y + 60), (30, 30, 30), -1)
            cv2.rectangle(img, (x + 28, y + h - 55), (x + w - 28, y + h - 30), (30, 30, 30), -1)
            cv2.line(img, (x + 15, y + h // 2), (x + w - 15, y + h // 2), (250, 250, 250), 2)
    return img


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "sample/parking.png"
    ids = {int(i) for i in sys.argv[2].split(",")} if len(sys.argv) > 2 else {1, 3, 4, 6}
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    cv2.imwrite(out, make_image(ids))
    print("Saved", out, "with occupied slots", sorted(ids))
