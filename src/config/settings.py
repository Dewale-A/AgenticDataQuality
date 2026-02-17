"""Configuration settings for Data Quality Assessment Tool."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Data Quality Thresholds
THRESHOLDS = {
    "completeness": float(os.getenv("COMPLETENESS_THRESHOLD", 0.95)),
    "uniqueness": float(os.getenv("UNIQUENESS_THRESHOLD", 0.99)),
    "validity": float(os.getenv("VALIDITY_THRESHOLD", 0.98)),
    "consistency": 0.95,
    "timeliness": 0.90,
}

# Severity Levels
SEVERITY = {
    "critical": {"min_score": 0, "max_score": 0.70, "label": "CRITICAL"},
    "high": {"min_score": 0.70, "max_score": 0.85, "label": "HIGH"},
    "medium": {"min_score": 0.85, "max_score": 0.95, "label": "MEDIUM"},
    "low": {"min_score": 0.95, "max_score": 1.0, "label": "LOW"},
}

# CDE (Critical Data Element) Configuration
# Fields matching these patterns are auto-flagged as CDEs
CDE_PATTERNS = [
    "customer_id", "account_id", "transaction_id",
    "ssn", "tax_id", "ein",
    "email", "phone", "address",
    "balance", "amount", "revenue",
    "date_of_birth", "dob",
    "name", "first_name", "last_name",
]

# Validation Rules by Data Type
VALIDATION_RULES = {
    "email": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
    "phone": r"^\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",
    "ssn": r"^\d{3}-?\d{2}-?\d{4}$",
    "date": r"^\d{4}-\d{2}-\d{2}$",
    "zip_code": r"^\d{5}(-\d{4})?$",
}

# Output Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "output")
