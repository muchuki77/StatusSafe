import os
from pyexpat import features
import sys
import math
from tabnanny import check
import pandas as pd
import io

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from rules_engine import extract_features

print("\n extract_features for student with OPT end date")
profile = {
    "student_id": "S-ENROLLED-NO-OPT",
    "today": "2026-01-14",
    "enrollment_status": "enrolled",
    "full_time": True,
    "program_level": "undergraduate",
    "program_start_date": "2025-09-01",
    "sevis_updated": True
}

print(extract_features(profile))


check("is_enrolled is 1.0 for enrolled student", extract_features(profile)["is_enrolled"] == 1.0)
check("is_full_time is 1.0 for full-time student", extract_features(profile)["is_full_time"] == 1.0)
check("check opt_days_masked is 0.0 for enrolled student with no opt_end_date", extract_features(profile)["opt_days_masked"] == 0.0)