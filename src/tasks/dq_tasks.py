"""Data Quality Assessment Tasks."""
from crewai import Task, Agent


def create_profiling_task(agent: Agent, data_file: str, cde_config: str) -> Task:
    """Create the data profiling task."""
    return Task(
        description=f"""Profile the dataset to understand its structure and quality characteristics.

        DATA FILE: {data_file}
        CDE CONFIG: {cde_config}

        Your profiling must include:
        1. Load and examine the dataset structure (columns, rows, data types)
        2. Load the CDE (Critical Data Element) configuration to identify which fields are CDEs
        3. Profile ALL columns with special emphasis on CDE fields:
           - Completeness (% non-null values)
           - Uniqueness (% unique values)
           - Data type consistency
           - Value distributions and statistics
        4. For CDE fields specifically, note:
           - Business definition and owner
           - Regulatory requirements
           - Whether they meet stricter CDE thresholds
        5. Identify columns with quality concerns (high nulls, low uniqueness, type issues)
        
        Provide a comprehensive profile with CDE analysis highlighted separately.""",
        expected_output="""A detailed data profile including:
        - Dataset overview (rows, columns, memory)
        - CDE field identification and their quality metrics
        - Column-by-column profile with completeness, uniqueness, statistics
        - Summary of quality concerns
        - CDE compliance status against defined thresholds""",
        agent=agent,
    )


def create_validation_task(agent: Agent, data_file: str, cde_config: str) -> Task:
    """Create the data validation task."""
    return Task(
        description=f"""Validate the dataset against business rules and CDE requirements.

        DATA FILE: {data_file}
        CDE CONFIG: {cde_config}

        Validation checks must include:
        1. Format validation (emails, phones, dates, IDs)
        2. Range validation (credit scores 300-850, no negative balances)
        3. Date logic (no future dates of birth)
        4. CDE-specific rules:
           - Non-nullable CDEs must have no nulls
           - Unique CDEs must have no duplicates
           - Format requirements per CDE definition
        5. Referential integrity where applicable
        6. Business rule compliance
        
        Categorize all issues by severity: CRITICAL, HIGH, MEDIUM, LOW
        CDE violations should generally be CRITICAL or HIGH.""",
        expected_output="""A validation report including:
        - Total records validated
        - Issue counts by severity (Critical/High/Medium/Low)
        - Detailed issue list with field, rule violated, count, and sample values
        - CDE violations highlighted separately
        - Overall validity score""",
        agent=agent,
    )


def create_anomaly_task(agent: Agent, data_file: str) -> Task:
    """Create the anomaly detection task."""
    return Task(
        description=f"""Detect statistical anomalies and outliers in the dataset.

        DATA FILE: {data_file}

        Analyze all numeric columns for:
        1. Statistical outliers using Z-score method (values > 3 standard deviations)
        2. Statistical outliers using IQR method (values beyond 1.5*IQR)
        3. Unusual distributions or patterns
        4. Potential data entry errors
        5. Values that are technically valid but statistically unusual
        
        Consider business context when flagging anomalies - some outliers may be 
        legitimate (e.g., high-net-worth customers with large balances).""",
        expected_output="""An anomaly report including:
        - Number of numeric columns analyzed
        - Columns with detected anomalies
        - For each anomalous column: outlier counts, statistical context
        - Assessment of whether anomalies likely indicate quality issues
        - Recommendations for investigation""",
        agent=agent,
    )


def create_report_task(agent: Agent, data_file: str) -> Task:
    """Create the final report writing task."""
    return Task(
        description=f"""Synthesize all findings into a comprehensive Data Quality Assessment Report.

        Create a professional report that includes:

        1. EXECUTIVE SUMMARY
           - Overall data quality score (0-100)
           - CDE quality score (0-100)
           - Key findings (top 3-5 issues)
           - Recommended actions
        
        2. DATA QUALITY SCORECARD
           - Completeness score
           - Validity score
           - Uniqueness score
           - Consistency score
           - CDE compliance score
        
        3. CDE ANALYSIS
           - Status of each Critical Data Element
           - CDE-specific issues and their business impact
           - Regulatory compliance concerns
        
        4. DETAILED FINDINGS
           - All issues organized by severity
           - Affected record counts
           - Sample problematic values
           - Root cause analysis where possible
        
        5. RECOMMENDATIONS
           - Prioritized remediation steps
           - Quick wins vs long-term improvements
           - Data governance process improvements
        
        6. APPENDIX
           - Full column profiles
           - Statistical details

        The report should be suitable for presentation to both technical teams 
        and business stakeholders.""",
        expected_output="""A complete Data Quality Assessment Report in markdown format with:
        - Executive summary with scores and key findings
        - Visual scorecard (using markdown tables)
        - CDE-focused analysis section
        - Prioritized issue list
        - Actionable recommendations
        - Technical appendix""",
        agent=agent,
        output_file="output/dq_assessment_report.md",
    )


def create_polish_task(agent: Agent, data_file: str) -> Task:
    """Create the senior editor polish task for executive-quality reports."""
    return Task(
        description=f"""Review and polish the Data Quality Assessment Report for executive presentation.

        You are editing a report that will be shared with Data Owners and senior leadership.
        Your task is to transform a good technical report into an exceptional executive document.

        EDITING PRIORITIES:

        1. EXECUTIVE SUMMARY REFINEMENT
           - Make it scannable in 30 seconds
           - Lead with business impact, not technical details
           - Use bullet points for key findings
           - Ensure scores are prominently displayed
        
        2. TABLE FORMATTING
           - Ensure all markdown tables are clean and properly aligned
           - Use simple table structures that render well
           - Break complex tables into simpler ones if needed
           - Add clear headers and consistent formatting
        
        3. LANGUAGE & TONE
           - Use confident, action-oriented language
           - Remove unnecessary jargon
           - Ensure consistency in terminology throughout
           - Write for a C-suite audience (clear, concise, impactful)
        
        4. STRUCTURE & FLOW
           - Ensure logical progression of sections
           - Add clear transitions between sections
           - Make sure recommendations directly tie to findings
           - Prioritize information by business impact
        
        5. VISUAL CLARITY
           - Use bold/italics strategically for emphasis
           - Ensure adequate white space
           - Use horizontal rules to separate major sections
           - Make severity levels visually distinct
        
        6. PROFESSIONAL POLISH
           - Check for consistent date/number formatting
           - Ensure professional tone throughout
           - Add appropriate document metadata (date, version)
           - Include clear contact/ownership information

        The final report should be something a Chief Data Officer would be proud to present 
        to the board of directors.""",
        expected_output="""A polished, executive-ready Data Quality Assessment Report with:
        - Clean, scannable executive summary
        - Properly formatted markdown tables
        - Professional, action-oriented language
        - Clear visual hierarchy
        - Consistent formatting throughout
        - Ready for C-suite presentation""",
        agent=agent,
        output_file="output/dq_assessment_report_final.md",
    )
