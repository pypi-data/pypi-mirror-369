from .significance_code import significance_code

def format_summary(summary_df, alpha=0.05):
    """Formats the summary DataFrame."""
    # Calculate confidence interval column names
    lower_ci = f'[{alpha/2:.3f}'
    upper_ci = f'{1 - alpha/2:.3f}]'
    
    # Remove the columns for the confidence intervals if they exist
    columns_to_drop = [lower_ci, upper_ci]
    existing_columns = [col for col in columns_to_drop if col in summary_df.columns]
    summary_df.drop(existing_columns, axis=1, inplace=True, errors='ignore')
    
    # Format the P>|t| column if it exists
    if 'P>|t|' in summary_df.columns:
        summary_df['P>|t|'] = summary_df['P>|t|'].astype(float).map(lambda x: f'{x:.6f}')
        summary_df[' '] = summary_df['P>|t|'].apply(significance_code)
    
    return summary_df
