import glob 
import os
import json

import streamlit as st
# import altair as alt
import numpy as np
import pandas as pd

# from scipy import stats
# from itertools import combinations
from colorutils import Color

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
# from matplotlib import font_manager
from statannotations.Annotator import Annotator

from streamlit_fcns import *


df = pd.read_excel(glob.glob(os.path.join(BEHAVIOR_ROOT, '2_3SPP*'))[0])
# df_TPP = pd.read_excel(glob.glob(os.path.join(BEHAVIOR_ROOT, '2_4TPP*'))[0])

# st.write(df_SPP)
# st.write(df_SPP)

json_file = './json/fig2_sub3.json'

## presets
params = {
         "title": 'SPP',
         "font_family": 'Times New Roman',
         "title_font_size": '15',
         "tick_font_size": '10',
         "annot_font_size": '12',
         "fig_height": '4',
         "fig_width": '4',
         'cbar_fraction': '0.14',
         'cbar_pad': '0.1',
         'cbar_shrink': '0.75',
         'cbar_fontsize': '10',
         'color1': '#e28743',
         'color2': '#1e81b0',
         'color3': '#38b01e',
         'edge_color': '#ffffff',
         'cmap': 'coolwarm',
         }

load_json = st.sidebar.selectbox("Choose a file to load parameter from", 
                                 options=glob.glob(os.path.join(os.path.dirname(json_file), '*.json')))
# load parameters from json
if st.sidebar.button("Load from saved json file"):
    tmp = json.load(open(load_json))
    params.update(tmp)
    # use update for compatibility



setup_cols = st.columns(3)

modified = {}

with setup_cols[0]:
    st.write('## Texts')

    modified['title'] = st.text_input('Plot title', value=params['title'])

    modified['font_family'] = st.selectbox('Font family', 
                                index=FONTS.index(params['font_family']),
                                options=FONTS)
    modified['title_font_size'] = st.slider('Title font size', 5, 30, int(params['title_font_size']))
    modified['tick_font_size'] = st.slider('Tick labels font size', 5, 30, int(params['tick_font_size']))
    # modified['axis_font_size'] = st.slider('Axis labels font size', 5, 30, int(params['axis_font_size']))
    modified['annot_font_size'] = st.slider('Annotation font size', 5, 30, int(params['annot_font_size']))
    

with setup_cols[1]:
    st.write('## Figure')
    modified['fig_height'] = st.text_input('Figure height', value=params['fig_height'])
    modified['fig_width'] = st.text_input('Figure width', value=params['fig_width'])
    assert float(modified['fig_height']) >= 0, "Height should be above zero and able to be interpreted as float"
    assert float(modified['fig_width']) >= 0, "Width should be above zero and able to be interpreted as float"
    
    show_ticks = st.checkbox("Show ticks (lines)?", value=True)
    show_half = st.checkbox("Only show lower half?", value=True)

    modified['cmap'] = st.selectbox(
        "Select a colormap", options=CMAPS,
        index=CMAPS.index(params['cmap']))
    
    if modified['cmap'] == "custom":
        st.write("Note: saturation will be averaged for balancing")
        modified['color1'] = st.color_picker('Color #1', params['color1'])
        modified['color2'] = st.color_picker('Color #2', params['color2'])

        h1, s1, _ = (Color(hex=modified['color1']).hsv)
        h2, s2, _ = (Color(hex=modified['color2']).hsv)
        # st.write(np.mean([s1,s2])*100)
        cmap = sns.diverging_palette(
            h_pos=h1, h_neg=h2, s=np.mean([s1,s2])*100, 
            center='light', as_cmap=True)

    else:
        cmap = modified['cmap']
    
    

with setup_cols[2]:
    st.write('## Colorbar')

    modified['cbar_pad'] = st.select_slider(
        "Select padding between heatmap and colorbar",
        options = np.round(np.arange(0.02, 0.22, 0.02), 2),
        value=float(params['cbar_pad'])
    )

    modified['cbar_fraction'] = st.select_slider(
        "Select fraction of the entire figure that the colorbar would take",
        options = np.round(np.arange(0.02, 0.22, 0.02), 2),
        value=float(params['cbar_fraction'])
    )

    modified['cbar_shrink'] = st.select_slider(
        "Select shrinkage on the colorbar",
        options = np.round(np.arange(0.05, 1.05, 0.05), 2),
        value=float(params['cbar_shrink'])
    )

    modified['cbar_fontsize'] = st.slider(
        'Colorbar font size', 5, 30, int(params['cbar_fontsize']))

    

sns.set_theme(font=modified['font_family'], style="whitegrid",
            # rc={"grid.color": str(modified['grid_color']), 
            #     "grid.linestyle": modified['grid_line_style'],
            #     "axes.edgecolor": str(modified['axis_color']),},
            )

fig, ax = plt.subplots(figsize=[4,4])

if show_half:
    mask = np.triu(df.corr())
else:
    mask=None

# st.write(df_TPP.corr())
ax = plot_corr_matrix(
    df, ticklabel_size=modified['tick_font_size'], 
    cbar_kws={
        "pad": modified['cbar_pad'], 
        "fraction": modified['cbar_fraction'], 
        "shrink": modified['cbar_shrink']
        }, 
    annot_size = modified["annot_font_size"],
    show_ticks=show_ticks, cmap=cmap,
    mask=mask
    )
ax.set_title(modified['title'], size=modified['title_font_size'])

cbar = ax.collections[0].colorbar
cbar.ax.tick_params(labelsize=modified['cbar_fontsize'])

st.pyplot(fig=fig)

for key in modified:
    modified[key] = str(modified[key])

st.write(modified)

if st.sidebar.button("Save values to json file"):
    
    with open(json_file, "w") as outfile:
        json.dump(modified, outfile, indent=4)
    
    # st.write('been here')
    st.sidebar.write(f"Parameters saved to {os.path.abspath(json_file)}")