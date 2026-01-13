"""
Sales Conversion Rate Calculator
================================
Calculates call-to-sale conversion rates by sales representative
across multiple channels (mail and transfer). Identifies top
performers and flags underperformers.

Author: Bri-sourcey
Tools: Python, Pandas
"""

import pandas as pd
from pathlib import Path


def load_calls_data(file_pattern, date_range):
    """
    Load and combine calls data from multiple date files.
    
    Args:
        file_pattern: Base filename pattern (e.g., 'MailCalls')
        date_range: List of date strings (e.g., ['0105', '0106', '0107'])
    
    Returns:
        DataFrame with aggregated calls by agent
    """
    all_calls = []
    
    for date in date_range:
        filename = f'{file_pattern}{date}.csv'
        if Path(filename).exists():
            df = pd.read_csv(filename)
            all_calls.append(df)
    
    if all_calls:
        combined = pd.concat(all_calls)
        return combined.groupby('AGENT')['CALLS'].sum().reset_index()
    
    return pd.DataFrame(columns=['AGENT', 'CALLS'])


def load_sales_data(filename):
    """Load sales data and count by representative."""
    df = pd.read_csv(filename)
    return df.groupby('SalesRep').size().reset_index(name='Sales')


def calculate_conversion_rates(calls_df, sales_df, mapping_df, channel_name):
    """
    Calculate conversion rates by merging calls and sales data.
    
    Args:
        calls_df: DataFrame with calls by agent
        sales_df: DataFrame with sales by rep
        mapping_df: DataFrame mapping agents to sales reps
        channel_name: Name of channel for column labeling
    
    Returns:
        DataFrame with conversion metrics
    """
    # Rename columns for clarity
    calls_df = calls_df.rename(columns={'CALLS': f'{channel_name}Calls'})
    sales_df = sales_df.rename(columns={'Sales': f'{channel_name}Sales'})
    
    # Merge with mapping
    results = mapping_df.merge(calls_df, on='AGENT', how='left')
    results = results.merge(sales_df, on='SalesRep', how='left')
    
    # Fill NaN with 0
    results = results.fillna(0)
    
    # Calculate conversion rate
    calls_col = f'{channel_name}Calls'
    sales_col = f'{channel_name}Sales'
    conv_col = f'{channel_name}Conversion'
    
    results[conv_col] = (results[sales_col] / results[calls_col] * 100).round(2)
    results[conv_col] = results[conv_col].replace([float('inf')], 0).fillna(0)
    
    return results


def identify_top_performers(results, conversion_col):
    """Identify the top converting sales rep."""
    if results[conversion_col].max() > 0:
        top_idx = results[conversion_col].idxmax()
        return results.loc[top_idx, 'SalesRep']
    return None


def identify_zero_sales(results, sales_col):
    """Identify reps with zero sales."""
    return results[results[sales_col] == 0]['SalesRep'].tolist()


def format_for_display(results, conversion_cols):
    """Format conversion columns with percentage signs for display."""
    display_df = results.copy()
    for col in conversion_cols:
        display_df[col] = display_df[col].astype(str) + '%'
    return display_df


def main():
    """Main execution function."""
    print("=" * 60)
    print("CONVERSION RATE ANALYSIS")
    print("=" * 60)
    
    # Configuration
    date_range = ['0105', '0106', '0107', '0108']
    
    # Load agent-to-rep mapping
    mapping = pd.read_csv('rep_mapping.csv')
    
    # Load calls data
    print("\nLoading calls data...")
    mail_calls = load_calls_data('MailCalls', date_range)
    transfer_calls = load_calls_data('TransferCalls', date_range)
    
    # Apply transfer call adjustment (70% factor for qualified calls)
    transfer_calls['CALLS'] = (transfer_calls['CALLS'] * 0.7).round(0)
    
    # Load sales data
    print("Loading sales data...")
    mail_sales = load_sales_data('MailSales.csv')
    transfer_sales = load_sales_data('TransferSales.csv')
    
    # Calculate conversion rates
    print("Calculating conversion rates...")
    
    # Start with mapping as base
    results = mapping.copy()
    
    # Mail channel
    mail_calls = mail_calls.rename(columns={'CALLS': 'MailCalls'})
    mail_sales = mail_sales.rename(columns={'Sales': 'MailSales'})
    results = results.merge(mail_calls, on='AGENT', how='left')
    results = results.merge(mail_sales, on='SalesRep', how='left')
    
    # Transfer channel
    transfer_calls = transfer_calls.rename(columns={'CALLS': 'TransferCalls'})
    transfer_sales = transfer_sales.rename(columns={'Sales': 'TransferSales'})
    results = results.merge(transfer_calls, on='AGENT', how='left')
    results = results.merge(transfer_sales, on='SalesRep', how='left')
    
    # Fill NaN
    results = results.fillna(0)
    
    # Calculate conversion rates
    results['MailConversion'] = (results['MailSales'] / results['MailCalls'] * 100).round(2)
    results['TransferConversion'] = (results['TransferSales'] / results['TransferCalls'] * 100).round(2)
    
    # Handle division errors
    results = results.replace([float('inf')], 0)
    results['MailConversion'] = results['MailConversion'].fillna(0)
    results['TransferConversion'] = results['TransferConversion'].fillna(0)
    
    # --- SUMMARY STATISTICS ---
    print("\n" + "=" * 60)
    print("WEEKLY SUMMARY")
    print("=" * 60)
    
    # Total metrics
    total_mail_calls = results['MailCalls'].sum()
    total_mail_sales = results['MailSales'].sum()
    total_transfer_calls = results['TransferCalls'].sum()
    total_transfer_sales = results['TransferSales'].sum()
    
    # Overall conversion rates
    overall_mail_conv = (total_mail_sales / total_mail_calls * 100).round(2) if total_mail_calls > 0 else 0
    overall_transfer_conv = (total_transfer_sales / total_transfer_calls * 100).round(2) if total_transfer_calls > 0 else 0
    
    print(f"\nMAIL CHANNEL:")
    print(f"  {int(total_mail_sales)} sales / {int(total_mail_calls)} calls = {overall_mail_conv}%")
    
    print(f"\nTRANSFER CHANNEL:")
    print(f"  {int(total_transfer_sales)} sales / {int(total_transfer_calls)} calls = {overall_transfer_conv}%")
    
    # Top performers
    top_mail = results.loc[results['MailConversion'].idxmax(), 'SalesRep'] if results['MailConversion'].max() > 0 else 'N/A'
    top_transfer = results.loc[results['TransferConversion'].idxmax(), 'SalesRep'] if results['TransferConversion'].max() > 0 else 'N/A'
    
    print(f"\nTOP PERFORMERS:")
    print(f"  Mail: {top_mail}")
    print(f"  Transfer: {top_transfer}")
    
    # Flag zero sales
    zero_mail = results[results['MailSales'] == 0]['SalesRep'].tolist()
    zero_transfer = results[results['TransferSales'] == 0]['SalesRep'].tolist()
    
    if zero_mail:
        print(f"\n⚠️  No mail sales: {', '.join(zero_mail)}")
    if zero_transfer:
        print(f"⚠️  No transfer sales: {', '.join(zero_transfer)}")
    
    # Format for display
    display_results = results.copy()
    display_results['MailConversion'] = display_results['MailConversion'].astype(str) + '%'
    display_results['TransferConversion'] = display_results['TransferConversion'].astype(str) + '%'
    
    # Select columns for output
    output_cols = ['SalesRep', 'MailCalls', 'MailSales', 'MailConversion', 
                   'TransferCalls', 'TransferSales', 'TransferConversion']
    
    print("\n" + "-" * 60)
    print("DETAILED BREAKDOWN")
    print("-" * 60)
    print(display_results[output_cols].to_string(index=False))
    
    # Export to Excel
    output_file = 'conversion_rates.xlsx'
    display_results[output_cols].to_excel(output_file, index=False)
    print(f"\n✓ Results exported to {output_file}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
