"""
QA Test Runner Script: Generates visual result images for all test benchmark images.
Outputs annotated results to tests/test_results/ for human inspection.
"""

import os
import glob
import cv2
import sys

# Ensure project root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.detector import DeepLaneDetector
from src.utils import load_and_validate_image, draw_lane_overlay

def run():
    img_dir = os.path.join(root_dir, "tests", "test_images")
    out_dir = os.path.join(root_dir, "tests", "test_results")
    os.makedirs(out_dir, exist_ok=True)

    detector = DeepLaneDetector(device="cpu", ema_alpha=0.35, ldw_threshold_m=0.25)
    
    image_files = sorted(glob.glob(os.path.join(img_dir, "*.jpg")))
    print(f"Found {len(image_files)} test benchmark images in {img_dir}\n")

    for img_path in image_files:
        fname = os.path.basename(img_path)
        img = load_and_validate_image(img_path)
        
        # Reset detector state for clean single-frame evaluation
        detector.reset()
        res = detector.process_frame(img)
        
        # Overlay visual AR corridor and HUD
        annotated = draw_lane_overlay(img, res["left_fit"], res["right_fit"], res)
        
        out_path = os.path.join(out_dir, f"result_{fname}")
        cv2.imwrite(out_path, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
        
        status = res["status"]
        offset = res["lateral_offset_m"]
        curv = res["curvature_radius_m"]
        ldw = "WARNING" if res["departure_warning"] else "NORMAL"
        print(f"[OK] {fname:25s} -> Status: {status:7s} | Offset: {offset:+.2f}m | Curvature: {curv:6.0f}m | Alert: {ldw:7s} | Saved: result_{fname}")

    print(f"\nAll visual result images successfully generated in: {out_dir}")

if __name__ == "__main__":
    run()
