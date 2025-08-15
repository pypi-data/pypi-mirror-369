import warnings

"""
PRegress Package
================

A package for Python Regression analysis and data visualization.

Modules
-------
modeling
    Functions for model fitting and prediction.
plots
    Functions for various types of plots.

Functions
---------
Modeling functions:
- add_explicit_variable
- apply_transformation
- box_cox
- bp_test
- bsr
- EvalEnvironment
- extract_variable
- fit
- format_summary
- handle_included_vars
- intervals
- ncv_test
- parse_formula
- predict
- print_anova_and_summary
- print_anova_table
- print_r_summary
- print_stata_summary
- shapiro_test
- significance_code
- step
- summary
- vif
- xy_split

Plotting functions:
- barplot
- boxplot
- abline
- hist
- hists
- plot_bsr
- plot_cor
- plot_cook
- plot_qq
- plot_res
- hist_res
- plots
- plot_xy
- plot_intervals
"""

# Import modeling functions
from .modeling import (
    add_explicit_variable, apply_transformation, box_cox, bp_test, bsr, EvalEnvironment, extract_variable, fit,
    format_summary, handle_included_vars, intervals, ncv_test, parse_formula, predict,
    print_anova_and_summary, print_anova_table, print_r_summary, print_stata_summary, shapiro_test,
    significance_code, step, summary, vif, xy_split
)

# Import plotting functions
from .plots import (
    barplot, boxplot, abline, hist, hists, plot_bsr, plot_cor, plot_cook, plot_intervals, plot_qq, plot_res, hist_res, plots, plot_xy
)

# Define plotXY as an alias for plot_xy if not already done in plots.py
def plotXY(*args, **kwargs):
    warnings.warn("plotXY is deprecated, use plot_xy instead", DeprecationWarning)
    return plot_xy(*args, **kwargs)
  
from .plots.plots import plots

from .utils import get_data

__all__ = [
    # Modeling functions
    'add_explicit_variable', 'apply_transformation', 'box_cox', 'bp_test', 'bsr', 'EvalEnvironment', 'extract_variable', 'fit',
    'format_summary', 'handle_included_vars', 'intervals', 'parse_formula', 'predict',
    'print_anova_and_summary', 'print_anova_table', 'print_r_summary', 'print_stata_summary', 'shapiro_test',
    'significance_code', 'step', 'summary', 'vif', 'xy_split',
    
    # Plotting functions
    'barplot','boxplot', 'abline', 'hist', 'hists', 'plot_bsr', 'plot_cor', 'plot_cook', 'plot_intervals', 'plot_qq', 
    'plot_res', 'hist_res', 'plots', 'plot_xy', 'plotXY',
    
    # Utility functions
    'get_data'
]
