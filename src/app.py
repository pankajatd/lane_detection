"""
Interactive Web Application & Autonomous Driving Telemetry Dashboard
Project: Real-Time Deep Learning Road Lane Detection System
Module: src/app.py

Features:
- Dual-panel multi-source media processing (Images & Real-time Video Streams).
- Preset autonomous driving scenarios (Highway Cruise, Curved Pass, Suburban Road).
- Live HUD overlay rendering (AR green drivable corridor, Electric Blue & Amber lines).
- Real-time ADAS telemetry cards: Lateral Offset, Road Curvature, LDW Alert badge.
- Interactive video frame streamer with memory-safe generator decoding.
- 1-Click CSV telemetry export for automotive log analysis.
"""

import os
import sys
import io
import time
from pathlib import Path
from typing import List, Dict, Any, Generator
import numpy as np
import cv2
from PIL import Image
import streamlit as st

# Ensure project root and src directory are in sys.path regardless of execution directory
_file_dir = Path(__file__).resolve().parent
_root_dir = _file_dir.parent
for _p in [str(_root_dir), str(_file_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from src.detector import DeepLaneDetector
    from src.utils import (
        validate_media_input,
        load_and_validate_image,
        extract_video_frame_iterator,
        draw_lane_overlay,
        format_telemetry_csv
    )
except (ModuleNotFoundError, ImportError):
    from detector import DeepLaneDetector
    from utils import (
        validate_media_input,
        load_and_validate_image,
        extract_video_frame_iterator,
        draw_lane_overlay,
        format_telemetry_csv
    )


# =============================================================================
# Streamlit Application Configuration & Custom Styling
# =============================================================================
st.set_page_config(
    page_title="DeepLane AI | Autonomous Driving Telemetry",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Automotive Cockpit CSS Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.55rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .badge-locked {
        background-color: #065f46;
        color: #34d399;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-searching {
        background-color: #374151;
        color: #9ca3af;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-warning {
        background-color: #991b1b;
        color: #fca5a5;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-safe {
        background-color: #065f46;
        color: #6ee7b7;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Helper: Intuitive End-User Dashboard Metric Cards
# =============================================================================
def render_metric_cards(result: Dict[str, Any], col1, col2, col3, col4):
    """Renders human-friendly, plain-English automotive telemetry cards."""
    status = result.get("status", "LOCKED")
    offset = float(result.get("lateral_offset_m", 0.0))
    curv = float(result.get("curvature_radius_m", 2500.0))
    ldw = bool(result.get("departure_warning", False))

    # 1. Camera Tracking
    status_badge = (
        '<span class="badge-locked">🟢 LOCKED (Both Lane Lines Tracked)</span>'
        if status == "LOCKED"
        else '<span class="badge-searching">⚪ SEARCHING (Scanning Road / No Lines Found)</span>'
    )
    col1.markdown(f'<div class="metric-card"><div class="metric-title">Camera Tracking</div><div class="metric-value">{status_badge}</div></div>', unsafe_allow_html=True)

    # 2. Vehicle Position in Lane
    direction = "right" if offset > 0.01 else "left" if offset < -0.01 else "center"
    if abs(offset) <= 0.12:
        pos_html = f'<div class="metric-value" style="color:#34d399;">✅ Centered <div style="font-size:0.8rem;color:#94a3b8;font-weight:400;">({abs(offset):.2f}m {direction} of center)</div></div>'
    else:
        pos_html = f'<div class="metric-value" style="color:#f59e0b;">⚠️ Drifting {direction.upper()} <div style="font-size:0.8rem;color:#94a3b8;font-weight:400;">({abs(offset):.2f}m from center)</div></div>'
    col2.markdown(f'<div class="metric-card"><div class="metric-title">Vehicle Lane Position</div>{pos_html}</div>', unsafe_allow_html=True)

    # 3. Road Shape Ahead (Intuitive: Straight vs Curved, not confusing raw radius!)
    if curv > 1800:
        curv_html = '<div class="metric-value">🛣️ Straight Road <div style="font-size:0.8rem;color:#94a3b8;font-weight:400;">No curve ahead</div></div>'
    elif curv > 800:
        curv_html = f'<div class="metric-value">↪️ Gentle Curve <div style="font-size:0.8rem;color:#94a3b8;font-weight:400;">(Turning radius: {int(curv)}m)</div></div>'
    else:
        curv_html = f'<div class="metric-value" style="color:#ef4444;">⚠️ Sharp Turn <div style="font-size:0.8rem;color:#94a3b8;font-weight:400;">(Sharp curve: {int(curv)}m)</div></div>'
    col3.markdown(f'<div class="metric-card"><div class="metric-title">Road Shape Ahead</div>{curv_html}</div>', unsafe_allow_html=True)

    # 4. Driver Safety Alert
    if not ldw:
        ldw_html = '<div class="metric-value"><span class="badge-safe">✓ SAFE IN LANE</span></div>'
    else:
        ldw_html = '<div class="metric-value"><span class="badge-warning">🚨 DEPARTURE ALERT!</span></div>'
    col4.markdown(f'<div class="metric-card"><div class="metric-title">Driver Safety Alert</div>{ldw_html}</div>', unsafe_allow_html=True)


# =============================================================================
# Neural Model Loader & Real Preset Catalog
# =============================================================================
def get_detector(ema_alpha: float = 0.35, ldw_threshold_m: float = 0.25) -> DeepLaneDetector:
    """Initializes the DeepLaneDetector perception engine."""
    return DeepLaneDetector(device="cpu", ema_alpha=ema_alpha, ldw_threshold_m=ldw_threshold_m)


PRESET_SCENARIOS = {
    "🛣️ Highway Cruise (Straight Road)": {
        "video": str(_root_dir / "data" / "sample_presets" / "highway_straight.mp4"),
        "image": str(_root_dir / "data" / "sample_presets" / "highway_straight_1.jpg"),
        "description": "Real highway dashcam footage under clear daylight. Demonstrates steady lane keeping with vehicle centered (offset < 0.10m) and road curvature recognized as Straight (> 2500m).",
        "expected_curvature": "Straight (> 2500m)",
        "expected_offset": "Centered (~0.03m)",
        "expected_ldw": "✓ SAFE LANE (Normal)"
    },
    "🔄 Curved Canyon Pass (High Curvature)": {
        "video": str(_root_dir / "data" / "sample_presets" / "curved_canyon.mp4"),
        "image": str(_root_dir / "data" / "sample_presets" / "curved_canyon_1.jpg"),
        "description": "Real mountain highway dashcam navigating an aggressive sweeping road curve. Demonstrates polynomial spline bending to follow road curvature (< 500m radius).",
        "expected_curvature": "High Curvature (< 500m)",
        "expected_offset": "Dynamic curve tracking",
        "expected_ldw": "Dynamic Alert on curve drift"
    },
    "⚠️ Dynamic Lane Departure (Drift & Warning)": {
        "video": str(_root_dir / "data" / "sample_presets" / "lane_departure.mp4"),
        "image": str(_root_dir / "data" / "sample_presets" / "suburban_departure_1.jpg"),
        "description": "Real highway dashcam capturing the vehicle shifting lateral position toward lane line markings. Demonstrates automatic triggering of the Crimson Red LDW Departure Alert badge when |offset| > 0.25m.",
        "expected_curvature": "Gentle curve",
        "expected_offset": "Drifting (> 0.25m)",
        "expected_ldw": "⚠️ DEPARTURE ALERT (Active)"
    }
}


# =============================================================================
# Sidebar Controls & Scenario Configuration
# =============================================================================
with st.sidebar:
    st.markdown("### 🚘 Perception Settings")
    
    media_mode = st.radio(
        "Select Ingestion Source:",
        ["Preset Driving Demos", "Upload Custom Media"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 🎛️ Driver Assistance Settings")

    conf_thresh = st.slider(
        "🎯 Paint Detection Sensitivity (Lower = Faded Paint | Higher = Ignore Cracks)",
        min_value=0.10,
        max_value=0.90,
        value=0.40,
        step=0.05,
        help="Lower (0.20): Use for worn/faded paint lines. Higher (0.60): Use to ignore asphalt tar cracks and skid marks."
    )

    ema_smoothing = st.slider(
        "🛡️ Line Stability (Lower = Quick Steering | Higher = Anti-Shake on Bumps)",
        min_value=0.10,
        max_value=1.00,
        value=0.35,
        step=0.05,
        help="Higher (0.50): Smooths out shaky camera vibration on bumpy roads. Lower (0.20): Reacts instantly to sharp steering turns."
    )

    ldw_limit = st.slider(
        "🔔 Departure Warning Alarm (Strict: 0.15m | Normal: 0.25m | Relaxed: 0.40m)",
        min_value=0.10,
        max_value=0.50,
        value=0.25,
        step=0.05,
        help="Controls how close to the line you can drift before the red warning alarm triggers."
    )

    corridor_opacity = st.slider(
        "💡 Green Carpet Brightness (Adjust Visual Glow on Road)",
        min_value=0.10,
        max_value=0.60,
        value=0.28,
        step=0.02,
        help="Higher (0.50): Bright luminous green corridor. Lower (0.15): Subtle translucent overlay."
    )

    st.markdown("---")
    st.markdown("### ⚙️ Video Stream Tuning")
    max_frames_to_process = st.slider(
        "⏱️ Video Clip Length (Short 2s: 60 | Standard 4s: 120 | Long 10s: 300)",
        min_value=30,
        max_value=300,
        value=120,
        step=30
    )
    frame_step = st.slider(
        "⏩ Video Frame Speed (1 = Process Every Frame | 2 = Faster 2x Playback)",
        min_value=1,
        max_value=4,
        value=1,
        step=1
    )

    st.markdown("---")
    st.caption("Deep Learning ADAS Engine • PyTorch CPU • OpenCV 4.9+")


# =============================================================================
# Main Application Dashboard
# =============================================================================
st.title("🚗 Real-Time Deep Learning Road Lane Detection")
st.markdown(
    "Automated deep convolutional lane boundary segmentation, 2nd-order polynomial curve fitting, "
    "and **Automotive Lane Departure Warning (LDW)** telemetry."
)

# Initialize Detector
detector = get_detector(ema_alpha=ema_smoothing, ldw_threshold_m=ldw_limit)
detector.ema_alpha = ema_smoothing
detector.ldw_threshold_m = ldw_limit


# =============================================================================
# Media Handling Logic
# =============================================================================
if media_mode == "Preset Driving Demos":
    preset_choice = st.selectbox(
        "Choose Driving Scenario:",
        list(PRESET_SCENARIOS.keys())
    )

    scenario_info = PRESET_SCENARIOS[preset_choice]

    # Informative Scenario Badge
    st.info(
        f"**Scenario Context:** {scenario_info['description']}\n\n"
        f"• **Expected Curvature:** `{scenario_info['expected_curvature']}`  \n"
        f"• **Expected Lateral Drift:** `{scenario_info['expected_offset']}`  \n"
        f"• **ADAS Departure Warning:** `{scenario_info['expected_ldw']}`"
    )

    test_type = st.radio(
        "Select Demo Format:",
        ["🎥 Stream Real Dashcam Video", "📸 Inspect Single HD Road Photo"],
        horizontal=True
    )

    if test_type == "📸 Inspect Single HD Road Photo":
        img_path = scenario_info["image"]
        if os.path.exists(img_path):
            detector.reset()
            raw_img = load_and_validate_image(img_path)
            with st.spinner("Analyzing real road geometry..."):
                result = detector.process_frame(raw_img, conf_threshold=conf_thresh)
                annotated_img = draw_lane_overlay(
                    frame=raw_img,
                    left_fit=result["left_fit"],
                    right_fit=result["right_fit"],
                    telemetry=result,
                    corridor_alpha=corridor_opacity
                )

            # Metric Cards
            k1, k2, k3, k4 = st.columns(4)
            render_metric_cards(result, k1, k2, k3, k4)

            # Side-by-Side Comparison
            col_left, col_right = st.columns(2)
            with col_left:
                st.image(raw_img, caption="Original Real Dashcam Road Scene", channels="RGB", use_container_width=True)
            with col_right:
                st.image(annotated_img, caption="AR Drivable Corridor & HUD Overlay", channels="RGB", use_container_width=True)

            csv_single = format_telemetry_csv([result])
            st.download_button("📥 Download Frame Telemetry (CSV)", data=csv_single, file_name="real_road_frame_telemetry.csv", mime="text/csv")
        else:
            st.error(f"Sample road image not found at: {img_path}")

    else:
        # Stream Real Dashcam Video
        run_video_demo = st.button("▶️ Play Real Dashcam Video Stream", type="primary")
        video_file_path = scenario_info["video"]

        if run_video_demo:
            if not os.path.exists(video_file_path):
                st.error(f"Sample video clip not found at: {video_file_path}")
            else:
                st.markdown("#### 📺 Real Dashcam Video Stream (720p HD)")

                # Telemetry KPI metric placeholders
                kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
                status_box = kpi_col1.empty()
                offset_box = kpi_col2.empty()
                curv_box = kpi_col3.empty()
                ldw_box = kpi_col4.empty()

                video_placeholder = st.empty()
                progress_bar = st.progress(0.0)

                telemetry_history: List[Dict[str, Any]] = []

                frame_idx = 0
                frame_gen = extract_video_frame_iterator(video_file_path, max_frames=max_frames_to_process)

                for raw_frame in frame_gen:
                    frame_idx += 1
                    if frame_idx % frame_step != 0:
                        continue

                    # Process frame through Deep Learning perception pipeline
                    result = detector.process_frame(raw_frame, conf_threshold=conf_thresh)
                    result["frame_id"] = frame_idx
                    result["timestamp_s"] = frame_idx / 25.0
                    telemetry_history.append(result)

                    # Render AR Overlay & HUD
                    annotated_frame = draw_lane_overlay(
                        frame=raw_frame,
                        left_fit=result["left_fit"],
                        right_fit=result["right_fit"],
                        telemetry=result,
                        corridor_alpha=corridor_opacity
                    )

                    # Update KPI Cards
                    render_metric_cards(result, status_box, offset_box, curv_box, ldw_box)

                    # Stream annotated frame
                    video_placeholder.image(annotated_frame, channels="RGB", use_container_width=True)
                    progress_bar.progress(min(1.0, frame_idx / max_frames_to_process))
                    time.sleep(0.01)

                progress_bar.empty()
                st.success(f"✓ Driving scenario completed: Processed {len(telemetry_history)} real dashcam frames.")

                # Telemetry Download Section
                st.markdown("---")
                st.subheader("📊 Driving Telemetry Analytics & Export")
                csv_data = format_telemetry_csv(telemetry_history)

                col_dl, col_summary = st.columns([1, 2])
                with col_dl:
                    st.download_button(
                        label="📥 Download Telemetry Log (CSV)",
                        data=csv_data,
                        file_name="driving_telemetry_log.csv",
                        mime="text/csv",
                        type="primary"
                    )

                with col_summary:
                    avg_offset = np.mean([abs(r["lateral_offset_m"]) for r in telemetry_history])
                    alert_count = sum(1 for r in telemetry_history if r["departure_warning"])
                    avg_latency = np.mean([r["inference_time_ms"] for r in telemetry_history])
                    st.info(f"**Trip Summary:** Mean Offset: `{avg_offset:.2f}m` | Warnings Triggered: `{alert_count}` | Avg Inference Latency: `{avg_latency:.1f}ms`")

else:
    # Custom File Upload Mode
    st.markdown("#### 📁 Upload Driving Media")
    uploaded_file = st.file_uploader(
        "Upload a road image (.jpg, .png) or video (.mp4, .avi):",
        type=["jpg", "jpeg", "png", "mp4", "avi", "mov"]
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        is_valid, media_type, msg = validate_media_input(file_bytes, uploaded_file.name)

        if not is_valid:
            st.error(f"❌ Validation Error: {msg}")
        else:
            st.success(f"✓ {msg}")

            # -------------------------------------------------------------
            # Single Image Processing
            # -------------------------------------------------------------
            if media_type == "image":
                detector.reset()
                raw_image = load_and_validate_image(file_bytes)
                with st.spinner("Analyzing road geometry..."):
                    result = detector.process_frame(raw_image, conf_threshold=conf_thresh)
                    annotated_img = draw_lane_overlay(
                        frame=raw_image,
                        left_fit=result["left_fit"],
                        right_fit=result["right_fit"],
                        telemetry=result,
                        corridor_alpha=corridor_opacity
                    )

                # Metrics Row
                k1, k2, k3, k4 = st.columns(4)
                render_metric_cards(result, k1, k2, k3, k4)

                # Side-by-side view
                col_left, col_right = st.columns(2)
                with col_left:
                    st.image(raw_image, caption="Original Road Input", channels="RGB", use_container_width=True)
                with col_right:
                    st.image(annotated_img, caption="AR Drivable Corridor & HUD", channels="RGB", use_container_width=True)

                # CSV Download for single frame
                csv_data = format_telemetry_csv([result])
                st.download_button("📥 Download Frame Telemetry (CSV)", data=csv_data, file_name="image_telemetry.csv", mime="text/csv")

            # -------------------------------------------------------------
            # Video Stream Processing
            # -------------------------------------------------------------
            elif media_type == "video":
                start_video = st.button("▶️ Process Video Stream", type="primary")
                if start_video:
                    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
                    status_box = kpi_col1.empty()
                    offset_box = kpi_col2.empty()
                    curv_box = kpi_col3.empty()
                    ldw_box = kpi_col4.empty()

                    video_placeholder = st.empty()
                    progress_bar = st.progress(0.0)
                    telemetry_history: List[Dict[str, Any]] = []

                    frame_idx = 0
                    frame_gen = extract_video_frame_iterator(file_bytes, max_frames=max_frames_to_process)

                    for raw_frame in frame_gen:
                        frame_idx += 1
                        if frame_idx % frame_step != 0:
                            continue

                        result = detector.process_frame(raw_frame, conf_threshold=conf_thresh)
                        result["frame_id"] = frame_idx
                        result["timestamp_s"] = frame_idx / 30.0
                        telemetry_history.append(result)

                        annotated_frame = draw_lane_overlay(
                            frame=raw_frame,
                            left_fit=result["left_fit"],
                            right_fit=result["right_fit"],
                            telemetry=result,
                            corridor_alpha=corridor_opacity
                        )

                        # Update HUD KPIs
                        render_metric_cards(result, status_box, offset_box, curv_box, ldw_box)

                        video_placeholder.image(annotated_frame, channels="RGB", use_container_width=True)
                        progress_bar.progress(min(1.0, frame_idx / max_frames_to_process))

                    progress_bar.empty()
                    st.success(f"✓ Video processing complete: Processed {len(telemetry_history)} frames.")

                    csv_data = format_telemetry_csv(telemetry_history)
                    st.download_button(
                        label="📥 Download Video Telemetry Log (CSV)",
                        data=csv_data,
                        file_name="video_telemetry_log.csv",
                        mime="text/csv",
                        type="primary"
                    )
