"""
Pytest configuration and root path resolution fixture
Project: Real-Time Deep Learning Road Lane Detection System
"""

import sys
import os
from pathlib import Path

# Resolve project root and src directories
project_root = Path(__file__).resolve().parent.parent
src_dir = project_root / "src"

for p in [str(project_root), str(src_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)
