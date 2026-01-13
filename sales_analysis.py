"""
Sales Performance Analysis Tool
===============================
Analyzes sales data to generate insights on revenue, rep performance,
product trends, customer demographics, and down payment compliance.
Automatically generates a formatted Word report for executive review.

Author: Bri-sourcey
Tools: Python, Pandas, python-docx
"""

import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from datetime import datetime


def load_and_combine_data(mail_file, transfer_file):
    """Load and combine mail and transfer sales data."""
    mail_sales = pd.read_csv(mail_file)
    transfer_sales = pd.read_csv(transfer_file)
    all_sales = pd.concat([mail_sales, transfer_sales])
    return mail_sales, transfer_sales, all_sales


def clean_currency(df, column):
    """Convert currency strings to float values."""
    return df[column].str.replace('[$,]', '', regex=True).astype(float)


def analyze_revenue(df):
    """Calculate total revenue and profit metrics."""
    df['GrossProfitNum'] = clean_currency(df, 'GrossProfit')
    df['TotalCostNum'] = clean_currency(df, 'TotalCost')
    
    total_profit = df['GrossProfitNum'].sum()
    total_revenue = df['TotalCostNum'].sum()
    avg_deal = df['GrossProfitNum'].mean()
    
    return total_profit, total_revenue, avg_deal


def analyze_rep_performance(df):
    """Calculate profit by sales representative."""
    df['GrossProfitNum'] = clean_currency(df, 'GrossProfit')
    rep_profit = df.groupby('SalesRep')['GrossProfitNum'].sum().sort_values(ascending=False)
    return rep_profit


def analyze_down_payment_compliance(df, threshold=0.03):
    """
    Analyze down payment compliance against threshold.
    Default threshold is 3% of total cost.
    """
    df['TotalCostNum'] = clean_currency(df, 'TotalCost')
    df['DownPmtCollectedNum'] = clean_currency(df, 'DownPmtCollected')
    df['RequiredAmount'] = df['TotalCostNum'] * threshold
    df['MeetsThreshold'] = df['DownPmtCollectedNum'] >= df['RequiredAmount']
    
    # Summary by rep
    compliance_by_rep = df.groupby('SalesRep').agg({
        'TotalCostNum': 'sum',
        'RequiredAmount': 'sum',
        'DownPmtCollectedNum': 'sum',
        'MeetsThreshold': 'mean'
    }).round(2)
    
    compliance_by_rep['Variance'] = compliance_by_rep['DownPmtCollectedNum'] - compliance_by_rep['RequiredAmount']
    compliance_by_rep['ComplianceRate'] = (compliance_by_rep['MeetsThreshold'] * 100).round(1)
    
    # Overall stats
    total_required = df['RequiredAmount'].sum()
    total_collected = df['DownPmtCollectedNum'].sum()
    overall_compliance = (df['MeetsThreshold'].mean() * 100).round(1)
    
    return compliance_by_rep, total_required, total_collected, overall_compliance


def analyze_sales_timing(df):
    """Analyze sales distribution by hour."""
    df['SoldDateTime'] = pd.to_datetime(df['SoldDateTime'])
    df['Hour'] = df['SoldDateTime'].dt.hour
    return df['Hour'].value_counts().sort_index()


def generate_word_report(data, filename='Sales_Report.docx'):
    """Generate formatted Word document with analysis results."""
    doc = Document()
    
    # Title
    doc.add_heading(f'Weekly Sales Report', 0)
    doc.add_paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    
    # Overview Section
    doc.add_heading('Overview', level=1)
    doc.add_paragraph(f'Total Revenue: ${data["total_revenue"]:,.2f}')
    doc.add_paragraph(f'Total Gross Profit: ${data["total_profit"]:,.2f}')
    doc.add_paragraph(f'Average Deal Profit: ${data["avg_deal"]:,.2f}')
    doc.add_paragraph(f'Total Deals: {data["total_deals"]}')
    
    # Top Performers Section
    doc.add_heading('Top Performers (by Profit)', level=1)
    for i, (rep, profit) in enumerate(data["top_reps"].items(), 1):
        doc.add_paragraph(f'{i}. {rep} — ${profit:,.0f}')
    
    # Compliance Section
    doc.add_heading('Down Payment Compliance', level=1)
    doc.add_paragraph(f'Overall Compliance Rate: {data["compliance_rate"]}%')
    doc.add_paragraph(f'Total Collected: ${data["total_collected"]:,.2f}')
    doc.add_paragraph(f'Total Required: ${data["total_required"]:,.2f}')
    
    doc.save(filename)
    print(f'✓ Report saved as {filename}')


def main():
    """Main execution function."""
    print("=" * 60)
    print("SALES PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Load data
    mail_sales, transfer_sales, all_sales = load_and_combine_data(
        'MailSales.csv', 
        'TransferSales.csv'
    )
    
    # Revenue analysis
    print("\n--- REVENUE METRICS ---")
    total_profit, total_revenue, avg_deal = analyze_revenue(all_sales)
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Total Gross Profit: ${total_profit:,.2f}")
    print(f"Average Deal Profit: ${avg_deal:,.2f}")
    
    # Rep performance
    print("\n--- REP PERFORMANCE ---")
    rep_profit = analyze_rep_performance(all_sales)
    print(rep_profit)
    
    # Down payment compliance
    print("\n--- DOWN PAYMENT COMPLIANCE (3% RULE) ---")
    compliance_by_rep, total_required, total_collected, overall_compliance = analyze_down_payment_compliance(all_sales)
    print(f"Overall Compliance: {overall_compliance}%")
    print(f"Collected: ${total_collected:,.2f} vs Required: ${total_required:,.2f}")
    print("\nBy Rep:")
    print(compliance_by_rep)
    
    # Product trends
    print("\n--- PRODUCT TRENDS ---")
    print(f"Coverage Types:\n{all_sales['Coverage'].value_counts()}")
    print(f"\nTop Terms:\n{all_sales['Term'].value_counts().head()}")
    
    # Customer breakdown
    print("\n--- CUSTOMER BREAKDOWN ---")
    print(f"Top States:\n{all_sales['State'].value_counts().head(10)}")
    print(f"\nPayment Types:\n{all_sales['PaymentType'].value_counts()}")
    
    # Timing analysis
    print("\n--- SALES BY HOUR ---")
    hourly_sales = analyze_sales_timing(all_sales)
    print(hourly_sales)
    
    # Generate report
    report_data = {
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'avg_deal': avg_deal,
        'total_deals': len(all_sales),
        'top_reps': rep_profit.head(3).to_dict(),
        'compliance_rate': overall_compliance,
        'total_collected': total_collected,
        'total_required': total_required
    }
    
    generate_word_report(report_data)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
