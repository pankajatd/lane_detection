# Technical Architecture Specification
## Project: Real-Time Deep Learning Road Lane Detection System (`lane_detection`)
**Author:** Technical Architect Subagent  
**Status:** DRAFT FOR HITL GATE 2 REVIEW  
**Scope:** High-Level System Design & Technology Stack Selection  

---

## 1. System Overview & Architectural Approach
To satisfy the business and technical needs defined in `plans/PRD.md`, the system is architected as a **modular, client-server computer vision application** divided into two primary high-level systems:

```
+-------------------------------------------------------------+
|                 PRESENTATION LAYER (Web UI)                 |
|   - Handles user driving video & image uploads (.mp4, .jpg) |
|   - Provides interactive preset benchmark driving demos     |
|   - Provides sensitivity & smoothing sliders                |
|   - Displays real-time HUD metrics (Offset, Curvature, LDW) |
|   - Provides 1-click CSV telemetry and media downloads      |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|          AI & GEOMETRIC PERCEPTION ENGINE (Backend)         |
|   - Stage 1: Media Ingestion & Stream Normalization         |
|   - Stage 2: Deep Learning Lane Segmentation (PyTorch CNN)  |
|   - Stage 3: Polynomial Geometric Curve Fitting (x=ay²+by+c)|
|   - Stage 4: Vehicle Offset & Lane Departure Warning (LDW)  |
|   - Stage 5: Augmented Reality HUD Corridor Renderer        |
+-------------------------------------------------------------+
```

---

## 2. Technology Stack Selection & Rationale

| System Layer | Selected Technology | Architectural Rationale |
| :--- | :--- | :--- |
| **Core Runtime** | **Python 3.10+** | Industry standard for machine learning, computer vision, and rapid application development. |
| **Computer Vision Engine** | **OpenCV (Headless)** | Ultra-fast, CPU-optimized video container decoding, frame iteration, and image matrix processing without requiring a display server. |
| **AI Inference Engine** | **PyTorch (CPU-Optimized)** | Enterprise-standard deep learning framework providing efficient tensor operations, sub-100ms CPU inference, and seamless model execution. |
| **Deep Learning Architecture** | **Deep Convolutional Neural Network (CNN)** | High-accuracy lane segmentation model capable of capturing road context across faded paint markings, shadows, and highway curves. |
| **Geometric Modeling** | **NumPy Polynomial Fitting** | Mathematically models road curvature ($x = ay^2 + by + c$) and applies temporal Exponential Moving Average (EMA) smoothing across dashed lines. |
| **Web UI Framework** | **Streamlit** | Enables building clean, reactive dashboard interfaces with built-in support for video playback, parameter sliders, and telemetry metric cards. |
| **Automated Test Runner** | **Pytest** | Standard test runner for verifying video ingestion, tensor normalization, geometric calculations, and visualization accuracy. |
| **Containerization** | **Docker & Docker Compose** | Ensures reproducible, 1-command deployment across Windows, macOS, and Linux cloud environments. |

---

## 3. High-Level System Components & Boundaries

### Component A: Web Presentation Layer
* **Responsibility**: Manages all user-facing interactions and dashboard rendering.
* **Boundaries**: Strictly handles media uploads, preset demo selection, video playback, display of telemetry KPI cards (Lateral Offset, Curvature, Departure Alert), and CSV report downloads. Contains zero deep learning or mathematical regression algorithms.

### Component B: Deep Learning Lane Perception Engine (The Detective)
* **Responsibility**: Ingests normalized frame tensors and predicts pixel-level probability distributions for the left and right lane boundaries.
* **Boundaries**: Pure analytical neural inference engine. Operates independently of drawing routines or user interfaces so it can be evaluated, tested, or upgraded in isolation.

### Component C: Geometric Modeling & Telemetry Engine
* **Responsibility**: Converts neural point clouds into continuous mathematical second-degree polynomial curves ($x = ay^2 + by + c$), calculates vehicle lateral drift offset, estimates road curvature radius, and evaluates Lane Departure Warning (LDW) triggers.
* **Boundaries**: Pure mathematical engine. Consumes perception outputs and produces calibrated physical metrics (meters, centimeters).

### Component D: Annotation & Augmented HUD Engine (The Painter)
* **Responsibility**: Combines geometric lane curves with the original camera frame to project an augmented reality (AR) driving corridor onto the road.
* **Boundaries**: Renders color-coded overlays (**Electric Blue for Left Lane**, **Amber for Right Lane**, **Semi-transparent Neon Green for Drivable Corridor**) and dynamic status alerts (**NORMAL (CENTERED)** vs. **⚠️ WARNING: LANE DEPARTURE**).

---

## 4. Non-Functional System Attributes

* **Hardware Efficiency**: Architected to execute in sub-100ms per frame on standard multi-core consumer/server CPUs without requiring expensive dedicated GPUs.
* **Modularity (Detective vs. Painter)**: The perception engine is decoupled from the visualization engine, allowing independent automated testing and maintenance.
* **Temporal Stability**: Implements a temporal Exponential Moving Average (EMA) buffer to prevent visual line jitter and bridge dashed highway markings.
* **Clean Architecture & Isolation**: The internal development governance (`MASTER_SDLC_AGENTS`) is completely decoupled from the project repository, ensuring clean, customer-ready deliverables.
