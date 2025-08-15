"""
Plots
============

This subpackage provides functions for various types of plots used in regression analysis.

Functions
---------
barplot
    Create a barplot of the data.
boxplot
    Create a boxplot of the data.
hist
    Create a histogram of the data.
hists
    Create multiple histograms of the data.
plot_bsr
    Create a plot of a best subsets object
plot_cor
    Plot the correlation matrix.
plot_cook
    Create a Cook's distance plot.
plot_intervals
    Create an intervals plot.
plot_qq
    Create a QQ plot.
plot_res
    Plot the residuals.
hist_res
    Plot the residuals vs. fitted values.
plots
    Create various plots.
plot_xy
    Plot the X vs. Y data.
"""

from .barplot import barplot
from .boxplot import boxplot
from .abline import abline
from .hist import hist
from .hists import hists
from .plot_bsr import plot_bsr
from .plot_intervals import plot_intervals
from .plot_cor import plot_cor
from .plot_cook import plot_cook
from .plot_qq import plot_qq
from .plot_res import plot_res
from .hist_res import hist_res
from .plots import plots
from .plot_xy import plot_xy

__all__ = [
    'barplot', 'boxplot', 'abline', 'hist', 'hists', 'plot_bsr', 'plot_cor', 'plot_cook', 'plot_intervals', 'plot_qq', 'plot_res',
    'hist_res', 'plots', 'plot_xy'
]
