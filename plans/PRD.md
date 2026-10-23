# Product Requirements Document (PRD)
## Real-Time Deep Learning Road Lane Detection & Autonomous Driving Telemetry System

**Document Version:** 1.0.0  
**Phase:** Phase 1 — Product Manager Agent  
**Framework:** 7-Agent SDLC Governance (Referenced from `C:\Pankaja\MASTER_SDLC_AGENTS\`)  
**Project Location:** `C:\Pankaja\AUTOMATED_SDLC_AGENT_PROJECTS\lane_detection\`  
**Target Milestone:** Human-in-the-Loop (HITL) Gate 1 Approval  

---

## 1. Executive Summary & Product Vision

### 1.1 Product Mission
The **Real-Time Deep Learning Road Lane Detection System** is an enterprise-grade automotive perception platform designed to detect, track, and mathematically model road lane boundaries in real time from dashcam and front-facing vehicle camera feeds. 

By employing deep neural network feature representation combined with polynomial geometric curve fitting, the system provides autonomous driving capabilities including **Lane Keep Assist (LKA)**, **Lane Departure Warning (LDW)**, and **Vehicle Centering Telemetry** on commodity x86 CPUs with zero GPU hardware dependencies.

### 1.2 The Problem
Traditional computer vision approaches (such as basic Canny edge detectors and Hough line transforms) are brittle in real-world driving environments. They frequently fail when:
* Road paint markings are faded, worn out, or partially broken.
* Overcast weather, tree shadows, or asphalt repaving seams create false edges.
* Sharp curved roads and highway off-ramps invalidate linear ($y = mx + b$) assumptions.
* Direct sunlight glare bleaches out contrast between asphalt and paint stripes.

### 1.3 The Solution
A robust **Deep Learning Lane Perception Engine** that learns holistic spatial context from large-scale driving datasets (such as TuSimple / BDD100K). The deep neural network identifies continuous lane topology even across broken lines and shadow occlusions, outputting mathematically modeled second-degree polynomial curves ($x = ay^2 + by + c$) to provide smooth driving corridor overlays and precise vehicle offset telemetry.

---

## 2. Target User Personas & Use Cases

| Persona | Role | Primary Objective |
| :--- | :--- | :--- |
| **Autonomous Vehicle (AV) Engineer** | ADAS Perception Researcher | Evaluates deep learning lane tracking accuracy across diverse highway and urban driving footage. |
| **Fleet Safety Manager** | Telematics Operations Lead | Monitors driver lane discipline and analyzes historical lane departure telemetry logs to improve safety. |
| **Edge AI Deployment Engineer** | Embedded Systems Architect | Verifies that deep neural network inference runs efficiently on standard x86 CPU hardware without thermal throttling. |

---

## 3. Functional Requirements (FRs)

### 3.1 FR-1: Multi-Source Media Ingestion
* **FR-1.1:** The system shall ingest driving video files (`.mp4`, `.avi`, `.mov`) up to 50MB.
* **FR-1.2:** The system shall support single driving scene images (`.jpg`, `.jpeg`, `.png`, `.webp`) for frame-by-frame diagnostic inspection.
* **FR-1.3:** The system shall provide built-in **Preset Benchmark Driving Demos** (e.g., straight highway cruise, curved road transition, sunlit road) for instant 1-click evaluation without requiring user uploads.

### 3.2 FR-2: Deep Learning Lane Perception & Segmentation
* **FR-2.1:** The system shall utilize a deep convolutional neural network backbone to predict pixel-level lane probability representations for both the **Left Ego-Lane** and **Right Ego-Lane**.
* **FR-2.2:** The deep learning model shall maintain continuous lane tracking across dashed/dotted road stripes without flickering or frame dropouts.
* **FR-2.3:** The neural engine shall remain resilient against asphalt grain noise, tree shadows, and road surface variations.

### 3.3 FR-3: Polynomial Curve Modeling & Geometry
* **FR-3.1:** The system shall fit second-order polynomial mathematical curves ($x = ay^2 + by + c$) to detected lane pixels, accurately capturing both straight roads and curved highway bends.
* **FR-3.2:** The system shall calculate the mathematical **Lane Center** line at the vehicle's forward trajectory horizon.

### 3.4 FR-4: Real-Time Autonomous Driving Telemetry & Lane Departure Warning (LDW)
* **FR-4.1:** The system shall compute the **Vehicle Lateral Offset**:
  $$\text{Offset} = \text{Lane Center} - \text{Vehicle Center}$$
  assuming the camera is mounted along the vehicle's central longitudinal axis.
* **FR-4.2:** The system shall issue a visual **Lane Departure Warning (LDW)** alert whenever the vehicle drifts more than a configurable threshold (e.g., $> 0.25\text{ meters}$) from the lane center.
* **FR-4.3:** The system shall calculate estimated **Road Curvature Radius (meters)** to indicate whether the vehicle is traveling straight or navigating a left/right curve.

### 3.5 FR-5: Interactive Presentation Dashboard (Streamlit)
* **FR-5.1:** A wide-screen, synchronized side-by-side or augmented HUD visualization:
  - Original road camera feed.
  - Augmented augmented reality (AR) driving corridor showing a semi-transparent green lane path and highlighted lane boundaries.
* **FR-5.2:** Granular sidebar controls:
  - Deep learning confidence threshold slider (`0.05` to `0.95`).
  - Polynomial smoothing window slider (for temporal anti-flicker stability).
  - Visual overlay customization (lane color, corridor opacity, boundary line thickness).
* **FR-5.3:** Live KPI metric cards:
  - Tracking Status (`LOCKED` / `SEARCHING`).
  - Lateral Offset ($cm$ or $m$).
  - Lane Curvature Radius ($m$).
  - Frame Inference Latency ($ms$) and Real-Time FPS.

### 3.6 FR-6: Telemetry Data Export
* **FR-6.1:** 1-click download of annotated output frames or processed video clips.
* **FR-6.2:** 1-click download of frame-by-frame telemetry logs in standardized RFC 4180 CSV format (Frame Number, Timestamp, Left Lane Position, Right Lane Position, Vehicle Offset, Curvature, and Departure Warning Flag).

---

## 4. Non-Functional Requirements (NFRs)

* **NFR-1 (Performance & CPU Latency):** Deep learning inference and post-processing shall execute in under **100ms per frame** on modern commodity x86 CPUs (enabling real-time user dashboard responsiveness).
* **NFR-2 (Memory & Stability):** Memory footprint shall remain bounded below 1.5 GB RAM during continuous video processing. Zero memory leaks across extended playback.
* **NFR-3 (Defensive Security & Input Validation):** All user video/image uploads shall undergo strict MIME validation, decompression bomb safeguards, and exception handling.
* **NFR-4 (Portability & Containerization):** The entire application shall be 100% containerized via `Dockerfile` and `docker-compose.yml`, runnable on any Windows, macOS, or Linux host with a single command.
* **NFR-5 (Testability):** The codebase shall achieve 100% passing automated test coverage (PyTest unit and integration suites) before production release.

---

## 5. Visual Standards & HUD Telemetry Contract

| Visual Element | Specification | Visual Representation |
| :--- | :--- | :--- |
| **Left Lane Boundary** | Solid or extrapolated line | **Electric Blue** `RGB(0, 150, 255)` |
| **Right Lane Boundary** | Solid or extrapolated line | **Bright Amber** `RGB(255, 191, 0)` |
| **Drivable Corridor Polygon** | Semi-transparent filled mesh | **Neon Green** `RGBA(0, 255, 128, 0.25)` |
| **Lane Center Trajectory** | Dashed trajectory guide | **Cyan** `RGB(0, 255, 255)` |
| **Safe Centered Status** | Vehicle offset $\le 0.25\text{m}$ | **Green Badge:** `NORMAL (CENTERED)` |
| **Lane Departure Alert** | Vehicle offset $> 0.25\text{m}$ | **Red Pulsing Badge:** `⚠️ WARNING: LANE DEPARTURE` |

---

## 6. Definition of Done (DoD) for Gate 1 Approval

This Product Requirements Document is complete when:
1. Product scope, functional requirements, and non-functional requirements are explicitly defined.
2. The Deep Learning lane perception approach is formally established.
3. Autonomous driving telemetry metrics (lateral offset, curvature, lane departure warning) are specified.
4. The user provides explicit Human-in-the-Loop (HITL) sign-off to proceed to Phase 2 (Technical Architect).

---

## 7. End-User Plain-English Terminology & Parameter Specifications

To ensure the final product is immediately understandable by non-technical drivers and end users (without requiring mathematical or calculus knowledge), all metrics and parameters follow these user-facing definitions:

### 7.1 Dashboard Metric Cards (Driver-Facing Display)

| Metric Card | Technical Variable | Plain-English Label | End-User Interpretation |
| :--- | :--- | :--- | :--- |
| **1. Camera Tracking** | `status` | **🟢 LOCKED (Both Lane Lines Tracked)** vs **⚪ SEARCHING (Scanning Road / No Lines Found)** | Confirms whether camera sees road markings clearly or if markings are obscured (snow, dirt, intersections). |
| **2. Vehicle Lane Position** | `lateral_offset_m` | **✅ Centered** vs **⚠️ Drifting Right/Left** | Tells the driver if the car is in the middle of the lane (`0.07m` = 2 inches off center = Centered). Flags drift when distance $> 0.12\text{m}$. |
| **3. Road Shape Ahead** | `curvature_radius_m` | **🛣️ Straight Road** vs **↪️ Gentle Curve** vs **⚠️ Sharp Turn** | Eliminates confusing radius numbers. Displays `Straight Road` when $R > 1800\text{m}$, `Gentle Curve` when $800 \le R \le 1800\text{m}$, and `Sharp Turn` when $R < 800\text{m}$. |
| **4. Driver Safety Alert** | `departure_warning` | **✓ SAFE IN LANE** vs **🚨 DEPARTURE ALERT!** | Green safety confirmation when driving inside lane; flashes bright red warning when car drifts over the line. |

### 7.2 Driver Assistance Control Settings (Sidebar Tuning with Bracketed Guidance)

| UI Label Displayed to End User | Technical Name | When to Adjust? |
| :--- | :--- | :--- |
| **🎯 Paint Detection Sensitivity (Lower = Faded Paint \| Higher = Ignore Cracks)** | `conf_threshold` | Slide **LEFT** for faded, worn-out road paint. Slide **RIGHT** if road has asphalt tar cracks or skid marks. |
| **🛡️ Line Stability (Lower = Quick Steering \| Higher = Anti-Shake on Bumps)** | `ema_smoothing` | Slide **RIGHT** on bumpy roads to stop lines from vibrating. Slide **LEFT** for faster response to quick swerves. |
| **🔔 Departure Warning Alarm (Strict: 0.15m \| Normal: 0.25m \| Relaxed: 0.40m)** | `ldw_threshold_m` | **0.15m (Strict)**: Narrow mountain road with no margin for error. **0.25m (Standard)**: Highway driving. **0.40m (Relaxed)**: Wide lanes. |
| **💡 Green Carpet Brightness (Adjust Visual Glow on Road)** | `corridor_opacity` | Higher (0.50) for bright luminous green corridor; Lower (0.15) for subtle translucent overlay. |
| **⏱️ Video Clip Length (Short 2s: 60 \| Standard 4s: 120 \| Long 10s: 300)** | `max_frames` | Quick 2-second check (60 frames) vs Full trip review (120–300 frames). |
| **⏩ Video Frame Speed (1 = Process Every Frame \| 2 = Faster 2x Playback)** | `frame_step` | 1 = Highest precision on every frame; 2 = Twice as fast playback speed. |
