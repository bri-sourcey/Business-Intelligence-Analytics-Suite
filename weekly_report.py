"""
Weekly Sales Performance Report Generator
=========================================
Comprehensive weekly analysis tool that processes sales and call data
to generate performance metrics including conversion rates, compliance
tracking, customer insights, and product trends.

Author: Bri-sourcey
Tools: Python, Pandas, glob
"""

import pandas as pd
import glob
from datetime import datetime


def load_sales_data(mail_file, transfer_file):
    """Load and combine sales data from both channels."""
    mail_sales = pd.read_csv(mail_file)
    transfer_sales = pd.read_csv(transfer_file)
    combined = pd.concat([mail_sales, transfer_sales])
    return mail_sales, transfer_sales, combined


def clean_currency_columns(df, columns):
    """Convert currency strings to float values."""
    for col in columns:
        if col in df.columns:
            df[col] = df[col].str.replace('[$,]', '', regex=True).astype(float)
    return df


def calculate_compliance_metrics(df, threshold=0.03):
    """
    Calculate down payment compliance metrics.
    
    Args:
        df: Sales DataFrame
        threshold: Required down payment percentage (default 3%)
    
    Returns:
        DataFrame with compliance flags added
    """
    df['Required3Pct'] = df['TotalCost'] * threshold
    df['Hit3Pct'] = df['DownPmtCollected'] >= df['Required3Pct']
    df['FullDownPmt'] = df['DownPmtMissing'] == 0
    return df


def load_calls_data(file_pattern):
    """Load and aggregate all calls files matching pattern."""
    files = glob.glob(f'{file_pattern}*.csv')
    if not files:
        return pd.DataFrame(columns=['AGENT', 'CALLS'])
    
    all_data = pd.concat([pd.read_csv(f) for f in files])
    return all_data.groupby('AGENT')['CALLS'].sum().reset_index()


def generate_rep_performance_table(reps, calls_dict, sales_count, sales_df, channel_name):
    """Generate formatted performance table for a channel."""
    print(f"\n--- {channel_name.upper()} PERFORMANCE ---")
    print(f"{'Rep':<25} {'Calls':<8} {'Sales':<8} {'Conv %':<10} {'3% Hit':<10} {'Full DP':<10}")
    print("-" * 80)
    
    for rep in reps:
        calls = calls_dict.get(rep, 0)
        sales_num = sales_count.get(rep, 0)
        conv = round(sales_num / calls * 100, 2) if calls > 0 else 0
        
        rep_data = sales_df[sales_df['SalesRep'] == rep]
        hit_rate = round(rep_data['Hit3Pct'].mean() * 100, 1) if len(rep_data) > 0 else 0
        full_dp = round(rep_data['FullDownPmt'].mean() * 100, 1) if len(rep_data) > 0 else 0
        
        print(f"{rep:<25} {calls:<8} {sales_num:<8} {str(conv) + '%':<10} {str(hit_rate) + '%':<10} {str(full_dp) + '%':<10}")


def analyze_sales_timing(df):
    """Analyze and display sales distribution by hour."""
    df['SoldDateTime'] = pd.to_datetime(df['SoldDateTime'])
    df['Hour'] = df['SoldDateTime'].dt.hour
    
    print("\n--- SALES BY HOUR ---")
    hour_counts = df['Hour'].value_counts().sort_index()
    for hour, count in hour_counts.items():
        bar = '█' * count
        print(f"  {hour:02d}:00  {bar} ({count})")
    
    return hour_counts


def analyze_customer_demographics(df):
    """Analyze customer location distribution."""
    print("\n--- TOP 10 STATES ---")
    state_counts = df['State'].value_counts()
    for state, count in state_counts.head(10).items():
        print(f"  {state}: {count}")
    return state_counts


def analyze_vehicle_data(df):
    """Analyze vehicle make and year trends."""
    print("\n--- TOP 10 VEHICLE MAKES ---")
    make_counts = df['Make'].value_counts().head(10)
    for make, count in make_counts.items():
        print(f"  {make}: {count}")
    
    year_avg = df['Year'].mean()
    print(f"\nAverage Vehicle Year: {round(year_avg)}")
    
    # Parse term data
    df['TermMonths'] = df['Term'].str.split('/').str[0].astype(int)
    df['TermMiles'] = df['Term'].str.split('/').str[1].astype(int)
    print(f"Average Term: {round(df['TermMonths'].mean())} months / {round(df['TermMiles'].mean())}k miles")
    
    return make_counts, year_avg


def analyze_down_payment_collection(df):
    """Analyze down payment collection by representative."""
    print("\n--- DOWN PAYMENT COLLECTION BY REP ---")
    dp_by_rep = df.groupby('SalesRep').agg({
        'DownPayment': 'sum',
        'DownPmtCollected': 'sum',
        'DownPmtMissing': 'sum'
    }).round(2)
    
    dp_by_rep['CollectionRate'] = (dp_by_rep['DownPmtCollected'] / dp_by_rep['DownPayment'] * 100).round(1)
    print(dp_by_rep.sort_values('DownPmtCollected', ascending=False))
    
    return dp_by_rep


def main():
    """Main execution function."""
    print("=" * 90)
    print(f"WEEKLY SALES REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 90)
    
    # --- LOAD DATA ---
    mail_sales, transfer_sales, all_sales = load_sales_data(
        'MailSales.csv', 
        'TransferSales.csv'
    )
    
    mapping = pd.read_csv('rep_mapping.csv')
    all_reps = list(mapping['SalesRep'])
    
    # --- CLEAN CURRENCY COLUMNS ---
    money_cols = ['TotalCost', 'DownPayment', 'DownPmtCollected', 'DownPmtMissing']
    for df in [all_sales, mail_sales, transfer_sales]:
        clean_currency_columns(df, money_cols)
    
    # --- CALCULATE COMPLIANCE ---
    for df in [all_sales, mail_sales, transfer_sales]:
        calculate_compliance_metrics(df)
    
    # --- LOAD CALLS DATA ---
    mail_calls = load_calls_data('MailCalls')
    transfer_calls = load_calls_data('TransferCalls')
    
    # Map agents to reps
    mail_calls = mail_calls.merge(mapping, on='AGENT', how='left')
    transfer_calls = transfer_calls.merge(mapping, on='AGENT', how='left')
    
    mail_calls_dict = dict(zip(mail_calls['SalesRep'], mail_calls['CALLS']))
    transfer_calls_dict = dict(zip(transfer_calls['SalesRep'], transfer_calls['CALLS']))
    
    # --- SALES COUNTS ---
    mail_sales_count = mail_sales.groupby('SalesRep').size().to_dict()
    transfer_sales_count = transfer_sales.groupby('SalesRep').size().to_dict()
    
    # --- REP PERFORMANCE TABLES ---
    generate_rep_performance_table(
        all_reps, mail_calls_dict, mail_sales_count, mail_sales, 'Mail'
    )
    
    generate_rep_performance_table(
        all_reps, transfer_calls_dict, transfer_sales_count, transfer_sales, 'Transfer'
    )
    
    # --- TOTALS ---
    print("\n--- SUMMARY TOTALS ---")
    print(f"Total Sales: {len(all_sales)}")
    print(f"  Mail Sales: {len(mail_sales)}")
    print(f"  Transfer Sales: {len(transfer_sales)}")
    print(f"Overall 3% Compliance Rate: {round(all_sales['Hit3Pct'].mean() * 100, 1)}%")
    print(f"Full Down Payment Rate: {round(all_sales['FullDownPmt'].mean() * 100, 1)}%")
    
    # --- ADDITIONAL ANALYSIS ---
    analyze_sales_timing(all_sales)
    analyze_customer_demographics(all_sales)
    analyze_vehicle_data(all_sales)
    analyze_down_payment_collection(all_sales)
    
    # --- PAYMENT PROGRESS ---
    print("\n--- PAYMENT PROGRESS DISTRIBUTION ---")
    print(all_sales['PaymentsMade'].value_counts().sort_index())
    
    print("\n" + "=" * 90)
    print("END OF WEEKLY REPORT")
    print("=" * 90)


if __name__ == "__main__":
    main()
