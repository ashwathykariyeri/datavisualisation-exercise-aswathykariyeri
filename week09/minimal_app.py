#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
World Happiness Dashboard (corrected version)

Run it from a terminal with:
    streamlit run minimal_app.py
"""

import streamlit as st          # Streamlit turns this script into a web page
import pandas as pd             # pandas reads the CSV into a table (DataFrame)
import plotly.express as px     # Plotly Express draws the interactive chart
from pathlib import Path        # Path builds file locations safely on any computer


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
# set_page_config MUST be the first Streamlit command in the script.
st.set_page_config(page_title="World Happiness Report", page_icon="🌐", layout="wide")
st.title("🌍 World Happiness Dashboard")           # big heading at the top
st.caption("Source: World Happiness Report 2023 | Kaggle")  # small grey text


# ---------------------------------------------------------------------------
# Data ingestion (this is the part that caused the FileNotFoundError)
# ---------------------------------------------------------------------------
FILE_NAME = "world_happiness_2023.csv"   # the exact name of your CSV file
HERE = Path(__file__).resolve().parent   # the folder that contains THIS script

# Instead of guessing one location, we list the places the file could be.
# Python checks them in order and uses the first one that really exists.
CANDIDATES = [
    HERE / "data" / FILE_NAME,           # data/ folder next to the script
    HERE.parent / "data" / FILE_NAME,    # data/ folder one level above the script
    HERE / FILE_NAME,                    # CSV sitting right next to the script
]

DATA = next((p for p in CANDIDATES if p.exists()), None)  # first match, or None

# If nothing matched, show a clear message on the page and stop,
# instead of crashing with a long red error.
if DATA is None:
    st.error(f"Could not find {FILE_NAME}. I looked in:")
    for p in CANDIDATES:                 # list each place we checked
        st.code(str(p))
    st.stop()                            # stop running the rest of the script


# @st.cache_data remembers the loaded table, so Streamlit does not
# re-read the file every time you click a filter.
@st.cache_data
def load_data(path):
    data = pd.read_csv(path)             # read the CSV into a table
    return data

df = load_data(DATA)

# Rename the columns to short, easy names.
# This only works if the CSV has exactly 9 columns in this order,
# so we check first and show a helpful message if it does not.
NEW_COLUMNS = ["Country", "Region", "Score", "GDP", "Social_Support",
               "Life_Expectancy", "Freedom", "Generosity", "Corruption"]

if len(df.columns) != len(NEW_COLUMNS):
    st.error(f"Expected {len(NEW_COLUMNS)} columns but found {len(df.columns)}:")
    st.write(list(df.columns))           # show the real column names
    st.stop()

df.columns = NEW_COLUMNS                 # apply the new names


# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
with st.sidebar:                                         # everything inside appears on the left
    st.header("Filters")
    regions = ["All Regions"] + sorted(df["Region"].unique().tolist())  # unique regions, A to Z
    selected_region = st.selectbox("Region", regions)    # dropdown menu
    top_n = st.slider("Show top N", 5, 25, 15)           # slider: min 5, max 25, start 15


# ---------------------------------------------------------------------------
# Filter the data
# ---------------------------------------------------------------------------
# If "All Regions" is chosen keep every row, otherwise keep only that region.
filtered = df if selected_region == "All Regions" else df[df["Region"] == selected_region]

# Take the N highest scores, then sort low to high so the best country
# appears at the TOP of the horizontal bar chart.
top = filtered.nlargest(top_n, "Score").sort_values("Score")


# ---------------------------------------------------------------------------
# KPI row (three headline numbers)
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)                         # three equal columns

col1.metric("Countries", len(filtered))                  # how many countries are shown

avg_filtered = filtered["Score"].mean()                  # average score of the selection
avg_global = df["Score"].mean()                          # average score of everyone
col2.metric("Avg Score", f"{avg_filtered:.2f}",
            f"{avg_filtered - avg_global:+.2f} vs global")  # + or - difference

happiest = filtered.nlargest(1, "Score")["Country"].values[0]  # name of the top country
col3.metric("Happiest", happiest)

st.divider()                                             # thin horizontal line


# ---------------------------------------------------------------------------
# Bar chart
# ---------------------------------------------------------------------------
fig = px.bar(
    top,
    x="Score",                                           # bar length = happiness score
    y="Country",                                         # one bar per country
    orientation="h",                                     # horizontal bars
    labels={"Score": "Happiness Score (0–10)", "Country": ""},
    template="plotly_white",                             # clean white background
    title=f"Happiest {top_n} Countries in 2023 - {selected_region}",
)

fig.update_layout(
    title_font=dict(family="Arial", size=13, color="slategrey"),
    xaxis=dict(range=[0, 8.0]),                          # fixed axis so bars are comparable
    height=600,                                          # chart height is set HERE, not in st.plotly_chart
)

# width="stretch" fills the page width. "height" is not an st.plotly_chart
# argument, so it was removed from this line.
st.plotly_chart(fig, width="stretch")

st.divider()
st.caption("Built with Streamlit + Plotly")
