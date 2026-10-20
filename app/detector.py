"""Core computer-vision logic for parking space detection.

Approach: every parking slot is a fixed rectangle (x, y, w, h). For each slot
we crop the region of interest (ROI), blur it, run Canny edge detection and
count edge pixels. An empty slot is plain asphalt (very few edges); a slot
with a car contains many edges (windows, body lines, wheels).
"""
import json
from typing import Dict, List

import cv2
import numpy as np

# A slot is "occupied" when the share of edge pixels in its ROI exceeds this.
DEFAULT_THRESHOLD = 0.04


def load_slots(path: str) -> List[Dict]:
    """Load slot rectangles from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def slot_occupancy(gray: np.ndarray, slot: Dict,
                   threshold: float = DEFAULT_THRESHOLD) -> Dict:
    """Return occupancy info for a single slot."""
    x, y, w, h = slot["x"], slot["y"], slot["w"], slot["h"]
    roi = gray[y:y + h, x:x + w]
    if roi.size == 0:
        raise ValueError("Slot %s lies outside the image" % slot.get("id"))
    blur = cv2.GaussianBlur(roi, (5, 5), 1.4)
    edges = cv2.Canny(blur, 50, 150)
    ratio = float(np.count_nonzero(edges)) / edges.size
    return {"id": slot["id"], "occupied": ratio > threshold,
            "edge_ratio": round(ratio, 4)}


def detect(image: np.ndarray, slots: List[Dict],
           threshold: float = DEFAULT_THRESHOLD) -> Dict:
    """Detect occupancy of all slots in a BGR image."""
    if image is None or image.size == 0:
        raise ValueError("Empty image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    results = [slot_occupancy(gray, s, threshold) for s in slots]
    occupied = sum(1 for r in results if r["occupied"])
    return {
        "total": len(results),
        "occupied": occupied,
        "free": len(results) - occupied,
        "slots": results,
    }


def annotate(image: np.ndarray, slots: List[Dict], result: Dict) -> np.ndarray:
    """Draw green (free) / red (occupied) boxes on a copy of the image."""
    out = image.copy()
    status = {r["id"]: r["occupied"] for r in result["slots"]}
    for s in slots:
        color = (0, 0, 255) if status[s["id"]] else (0, 200, 0)
        cv2.rectangle(out, (s["x"], s["y"]),
                      (s["x"] + s["w"], s["y"] + s["h"]), color, 2)
        cv2.putText(out, str(s["id"]), (s["x"] + 5, s["y"] + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    return out
