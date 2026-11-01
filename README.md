# Business-Intelligence-Analytics-Suite
A Python-based analytics toolkit for processing operational data, tracking KPIs, and generating automated executive reports.

## Overview

This project automates the analysis of business performance data, providing insights into:
- Revenue and profitability metrics
- Team and individual performance tracking
- Operational efficiency and conversion rates
- Compliance monitoring
- Geographic and demographic trends

## Features

### 📊 Performance Analysis (`sales_analysis.py`)
- Calculates revenue, profit margins, and average transaction values
- Ranks team members by key performance indicators
- Monitors compliance against business rules and thresholds
- Analyzes trends across product lines and customer segments
- **Auto-generates formatted Word reports** for stakeholder review

### 📈 Conversion & Efficiency Calculator (`conversion.py`)
- Processes activity data across multiple business channels
- Calculates efficiency and conversion metrics by team member
- Identifies top performers and flags areas for improvement
- Exports results to Excel for further analysis

### 📋 Weekly Performance Report (`weekly_report.py`)
- Comprehensive weekly KPI dashboard
- Individual performance breakdowns with compliance metrics
- Visual activity distribution analysis
- Customer demographic insights
- Trend tracking and variance reporting

## Tech Stack

- **Python 3.x**
- **Pandas** - Data manipulation and analysis
- **python-docx** - Automated Word document generation
- **openpyxl** - Excel export functionality

## Installation

```bash
# Clone the repository
git clone https://github.com/bri-sourcey/Business-Intelligence-Analytics-Suite.git

# Install dependencies
pip install pandas python-docx openpyxl
```

## Usage

```python
# Run performance analysis
python sales_analysis.py

# Calculate conversion metrics
python conversion.py

# Generate weekly report
python weekly_report.py
```

## Sample Output

```
==================================================
WEEKLY PERFORMANCE REPORT
==================================================

--- TEAM PERFORMANCE ---
Name                     Activity  Closed   Conv %    Compliance  
--------------------------------------------------------------------------------
Alex Johnson             150       12       8.0%      85.0%     
Maria Garcia             120       15       12.5%     92.0%     

--- SUMMARY ---
Total Transactions: 45
Overall Compliance Rate: 87.5%
Efficiency Rating: 94.2%
```

## Key Metrics

| Metric | Description |
|--------|-------------|
| Conversion Rate | Successful outcomes ÷ Total activities |
| Compliance Rate | Transactions meeting threshold requirements |
| Efficiency Score | Performance against baseline targets |
| Collection Rate | Amount received ÷ Amount expected |

## Project Structure

```
Business-Intelligence-Analytics-Suite/
├── sales_analysis.py        # Core performance analysis
├── conversion.py            # Efficiency metrics
├── weekly_report.py         # Comprehensive reporting
└── README.md
```

## Skills Demonstrated

- Data wrangling and transformation with Pandas
- Automated report generation
- Business metrics and KPI calculation
- Clean, modular Python code
- Data visualization and formatting

## Author

**Brianna Savoy**  
Data Analyst | MBA Candidate (2027)

## License

This project is available for portfolio and demonstration purposes.
