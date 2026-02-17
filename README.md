# 🔍 AgenticDataQuality

A production-ready **multi-agent AI system** for automated data quality assessment with special focus on Critical Data Elements (CDEs). Built with [CrewAI](https://crewai.com), this system demonstrates how autonomous AI agents can collaborate to profile, validate, and assess enterprise data quality.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENTIC DATA QUALITY ASSESSMENT                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   📊 PROFILING           ✓ VALIDATION          🔍 ANOMALY DETECTION        │
│   ┌─────────────┐        ┌─────────────┐        ┌─────────────┐            │
│   │  Profiler   │───────▶│  Validator  │───────▶│  Anomaly    │            │
│   │   Agent     │        │   Agent     │        │  Detector   │            │
│   └─────────────┘        └─────────────┘        └─────────────┘            │
│         │                       │                      │                    │
│         │  • Schema analysis    │  • Business rules    │  • Z-score        │
│         │  • Completeness       │  • Format checks     │  • IQR method     │
│         │  • Uniqueness         │  • CDE validation    │  • Outliers       │
│         │  • CDE profiling      │  • Range checks      │                    │
│         │                       │                      │                    │
│         └───────────────────────┴──────────────────────┘                    │
│                                 │                                           │
│                                 ▼                                           │
│                       ┌─────────────────┐                                  │
│                       │  Report Writer  │                                  │
│                       │     Agent       │                                  │
│                       └─────────────────┘                                  │
│                                 │                                           │
│                                 ▼                                           │
│                       ┌─────────────────┐                                  │
│                       │   DQ REPORT     │                                  │
│                       │  • Scorecard    │                                  │
│                       │  • CDE Status   │                                  │
│                       │  • Issues       │                                  │
│                       │  • Remediation  │                                  │
│                       └─────────────────┘                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Overview

This system addresses a critical enterprise pain point: **data quality assessment**. Organizations struggle with inconsistent data, unknown quality issues, and lack of visibility into data health—especially for Critical Data Elements that drive business decisions and regulatory compliance.

### What are Critical Data Elements (CDEs)?

CDEs are the most important data fields in an organization—those that:
- Drive key business decisions
- Are required for regulatory reporting
- Impact financial calculations
- Are shared across multiple systems

Examples: Customer ID, Account Balance, Credit Score, Date of Birth, Email

## 🤖 Agent Roles

| Agent | Role | Tools | Model |
|-------|------|-------|-------|
| **Profiler Agent** | Analyzes schema, completeness, uniqueness, with CDE focus | `data_loader`, `cde_loader`, `data_profiler` | GPT-4o-mini |
| **Validator Agent** | Validates against business rules and CDE requirements | `data_validator` | GPT-4o-mini |
| **Anomaly Detector** | Identifies statistical outliers using Z-score & IQR | `anomaly_detector` | GPT-4o-mini |
| **Report Writer** | Synthesizes findings into actionable assessment report | — | GPT-4o-mini |
| **Senior Editor** *(optional)* | Polishes report for executive/C-suite presentation | — | **GPT-4o** |

### Executive Polish Mode

For reports that will be shared with Data Owners and senior leadership, enable the `--polish` flag. This adds a **Senior Editor Agent** (using GPT-4o) that:

- Refines the executive summary for 30-second scannability
- Cleans up table formatting
- Uses confident, action-oriented language
- Ensures professional tone suitable for board presentations
- Ties recommendations directly to business impact

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/Dewale-A/AgenticDataQuality.git
cd AgenticDataQuality

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Assessment

```bash
# Interactive mode
python main.py

# Assess sample data with CDE config
python main.py --data sample_data/customers.csv --cde sample_data/cde_config.json

# With executive polish (adds Senior Editor review)
python main.py --data sample_data/customers.csv --cde sample_data/cde_config.json --polish

# Short form
python main.py -d sample_data/customers.csv -c sample_data/cde_config.json -p

# List available sample files
python main.py --list
```

## 📁 Project Structure

```
AgenticDataQuality/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── sample_data/
│   ├── customers.csv      # Sample customer data
│   └── cde_config.json    # CDE configuration
├── output/                # Generated reports
├── docs/
│   └── architecture.svg   # System diagram
└── src/
    ├── agents/
    │   └── dq_agents.py   # Agent definitions
    ├── tasks/
    │   └── dq_tasks.py    # Task definitions
    ├── tools/
    │   └── data_tools.py  # Profiling & validation tools
    └── config/
        └── settings.py    # Configuration
```

## 📊 Sample Data

The included sample dataset (`customers.csv`) contains intentional quality issues:

| Issue Type | Field | Example |
|------------|-------|---------|
| Missing values | email, phone, date_of_birth | Null entries |
| Invalid format | email | "invalid-email" |
| Invalid format | phone | "invalid-phone" |
| Future date | date_of_birth | 2025-12-01 |
| Negative value | account_balance | -500.00 |
| Duplicates | customer_id, email | CUST001/CUST011 |

## 📋 CDE Configuration

Define your Critical Data Elements in JSON:

```json
{
  "critical_data_elements": [
    {
      "field": "customer_id",
      "business_definition": "Unique identifier for each customer",
      "data_owner": "Customer Data Management",
      "regulatory_requirement": "KYC/AML",
      "nullable": false,
      "unique": true
    }
  ],
  "quality_thresholds": {
    "cde_completeness": 0.99,
    "cde_validity": 0.99
  }
}
```

## 📈 Output Report

The assessment generates a comprehensive report including:

- **Executive Summary**: Overall DQ score, key findings
- **Data Quality Scorecard**: Completeness, validity, uniqueness scores
- **CDE Analysis**: Status of each Critical Data Element
- **Detailed Findings**: All issues by severity with affected records
- **Recommendations**: Prioritized remediation steps

## ⚙️ Configuration

Key settings in `.env`:

```bash
OPENAI_API_KEY=sk-...              # Required
OPENAI_MODEL=gpt-4o-mini           # Model selection
COMPLETENESS_THRESHOLD=0.95        # Minimum completeness
VALIDITY_THRESHOLD=0.98            # Minimum validity
```

## 🔧 Extending the System

### Adding Custom Validation Rules

Edit `src/tools/data_tools.py` to add rules in the `ValidatorTool`:

```python
# Add custom validation in ValidatorTool._run()
if 'my_field' in df.columns:
    invalid = df[~df['my_field'].str.match(r'pattern')]
    if len(invalid) > 0:
        issues.append({
            "field": "my_field",
            "rule": "custom_validation",
            "severity": "HIGH",
            "invalid_count": len(invalid)
        })
```

### Adding New Data Sources

The system supports CSV and JSON. To add database support, extend `DataLoaderTool`:

```python
elif connection_string.startswith('postgresql://'):
    df = pd.read_sql(query, connection_string)
```

## 📈 Future Enhancements

- [ ] Database connectivity (PostgreSQL, MySQL, Snowflake)
- [ ] Scheduled monitoring with historical trending
- [ ] Remediation workflow with ticketing integration
- [ ] Dashboard visualization
- [ ] Data lineage tracking
- [ ] ML-based anomaly detection

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 👤 Author

**Dewale A** - Data & AI Governance Professional
- GitHub: [@Dewale-A](https://github.com/Dewale-A)
- LinkedIn: [Connect](https://linkedin.com/in/dewale-a)

---

*Built as part of a portfolio demonstrating autonomous multi-agent systems for enterprise data management.*
