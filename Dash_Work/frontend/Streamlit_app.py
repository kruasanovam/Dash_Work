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
import plotly.express as px
from google.cloud import storage

api_url = st.secrets["api_url"]

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
## END OF CHOOSE DATA BASE FOR MAP ##
#### END OF SIDEBAR ####


## GET THE GEO DATA FOR THE MAP ##
@st.cache_data()
def get_map(geolevel):
    bucket_name = "dash_work_masha"

    pathdata = os.path.dirname(os.path.abspath(__file__))
    if geolevel == "Districts and Cities":
        loadfile = "counties"

    if geolevel =="Bundeslaender":
        loadfile = "states"

    source_blob_name = f"{loadfile}.geo.json"

    gdf = gpd.read_file(os.path.join(pathdata, "..", "..", "data","raw_generated", source_blob_name))
    return gdf

gdf = get_map(geo_level)
## END OF GEO DATA FOR MAP ##

## GET COLORS FOR CHOROPLETH MAP ##
@st.cache_data()
def get_map_data(geo_level):
    if geo_level=="Districts and Cities":
        filter_variable = "landkreis"
    if geo_level=="Bundeslaender":
        filter_variable = "bundesland"
    url = f"{api_url}/maps"
    params = {"grouper_var": filter_variable}
    response = requests.get(url, params).json()["result"]
    response = pd.read_json(response)
    return response, filter_variable

map_colors, filter_variable = get_map_data(geo_level)

map_colors["NumberofJobs"] = map_colors["num_jobs"].astype(float)

try:
    map_colors["landkreis"] = map_colors["landkreis_georef"]
except:
    pass

## FINISH GET COLORS FOR CHOROPLETH

#### BODY ####
pathbody = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(pathbody, "style.css")) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("Open positions in Germany")

col1, col2 = st.columns(2)

### Column 1

with col1:

    # ## GET SCORE - CURRENTLY: ABSOLUTE NUMBER OF JOBS ONLINE PER GEO UNIT ##
    if geo_level == "Bundeslaender":
         grouper_var = "bundesland"
         dropper_var = "landkreis"
    else:
         grouper_var = "landkreis"
         dropper_var = "bundesland"

    gdf.index = gdf["name"]
    gdf[grouper_var] = gdf["name"]

    #### MAP ####
    m = folium.Map(location=[51.1657, 10.4515], tiles="cartodbpositron", zoom_start=5.5, width="100%", height=400)

    print ()

    gjson = folium.Choropleth(
        geo_data=gdf,
        name="choropleth",
        # data=jobs_online,
        # columns=[grouper_var, "refnr"],
        data=map_colors,
        columns=[grouper_var, "NumberofJobs"],
        key_on="feature.properties.name",
        fill_color="Blues",
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
                            aliases=[" ",
                                ],
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

    # ## GET CLICK ON GEO UNIT ##

    output = st_folium(m, returned_objects=["last_object_clicked"], width="100%", height=600)

    if output["last_object_clicked"] is not None:
        punkt = Point(output["last_object_clicked"]["lng"], output["last_object_clicked"]["lat"])

        for i in range(len(gdf.geometry)):
            polygon = gdf.geometry[i]
            if polygon.contains(punkt):
                st.write("The point you clicked on is in", gdf.name[i])
                filter_var = gdf.name[i]

    ## END OF GET CLICK ON GEO UNIT ##
        params = {"grouper_var": grouper_var,
                        "filter_var": filter_var
                    }
        #### COLUMN 2 DASHBOARD TILES ####

        with col2:
            df_filtered_employer = requests.get(f"{api_url}/top_5_employers/", params=params).json()["result"]
            df_filtered_employer = pd.read_json(df_filtered_employer)

            df_filtered_branchengruppe = requests.get(f"{api_url}/top_5_branchengruppe/", params=params).json()["result"]
            df_filtered_branchengruppe = pd.read_json(df_filtered_branchengruppe)

            #num_of_jobs = map_colors[map_colors[filter_var]==filter_var]["NumberofJobs"]

            # with st.container():
            #     st.write(f"""<div class='cards'/><b>{filter_var}</b><br>
            #             Open jobs: {map_colors["NumberofJobs"]}</div>""", unsafe_allow_html=True)

            with st.container():
                listTabs = ["Top Employers", "New Jobs Over Time", "Top Sectors","Company Sizes"]
                whitespace = 15
                tabs = st.tabs([s.center(whitespace,"\u2001") for s in listTabs])
                with tabs[0]:
                    st.write(f"""<b>Employers with most job offers in {filter_var}</b>""", unsafe_allow_html=True)
                    plot_employer = px.bar(df_filtered_employer, x="arbeitgeber", y="refnr", width=490, height=350, text_auto=True)
                    plot_employer.update_layout(
                        #paper_bgcolor="#EFF2F6",
                        #plot_bgcolor="#EFF2F6",
                        xaxis_title=None,
                        yaxis_title=None,
                            )
                    plot_employer.update_traces(
                        marker_color="#09316B"
                            )

                    st.plotly_chart(plot_employer, use_container_width=True)

                with tabs[1]:
                    st.write(f"""<b>New jobs in {filter_var} over the last 5 years</b>""", unsafe_allow_html=True)

                    df_filtered_pubdate = requests.get(f"{api_url}/pub_date/", params=params).json()["result"]
                    df_filtered_pubdate = pd.read_json(df_filtered_pubdate)


                    plot_pubdate = px.line(df_filtered_pubdate, x="aktuelleVeroeffentlichungsdatum", y="refnr", width=500, height=350)
                    plot_pubdate.update_layout(
                        #paper_bgcolor="#EFF2F6",
                        #plot_bgcolor="#EFF2F6",
                        xaxis_title=None,
                        yaxis_title=None,
                            )
                    plot_pubdate.update_traces(
                        marker_color="#09316B"
                            )
                    st.plotly_chart(plot_pubdate, use_container_width=True)

                with tabs[2]:
                    st.write(f"""<b>Sectors with most job offers in {filter_var}</b>""", unsafe_allow_html=True)
                    plot_sector = px.bar(df_filtered_branchengruppe, x="branchengruppe", y="refnr", width=500, height=350, text_auto=True)
                    plot_sector.update_layout(
                        #paper_bgcolor="#EFF2F6",
                        #plot_bgcolor="#EFF2F6",
                        xaxis_title=None,
                        yaxis_title=None,
                            )
                    plot_sector.update_traces(
                        marker_color="#09316B"
                        )

                    plot_sector.add_annotation(
                    x="Sector",
                    xref="x",
                    yref="y",
                    font=dict(
                        family="Courier New, monospace",
                        size=16,
                        color="#ffffff"
                        ),
                        )

                    st.plotly_chart(plot_sector, use_container_width=True)

                with tabs[3]:
                    st.write(f"""<b>Split of jobs in {filter_var} based on company size</b>""", unsafe_allow_html=True)
                    plot_size = px.bar(df_filtered_employer, x="arbeitgeber", y="refnr", width=500, height=350, text_auto=True)
                    plot_size.update_layout(
                        #paper_bgcolor="#EFF2F6",
                        #plot_bgcolor="#EFF2F6",
                        xaxis_title=None,
                        yaxis_title=None,
                            )
                    plot_size.update_traces(
                        marker_color="#09316B"
                    )

                    st.plotly_chart(plot_size, use_container_width=True)

# except NameError:
#     st.write("")
