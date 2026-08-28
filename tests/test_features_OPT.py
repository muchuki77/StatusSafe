import os
import sys
import math
import pandas as pd
import io

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from rules_engine import extract_features
profile = {
    "student_id": "S_RED_R1",
    "today": "2026-01-14",
    "enrollment_status": "not_enrolled",
    "full_time": False,
    "program_level": "graduate",
    "program_start_date": "2024-08-26",
    "opt_end_date": "2025-12-01",
    "sevis_updated": False
}


print(extract_features(profile))