"""
Comprehensive Document Generation and PDF Conversion Script
Generates:
1. plans/detailed-design.docx & .pdf
2. Deployment_and_Customer_Handover_Guide.docx & .pdf
3. Docker_Generation_and_Testing_Manual.docx & .pdf
Includes explicit governance attribution to MASTER_SDLC_AGENTS framework.
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import win32com.client
import pythoncom

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def style_table(table, col_widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        is_header = (i == 0)
        for j, cell in enumerate(row.cells):
            set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
            if is_header:
                set_cell_background(cell, "1E293B")
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.size = Pt(9.5)
            else:
                bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
                set_cell_background(cell, bg)
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9.0)
                        run.font.color.rgb = RGBColor(30, 41, 59)
            if col_widths and j < len(col_widths):
                cell.width = col_widths[j]

def convert_docx_to_pdf(docx_path, pdf_path):
    print(f"Converting {os.path.basename(docx_path)} -> {os.path.basename(pdf_path)}...")
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False
    try:
        doc = word.Documents.Open(os.path.abspath(docx_path))
        doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)
        doc.Close()
        print(f"Successfully generated: {pdf_path}")
    except Exception as e:
        print(f"Error converting to PDF: {e}")
        raise e
    finally:
        word.Quit()
        pythoncom.CoUninitialize()

# =============================================================================
# 1. Detailed Design Document (.docx & .pdf)
# =============================================================================
def build_detailed_design_doc(output_dir):
    docx_path = os.path.join(output_dir, "detailed-design.docx")
    pdf_path = os.path.join(output_dir, "detailed-design.pdf")
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    title = doc.add_paragraph()
    r_title = title.add_run("Detailed Design Document (DDD)")
    r_title.font.size = Pt(24)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    subtitle = doc.add_paragraph()
    r_sub = subtitle.add_run("Real-Time Deep Learning Road Lane Detection & Autonomous Driving Telemetry System")
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    meta = doc.add_paragraph()
    r_meta = meta.add_run("Framework: MASTER_SDLC_AGENTS | Version 1.0.0 | Phase 7: DevOps Release | Date: 2026-10-23")
    r_meta.font.size = Pt(9.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(100, 116, 139)
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 1. Executive Summary
    doc.add_heading("1. Executive Summary & Autonomous Governance", level=1)
    doc.add_paragraph(
        "The Real-Time Deep Learning Road Lane Detection System is an automotive-grade perception and telemetry "
        "engine engineered for Advanced Driver Assistance Systems (ADAS). Operating at 30+ FPS on commodity x86 "
        "CPUs without requiring GPU hardware, the system delivers real-time lane boundary tracking, vehicle lateral "
        "centering measurement, road curvature estimation, and instant Lane Departure Warnings (LDW)."
    )
    doc.add_paragraph(
        "Autonomous Governance via MASTER_SDLC_AGENTS Framework:\n"
        "This project was developed, tested, and released under the strict governance of the 7-Agent Master SDLC Framework "
        "(MASTER_SDLC_AGENTS) with Human-in-the-Loop (HITL) quality gates across all 7 lifecycle phases:\n"
        "• Phase 1 (Product Manager): Formulated PRD.md with plain-English terminology and bracketed tooltips.\n"
        "• Phase 2 (Technical Architect): Authored architecture-spec.md establishing 4-tier perception pipeline.\n"
        "• Phase 3 (Tech Lead): Authored task-queue.md defining modular tasks and Definition of Done.\n"
        "• Phase 4 (Software Engineer): Implemented src/utils.py, src/detector.py, and src/app.py.\n"
        "• Phase 5 (QA Test Engineer): Validated 38/38 passing unit and integration tests in tests/.\n"
        "• Phase 6 (Security Auditor): Conducted SAST static analysis and certified SAFE TO COMMIT.\n"
        "• Phase 7 (DevOps Engineer): Packaged production Docker container, manuals, and customer deliverables."
    )

    # 2. Detective vs Painter
    doc.add_heading("2. Architectural Pattern: Detective vs. Painter", level=1)
    doc.add_paragraph(
        "The application architecture strictly decouples mathematical perception from graphical presentation through "
        "the Detective vs. Painter design pattern:\n"
        "• The Detective (src/detector.py): Multi-spectrum HLS paint isolation (yellow/white), adaptive Canny edges, "
        "vanishing-point Hough line clustering, and temporal EMA smoothing.\n"
        "• The Painter (src/utils.py): Augmented reality neon-green drivable corridor, electric blue & amber lane lines, "
        "dynamically scaled HUD box, and RFC 4180 CSV export.\n"
        "• The Driver Console (src/app.py): Reactive Streamlit dashboard with bracketed driver guidance and live dashcam playback."
    )

    # 3. System Contracts
    doc.add_heading("3. System Contracts & Telemetry Schema", level=1)
    t1 = doc.add_table(rows=1, cols=4)
    t1.rows[0].cells[0].text = "Field Name"
    t1.rows[0].cells[1].text = "Data Type"
    t1.rows[0].cells[2].text = "Units / Range"
    t1.rows[0].cells[3].text = "Automotive Description"
    fields = [
        ("status", "string", "LOCKED | SEARCHING", "Camera tracking lock state on road lines"),
        ("left_fit", "np.ndarray", "[a, b, c]", "2nd-order polynomial fit for left lane boundary"),
        ("right_fit", "np.ndarray", "[a, b, c]", "2nd-order polynomial fit for right lane boundary"),
        ("lateral_offset_m", "float", "Meters (±m)", "Vehicle deviation from lane centerline (Positive = Right)"),
        ("curvature_radius_m", "float", "150m - 2500m", "Turning radius of the road curve ahead (> 1800m = Straight)"),
        ("departure_warning", "boolean", "True | False", "Active alarm when vehicle drifts beyond safety threshold"),
        ("inference_time_ms", "float", "Milliseconds", "End-to-end perception pipeline latency per frame"),
        ("horizon_y", "integer", "Pixels (Y)", "Calculated highway vanishing point horizon coordinate")
    ]
    for row in fields:
        r = t1.add_row()
        for idx, val in enumerate(row):
            r.cells[idx].text = val
    style_table(t1, [Inches(1.5), Inches(1.0), Inches(1.4), Inches(2.6)])
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 4. Plain English Glossary
    doc.add_heading("4. End-User Plain-English Parameter Specifications", level=1)
    t2 = doc.add_table(rows=1, cols=3)
    t2.rows[0].cells[0].text = "Metric Card"
    t2.rows[0].cells[1].text = "Plain-English Label"
    t2.rows[0].cells[2].text = "Driver-Facing Interpretation"
    metrics = [
        ("Camera Tracking", "🟢 LOCKED (Both Lane Lines Tracked)\n⚪ SEARCHING (Scanning Road / No Lines Found)", "Confirms camera sees road markings clearly or if markings are obscured (snow, dirt, intersections)."),
        ("Vehicle Lane Position", "✅ Centered (e.g. 0.04m right of center)\n⚠️ Drifting Right/Left (> 0.12m)", "Shows vehicle position relative to lane center in centimeters."),
        ("Road Shape Ahead", "🛣️ Straight Road (No curve ahead)\n↪️ Gentle Curve (Radius: 1200m)\n⚠️ Sharp Turn (Radius: 450m)", "Plain-English trajectory ahead without confusing calculus equations."),
        ("Driver Safety Alert", "✓ SAFE IN LANE (Normal)\n🚨 DEPARTURE ALERT! (Flashing red)", "Green confirmation when inside lane; flashes red alert when car drifts across boundaries.")
    ]
    for row in metrics:
        r = t2.add_row()
        for idx, val in enumerate(row):
            r.cells[idx].text = val
    style_table(t2, [Inches(1.6), Inches(2.5), Inches(2.4)])
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 5. ResNet vs MobileNet vs YOLO Deep Dive
    doc.add_heading("5. Comparative Architectural Guide: ResNet vs. MobileNet vs. YOLO", level=1)
    t4 = doc.add_table(rows=1, cols=4)
    t4.rows[0].cells[0].text = "Architectural Dimension"
    t4.rows[0].cells[1].text = "ResNet (18 / 34 / 50)"
    t4.rows[0].cells[2].text = "MobileNet (V2 / V3)"
    t4.rows[0].cells[3].text = "YOLO (v8 / v9 / v11)"
    comparison = [
        ("Vision Paradigm", "Residual skip backbones & segmentation", "Depthwise separable convolutions", "Single-stage bounding box regression"),
        ("Model Parameters", "11M - 25M parameters", "2.5M - 4.0M parameters", "3.0M - 20M parameters"),
        ("x86 CPU Latency", "25ms - 45ms per frame", "10ms - 20ms per frame", "35ms - 70ms per frame"),
        ("Edge / ARM Efficiency", "Moderate (Requires NPU / x86)", "Superior (Raspberry Pi, ARM, Drone)", "Good (Optimized for edge TensorRT)"),
        ("Lane Spline Suitability", "Superior (Preserves continuous edges)", "Moderate (Lower feature resolution)", "Sub-optimal (Designed for bounding boxes)"),
        ("RAM Consumption", "250MB - 400MB", "< 150MB", "300MB - 600MB")
    ]
    for row in comparison:
        r = t4.add_row()
        for idx, val in enumerate(row):
            r.cells[idx].text = val
    style_table(t4, [Inches(1.8), Inches(1.6), Inches(1.6), Inches(1.5)])
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 6. Edge Case Resolutions
    doc.add_heading("6. Real-World Edge-Case Resolutions & Lessons Learned", level=1)
    doc.add_paragraph(
        "1. Parabolic Spline Looping: Standard 2nd-order polynomial fits (x = ay^2 + by + c) generated parabolic loops "
        "into the sky on mountain curves. Resolved by implementing vanishing-point constrained line clustering with slope filtering.\n\n"
        "2. Docker Port 8501 Conflict: A lingering container occupied port 8501. Resolved by inspecting docker processes, "
        "terminating conflicting containers, and configuring clean host mappings in docker-compose.yml.\n\n"
        "3. Streamlit Stale Session Cache: Streamlit's @st.cache_resource held stateful detector instances across runs. "
        "Resolved by eliminating singleton caching and implementing detector.reset() for clean single-frame evaluation.\n\n"
        "4. Faded Paint and Tar Crack Rejection: Asphalt tar cracks caused false edge triggers. Resolved with dual-spectrum "
        "HLS yellow and white color segmentation combined with trapezoidal road horizon masking.\n\n"
        "5. Decompression Bomb Hardening: Image.MAX_IMAGE_PIXELS was capped at 50,000,000 pixels in src/utils.py."
    )

    doc.save(docx_path)
    print(f"Detailed Design Document (.docx) saved to: {docx_path}")
    convert_docx_to_pdf(docx_path, pdf_path)

# =============================================================================
# 2. Customer Handover Guide (.docx & .pdf)
# =============================================================================
def build_customer_handover_guide(project_root):
    docx_path = os.path.join(project_root, "Deployment_and_Customer_Handover_Guide.docx")
    pdf_path = os.path.join(project_root, "Deployment_and_Customer_Handover_Guide.pdf")
    doc = Document()

    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    title = doc.add_paragraph()
    r = title.add_run("Deployment & Customer Handover Guide")
    r.font.size = Pt(22)
    r.font.bold = True
    r.font.color.rgb = RGBColor(15, 23, 42)

    sub = doc.add_paragraph()
    r_sub = sub.add_run("Real-Time Deep Learning Road Lane Detection & Autonomous Driving Telemetry System")
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    meta = doc.add_paragraph()
    r_m = meta.add_run("Framework: MASTER_SDLC_AGENTS | Phase 7 Release | Date: 2026-10-23 | Status: Approved")
    r_m.font.size = Pt(9.5)
    r_m.font.italic = True
    r_m.font.color.rgb = RGBColor(100, 116, 139)
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    doc.add_heading("1. Executive Overview & Autonomous Framework Governance", level=1)
    doc.add_paragraph(
        "This deliverable was engineered under the autonomous governance of the MASTER_SDLC_AGENTS 7-Agent Framework. "
        "Every phase was strictly validated through Human-in-the-Loop gates, from Product Requirements Document (PRD) "
        "to full security audits and containerized release packaging."
    )

    doc.add_heading("2. Deployment Options", level=1)
    doc.add_paragraph(
        "Option A: Production Docker Container (Recommended)\n"
        "• Execute: docker compose up --build -d\n"
        "• Web URL: http://localhost:8501\n\n"
        "Option B: Local Python Virtual Environment\n"
        "• Setup: python -m venv venv && .\\venv\\Scripts\\activate && pip install -r requirements.txt\n"
        "• Launch: streamlit run src/app.py\n\n"
        "Option C: Cloud Deployment (Streamlit Community Cloud)\n"
        "• Ready to deploy with packages.txt (libgl1, libglib2.0-0) and requirements.txt."
    )

    doc.add_heading("3. End-User Operational Guide & Telemetry Cards", level=1)
    t1 = doc.add_table(rows=1, cols=3)
    t1.rows[0].cells[0].text = "Dashboard Indicator"
    t1.rows[0].cells[1].text = "State Displayed"
    t1.rows[0].cells[2].text = "Driver Action Required"
    ops = [
        ("Camera Tracking", "🟢 LOCKED (Both Lane Lines Tracked)\n⚪ SEARCHING (Scanning Road / No Lines Found)", "LOCKED: Normal operation.\nSEARCHING: Pay manual attention; lines obscured."),
        ("Vehicle Lane Position", "✅ Centered (within 0.12m)\n⚠️ Drifting Right/Left (> 0.12m)", "Steer slightly toward center if drifting badge appears."),
        ("Road Shape Ahead", "🛣️ Straight Road\n↪️ Gentle Curve\n⚠️ Sharp Turn", "Anticipate steering adjustments based on curve severity."),
        ("Driver Safety Alert", "✓ SAFE IN LANE (Normal)\n🚨 DEPARTURE ALERT! (Flashing red)", "Immediate correction required if Departure Alert triggers.")
    ]
    for row in ops:
        r = t1.add_row()
        for idx, val in enumerate(row):
            r.cells[idx].text = val
    style_table(t1, [Inches(1.8), Inches(2.5), Inches(2.2)])
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    doc.save(docx_path)
    print(f"Customer Handover Guide (.docx) saved to: {docx_path}")
    convert_docx_to_pdf(docx_path, pdf_path)

# =============================================================================
# 3. Docker Generation & Testing Manual (.docx & .pdf)
# =============================================================================
def build_docker_testing_manual(project_root):
    docx_path = os.path.join(project_root, "Docker_Generation_and_Testing_Manual.docx")
    pdf_path = os.path.join(project_root, "Docker_Generation_and_Testing_Manual.pdf")
    doc = Document()

    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    title = doc.add_paragraph()
    r = title.add_run("Docker Generation & Testing Manual")
    r.font.size = Pt(22)
    r.font.bold = True
    r.font.color.rgb = RGBColor(15, 23, 42)

    sub = doc.add_paragraph()
    r_sub = sub.add_run("Container Architecture, Health Monitoring & Operational Verification")
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    meta = doc.add_paragraph()
    r_m = meta.add_run("Framework: MASTER_SDLC_AGENTS | DevOps Manual | Date: 2026-10-23 | Status: Production-Ready")
    r_m.font.size = Pt(9.5)
    r_m.font.italic = True
    r_m.font.color.rgb = RGBColor(100, 116, 139)
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    doc.add_heading("1. Container Architecture & Security Specs", level=1)
    doc.add_paragraph(
        "• Base Image: python:3.10-slim (Minimal Debian footprint)\n"
        "• System Packages: libgl1, libglib2.0-0, curl\n"
        "• Security User: Non-privileged appuser (UID 1000) for unprivileged execution\n"
        "• Service Port: 8501 (Mapped 1:1 on host)\n"
        "• Health Check: curl -f http://localhost:8501/_stcore/health"
    )

    doc.add_heading("2. Step-by-Step Container Deployment", level=1)
    doc.add_paragraph(
        "1. Build and launch container in detached mode:\n"
        "   docker compose up --build -d\n\n"
        "2. Verify container running state:\n"
        "   docker ps\n\n"
        "3. Inspect live container logs:\n"
        "   docker logs -f lane_detection_dashboard\n\n"
        "4. Access web dashboard in browser: http://localhost:8501"
    )

    doc.add_heading("3. Health Monitoring & Maintenance", level=1)
    doc.add_paragraph(
        "Healthcheck Verification:\n"
        "Docker executes automated probes every 30s. The status in 'docker ps' displays '(healthy)' after 20s initial boot.\n\n"
        "Teardown:\n"
        "docker compose down"
    )

    doc.save(docx_path)
    print(f"Docker Testing Manual (.docx) saved to: {docx_path}")
    convert_docx_to_pdf(docx_path, pdf_path)

if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    plans_dir = os.path.join(root, "plans")
    build_detailed_design_doc(plans_dir)
    build_customer_handover_guide(root)
    build_docker_testing_manual(root)
