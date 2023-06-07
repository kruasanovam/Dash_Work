import streamlit as st
from leafmap import leafmap



m = leafmap.Map()
url = "https://raw.githubusercontent.com/opengeos/leafmap/master/examples/data/us_cities.geojson"
m.add_point_layer(url, popup=["name", "pop_max"], layer_name="US Cities")
m