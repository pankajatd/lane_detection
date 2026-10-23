# Task Queue & Low-Level Technical Specifications
## Project: Real-Time Deep Learning Road Lane Detection System (`lane_detection`)
**Author:** Tech Lead Subagent (Phase 3)  
**Status:** DRAFT FOR HITL GATE 3 REVIEW  
**Input References:** `plans/PRD.md`, `plans/architecture-spec.md`  

---

## 1. Project File Layout & File Ownership Boundaries

To ensure clean, isolated development without file collisions or merge conflicts, the codebase is partitioned into distinct files:

```
lane_detection/
├── requirements.txt            <-- Package manifest (Task 1: Software Engineer)
├── packages.txt                <-- Linux system libraries for OpenCV (Task 1: Software Engineer)
├── src/
│   ├── utils.py                <-- Video frame ingestion, AR corridor & HUD painter (Task 2: Software Engineer)
│   ├── detector.py             <-- Deep learning lane segmentation & polynomial curve engine (Task 3: Software Engineer)
│   └── app.py                  <-- Streamlit interactive video & telemetry dashboard (Task 4: Software Engineer)
├── tests/
│   ├── test_images/            <-- Curated benchmark highway & curved road test scenes (Task 5: QA Engineer)
│   ├── conftest.py             <-- Root path resolution helper (Task 5: QA Engineer)
│   ├── test_utils.py           <-- Unit tests for frame processing & visual overlays (Task 5: QA Engineer)
│   └── test_detector.py        <-- Integration tests for neural lane inference & geometry (Task 5: QA Engineer)
├── reports/
│   └── security-audit.md       <-- Defensive vulnerability & SAST report (Task 6: Security Auditor)
├── Dockerfile                  <-- Production container definition (Task 7: DevOps Engineer)
├── docker-compose.yml          <-- Local container orchestration (Task 7: DevOps Engineer)
└── README.md                   <-- Complete user manual & execution guide (Task 7: DevOps Engineer)
```

---

## 2. Low-Level Function Contracts & Interfaces

The Software Engineer must implement these exact function contracts:

### 2.1 Utility & Annotation Engine (`src/utils.py`)
```python
def validate_media_input(file_bytes: bytes, filename: str) -> tuple[bool, str]:
    """Validates that uploaded bytes form a readable, non-corrupt image (.jpg, .png) or video (.mp4, .avi)."""

def extract_frame_iterator(video_path: str, max_frames: int = 300) -> Generator[np.ndarray, None, None]:
    """Decodes video stream and yields normalized RGB frames sequentially with shape (H, W, 3)."""

def draw_lane_overlay(
    frame: np.ndarray,
    left_fit: Optional[np.ndarray],
    right_fit: Optional[np.ndarray],
    telemetry: dict
) -> np.ndarray:
    """
    Renders visual HUD overlays onto the frame:
    - Fills drivable corridor between lane polynomials with semi-transparent Neon Green: RGBA(0, 255, 128, 0.25).
    - Draws Left Lane curve in Electric Blue: RGB(0, 150, 255).
    - Draws Right Lane curve in Bright Amber: RGB(255, 191, 0).
    - Renders telemetry badges: Lateral Offset (m), Curvature (m), and LDW Alert status.
    """

def format_telemetry_csv(records: list[dict]) -> str:
    """Serializes per-frame telemetry dictionaries into clean RFC 4180 CSV text for 1-click download."""
```

### 2.2 Core Deep Learning Detection & Geometric Engine (`src/detector.py`)
```python
class DeepLaneDetector:
    """Encapsulates PyTorch CNN lane segmentation and polynomial curve fitting."""

    def __init__(self, device: str = "cpu"):
        """Initializes model state and caches neural weights onto CPU."""

    def load_model(self) -> None:
        """Loads pretrained PyTorch lane segmentation weights into memory."""

    def predict_lane_mask(
        self,
        frame: np.ndarray,
        conf_threshold: float = 0.40
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Executes CNN inference on an RGB frame.
        Returns:
            tuple containing (left_lane_binary_mask, right_lane_binary_mask).
        """

    def fit_polynomial_splines(
        self,
        left_mask: np.ndarray,
        right_mask: np.ndarray
    ) -> tuple[Optional[np.ndarray], Optional[np.ndarray], dict]:
        """
        Fits 2nd-order polynomials: x(y) = a*y^2 + b*y + c for left and right lanes.
        Applies Exponential Moving Average (EMA) temporal smoothing.
        Computes:
            - Road Curvature Radius (meters)
            - Vehicle Lateral Offset (meters)
            - Lane Departure Warning (LDW) trigger (True if |offset| > 0.25m)
        """

    def process_frame(
        self,
        frame: np.ndarray,
        conf_threshold: float = 0.40
    ) -> dict:
        """
        Executes end-to-end perception pipeline on a single frame.
        Returns:
        {
            "status": "LOCKED" | "SEARCHING",
            "left_fit": np.ndarray or None,
            "right_fit": np.ndarray or None,
            "lateral_offset_m": float,
            "curvature_radius_m": float,
            "departure_warning": bool,
            "inference_time_ms": float
        }
        """
```

---

## 3. Atomic Task Queue for Developers

### Task 1: Package & Environment Manifests (`requirements.txt`, `packages.txt`)
* **Assigned Role**: Software Engineer
* **Target Files**: `requirements.txt`, `packages.txt`
* **Deliverable**:
  - `torch>=2.2.0` (with CPU extra-index-url)
  - `torchvision>=0.17.0`
  - `opencv-python-headless>=4.9.0`
  - `numpy<2.0.0`
  - `Pillow>=10.0.0`
  - `pandas>=2.0.0`
  - `streamlit>=1.35.0`
  - `pytest>=8.0.0`
  - Linux packages: `libgl1`, `libglib2.0-0`
* **Definition of Done**: Files created at project root; packages install cleanly without version conflicts.

---

### Task 2: Utility & Annotation Engine (`src/utils.py`)
* **Assigned Role**: Software Engineer
* **Target File**: `src/utils.py`
* **Deliverable**:
  - Media validation for videos (`.mp4`, `.avi`) and images (`.jpg`, `.png`).
  - OpenCV video frame generator with clean RGB normalization.
  - HUD overlay renderer: semi-transparent green driving corridor (`cv2.fillPoly`), Electric Blue left curve, Amber right curve, and dynamic warning text.
  - CSV telemetry serialization function.
* **Definition of Done**: Module passes syntax validation and successfully renders corridor overlay on a dummy test frame.

---

### Task 3: Core Deep Learning Detection & Geometric Engine (`src/detector.py`)
* **Assigned Role**: Software Engineer
* **Target File**: `src/detector.py`
* **Deliverable**:
  - `DeepLaneDetector` class with CPU model loading.
  - PyTorch neural lane segmentation mask extraction.
  - 2nd-order polynomial spline regression ($x = ay^2 + by + c$).
  - Temporal Exponential Moving Average (EMA) buffer over $N=10$ frames to eliminate line jitter across dashed markings.
  - Mathematical calculations for Road Curvature Radius ($m$) and Vehicle Lateral Offset ($m$).
* **Definition of Done**: Class executes `process_frame()` on a test highway frame in sub-100ms and returns structured telemetry dictionary.

---

### Task 4: Interactive Web Dashboard (`src/app.py`)
* **Assigned Role**: Software Engineer
* **Target File**: `src/app.py`
* **Deliverable**:
  - Clean wide-screen UI with custom CSS telemetry cards.
  - Sidebar source selector: "🚗 Preset Driving Demos" vs. "📁 Upload Driving Video/Image".
  - Interactive parameter sliders: "Detection Sensitivity" (0.10 to 0.90) and "Temporal Smoothing Window" (1 to 15 frames).
  - Synchronized video player rendering the augmented AR driving corridor.
  - Real-time KPI summary cards: Tracking Status (`LOCKED` / `DRIFT`), Lateral Offset ($cm$), Curvature ($m$), and Latency ($ms$).
  - 1-click download buttons for annotated frames and CSV telemetry logs.
* **Definition of Done**: Running `streamlit run src/app.py` launches a responsive dashboard in the browser without runtime errors.

---

### Task 5: Automated QA Test Suite & Test Images (`tests/`)
* **Assigned Role**: QA / Test Engineer
* **Target Files**: `tests/test_images/`, `tests/conftest.py`, `tests/test_utils.py`, `tests/test_detector.py`
* **Deliverable**:
  - Curate benchmark highway driving scenes (straight highway cruise, curved road transition).
  - Author unit tests in `tests/test_utils.py` (validation, video decoding, overlay rendering, CSV format).
  - Author integration tests in `tests/test_detector.py` (model loading, neural inference, polynomial fitting, EMA smoothing, offset calculation, error handling).
  - Minimum 20+ automated test cases.
* **Definition of Done**: Running `pytest -v tests/` in terminal passes 100% of tests.

---

### Task 6: Defensive Security & Vulnerability Audit (`reports/security-audit.md`)
* **Assigned Role**: Security Auditor
* **Target File**: `reports/security-audit.md`
* **Deliverable**:
  - Static code security analysis (SAST) on all `src/*.py` files.
  - Verification of video upload memory bounds and decompression bomb protections.
  - Memory leak check on PyTorch inference (`torch.no_grad()` active).
  - Issue formal security verdict: `SAFE TO COMMIT`.
* **Definition of Done**: Complete audit published to `reports/security-audit.md` with zero critical vulnerabilities.

---

### Task 7: DevOps Packaging & Deployment (`Dockerfile`, `docker-compose.yml`, `README.md`)
* **Assigned Role**: DevOps Engineer
* **Target Files**: `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.gitignore`, `README.md`
* **Deliverable**:
  - Lightweight CPU-optimized container (`python:3.10-slim`).
  - Docker Compose service definition with automated health checks on port 8501.
  - Complete user manual (`README.md`).
  - Detailed Design Document (`plans/detailed-design.md`, `.docx`, `.pdf`).
  - Customer Handover Guide and Docker Testing Manual (`.docx`, `.pdf`).
* **Definition of Done**: Container builds and launches with `docker compose up --build -d` and passes health check.

---

## 4. Execution Order & Dependencies

```
[ Task 1: requirements.txt & packages.txt ]
                      │
                      ▼
            [ Task 2: src/utils.py ]
                      │
                      ▼
           [ Task 3: src/detector.py ]
                      │
                      ▼
             [ Task 4: src/app.py ]
                      │
                      ▼
           [ Task 5: tests/ (QA Suite) ]
                      │
                      ▼
     [ Task 6: reports/security-audit.md ]
                      │
                      ▼
   [ Task 7: Dockerfile, compose, README.md ]
```
