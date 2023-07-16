import os

import numpy as np
import seaborn as sns

from scipy import stats

BEHAVIOR_ROOT = '../../../Studies/01_NumberData/Behaviordata/'
ROI_ROOT = '../../../Studies/01_NumberData/ROIs/'

FONTS = ['Arial', 'Times New Roman', 'Helvetica']
LINE_STYLES = ['-', ':', '--']
GRIDLINE_INTERVALS = [0.01, 0.02, 0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 5]
CMAPS = ["coolwarm", "vlag", "custom"]

def get_cond(conds, arr):
    # get the condition from arr (usually a string, haven't test other situation)
    for r in conds:
        if r in arr:
            return r
    # added this to prevent non-capitalized situation
    # didn't use this upfront because query could occur in 
    # unwanted fractions
    for r in conds:
        if r.lower() in arr.lower():
            return r
    raise NotImplementedError("Some conditions were not parsed, please check query strings if there are any typo")

# def num(str):
#     substr = re.sub("[^0-9]", "", str)
#     if len(substr) >= 2:
#         substr = substr[:2]
#     if int(substr) > 10:
#         substr = substr[0]
#     return re.sub("[^0-9]", "", substr)

def check_float(v):
    # check if variable can be interpreted as float
    try:
        float(v)
        return True
    except:
        return False


def plot_corr_matrix(data, annot_size = 16, ticklabel_size=12, 
                     calculation=stats.pearsonr, vlim=(-1, 1),
                     cbar_kws=None, show_ticks=True,
                     cmap='coolwarm', mask=None):
    # copied from neurolaw_plot.ipynb
    # slightly modified
    # define matrix
    
    labels = list(data.columns)
    corr_matrix = np.zeros((len(labels), len(labels)))
    p_matrix = np.zeros_like(corr_matrix)
    # calculate matrix
    for i, col_i in enumerate(labels):
        for j, col_j in enumerate(labels):
            # get correlation/difference
            corr_matrix[i, j], p_matrix[i, j] = calculation(data[col_i], data[col_j])
            p_matrix[i, j] = 1 if i == j else p_matrix[i, j]
    # plot matrix
    sig_annot = np.array([[("*" if p < 0.05 else "") + ("*" if p < 0.01 else "")\
        + ("*" if p < 0.001 else "") for p in row] for row in p_matrix])
    ax = sns.heatmap(corr_matrix, vmin=vlim[0], vmax=vlim[1], cmap=cmap, 
                     annot=sig_annot, annot_kws={"fontsize": annot_size}, fmt="", 
                     cbar_kws=cbar_kws, mask=mask,
                     square=True)
    # ax.set_title(title, fontsize=16)
    ax.set_xticklabels(labels=labels, fontsize=ticklabel_size, rotation=50, ha="right")
    # ax.yaxis.set_tick_params(rotation=0)
    ax.set_xticklabels(labels, fontsize=ticklabel_size)
    ax.set_yticklabels(labels, fontsize=ticklabel_size, rotation=0)
    ax.tick_params(left=show_ticks, bottom=show_ticks)

    return ax