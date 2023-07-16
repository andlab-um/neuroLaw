import glob 
import os
import json

import streamlit as st
# import altair as alt

import numpy as np
import pandas as pd
from scipy import stats
from itertools import combinations

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager
from statannotations.Annotator import Annotator

from streamlit_fcns import *

"""
customize parts
"""
hatches=[' ', '//', ' ','//']

data_file = glob.glob(os.path.join(BEHAVIOR_ROOT, '1_4*'))[0]
df = pd.read_excel(data_file)
# df = df.reset_index(drop=True)
df = df.reset_index(drop=False)
df = df.rename(columns={'index': 'trial', 'Emo-immediate':'Emo-Immediate'})

# st.write(df)

df_long = df.melt(id_vars=['trial', 'Group'], var_name='variable', value_name='value')

rewards = ['Immediate', 'Delayed']
# # offense = ['Mis', 'Fel', 'Cap']
df_long['rewards'] = [get_cond(rewards, v) for v in df_long['variable']]
# st.write(df_long)


json_file = './json/fig1_sub4.json'
## presets
params = {"x_axis_label": 'Group',
         "y_axis_label": 'Degree of Punishment',
         "legend_title": 'Time',
         "font_family": 'Times New Roman',
         "tick_font_size": '12',
         "axis_font_size": '15',
         "axis_color": '0.9',
         "grid_color": '0.9',
         "grid_line_style": '-',
         "fig_height": '4',
         "fig_width": '4',
         'color1': '#e28743',
         'color2': '#1e81b0',
         'color3': '#38b01e',
         'edge_color': '#ffffff',
         'ci': '95',
         'capsize': '0.08',
         'errwidth': '1.1',
         'errcolor': '#000000',
         'ylim_lower': '0',
         'ylim_upper': '9',
         'grid_line_interval': '1'
         }

load_json = st.sidebar.selectbox("Choose a file to load parameter from", 
                                 options=glob.glob(os.path.join(os.path.dirname(json_file), '*.json')))
# load parameters from json
if st.sidebar.button("Load from saved json file"):
    tmp = json.load(open(load_json))
    params.update(tmp)
    # use update for compatibility


x = 'Group'
hue = 'rewards'
y = 'value'

order = pd.unique(df_long[x])
hue_order = pd.unique(df_long[hue])


setup_cols = st.columns(4)

modified = {}

with setup_cols[0]:
    st.write('## Texts')

    modified['x_axis_label'] = st.text_input('x-axis label', value=params['x_axis_label'])
    modified['y_axis_label'] = st.text_input('y-axis label', value=params['y_axis_label'])
    modified['legend_title'] = st.text_input('legend title', value=params['legend_title'])

    
    modified['font_family'] = st.selectbox('Font family', 
                                index=FONTS.index(params['font_family']),
                                options=FONTS)
    modified['tick_font_size'] = st.slider('Tick labels font size', 5, 30, int(params['tick_font_size']))
    modified['axis_font_size'] = st.slider('Axis labels font size', 5, 30, int(params['axis_font_size']))
    # legend_font_size = st.slider('Legend font size', 5, 40, 15)

with setup_cols[1]:
    st.write('## Figure')
    
    modified['grid_line_interval'] = st.select_slider(
        "Grid line interval", options = GRIDLINE_INTERVALS,
        value = float(params['grid_line_interval']) 
    )

    modified['grid_line_style'] = st.selectbox('Grid line style', options=LINE_STYLES, 
                                   index=LINE_STYLES.index(params['grid_line_style']))
    
    modified['fig_height'] = st.text_input('Figure height', value=params['fig_height'])
    modified['fig_width'] = st.text_input('Figure width', value=params['fig_width'])
    # modified['ylim_lower'] = st.text_input('y axis lower limit', value=params['ylim_lower'])
    ylim = st.select_slider(
        'Range for y-axis', 
        options=np.round((np.arange(0,np.ceil(np.max(df_long[y]))+1,0.5)),1), 
        value = (float(params['ylim_lower']), float(params['ylim_upper'])))
    # st.write(ylim)
    modified['ylim_lower'] = ylim[0]
    modified['ylim_upper'] = ylim[1]
    assert float(modified['fig_height']) >= 0, "Height should be above zero and able to be interpreted as float"
    assert float(modified['fig_width']) >= 0, "Width should be above zero and able to be interpreted as float"
    # assert check_float(modified['ylim_lower']), "Lower limit should be able to be interpreted as float"


with setup_cols[2]:
    st.write('## Color')
    st.write('[color picker](https://imagecolorpicker.com/)')

    modified['color1'] = st.color_picker('Color #1', params['color1'])
    modified['color2'] = st.color_picker('Color #2', params['color2'])
    modified['color3'] = st.color_picker('Color #3', params['color3'])
    modified['edge_color'] = st.color_picker('Edge color', params['edge_color'])

    modified['axis_color'] = st.select_slider('Asix edge color (-> white)', 
                                  options=np.round((np.arange(0,1.1,0.1)),1),
                                  value=float(params['axis_color']))
    modified['grid_color'] = st.select_slider('Grid line color (-> white)', 
                                  options=np.round((np.arange(0,1.1,0.1)),1),
                                  value=float(params['grid_color']))
    
    bool_hatch = st.checkbox("Plot hatches?", value=False)

with setup_cols[3]:
    st.write("## Significance")

    annot = st.checkbox("In-graph significance")
    err_bar = st.checkbox("Error bar")
    modified['ci'] = st.select_slider('Confidence interval (%)', 
                                options=np.round((np.arange(80,105,5)),0),
                                value=int(params['ci']))
    modified['capsize'] = st.select_slider('Capsize (horizontal line length)', 
                                options=np.round((np.arange(0,0.22,0.02)),2),
                                value=float(params['capsize']))
    modified['errwidth'] = st.select_slider('Error bar line width', 
                                options=np.round((np.arange(0.1,2.1,0.1)),1),
                                value=float(params['errwidth']))
    modified['errcolor'] = st.color_picker('Error bar color', params['errcolor'])
    if err_bar:
        ci = modified['ci']
    else:
        ci = None


custom_palette = sns.color_palette([modified['color1'], modified['color2'], modified['color3']])

# sns.set_style()
sns.set_theme(font=modified['font_family'], style="whitegrid",
            rc={"grid.color": str(modified['grid_color']), 
                "grid.linestyle": modified['grid_line_style'],
                "axes.edgecolor": str(modified['axis_color']),},
            )

plot = sns.catplot(kind="bar", x=x, hue=hue, y=y, 
                   order=order, hue_order=hue_order,
                   data=df_long, palette=custom_palette, 
                   height=float(modified['fig_height']),
                   aspect=float(modified['fig_width'])/float(modified['fig_height']),
                   legend=True, legend_out=True, edgecolor=modified['edge_color'],
                   ci=ci, capsize=modified['capsize'], 
                   errcolor=modified['errcolor'], errwidth=modified['errwidth'])

# plot.ax.set_ylim()
if bool_hatch:
    bars = plot.axes[0][0].patches
    for pat,bar in zip(hatches,bars):
        bar.set_hatch(pat)

yticks = np.round(np.arange(
    ylim[0], ylim[1]+modified['grid_line_interval']/2, modified['grid_line_interval']),2)
plot.set(ylim=ylim, yticks=yticks)

plot.set_axis_labels(x_var=modified['x_axis_label'], y_var=modified['y_axis_label'])
plot.set_xticklabels(size=modified['tick_font_size'])
plot.set_yticklabels(yticks, size=modified['tick_font_size'])
plot.set_xlabels(size=modified['axis_font_size'])
plot.set_ylabels(size=modified['axis_font_size'])
# axes = plot.axes
# axes[0,0].set_ylim((float(modified['ylim_lower']), None))


if annot:
    # st.write("NOTE: Had to use t-test_ind as n(TPP)!=n(SPP)")
    pairs = [[(o, ho) for ho in hue_order] for o in order]
    # st.write(pairs)
    annotator = Annotator(ax=plot.ax, data=df_long, pairs=pairs,
                        x=x, hue=hue, y=y, 
                        order=order, hue_order=hue_order)
    annotator.configure(test="t-test_paired", text_format="star", loc="inside")
    annotator.apply_and_annotate()

legend = plot.legend
legend.set_title(modified['legend_title'])
# legend.set_fontsize(legend_font_size)
# plt.setp(legend.get_texts(), fontsize=legend_font_size) 
st.pyplot(fig=plot)

for key in modified:
    modified[key] = str(modified[key])

st.write(modified)

if st.sidebar.button("Save values to json file"):
    
    with open(json_file, "w") as outfile:
        json.dump(modified, outfile, indent=4)
    
    # st.write('been here')
    st.sidebar.write(f"Parameters saved to {os.path.abspath(json_file)}")

