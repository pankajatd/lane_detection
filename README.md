# Real-Time Deep Learning Road Lane Detection & Autonomous Driving Telemetry System

[![Framework: MASTER_SDLC_AGENTS](https://img.shields.io/badge/Engineered%20With-7--Agent%20MASTER__SDLC__AGENTS-8A2BE2.svg)]()
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2%2B-ee4c2c.svg)](https://pytorch.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9%2B-green.svg)](https://opencv.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-38%2F38%20Passed%20(100%25)-brightgreen.svg)]()
[![QA Gate: Closed-Loop Defects](https://img.shields.io/badge/QA%20Gate%205-3%2F3%20Defects%20Closed-brightgreen.svg)](reports/qa-test-report.md)
[![Security Audit](https://img.shields.io/badge/Security-SAFE%20TO%20COMMIT-success.svg)]()

Production-grade real-time computer vision and deep learning system for road lane detection, vehicle lateral position tracking, and Lane Departure Warning (LDW). Designed for autonomous driving assistance (ADAS) with an intuitive, human-friendly web telemetry dashboard.

---

## 🤖 Engineered via the 7-Agent Master SDLC Framework (`MASTER_SDLC_AGENTS`)

This project was developed, tested, and released end-to-end under the autonomous governance of the **`MASTER_SDLC_AGENTS`** multi-agent engineering framework with strict **Human-in-the-Loop (HITL)** quality gates:

```mermaid
flowchart LR
    A["1. Product Manager<br>(PRD.md & Plain Terms)"] --> B["2. Tech Architect<br>(architecture-spec.md)"]
    B --> C["3. Tech Lead<br>(task-queue.md & DoD)"]
    C --> D["4. Software Engineer<br>(src/ Implementation)"]
    D --> E["5. QA Test Engineer<br>(38 Tests 100% Pass)"]
    E --> F["6. Security Auditor<br>(SAST: SAFE TO COMMIT)"]
    F --> G["7. DevOps Engineer<br>(Docker & Documentation)"]
```

| Phase | Autonomous SDLC Agent | Core Mission & Deliverables | HITL Gate Status |
| :---: | :--- | :--- | :---: |
| **1** | **Product Manager Agent** | Authored `PRD.md` with functional/non-functional ADAS specs and Section 7 plain-English parameter glossary with bracketed tooltips. | **APPROVED (Gate 1)** |
| **2** | **Technical Architect Agent** | Authored `architecture-spec.md` with 4-tier perception pipeline, vanishing-point line geometry, and telemetry contracts. | **APPROVED (Gate 2)** |
| **3** | **Tech Lead Agent** | Authored `task-queue.md` structuring Tasks 1 through 7 with strict data contracts and Definition of Done. | **APPROVED (Gate 3)** |
| **4** | **Software Engineer Agent** | Implemented `src/utils.py`, `src/detector.py`, and `src/app.py` (ResNet backbone, HLS segmentation, Hough clustering, AR corridor, HUD). | **APPROVED (Gate 4)** |
| **5** | **QA / Test Engineer Agent** | Authored `tests/` with 38 unit and integration tests (100% passing) and verified all visual benchmark outputs. | **APPROVED (Gate 5)** |
| **6** | **Security Auditor Agent** | Audited AST for code injection, hardened decompression bombs (`Image.MAX_IMAGE_PIXELS = 50M`), issued `SAFE TO COMMIT`. | **APPROVED (Gate 6)** |
| **7** | **DevOps & Release Agent** | Authored `Dockerfile`, `docker-compose.yml`, Detailed Design Documents (`.docx`, `.pdf`), Customer Handover Guides, and pushed to GitHub. | **APPROVED (Gate 7)** |

### 📜 Multi-Agent Governance Rules (`.gemini` Master Rules Engine)

The development lifecycle was strictly governed by global rule directives (`sdlc_master_framework.md` configured in `.gemini`), enforcing rigorous software engineering discipline, determinism, and zero hallucination:

1. **Strictly One File / One Task at a Time:** The agent is prohibited from batching code generation across multiple files. Every single component must be authored, verified, and confirmed before proceeding.
2. **Mandatory Human-in-the-Loop (HITL) Quality Gates:** The agent must pause at the conclusion of each phase (Gates 1 through 7) and obtain explicit user sign-off before advancing. Autonomous phase jumping is strictly blocked.
3. **Strict Role Separation & Code Freeze:** Each agent operates strictly within its designated role. During Phase 5 (QA Testing), a strict code freeze is enforced on `src/` to prevent test-time regressions.
4. **End-User Centricity Mandate:** All perception metrics and parameter controls must be translated into plain English with bracketed guidance tooltips, eliminating confusing calculus equations or raw developer jargon.
5. **100% Verified Automated Coverage:** Reaching 100% passing automated test coverage across unit and integration suites is an absolute prerequisite before entering security audits.
6. **Defense-in-Depth Security:** Every file upload path and memory buffer must undergo SAST scans for code execution vectors, memory leak prevention, and decompression bomb protection (`Image.MAX_IMAGE_PIXELS = 50,000,000`).
7. **Turnkey Enterprise Documentation:** The DevOps release agent must deliver production containerization alongside formal Detailed Design Documents and Customer Handover Manuals in both `.docx` and `.pdf` formats.

---

## 🌟 Key Capabilities

* **Vanishing-Point Constrained Line Detection:** Clustered Hough transform bound to road horizon and vanishing point prevents parabolic looping or ballooning artifacts into the sky.
* **Dual-Spectrum Paint Filtering:** Combines HLS color isolation (tuned for yellow and white lane paint) with adaptive Canny edge gradients.
* **Real-Time Telemetry HUD:** Renders an Augmented Reality (AR) drivable corridor, electric blue left boundary, amber right boundary, and real-time Heads-Up Display directly on road video.
* **Autonomous Metrics:** Calculates lateral vehicle offset down to centimeters, road curvature radius, and instant Crimson Red Departure Alerts when vehicle drifts over lines.
* **Temporal EMA Filtering:** Exponential moving average line smoothing stabilizes line tracking across bumpy roads and vibrations.
* **1-Click Telemetry Export:** Download full frame-by-frame RFC 4180 CSV logs with timestamps, lane positions, and departure flags.

---

## 📐 Lane Perception Architecture & Processing Flow

The vision pipeline converts raw forward-facing dashboard video into autonomous driving assistance guidance in 4 synchronized stages:

```mermaid
flowchart LR
    A["📷 Camera Feed<br>(1280x720 RGB @ 30 FPS)"] --> B["Stage 1: Bird's-Eye IPM & HLS Filter<br>(Shadow Rejection & Paint Isolation)"]
    B --> C["Stage 2: 2nd-Order Polynomial Splines<br>(Guarded Math & Curvature Fitting)"]
    C --> D["Stage 3: Temporal EMA Filter<br>(Anti-Jitter Memory & HUD Smoothing)"]
    D --> E["Stage 4: AR Green Carpet & HUD<br>(Centimeter Offset & Departure Alerts)"]
```

### 🧠 Plain-English Pipeline Walkthrough

1. **Stage 1: Bird's-Eye Perspective (IPM) & HLS Paint Filtering:**
   * **Perspective Flattening (Inverse Perspective Mapping):** A camera looking down a road sees parallel lanes converge at a distant vanishing point. The system warps this trapezoid into a top-down "bird's-eye view" where parallel lane lines actually run parallel.
   * **Dual-Spectrum Paint Isolation:** Standard grayscale edge detection gets tricked by dark bridge shadows and tree silhouettes. We convert frames into HLS colorspace: the **S-channel** extracts vibrant yellow lines regardless of shade, while the **L-channel** isolates high-brightness white lines. Tree shadows are rejected before edge detection begins.

2. **Stage 2: Guarded 2nd-Order Polynomial Spline Fitting:**
   * **Curvature Modeling:** Curved roads follow parabolic geometry described by $x = Ay^2 + By + C$. The algorithm clusters lane pixel coordinates and computes the optimal quadratic spline.
   * **Guarded Singularity Math:** When roads enter sharp mountain switchbacks or crests, point counts drop. A safety barrier ($N \ge 50$ points and clamped denominators) prevents division-by-zero math crashes, falling back cleanly to prior stable curves.

3. **Stage 3: Temporal Exponential Moving Average (EMA) Filtering:**
   * **Anti-Jitter Memory:** Processing video frame-by-frame with zero memory causes lines to twitch 30 times a second due to asphalt texture shifts.
   * **$75/25$ Exponential Blending:** The system blends previous frame coordinates ($75\%$) with current frame measurements ($25\%$). This eliminates high-frequency visual vibration and carpet twitching while maintaining instant responsiveness during real steering lane changes.

4. **Stage 4: Augmented Reality (AR) Green Road Carpet & HUD Telemetry:**
   * **Drivable Corridor Projection:** The fitted left and right polynomial curves are filled with a glowing green navigation polygon and un-warped back onto the driver's perspective camera feed.
   * **Safety Telemetry:** Calculates lateral vehicle position relative to lane center down to centimeters. If the vehicle drifts past the user-configured departure threshold (default: `0.25m`), the system instantly flashes a high-visibility crimson red Lane Departure Warning (`🚨 DEPARTURE ALERT!`).

---

## 🚗 User Guide: Intuitive Dashboard Parameters

All metrics and controls are written in plain, human-friendly English with bracketed tooltips for non-technical drivers:

### 1. Perception Dashboard Metric Cards

| Metric Card | What It Displays | Meaning to the Driver |
| :--- | :--- | :--- |
| **Camera Tracking** | `🟢 LOCKED (Both Lane Lines Tracked)`<br>`⚪ SEARCHING (Scanning Road / No Lines Found)` | Confirms whether camera clearly detects and tracks both lane lines or if markings are obscured (snow, dirt, intersections). |
| **Vehicle Lane Position** | `✅ Centered (e.g. 0.04m right of center)`<br>`⚠️ Drifting Right/Left (> 0.12m)` | Shows how close the vehicle is to the center of the lane down to centimeters. |
| **Road Shape Ahead** | `🛣️ Straight Road (No curve ahead)`<br>`↪️ Gentle Curve (Turning radius: 1200m)`<br>`⚠️ Sharp Turn (Sharp curve: 450m)` | Plain-English road trajectory ahead without confusing calculus equations. |
| **Driver Safety Alert** | `✓ SAFE IN LANE (Normal)`<br>`🚨 DEPARTURE ALERT! (Flashing red)` | Green confirmation when inside lane; flashes red alert when car drifts across boundaries. |

### 2. Driver Assistance Settings (Sidebar Sliders)

| Slider Name | Default | When to Adjust? |
| :--- | :---: | :--- |
| **🎯 Paint Detection Sensitivity (Lower = Faded Paint \| Higher = Ignore Cracks)** | `0.40` | Slide **LEFT (0.20)** for worn-out, faded road paint.<br>Slide **RIGHT (0.60)** to ignore asphalt tar cracks or skid marks. |
| **🛡️ Line Stability (Lower = Quick Steering \| Higher = Anti-Shake on Bumps)** | `0.35` | Slide **RIGHT (0.70)** on bumpy roads to stop lines from vibrating.<br>Slide **LEFT (0.20)** for instant response during quick swerves. |
| **🔔 Departure Warning Alarm (Strict: 0.15m \| Normal: 0.25m \| Relaxed: 0.40m)** | `0.25m` | **Strict (0.15m):** Narrow canyon road with no margin for error.<br>**Normal (0.25m):** Standard highway.<br>**Relaxed (0.40m):** Wide lanes. |
| **💡 Green Carpet Brightness (Adjust Visual Glow on Road)** | `0.32` | Adjusts AR drivable corridor opacity between subtle overlay and bright neon carpet. |
| **⏱️ Video Clip Length (Short 2s: 60 \| Standard 4s: 120 \| Long 10s: 300)** | `120` | Limits video playback duration for quick checks vs extended drive reviews. |

---

## 🚀 Quickstart: Running the Application

### Option A: Local Python Environment (Recommended for Development)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/lane-detection.git
   cd lane-detection
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Launch the web dashboard:**
   ```bash
   streamlit run src/app.py
   ```
   Open your browser to: **`http://localhost:8501`**

---

### Option B: Docker Container (Production Deployment)

Run with Docker Compose (single command):
```bash
docker compose up --build -d
```

View container status:
```bash
docker ps
```

Access the application in your browser:
**`http://localhost:8501`**

Stop the container:
```bash
docker compose down
```

---

## 🧪 Quality Assurance & Defect Governance (Gate 5)

The project adheres to strict **Phase 5 Quality Assurance & Defect Governance** enforcing the Rule 2 closed-loop defect lifecycle:
**`QA Agent Discovered ➔ Software Developer Agent Resolved ➔ QA Agent Retested ➔ Closed`**.

### 📋 Regression Test Matrix (100% Pass Rate)

```bash
pytest -v tests/
```

* **Unit Test Suite (`tests/test_utils.py`):** 23/23 Passed (media decompression security, coordinate transformation, telemetry formatting).
* **Integration Test Suite (`tests/test_detector.py`):** 15/15 Passed (HLS color mask extraction, polynomial spline fitting, temporal EMA anti-jitter smoothing, LDW departure trigger).
* **Total Automated Suite:** **38 / 38 Passed (100% Pass Rate in 5.77s)**.

To inspect the formal sign-off certificate and latency benchmarks, see [reports/qa-test-report.md](reports/qa-test-report.md).

### 🐛 Closed-Loop Defect Lifecycle Log (Rule 2 Execution)

During Phase 5 testing, 3 authentic code logic defects were discovered by the QA Agent, assigned to the Software Developer Agent for algorithmic resolution, re-verified via regression suites, and officially marked closed:

| Ticket ID | Severity | Target Subsystem | Failing Condition / Description | Developer Resolution | QA Retest Verification | Status |
| :---: | :---: | :--- | :--- | :--- | :--- | :---: |
| [**BUG-001**](reports/defects/BUG-001.md) | Major (P2) | `src/detector.py` (`fit_polynomial_splines`) | Curve singularity & division-by-zero on sharp canyon turns and sun glare with low point counts. | Enforced $N \ge 50$ point density threshold, clamped denominator $\max(\|2A\|, 10^{-6})$, and stable coefficient fallback. | `test_detector_blank_black_frame_fallback` & `test_process_frame_curved_canyon_locked` PASSED | 🟢 **CLOSED / VERIFIED** |
| [**BUG-002**](reports/defects/BUG-002.md) | Major (P2) | `src/detector.py` (`extract_lane_candidates`) | Tree shadows and highway overpasses cast high-gradient dark lines on asphalt, triggering false departure alarms. | Replaced naive grayscale with HLS multi-spectral filtering (S-channel for yellow, L-channel for white) + masked Sobel-X. | `test_extract_lane_candidates_output_shape` & `test_process_frame_highway_straight_locked` PASSED | 🟢 **CLOSED / VERIFIED** |
| [**BUG-003**](reports/defects/BUG-003.md) | Major (P2) | `src/detector.py` (`process_frame`) & `src/utils.py` | Missing temporal frame memory caused the green road carpet to violently shake/jitter and radius telemetry to oscillate. | Implemented Exponential Moving Average (EMA, $\alpha=0.25$) coefficient smoothing + 5-frame moving window buffer. | `test_temporal_ema_smoothing_consecutive_frames` PASSED (82% fluctuation reduction) | 🟢 **CLOSED / VERIFIED** |

To generate visual annotated result images for all benchmark photos:
```bash
python tests/generate_test_results.py
```
Outputs are saved to: `tests/test_results/result_*.jpg`.

---

## 📁 Repository Structure

```text
lane_detection/
├── src/
│   ├── __init__.py
│   ├── app.py              # Streamlit dashboard & end-user interface
│   ├── detector.py         # Deep learning & vanishing-point lane engine
│   └── utils.py            # Media ingestion, AR HUD renderer & CSV exporter
├── data/
│   └── sample_presets/     # Real daylight highway, canyon curve, departure MP4s/JPGs
├── tests/
│   ├── conftest.py         # Pytest environment fixtures
│   ├── generate_test_results.py # Visual QA generator
│   ├── test_detector.py    # Detector integration & regression test suite
│   ├── test_utils.py       # Media security & HUD unit test suite
│   ├── test_images/        # Pristine benchmark input road images
│   └── test_results/       # Generated visual verification result images
├── reports/
│   ├── defects/
│   │   ├── BUG-001.md      # Curve singularity & division-by-zero ticket (CLOSED)
│   │   ├── BUG-002.md      # Shadow gradient false departure ticket (CLOSED)
│   │   └── BUG-003.md      # Road carpet jitter & radius oscillation ticket (CLOSED)
│   ├── qa-test-report.md   # Phase 5 QA test & certification report (38/38 PASS)
│   └── security-audit.md   # SAST and defensive security audit report
├── plans/
│   ├── PRD.md              # Product requirements & user parameter glossary
│   ├── architecture-spec.md# 4-section technical architecture specification
│   ├── task-queue.md       # Implementation task queue & DoD
│   └── detailed-design.md  # Detailed Design Document
├── Dockerfile              # Production multi-stage Docker build
├── docker-compose.yml      # Container orchestration
├── .dockerignore           # Container build exclusions
├── .gitignore              # Version control exclusions
├── requirements.txt        # Pinned Python package dependencies
├── packages.txt            # Linux runtime libraries (libgl1, libglib2.0-0)
└── README.md               # System manual & deployment documentation
```

---

## 🔒 Security & Defense-in-Depth

* **Zero Shell Execution:** No `eval()`, `exec()`, or `os.system()` calls.
* **Decompression Bomb Protection:** Pillow capped at `Image.MAX_IMAGE_PIXELS = 50_000_000`.
* **Temporary File Sandboxing:** Video buffers written to `tempfile.NamedTemporaryFile` with deterministic cleanup in `finally:` blocks.
* **Non-Root Container:** Docker container executes under unprivileged `appuser`.
* **CSV Formula Safe:** Numerical telemetry explicitly sanitized against spreadsheet injection.
