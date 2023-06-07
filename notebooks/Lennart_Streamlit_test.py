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

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("Open positions in Germany")

st.sidebar.info(
    """
    Dash_Work Test for Streamlit>
    - GitHub repository: <https://github.com/LennartSchulze/Dash_Work>
    """
)

st.sidebar.title("Filters")
st.sidebar.info(
    """
    Add Filter here
    """
)
st.sidebar.selectbox("Select Sector", options=[1,2])



@st.cache_data()
def get_data():
    gdf = gpd.read_file("/Users/tmotzkus/Downloads/landkreise_simplify200.geojson")
    return gdf

gdf = get_data()

# @st.cache()
# def get_map(gdf):
#     m = folium.Map(location=[51, 9], tiles="cartodbpositron", zoom_start=6)
#     style = {"fill_color": "green", "opacity" : .5, "weight": 1,"color": "green", "fillOpacity": .5}
#     gjson = folium.GeoJson(data=gdf, style_function=lambda x:style).add_to(m)
#     popup=folium.GeoJsonPopup(fields=["einwohner"]).add_to(gjson)
#     return m


m = folium.Map(location=[51.1657, 10.4515], tiles="cartodbpositron", zoom_start=6)
style = {"fill_color": "green", "opacity" : .5, "weight": 1,"color": "green", "fillOpacity": .5}
gjson = folium.GeoJson(data=gdf, style_function=lambda x:style).add_to(m)
gjson.add_child(folium.features.GeoJsonTooltip(['GEN'],labels=False))

popup=folium.GeoJsonPopup(fields=["GEN"]).add_to(gjson)

st_folium(m, returned_objects=[],  width=600, height=600)


# def app():

#     m = get_map(gdf)
#     st_folium(m)

# app()
