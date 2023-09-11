## User guide

Install required packages before run

```shell
pip install -r requirements.txt
```

This installs the required packages to run the visualization code (most important would be seaborn and streamlit)

For running, enter the `streamlit` folder first, then run `streamlit run index.py` in shell:

```shell
cd streamlit
streamlit run index.py
```

Then select subplot on the left sidebar. The indexes (names) are given based on the slideshow, which might be changed in the process, please check content before proceding.

On each subpage of the visualization, one can customize multiple aspects of that visualization. 

## Sidebar (left)

select pages

load and save parameters: if the satisfied with current setting, parameters can be saved using 'save values to json file' for future reference; click on 'load from saved json file' to load the saved parameters (NOTE: there's only one saving slot!)

## Main plotting section

Upper section: parameter selection; each selection has a default value in the code. In general, only in-graph significance and error bar needs to be changed for most of the plots.

Middle section: the plot based on parameters. Right click (and select corresponding tab) to save image

Lower section: a summary of all parameters, this should always be the same as what's selected in the upper section. This is also what's stored in the json file.

