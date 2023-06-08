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
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

st.set_page_config(layout="wide")

#### SIDE BAR ####

## INFORMATION ON PROJECT ##
st.sidebar.title("Dash/Work")
st.sidebar.write(
    '''
    This is a Dashboard to get an overview on the  labor market  in German regions. Based on currently open job postings, we calculate a score to measure the status of the labor market for each German district and city.
    ''')
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


#### BODY ####
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("Open positions in Germany")

## CHOOSE DATA BASE FOR MAP ##
chosen_map = f"{geo_level_options.index(geo_level)}{sector_options.index(sector)}{company_size_options.index(company_size)}{skill_level_options.index(skill_level)}"
## END OF CHOOSE DATA BASE FOR MAP ##

## GET THE GEO DATA FOR  THE MAP ##
@st.cache_data()
def get_map(chosen_map):
    if chosen_map == "0000":
        loadfile = "counties"
    if chosen_map =="1000":
        loadfile = "states"
    gdf = gpd.read_file(f"{loadfile}.geo.json")
    return gdf

gdf = get_map(chosen_map)
## END OF GETTING GEO DATA FOR THE MAP ##

## GET DATA FROM MASTER JOBS FILE ##
@st.cache_data()
def get_data():
    df = pd.read_csv("MOCK_MASTER_ALL_JOB.csv", sep=";")
    return df

df = get_data()
## END OF GET MASTER FILE DATA

## GET SCORE - CURRENTLY: ABSOLUTE NUMBER OF JOBS ONLINE PER GEO UNIT ##
if geo_level == "Bundeslaender":
    grouper_var = "bundesland"
    dropper_var = "landkreis"
else:
    grouper_var = "landkreis"
    dropper_var = "bundesland"

jobs_online = df.groupby(grouper_var).count().drop(columns=["arbeitgeber", "publication_date","hashId", "zip", dropper_var])
jobs_online = jobs_online.reset_index()

gdf.index = gdf["name"]
gdf[grouper_var] = gdf["name"]



m = folium.Map(location=[51.1657, 10.4515], tiles="cartodbpositron", zoom_start=6)

gjson = folium.Choropleth(
    geo_data=gdf,
    name="choropleth",
    data=jobs_online,
    columns=[grouper_var, "refnr"],
    key_on="feature.id",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=1,
    legend_name="Employment Status",
).add_to(m)

#Add Customized Tooltips to the map
folium.features.GeoJson(
                    data=gdf,
                    name='New Jobs Online',
                    smooth_factor=2,
                    style_function=lambda x: {'color':'black','fillColor':'transparent','weight':0.5},
                    tooltip=folium.features.GeoJsonTooltip(
                        fields=[grouper_var,
                                ],
                        #aliases=[grouper_var,
                        #        ],
                        localize=True,
                        sticky=False,
                        labels=True,
                        style="""
                            background-color: #F0EFEF;
                            border: 2px solid black;
                            border-radius: 3px;
                            box-shadow: 3px;
                        """,
                        max_width=100,),
                            highlight_function=lambda x: {'weight':3,'fillColor':'grey'},
                        ).add_to(m)


#folium.LayerControl().add_to(m) #UNNECESSARY IF WE ONLY HAVE ONE MEANINGFUL LAYER - MAYBE CUT + Sometimes Buggy

#output = st_folium(
#    m, width=700, height=500, returned_objects=["last_object_clicked"]
#    )


output = st_folium(m, returned_objects=["last_object_clicked"], width=600, height=600)
punkt = Point(output["last_object_clicked"]["lng"], output["last_object_clicked"]["lat"])

for i in range(len(gdf.geometry)):
    polygon = gdf.geometry[i]
    if polygon.contains(punkt):
        st.write("The point you clicked on is in", gdf.name[i])
