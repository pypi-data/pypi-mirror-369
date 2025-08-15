from .print_anova_and_summary import print_anova_and_summary



def print_stata_summary(model, summary_df, conf_intervals, conf=0.95):
    """Prints the summary in STATA style."""
    print_anova_and_summary(model)
    
    # Dynamically generate the confidence interval label
    conf_label = f"{conf * 100:.0f}% Conf. Interval"
    
    print("------------------------------------------------------------------------------")
    print(f"             |      Coef.   Std. Err.      t    P>|t|     [{conf_label}]")
    print("-------------+----------------------------------------------------------------")
 
    for row in summary_df.itertuples():
        coef = float(row[1])
        std_err = float(row[2])
        t_value = float(row[3])
        p_value = float(row[4])
        conf_int_low, conf_int_high = conf_intervals.loc[row.Index]
        var_name = row.Index
        print(f"{var_name:>12} | {coef:>10.4f}   {std_err:>8.4f}   {t_value:>7.2f}   {p_value:>6.4f}   [{conf_int_low:>8.4f}, {conf_int_high:>8.4f}]")
    print("-------------+----------------------------------------------------------------")
