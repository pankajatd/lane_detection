"""
Integration & Regression Test Suite for Deep Lane Detector (src/detector.py)
Project: Real-Time Deep Learning Road Lane Detection System
"""

import os
import pytest
import numpy as np
import cv2

from src.detector import DeepLaneDetector
from src.utils import load_and_validate_image


@pytest.fixture
def detector():
    """Initializes a clean detector instance."""
    return DeepLaneDetector(device="cpu", ema_alpha=0.35, ldw_threshold_m=0.25)


@pytest.fixture
def test_images_dir():
    return os.path.join(os.path.dirname(__file__), "test_images")


# =============================================================================
# 1. Detector Initialization & Lifecycle Tests
# =============================================================================
def test_detector_initialization_cpu(detector):
    assert detector is not None
    assert str(detector.device) == "cpu"
    assert detector.ema_alpha == 0.35
    assert detector.ldw_threshold_m == 0.25


def test_detector_reset(detector):
    detector.prev_left_line = (-1.2, 500.0)
    detector.prev_offset = 0.35
    detector.reset()
    assert detector.prev_left_line is None
    assert detector.prev_right_line is None
    assert detector.prev_offset == 0.0


# =============================================================================
# 2. Feature Extraction & Mask Tests
# =============================================================================
def test_extract_lane_candidates_output_shape(detector):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    candidates = detector.extract_lane_candidates(frame)
    assert candidates.shape == (480, 640)
    assert candidates.dtype == np.uint8


def test_predict_lane_mask_shapes(detector):
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    left_mask, right_mask = detector.predict_lane_mask(frame)
    assert left_mask.shape == (720, 1280)
    assert right_mask.shape == (720, 1280)


# =============================================================================
# 3. Benchmark Image Detection Tests
# =============================================================================
def test_process_frame_returns_expected_keys(detector):
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    res = detector.process_frame(frame)
    expected_keys = [
        "status", "left_fit", "right_fit", "lateral_offset_m",
        "curvature_radius_m", "departure_warning", "inference_time_ms", "horizon_y"
    ]
    for k in expected_keys:
        assert k in res


def test_process_frame_highway_straight_locked(detector, test_images_dir):
    img_path = os.path.join(test_images_dir, "highway_straight_1.jpg")
    if os.path.exists(img_path):
        img = load_and_validate_image(img_path)
        detector.reset()
        res = detector.process_frame(img)
        assert res["status"] == "LOCKED"
        assert res["left_fit"] is not None
        assert res["right_fit"] is not None


def test_process_frame_highway_straight_offset_centered(detector, test_images_dir):
    img_path = os.path.join(test_images_dir, "highway_straight_1.jpg")
    if os.path.exists(img_path):
        img = load_and_validate_image(img_path)
        detector.reset()
        res = detector.process_frame(img)
        # Centered vehicle offset should be within +-0.15m
        assert abs(res["lateral_offset_m"]) < 0.15
        assert res["departure_warning"] is False


def test_process_frame_highway_curvature_straight(detector, test_images_dir):
    img_path = os.path.join(test_images_dir, "highway_straight_1.jpg")
    if os.path.exists(img_path):
        img = load_and_validate_image(img_path)
        detector.reset()
        res = detector.process_frame(img)
        # Straight highway curvature radius should be high (>= 2000m)
        assert res["curvature_radius_m"] >= 2000.0


def test_process_frame_curved_canyon_locked(detector, test_images_dir):
    img_path = os.path.join(test_images_dir, "curved_canyon_1.jpg")
    if os.path.exists(img_path):
        img = load_and_validate_image(img_path)
        detector.reset()
        res = detector.process_frame(img)
        assert res["status"] == "LOCKED"


def test_process_frame_user_road_locked(detector, test_images_dir):
    img_path = os.path.join(test_images_dir, "user_road_exact.jpg")
    if os.path.exists(img_path):
        img = load_and_validate_image(img_path)
        detector.reset()
        res = detector.process_frame(img)
        assert res["status"] == "LOCKED"
        assert abs(res["lateral_offset_m"]) < 0.30


def test_process_frame_departure_warning_trigger(detector, test_images_dir):
    # Set strict LDW threshold to verify alert trigger logic
    detector.ldw_threshold_m = 0.005
    img_path = os.path.join(test_images_dir, "highway_straight_1.jpg")
    if os.path.exists(img_path):
        img = load_and_validate_image(img_path)
        detector.reset()
        res = detector.process_frame(img)
        # Any non-zero drift exceeding 0.005m triggers the alert
        if abs(res["lateral_offset_m"]) > 0.005:
            assert res["departure_warning"] is True


def test_process_frame_inference_latency_benchmark(detector):
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    res = detector.process_frame(frame)
    # CPU latency check
    assert res["inference_time_ms"] > 0.0
    assert res["inference_time_ms"] < 500.0


def test_temporal_ema_smoothing_consecutive_frames(detector):
    frame1 = np.zeros((720, 1280, 3), dtype=np.uint8)
    cv2.line(frame1, (200, 719), (600, 420), (255, 255, 255), 8)
    cv2.line(frame1, (1000, 719), (680, 420), (255, 255, 255), 8)
    detector.reset()
    r1 = detector.process_frame(frame1)

    # Frame 2 with slight shift
    frame2 = np.zeros((720, 1280, 3), dtype=np.uint8)
    cv2.line(frame2, (220, 719), (610, 420), (255, 255, 255), 8)
    cv2.line(frame2, (1020, 719), (690, 420), (255, 255, 255), 8)
    r2 = detector.process_frame(frame2)

    assert r1["status"] == "LOCKED"
    assert r2["status"] == "LOCKED"


def test_detector_blank_black_frame_fallback(detector):
    black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    detector.reset()
    res = detector.process_frame(black_frame)
    # Graceful fallback without crashing
    assert "status" in res
    assert res["departure_warning"] is False


def test_detector_random_noise_frame_fallback(detector):
    noise_frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    detector.reset()
    res = detector.process_frame(noise_frame)
    # Should handle noise gracefully
    assert "status" in res
