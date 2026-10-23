"""
Unit Test Suite for Utility & HUD Annotation Module (src/utils.py)
Project: Real-Time Deep Learning Road Lane Detection System
"""

import os
import io
import pytest
import numpy as np
from PIL import Image
import cv2

from src.utils import (
    validate_media_input,
    load_and_validate_image,
    extract_video_frame_iterator,
    draw_lane_overlay,
    format_telemetry_csv,
    COLOR_CORRIDOR,
    COLOR_LEFT_LANE,
    COLOR_RIGHT_LANE
)


# =============================================================================
# 1. Media Input Validation Tests
# =============================================================================
def test_validate_media_input_valid_jpg():
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    is_valid, m_type, msg = validate_media_input(buf.getvalue(), "test.jpg")
    assert is_valid is True
    assert m_type == "image"


def test_validate_media_input_valid_png():
    img = Image.new("RGB", (100, 100), color=(0, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    is_valid, m_type, msg = validate_media_input(buf.getvalue(), "test.png")
    assert is_valid is True
    assert m_type == "image"


def test_validate_media_input_valid_mp4():
    fake_video = b"\x00" * 2048
    is_valid, m_type, msg = validate_media_input(fake_video, "highway.mp4")
    assert is_valid is True
    assert m_type == "video"


def test_validate_media_input_empty_payload():
    is_valid, m_type, msg = validate_media_input(b"", "empty.jpg")
    assert is_valid is False
    assert m_type == "unknown"


def test_validate_media_input_corrupted_image():
    corrupted_bytes = b"NOT_A_REAL_IMAGE_HEADER_DATA"
    is_valid, m_type, msg = validate_media_input(corrupted_bytes, "corrupt.jpg")
    assert is_valid is False
    assert m_type == "image"


def test_validate_media_input_unsupported_extension():
    data = b"some binary data content"
    is_valid, m_type, msg = validate_media_input(data, "document.pdf")
    assert is_valid is False
    assert m_type == "unknown"


def test_validate_media_input_tiny_video_header():
    tiny_video = b"\x00" * 100  # < 1024 bytes
    is_valid, m_type, msg = validate_media_input(tiny_video, "short.mp4")
    assert is_valid is False
    assert m_type == "video"


# =============================================================================
# 2. Image Loading & Normalization Tests
# =============================================================================
def test_load_and_validate_image_from_numpy():
    arr = np.ones((120, 160, 3), dtype=np.uint8) * 128
    res = load_and_validate_image(arr)
    assert isinstance(res, np.ndarray)
    assert res.shape == (120, 160, 3)
    assert res.dtype == np.uint8


def test_load_and_validate_image_from_pil():
    pil_img = Image.new("RGB", (80, 60), color=(100, 150, 200))
    res = load_and_validate_image(pil_img)
    assert isinstance(res, np.ndarray)
    assert res.shape == (60, 80, 3)


def test_load_and_validate_image_from_bytes():
    pil_img = Image.new("RGB", (90, 70), color=(50, 60, 70))
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG")
    res = load_and_validate_image(buf.getvalue())
    assert isinstance(res, np.ndarray)
    assert res.shape == (70, 90, 3)


def test_load_and_validate_image_grayscale_conversion():
    gray_arr = np.ones((100, 100), dtype=np.uint8) * 200
    res = load_and_validate_image(gray_arr)
    assert res.shape == (100, 100, 3)


def test_load_and_validate_image_rgba_conversion():
    rgba_arr = np.ones((80, 80, 4), dtype=np.uint8) * 255
    res = load_and_validate_image(rgba_arr)
    assert res.shape == (80, 80, 3)


def test_load_and_validate_image_none_raises_error():
    with pytest.raises(ValueError):
        load_and_validate_image(None)


def test_load_and_validate_image_empty_raises_error():
    with pytest.raises(ValueError):
        load_and_validate_image(np.array([]))


# =============================================================================
# 3. Video Stream Generator Tests
# =============================================================================
def test_extract_video_frame_iterator_max_frames():
    preset_vid = os.path.join(
        os.path.dirname(__file__), "..", "data", "sample_presets", "highway_straight.mp4"
    )
    if os.path.exists(preset_vid):
        frames = list(extract_video_frame_iterator(preset_vid, max_frames=5))
        assert len(frames) == 5
        assert isinstance(frames[0], np.ndarray)
        assert len(frames[0].shape) == 3


def test_extract_video_frame_iterator_rgb_channels():
    preset_vid = os.path.join(
        os.path.dirname(__file__), "..", "data", "sample_presets", "highway_straight.mp4"
    )
    if os.path.exists(preset_vid):
        for frame in extract_video_frame_iterator(preset_vid, max_frames=2):
            assert frame.shape[2] == 3
            assert frame.dtype == np.uint8


# =============================================================================
# 4. HUD & Corridor Rendering Tests
# =============================================================================
def test_draw_lane_overlay_valid_polynomials():
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    left_fit = np.array([0.0, -1.2, 800.0])
    right_fit = np.array([0.0, 1.2, -200.0])
    telemetry = {
        "status": "LOCKED",
        "lateral_offset_m": 0.05,
        "curvature_radius_m": 2500.0,
        "departure_warning": False,
        "horizon_y": 420
    }
    annotated = draw_lane_overlay(frame, left_fit, right_fit, telemetry)
    assert annotated.shape == frame.shape
    assert annotated.dtype == np.uint8


def test_draw_lane_overlay_missing_lines():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    telemetry = {
        "status": "SEARCHING",
        "lateral_offset_m": 0.0,
        "curvature_radius_m": 2500.0,
        "departure_warning": False
    }
    annotated = draw_lane_overlay(frame, None, None, telemetry)
    assert annotated.shape == (480, 640, 3)


def test_draw_lane_overlay_empty_frame_raises_error():
    with pytest.raises(ValueError):
        draw_lane_overlay(np.array([]), None, None)


def test_draw_lane_overlay_hud_badges_normal():
    frame = np.ones((600, 800, 3), dtype=np.uint8) * 50
    telemetry = {
        "status": "LOCKED",
        "lateral_offset_m": 0.04,
        "curvature_radius_m": 2500.0,
        "departure_warning": False
    }
    annotated = draw_lane_overlay(frame, None, None, telemetry)
    assert annotated.shape == frame.shape


def test_draw_lane_overlay_hud_badges_warning():
    frame = np.ones((600, 800, 3), dtype=np.uint8) * 50
    telemetry = {
        "status": "LOCKED",
        "lateral_offset_m": 0.42,
        "curvature_radius_m": 600.0,
        "departure_warning": True
    }
    annotated = draw_lane_overlay(frame, None, None, telemetry)
    assert annotated.shape == frame.shape


# =============================================================================
# 5. CSV Serialization Tests
# =============================================================================
def test_format_telemetry_csv_empty_records():
    csv_str = format_telemetry_csv([])
    assert "Frame #" in csv_str
    assert "Lateral Offset (m)" in csv_str


def test_format_telemetry_csv_with_records():
    records = [
        {
            "frame_id": 1,
            "timestamp_s": 0.033,
            "status": "LOCKED",
            "lateral_offset_m": 0.045,
            "curvature_radius_m": 2500.0,
            "departure_warning": False,
            "inference_time_ms": 35.2
        },
        {
            "frame_id": 2,
            "timestamp_s": 0.066,
            "status": "LOCKED",
            "lateral_offset_m": -0.280,
            "curvature_radius_m": 1200.0,
            "departure_warning": True,
            "inference_time_ms": 36.1
        }
    ]
    csv_str = format_telemetry_csv(records)
    lines = csv_str.strip().split("\n")
    assert len(lines) == 3  # Header + 2 data rows
    assert "0.045" in lines[1]
    assert "YES" in lines[2]
