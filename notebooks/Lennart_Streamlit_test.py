import datetime
import os
import pathlib
import requests
import zipfile
import pandas as pd
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide")

#### SIDE BAR ####

## INFORMATION ON PROJECT ##
st.sidebar.title("Dash/Work")
st.sidebar.write(
    '''
    This is a Dashboard to get an overview on the  labor market  in German regions. Based on currently open job postings, we calculate a score to measure the status of the labor market for each German district and city.
    '''

)
st.sidebar.write("Find our team and contact information here: [GitHub Repository](https://github.com/LennartSchulze/Dash_Work)")
## END OF INFORMATION ON PROJECT ##


## OPTIONS ##
st.sidebar.title("Options")

geo_level_options = ["Districts and Cities", "Bundeslaender"]
geo_level_default = geo_level_options.index("Districts and Cities") #set default
geo_level = st.sidebar.selectbox("Choose geographical level", options=geo_level_options, index=geo_level_default)

sector_options = ["All Sectors", "Sector1","Sector2"]
sector_default = sector_options.index("All Sectors") #set default
sector = st.sidebar.selectbox("Focus on a specific sector", options=sector_options, index=sector_default)

company_size_options = ["All Companies", "0-5 employees","6-20 employees", "20-200 employees","more than 200 employees"]
company_size_default = company_size_options.index("All Companies") #set default
company_size = st.sidebar.selectbox("Focus on a specific company size", options=company_size_options, index=company_size_default)

skill_level_options = ["All Levels", "University Education", "Vocational Training", "No Training required"]
skill_level_default = skill_level_options.index("All Levels")
skill_level = st.sidebar.selectbox("Focus on a specific skill level", options=skill_level_options, index=skill_level_default)
## END OF OPTIONS ##

#### END OF SIDEBAR ####

#### MAP ####

## CHOOSE DATA BASE FOR MAP ##
chosen_map = f"{geo_level_options.index(geo_level)}{sector_options.index(sector)}{company_size_options.index(company_size)}{skill_level_options.index(skill_level)}"
st.write(chosen_map)
## END OF CHOOSE DATA BASE AND MAP ##


@st.cache_data()
def get_data(chosen_map):
    if chosen_map == "0000":
        loadfile = "plz-5stellig"
    gdf = gpd.read_file(f"{loadfile}.geojson")
    return gdf

gdf = get_data(chosen_map)
st.write(gdf.einwohner)
