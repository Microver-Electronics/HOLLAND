import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
from PIL import Image
import numpy as np
import pandas as pd
import datetime
import math
from streamlit.components.v1 import html
import plotly.graph_objects as go
import pydeck as pdk
import os
from datetime import timedelta
from datetime import datetime as dt
import time

st.set_page_config(layout="wide")
st.markdown("<div id='linkto_top'></div>", unsafe_allow_html=True)
st.markdown( f"""
<style>
    #MainMenu {{visibility: hidden;}}
	.css-1dp5vir {{
    position: absolute;
    top: 0px;
    right: 0px;
    left: 0px;
    height: 0.125rem;
    background-image: linear-gradient(90deg, rgba(40,94,174,255), rgba(20,190,241,255));
    z-index: 999990;
}}
    p {{
    font-size: 1.5rem !important;
}}

    i {{
        color: white;
}}
    
    i:hover {{
        color: #14bef1;
}}
</style>
""", unsafe_allow_html=True)

holland_logo = Image.open('./images/holland.png')


st.image(holland_logo, width=350)
st.markdown("**_Deuta Radar Post-processing Tool_**")
st.write('<p style="color:#8a8a8a;"><em>v 1.1.3</em></p>',
unsafe_allow_html=True)

def corrupt_data_drs42(v, props=''):
    return props if len(v) != 27 else None

st.text("")

uploaded_files_dr42 = st.file_uploader("Load a DR42 or DR08 CSV file for visualization", accept_multiple_files=True)
for uploaded_file_dr42 in uploaded_files_dr42:
    try:
        data = pd.read_csv(uploaded_file_dr42)

        if((data["Radar Message"][0][0] == "#") or (data["Radar Message"][1][0] == "#") or (data["Radar Message"][2][0] == "#") or (data["Radar Message"][3][0] == "#")):
            st.write("filename:", uploaded_file_dr42.name)

            speed_tab, distance_tab, rms_tab, map_tab = st.tabs(["Speed Over Time", "Distance Over Time", "RMS", "Map"])

            data.loc[(data['Masked Status Byte'] == 0), 'Data State'] = 'Invalid'
            data.loc[(data['Radar Message'].str.len() != 27), 'Data State'] = 'Invalid'

            data_corrupt = data[data['Data State'] == "Invalid"]
            data_correct = data[data['Data State'] == "Valid"]

            with speed_tab:

                fine_x = [xi for xi, s in zip(data["Timestamp"], data["Data State"]) if s == "Valid"]
                fine_y = [yi for yi, s in zip(data["Speed"], data["Data State"]) if s == "Valid"]
                incorrect_x = [xi for xi, s in zip(data["Timestamp"], data["Data State"]) if s == "Invalid"]
                incorrect_y = [yi for yi, s in zip(data["Speed"], data["Data State"]) if s == "Invalid"]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=fine_x, y=fine_y, mode="markers+lines", name="Valid", hoverinfo='text',
                                         text=["Status Byte: {}<br>Speed: {}<br>Timestamp: {}".format(sb, speed, ts)
                                               for sb, speed, ts in
                                               zip(data_correct["Status Byte"], data_correct["Speed"],
                                                   data_correct["Timestamp"])]))
                fig.add_trace(go.Scatter(x=incorrect_x, y=incorrect_y, mode="markers", name="Invalid",
                                         line=dict(color="red"), hoverinfo='text',
                                         text=["Status Byte: {}<br>Speed: {}<br>Timestamp: {}".format(sb, speed, ts)
                                               for sb, speed, ts in
                                               zip(data_corrupt["Status Byte"], data_corrupt["Speed"],
                                                   data_corrupt["Timestamp"])]))

                fig.update_layout(
                    xaxis_title='Date',
                    yaxis_title='Speed (km/h)'
                )

                st.plotly_chart(fig, use_container_width=True)
            with distance_tab:
                fine_x = [xi for xi, s in zip(data["Timestamp"], data["Data State"]) if s == "Valid"]
                fine_y = [yi for yi, s in zip(data["Distance"], data["Data State"]) if s == "Valid"]
                incorrect_x = [xi for xi, s in zip(data["Timestamp"], data["Data State"]) if s == "Invalid"]
                incorrect_y = [yi for yi, s in zip(data["Distance"], data["Data State"]) if s == "Invalid"]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=fine_x, y=fine_y, mode="markers+lines", name="Valid", hoverinfo='text',
                                         text=["Status Byte: {}<br>Distance: {}<br>Timestamp: {}".format(sb, speed,
                                                                                                         ts) for
                                               sb, speed, ts in
                                               zip(data_correct["Status Byte"], data_correct["Distance"],
                                                   data_correct["Timestamp"])]))
                fig.add_trace(go.Scatter(x=incorrect_x, y=incorrect_y, mode="markers", name="Invalid",
                                         line=dict(color="red"), hoverinfo='text',
                                         text=["Status Byte: {}<br>Distance: {}<br>Timestamp: {}".format(sb, distance, ts)
                                               for sb, distance, ts in
                                               zip(data_corrupt["Status Byte"], data_corrupt["Distance"],
                                                   data_corrupt["Timestamp"])]))

                fig.update_layout(
                    xaxis_title='Date',
                    yaxis_title='Distance (meter)'
                )

                st.plotly_chart(fig, use_container_width=True)



            with rms_tab:
                fine_x = [xi for xi, s in zip(data["Timestamp"], data["Data State"]) if s == "Valid"]
                fine_y = [yi for yi, s in zip(data["RMS"], data["Data State"]) if s == "Valid"]
                incorrect_x = [xi for xi, s in zip(data["Timestamp"], data["Data State"]) if s == "Invalid"]
                incorrect_y = [yi for yi, s in zip(data["RMS"], data["Data State"]) if s == "Invalid"]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=fine_x, y=fine_y, mode="markers+lines", name="Valid", hoverinfo='text',
                                         text=["Status Byte: {}<br>RMS: {}<br>Timestamp: {}".format(sb, rms, ts)
                                               for sb, rms, ts in
                                               zip(data_correct["Status Byte"], (data_correct["RMS"]),
                                                   data_correct["Timestamp"])]))
                fig.add_trace(go.Scatter(x=incorrect_x, y=incorrect_y, mode="markers", name="Invalid",
                                         line=dict(color="red"), hoverinfo='text',
                                         text=["Status Byte: {}<br>RMS: {}<br>Timestamp: {}".format(sb, rms, ts)
                                               for sb, rms, ts in
                                               zip(data_corrupt["Status Byte"], data_corrupt["RMS"],
                                                   data_corrupt["Timestamp"])]))

                fig.update_layout(
                    xaxis_title='Date',
                    yaxis_title='RMS'
                )

                st.plotly_chart(fig, use_container_width=True)

            with map_tab:
                try:

                    chart_data = pd.DataFrame(data[["Latitude", "Longitude", "Data State", "Status Byte", "Speed", "Distance", "RMS"]].values.tolist(),
                                              columns=['lat', 'lon', 'ds', 'sb', 's', 'd', 'rms'])
                    valid_data = chart_data[chart_data['ds'] == 'Valid']
                    valid_data = valid_data.dropna()
                    valid_data = valid_data.reset_index(drop=True)

                    invalid_data = chart_data[chart_data['ds'] == 'Invalid']
                    invalid_data = invalid_data.dropna()
                    invalid_data = invalid_data.reset_index(drop=True)

                    st.pydeck_chart(pdk.Deck(
                            map_provider="mapbox",
                            map_style="satellite",
                            initial_view_state=pdk.ViewState(
                            latitude=valid_data["lat"][0],
                            longitude=valid_data["lon"][0],
                            zoom=19,
                        ),

                        layers=[pdk.Layer('ScatterplotLayer', data=valid_data, get_position='[lon, lat]',
                                          get_color='[20, 190, 241]', get_radius=0.5,
                                          pickable=True, auto_highlight=True,
                                          ),
                                pdk.Layer('ScatterplotLayer', data=invalid_data, get_position='[lon, lat]',
                                          get_color='[255, 0, 0]', get_radius=0.5,
                                          pickable=True, auto_highlight=True,
                                          )
                                ],
                        tooltip={
                            'html': '<b>Speed:</b> {s} <br> <b>Distance:</b> {d} <br> <b>RMS:</b> {rms} <br> <b>Status Byte:</b> {sb} <br> <b>Data State:</b> {ds} <br>',
                            'style': {
                                'color': 'white'
                            }
                        }
                    ))

                except:
                    st.write("No gps data was found for this csv.")

            data = data.dropna(axis=1, how="all")
            data = data.drop(["Masked Status Byte"], axis=1)

            st.dataframe(data, use_container_width=True)

        else:
            st.write("PLEASE LOAD A DR42 OR DR8 CSV FILE")

    except:
        st.write("PLEASE LOAD A DR42 OR DR8 CSV FILE")
        pass
