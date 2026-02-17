"""Data Quality Assessment Tools."""
import json
import os
import re
from datetime import datetime
from typing import Any

import pandas as pd
from crewai.tools import BaseTool
from scipy import stats


class DataLoaderTool(BaseTool):
    """Load and parse data files."""
    
    name: str = "data_loader"
    description: str = "Load data from CSV or JSON files. Returns dataset info and sample rows."
    
    def _run(self, file_path: str) -> str:
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            else:
                return f"Error: Unsupported file format. Use CSV or JSON."
            
            info = {
                "file": os.path.basename(file_path),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "sample_rows": df.head(3).to_dict(orient='records'),
                "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
            }
            return json.dumps(info, indent=2, default=str)
        except Exception as e:
            return f"Error loading file: {str(e)}"


class CDELoaderTool(BaseTool):
    """Load Critical Data Element configuration."""
    
    name: str = "cde_loader"
    description: str = "Load CDE (Critical Data Element) configuration from JSON file."
    
    def _run(self, config_path: str) -> str:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            cde_summary = {
                "dataset": config.get("dataset"),
                "description": config.get("description"),
                "cde_count": len(config.get("critical_data_elements", [])),
                "cde_fields": [cde["field"] for cde in config.get("critical_data_elements", [])],
                "thresholds": config.get("quality_thresholds", {}),
                "cde_details": config.get("critical_data_elements", [])
            }
            return json.dumps(cde_summary, indent=2)
        except Exception as e:
            return f"Error loading CDE config: {str(e)}"


class ProfilerTool(BaseTool):
    """Profile dataset columns for data quality metrics."""
    
    name: str = "data_profiler"
    description: str = "Profile a dataset to calculate completeness, uniqueness, data types, and statistics for each column. Provide file_path and optionally cde_fields as comma-separated list."
    
    def _run(self, file_path: str, cde_fields: str = "") -> str:
        try:
            df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_json(file_path)
            cde_list = [f.strip() for f in cde_fields.split(',')] if cde_fields else []
            
            profile = []
            for col in df.columns:
                col_data = df[col]
                is_cde = col in cde_list
                
                # Basic stats
                total = len(col_data)
                non_null = col_data.notna().sum()
                null_count = col_data.isna().sum()
                unique_count = col_data.nunique()
                
                col_profile = {
                    "column": col,
                    "is_cde": is_cde,
                    "data_type": str(col_data.dtype),
                    "total_rows": total,
                    "non_null_count": int(non_null),
                    "null_count": int(null_count),
                    "completeness": round(non_null / total, 4),
                    "unique_count": int(unique_count),
                    "uniqueness": round(unique_count / non_null, 4) if non_null > 0 else 0,
                    "duplicate_count": int(non_null - unique_count),
                }
                
                # Numeric stats
                if pd.api.types.is_numeric_dtype(col_data):
                    col_profile.update({
                        "min": float(col_data.min()) if not col_data.isna().all() else None,
                        "max": float(col_data.max()) if not col_data.isna().all() else None,
                        "mean": round(float(col_data.mean()), 2) if not col_data.isna().all() else None,
                        "std": round(float(col_data.std()), 2) if not col_data.isna().all() else None,
                    })
                
                # String stats
                if col_data.dtype == 'object':
                    lengths = col_data.dropna().astype(str).str.len()
                    col_profile.update({
                        "min_length": int(lengths.min()) if len(lengths) > 0 else None,
                        "max_length": int(lengths.max()) if len(lengths) > 0 else None,
                        "sample_values": list(col_data.dropna().head(3).astype(str)),
                    })
                
                profile.append(col_profile)
            
            # Summary
            cde_profiles = [p for p in profile if p["is_cde"]]
            non_cde_profiles = [p for p in profile if not p["is_cde"]]
            
            summary = {
                "total_columns": len(profile),
                "cde_columns": len(cde_profiles),
                "overall_completeness": round(sum(p["completeness"] for p in profile) / len(profile), 4),
                "cde_completeness": round(sum(p["completeness"] for p in cde_profiles) / len(cde_profiles), 4) if cde_profiles else None,
                "columns_with_nulls": len([p for p in profile if p["null_count"] > 0]),
                "columns_with_duplicates": len([p for p in profile if p["duplicate_count"] > 0]),
                "column_profiles": profile
            }
            
            return json.dumps(summary, indent=2)
        except Exception as e:
            return f"Error profiling data: {str(e)}"


class ValidatorTool(BaseTool):
    """Validate data against business rules."""
    
    name: str = "data_validator"
    description: str = "Validate dataset against business rules. Checks email formats, date ranges, numeric bounds, and custom rules."
    
    def _run(self, file_path: str, cde_config_path: str = "") -> str:
        try:
            df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_json(file_path)
            
            # Load CDE config if provided
            cde_rules = {}
            if cde_config_path and os.path.exists(cde_config_path):
                with open(cde_config_path, 'r') as f:
                    config = json.load(f)
                    for cde in config.get("critical_data_elements", []):
                        cde_rules[cde["field"]] = cde
            
            issues = []
            
            # Email validation
            if 'email' in df.columns:
                email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                invalid_emails = df[df['email'].notna() & ~df['email'].astype(str).str.match(email_pattern)]
                if len(invalid_emails) > 0:
                    issues.append({
                        "field": "email",
                        "rule": "format_validation",
                        "severity": "HIGH",
                        "invalid_count": len(invalid_emails),
                        "sample_invalid": list(invalid_emails['email'].head(3)),
                        "message": f"{len(invalid_emails)} records have invalid email format"
                    })
            
            # Phone validation
            if 'phone' in df.columns:
                phone_pattern = r'^\d{3}-\d{3}-\d{4}$'
                invalid_phones = df[df['phone'].notna() & ~df['phone'].astype(str).str.match(phone_pattern)]
                if len(invalid_phones) > 0:
                    issues.append({
                        "field": "phone",
                        "rule": "format_validation",
                        "severity": "MEDIUM",
                        "invalid_count": len(invalid_phones),
                        "sample_invalid": list(invalid_phones['phone'].head(3)),
                        "message": f"{len(invalid_phones)} records have invalid phone format"
                    })
            
            # Date validation (no future dates for DOB)
            if 'date_of_birth' in df.columns:
                today = datetime.now().date()
                df['dob_parsed'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
                future_dob = df[df['dob_parsed'].dt.date > today]
                if len(future_dob) > 0:
                    issues.append({
                        "field": "date_of_birth",
                        "rule": "future_date",
                        "severity": "CRITICAL",
                        "invalid_count": len(future_dob),
                        "sample_invalid": list(future_dob['date_of_birth'].head(3).astype(str)),
                        "message": f"{len(future_dob)} records have future date of birth"
                    })
            
            # Negative balance check
            if 'account_balance' in df.columns:
                negative_balance = df[df['account_balance'] < 0]
                if len(negative_balance) > 0:
                    issues.append({
                        "field": "account_balance",
                        "rule": "negative_value",
                        "severity": "HIGH",
                        "invalid_count": len(negative_balance),
                        "sample_invalid": list(negative_balance['account_balance'].head(3)),
                        "message": f"{len(negative_balance)} records have negative account balance"
                    })
            
            # Credit score range check
            if 'credit_score' in df.columns:
                invalid_scores = df[(df['credit_score'] < 300) | (df['credit_score'] > 850)]
                if len(invalid_scores) > 0:
                    issues.append({
                        "field": "credit_score",
                        "rule": "range_validation",
                        "severity": "HIGH",
                        "invalid_count": len(invalid_scores),
                        "sample_invalid": list(invalid_scores['credit_score'].head(3)),
                        "message": f"{len(invalid_scores)} records have credit score outside valid range (300-850)"
                    })
            
            # CDE null checks
            for field, rules in cde_rules.items():
                if field in df.columns and rules.get("nullable") == False:
                    null_count = df[field].isna().sum()
                    if null_count > 0:
                        issues.append({
                            "field": field,
                            "rule": "cde_not_nullable",
                            "severity": "CRITICAL",
                            "invalid_count": int(null_count),
                            "message": f"CDE field '{field}' has {null_count} null values but is marked as non-nullable"
                        })
            
            # Duplicate check for unique fields
            for field, rules in cde_rules.items():
                if field in df.columns and rules.get("unique") == True:
                    dup_count = df[field].dropna().duplicated().sum()
                    if dup_count > 0:
                        issues.append({
                            "field": field,
                            "rule": "cde_uniqueness",
                            "severity": "CRITICAL",
                            "invalid_count": int(dup_count),
                            "message": f"CDE field '{field}' has {dup_count} duplicate values but is marked as unique"
                        })
            
            result = {
                "total_records": len(df),
                "total_issues": len(issues),
                "critical_issues": len([i for i in issues if i["severity"] == "CRITICAL"]),
                "high_issues": len([i for i in issues if i["severity"] == "HIGH"]),
                "medium_issues": len([i for i in issues if i["severity"] == "MEDIUM"]),
                "validity_score": round(1 - (sum(i["invalid_count"] for i in issues) / (len(df) * len(df.columns))), 4),
                "issues": issues
            }
            
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            return f"Error validating data: {str(e)}"


class AnomalyDetectorTool(BaseTool):
    """Detect statistical anomalies in data."""
    
    name: str = "anomaly_detector"
    description: str = "Detect statistical anomalies and outliers in numeric columns using z-scores and IQR methods."
    
    def _run(self, file_path: str) -> str:
        try:
            df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_json(file_path)
            
            anomalies = []
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            for col in numeric_cols:
                col_data = df[col].dropna()
                if len(col_data) < 3:
                    continue
                
                # Z-score method
                z_scores = stats.zscore(col_data)
                outliers_z = (abs(z_scores) > 3).sum()
                
                # IQR method
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                outliers_iqr = ((col_data < (Q1 - 1.5 * IQR)) | (col_data > (Q3 + 1.5 * IQR))).sum()
                
                if outliers_z > 0 or outliers_iqr > 0:
                    anomalies.append({
                        "column": col,
                        "outliers_zscore": int(outliers_z),
                        "outliers_iqr": int(outliers_iqr),
                        "stats": {
                            "mean": round(float(col_data.mean()), 2),
                            "std": round(float(col_data.std()), 2),
                            "Q1": round(float(Q1), 2),
                            "Q3": round(float(Q3), 2),
                            "IQR": round(float(IQR), 2)
                        }
                    })
            
            result = {
                "numeric_columns_analyzed": len(numeric_cols),
                "columns_with_anomalies": len(anomalies),
                "anomalies": anomalies
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error detecting anomalies: {str(e)}"
