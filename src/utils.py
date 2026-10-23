"""
Utility, Image Processing & Visual HUD Annotation Module
Project: Real-Time Deep Learning Road Lane Detection System
Provides robust media validation, video stream frame extraction,
augmented reality (AR) driving corridor rendering, and telemetry formatting.
"""

import os
import io
import tempfile
from typing import Union, List, Dict, Tuple, Optional, Generator, Any
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
import cv2

# Defense-in-depth: Cap max image pixels to 50 megapixels to prevent decompression bomb DoS
Image.MAX_IMAGE_PIXELS = 50_000_000

# =============================================================================
# Visual Color Contract Constants (RGB format)
# =============================================================================
COLOR_LEFT_LANE: Tuple[int, int, int] = (0, 150, 255)        # Electric Blue
COLOR_RIGHT_LANE: Tuple[int, int, int] = (255, 191, 0)       # Bright Amber / Gold
COLOR_CORRIDOR: Tuple[int, int, int] = (0, 255, 128)        # Neon Green
COLOR_CENTER_LINE: Tuple[int, int, int] = (0, 255, 255)      # Cyan / Light Blue
COLOR_NORMAL_BADGE: Tuple[int, int, int] = (34, 197, 94)     # Emerald Green
COLOR_WARNING_BADGE: Tuple[int, int, int] = (239, 68, 68)    # Crimson Red
COLOR_TEXT_WHITE: Tuple[int, int, int] = (255, 255, 255)
COLOR_HUD_BG: Tuple[int, int, int] = (15, 23, 42)            # Dark Slate Navy


def validate_media_input(
    file_bytes: Union[bytes, io.BytesIO],
    filename: str
) -> Tuple[bool, str, str]:
    """
    Validates uploaded file bytes to ensure they represent a valid, supported media container.

    Args:
        file_bytes: In-memory byte buffer or raw bytes.
        filename: Original file name string.

    Returns:
        tuple: (is_valid: bool, media_type: str ['image', 'video', 'unknown'], message: str)
    """
    if not file_bytes:
        return False, "unknown", "File byte stream is empty."

    raw_bytes = file_bytes.getvalue() if isinstance(file_bytes, io.BytesIO) else file_bytes
    if len(raw_bytes) == 0:
        return False, "unknown", "File payload has 0 bytes."

    ext = os.path.splitext(filename.lower())[1]

    # Image validation
    if ext in [".jpg", ".jpeg", ".png", ".webp"]:
        try:
            stream = io.BytesIO(raw_bytes)
            with Image.open(stream) as img:
                img.verify()
            return True, "image", f"Valid image format: {ext}"
        except Exception as e:
            return False, "image", f"Corrupt image payload: {str(e)}"

    # Video validation
    elif ext in [".mp4", ".avi", ".mov", ".mkv"]:
        # Verify non-trivial byte size (videos require header containers >= 1024 bytes)
        if len(raw_bytes) < 1024:
            return False, "video", "Video file payload is too small to contain valid container headers."
        return True, "video", f"Supported video container: {ext}"

    else:
        return False, "unknown", f"Unsupported file extension: {ext}. Expected .mp4, .avi, .jpg, .png."


def load_and_validate_image(
    image_input: Union[bytes, io.BytesIO, Image.Image, np.ndarray, str]
) -> np.ndarray:
    """
    Ingests file bytes, BytesIO stream, PIL Image, file path, or NumPy array.
    Ensures standard 3-channel RGB uint8 format with shape (H, W, 3).

    Returns:
        np.ndarray: An image array of shape (H, W, 3) and dtype uint8.

    Raises:
        ValueError: If input is corrupt, empty, or cannot be parsed as an RGB image.
    """
    if image_input is None:
        raise ValueError("Image input cannot be None.")

    try:
        if isinstance(image_input, np.ndarray):
            img = image_input.copy()
            if img.size == 0 or len(img.shape) < 2:
                raise ValueError("NumPy array is empty or has invalid dimensions.")
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            elif img.shape[2] != 3:
                raise ValueError(f"Unsupported number of image channels: {img.shape[2]}")
            return img.astype(np.uint8)

        elif isinstance(image_input, Image.Image):
            pil_img = ImageOps.exif_transpose(image_input)
            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")
            arr = np.array(pil_img)
            if arr.size == 0:
                raise ValueError("Converted PIL image array is empty.")
            return arr.astype(np.uint8)

        elif isinstance(image_input, (bytes, io.BytesIO)):
            raw_bytes = image_input.getvalue() if isinstance(image_input, io.BytesIO) else image_input
            if len(raw_bytes) == 0:
                raise ValueError("Byte stream is empty.")
            stream = io.BytesIO(raw_bytes)
            with Image.open(stream) as pil_img:
                pil_img = ImageOps.exif_transpose(pil_img)
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")
                arr = np.array(pil_img)
            return arr.astype(np.uint8)

        elif isinstance(image_input, str):
            if not os.path.exists(image_input):
                raise ValueError(f"Image path does not exist: {image_input}")
            with Image.open(image_input) as pil_img:
                pil_img = ImageOps.exif_transpose(pil_img)
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")
                arr = np.array(pil_img)
            return arr.astype(np.uint8)

        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Failed to decode image input: {str(e)}") from e


def extract_video_frame_iterator(
    video_source: Union[str, bytes],
    max_frames: int = 450
) -> Generator[np.ndarray, None, None]:
    """
    Decodes video frames from a file path or in-memory byte buffer.
    Yields standardized RGB uint8 frames sequentially.

    Args:
        video_source: File path string or raw video bytes.
        max_frames: Maximum number of frames to yield (prevents unbounded memory consumption).

    Yields:
        np.ndarray: Sequential video frame of shape (H, W, 3) in RGB format.
    """
    temp_file_path = None
    try:
        if isinstance(video_source, bytes):
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
                tf.write(video_source)
                temp_file_path = tf.name
            target_path = temp_file_path
        else:
            target_path = video_source

        cap = cv2.VideoCapture(target_path)
        if not cap.isOpened():
            raise ValueError(f"Unable to open video stream from source: {target_path}")

        frame_count = 0
        while cap.isOpened() and frame_count < max_frames:
            ret, frame = cap.read()
            if not ret or frame is None or frame.size == 0:
                break

            # Convert OpenCV default BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yield rgb_frame
            frame_count += 1

        cap.release()

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass


def draw_lane_overlay(
    frame: np.ndarray,
    left_fit: Optional[np.ndarray],
    right_fit: Optional[np.ndarray],
    telemetry: Optional[Dict[str, Any]] = None,
    corridor_alpha: float = 0.32
) -> np.ndarray:
    """
    Renders the Augmented Reality (AR) driving corridor, anti-aliased lane boundaries,
    and on-screen Heads-Up Display (HUD) telemetry overlay directly onto the road frame.

    Args:
        frame: Original RGB video frame array of shape (H, W, 3).
        left_fit: 2nd-order polynomial coefficients [a, b, c] for left lane in camera perspective.
        right_fit: 2nd-order polynomial coefficients [a, b, c] for right lane in camera perspective.
        telemetry: Optional dict containing offset, curvature, status, and departure warnings.
        corridor_alpha: Opacity factor for the green driving corridor mesh (0.1 to 0.6).

    Returns:
        np.ndarray: Annotated RGB frame copy.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Cannot render overlay on an empty or None frame.")

    canvas = frame.copy()
    height, width = canvas.shape[:2]

    # Resolve Horizon line
    horizon_y = int(height * 0.55)
    if telemetry is not None and "horizon_y" in telemetry:
        horizon_y = int(telemetry["horizon_y"])

    # -------------------------------------------------------------------------
    # 1. Project Drivable Corridor Mesh & Boundary Curves Directly on Road Plane
    # -------------------------------------------------------------------------
    if left_fit is not None and right_fit is not None:
        try:
            plot_y = np.linspace(horizon_y, height - 1, num=50)
            left_fitx = left_fit[0] * plot_y**2 + left_fit[1] * plot_y + left_fit[2]
            right_fitx = right_fit[0] * plot_y**2 + right_fit[1] * plot_y + right_fit[2]

            # Construct polygon mesh
            pts_left = np.array([np.transpose(np.vstack([left_fitx, plot_y]))])
            pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, plot_y])))])
            pts = np.hstack((pts_left, pts_right))

            # Render semi-transparent neon green driving mesh
            overlay = canvas.copy()
            cv2.fillPoly(overlay, np.int_([pts]), COLOR_CORRIDOR)
            canvas = cv2.addWeighted(overlay, corridor_alpha, canvas, 1.0 - corridor_alpha, 0)

            stroke_w = max(3, int(width * 0.005))

            # Left Lane in Electric Blue
            pts_left_line = np.int32(np.column_stack((left_fitx, plot_y)))
            cv2.polylines(canvas, [pts_left_line], isClosed=False, color=COLOR_LEFT_LANE, thickness=stroke_w, lineType=cv2.LINE_AA)

            # Right Lane in Bright Amber
            pts_right_line = np.int32(np.column_stack((right_fitx, plot_y)))
            cv2.polylines(canvas, [pts_right_line], isClosed=False, color=COLOR_RIGHT_LANE, thickness=stroke_w, lineType=cv2.LINE_AA)

            # Center Trajectory Guide in Cyan
            center_fitx = (left_fitx + right_fitx) / 2.0
            pts_center = np.int32(np.column_stack((center_fitx, plot_y)))
            cv2.polylines(canvas, [pts_center], isClosed=False, color=COLOR_CENTER_LINE, thickness=max(2, stroke_w // 2), lineType=cv2.LINE_AA)

        except Exception:
            pass

    # -------------------------------------------------------------------------
    # 2. Heads-Up Display (HUD) Cockpit Telemetry Box
    # -------------------------------------------------------------------------
    if telemetry is not None:
        offset_m = float(telemetry.get("lateral_offset_m", 0.0))
        curvature_m = float(telemetry.get("curvature_radius_m", 2500.0))
        is_departure = bool(telemetry.get("departure_warning", False))
        status = str(telemetry.get("status", "LOCKED"))

        hud_w = max(180, min(360, int(width * 0.35)))
        hud_h = max(70, min(105, int(height * 0.18)))
        hud_overlay = canvas.copy()
        cv2.rectangle(hud_overlay, (12, 12), (12 + hud_w, 12 + hud_h), COLOR_HUD_BG, -1)
        canvas = cv2.addWeighted(hud_overlay, 0.75, canvas, 0.25, 0)
        cv2.rectangle(canvas, (12, 12), (12 + hud_w, 12 + hud_h), (51, 65, 85), 1, cv2.LINE_AA)

        font_scale = max(0.40, min(0.55, width / 2000.0))
        font = cv2.FONT_HERSHEY_SIMPLEX
        offset_side = "LEFT" if offset_m < -0.01 else "RIGHT" if offset_m > 0.01 else "CENTER"
        
        # Human-Readable Position
        if abs(offset_m) <= 0.12:
            pos_str = "Position: Centered in Lane"
        else:
            pos_str = f"Position: Drifting {offset_side} ({abs(offset_m):.2f}m)"

        # Human-Readable Road Shape (No confusing radius meters!)
        if curvature_m > 1800:
            road_str = "Road Ahead: Straight"
        elif curvature_m > 800:
            road_str = f"Road Ahead: Gentle Curve ({offset_side})"
        else:
            road_str = f"Road Ahead: Sharp Curve Ahead"

        y_pos_line = int(12 + hud_h * 0.30)
        y_road_line = int(12 + hud_h * 0.58)
        y_badge_top = int(12 + hud_h * 0.70)
        y_badge_bot = int(12 + hud_h * 0.94)

        cv2.putText(canvas, pos_str, (22, y_pos_line), font, font_scale, COLOR_TEXT_WHITE, 1, cv2.LINE_AA)
        cv2.putText(canvas, road_str, (22, y_road_line), font, font_scale, COLOR_TEXT_WHITE, 1, cv2.LINE_AA)

        badge_color = COLOR_WARNING_BADGE if is_departure else COLOR_NORMAL_BADGE
        badge_text = "STEERING ALERT: DEPARTURE!" if is_departure else "STATUS: SAFE IN LANE"
        cv2.rectangle(canvas, (22, y_badge_top), (22 + min(240, hud_w - 20), y_badge_bot), badge_color, -1)
        cv2.putText(canvas, badge_text, (28, int(y_badge_bot - 4)), font, font_scale * 0.82, COLOR_TEXT_WHITE, 1, cv2.LINE_AA)

    return canvas

    return canvas


def format_telemetry_csv(records: List[Dict[str, Any]]) -> str:
    """
    Serializes per-frame telemetry records into a standard RFC 4180 CSV string format
    for 1-click download in the web dashboard.
    """
    if not records:
        df = pd.DataFrame(
            columns=[
                "Frame #",
                "Timestamp (s)",
                "Status",
                "Lateral Offset (m)",
                "Offset Direction",
                "Curvature Radius (m)",
                "Departure Warning",
                "Inference Latency (ms)",
            ]
        )
        return df.to_csv(index=False)

    rows = []
    for r in records:
        f_id = r.get("frame_id", 0)
        ts = round(float(r.get("timestamp_s", 0.0)), 3)
        status = r.get("status", "LOCKED")
        offset = round(float(r.get("lateral_offset_m", 0.0)), 3)
        direction = "LEFT" if offset < -0.01 else "RIGHT" if offset > 0.01 else "CENTER"
        curv = round(float(r.get("curvature_radius_m", 2500.0)), 1)
        warn = "YES" if r.get("departure_warning", False) else "NO"
        latency = round(float(r.get("inference_time_ms", 0.0)), 1)

        rows.append(
            {
                "Frame #": f_id,
                "Timestamp (s)": ts,
                "Status": status,
                "Lateral Offset (m)": offset,
                "Offset Direction": direction,
                "Curvature Radius (m)": curv,
                "Departure Warning": warn,
                "Inference Latency (ms)": latency,
            }
        )

    df = pd.DataFrame(rows)
    return df.to_csv(index=False)
