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
st.write('<p style="color:#8a8a8a;"><em>v 1.1.0</em></p>',
unsafe_allow_html=True)




def corrupt_data_drs05(v, props=''):
    return props if len(v) != 26 else None

def corrupt_data_drs42(v, props=''):
    return props if len(v) != 27 else None

st.text("")
drs05_tab, dr42_tab = st.tabs(["DRS05", "DR42/DR8"])

with drs05_tab:
    uploaded_files_drs05 = st.file_uploader("Load a DRS05 CSV file for visualization", accept_multiple_files=True)
    for uploaded_file_drs05 in uploaded_files_drs05:
        try:
            data = pd.read_csv(uploaded_file_drs05)

            if ((data["Radar Message"][0][0] != "#") or (data["Radar Message"][1][0] != "#") or (data["Radar Message"][2][0] != "#") or (data["Radar Message"][3][0] != "#") or (data["Radar Message"][4][0] != "#")):

                data_first_drs05 = data.copy()
                st.write("filename:", uploaded_file_drs05.name)

                data["Speed"] = 0
                data["Distance"] = 0
                data["Status Byte"] = 0
                data["Data State"] = "Valid"

                for i in range(len(data)):
                    try:
                        speed = data["Radar Message"][i][4:8]
                        speed = int(speed, base=16)

                        speed = (speed * 600) / 65535
                        data["Speed"][i] = speed

                        distance_counter = data["Radar Message"][i][8:14]
                        distance_counter = int(distance_counter, base=16)
                        distance_counter = distance_counter / 100
                        data["Distance"][i] = distance_counter

                        status_byte = data["Radar Message"][i][22:24]
                        ini_string = status_byte
                        n = int(ini_string, 16)
                        bStr = ''
                        while n > 0:
                            bStr = str(n % 2) + bStr
                            n = n >> 1
                        res = bStr

                        data["Status Byte"][i] = "0x" + data["Radar Message"][i][22:24] + ", " + "0b" + res
                    except:
                        pass

                counter = 0

                for j in list(data["Timestamp"].unique()):
                    for i in range(len(data.loc[data['Timestamp'] == j])):
                        time = data["Timestamp"][counter].split(" ")[3].split(":")
                        split_second = 60 / (len(data.loc[data['Timestamp'] == j]) + i)
                        date = datetime.datetime(int(data["Timestamp"][counter].split(" ")[-1]),
                                                 2,
                                                 int(data["Timestamp"][counter].split(" ")[2]),
                                                 int(time[0]),
                                                 int(time[1]),
                                                 int(time[2]),
                                                 int((split_second * 10000) * i))

                        data["Timestamp"][counter] = date

                        counter += 1


                data['Status Byte'] = data['Status Byte'].astype(str)


                speed_tab, distance_tab = st.tabs(["Speed Over Time", "Distance Over Time"])

                data.loc[data['Radar Message'].str.len() != 26, 'Data State'] = 'Invalid'
                data_corrupt = data[data['Radar Message'].str.len() != 26]
                data_correct = data[data['Radar Message'].str.len() == 26]




                with speed_tab:
                    fine_x = [xi for xi, s in zip(data["Timestamp"], data["Data State"]) if s == "Valid"]
                    fine_y = [yi for yi, s in zip(data["Speed"], data["Data State"]) if s == "Valid"]
                    incorrect_x = [xi for xi, s in zip(data["Timestamp"], data["Data State"]) if s == "Invalid"]
                    incorrect_y = [yi for yi, s in zip(data["Speed"], data["Data State"]) if s == "Invalid"]


                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=fine_x, y=fine_y, mode="markers+lines", name="Valid", hoverinfo='text', text=["Status Byte: {}<br>Speed: {}<br>Timestamp: {}".format(sb, speed, ts) for sb, speed, ts in zip(data_correct["Status Byte"], data_correct["Speed"], data_correct["Timestamp"])]))
                    fig.add_trace(go.Scatter(x=incorrect_x, y=incorrect_y, mode="markers", name="Invalid", line=dict(color="red"), hoverinfo='text', text=["Timestamp: {}<br>Radar Message: {}".format(tm, rm) for tm, rm in zip(data_corrupt["Timestamp"], data_corrupt["Radar Message"])]))

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
                                             text=["Status Byte: {}<br>Distance: {}<br>Timestamp: {}".format(sb, speed, ts) for
                                                   sb, speed, ts in zip(data_correct["Status Byte"], data_correct["Distance"],
                                                                        data_correct["Timestamp"])]))
                    fig.add_trace(
                        go.Scatter(x=incorrect_x, y=incorrect_y, mode="markers", name="Invalid", line=dict(color="red"),
                                   hoverinfo='text', text=["Timestamp: {}<br>Radar Message: {}".format(tm, rm) for tm, rm in
                                                           zip(data_corrupt["Timestamp"], data_corrupt["Radar Message"])]))

                    fig.update_layout(
                        xaxis_title='Date',
                        yaxis_title='Distance (meter)'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                data_first_drs05 = data_first_drs05.dropna(axis=1, how="all")

                data_first_drs05 = data_first_drs05.style.applymap(corrupt_data_drs05, props='background-color:#800000;', subset=["Radar Message"])



                st.dataframe(data_first_drs05, use_container_width=True)



            else:
                st.write("PLEASE LOAD A DRS05 CSV FILE")

        except:
            st.write("PLEASE LOAD A DRS05 CSV FILE")
            pass

with dr42_tab:
    uploaded_files_dr42 = st.file_uploader("Load a DR42 or DR8 CSV file for visualization", accept_multiple_files=True)
    for uploaded_file_dr42 in uploaded_files_dr42:
        try:
            data = pd.read_csv(uploaded_file_dr42)

            if((data["Radar Message"][0][0] == "#") or (data["Radar Message"][1][0] == "#") or (data["Radar Message"][2][0] == "#") or (data["Radar Message"][3][0] == "#")):
                data_first_dr42 = data.copy()
                st.write("filename:", uploaded_file_dr42.name)

                speed_tab, distance_tab, rms_tab, map_tab = st.tabs(["Speed Over Time", "Distance Over Time", "RMS", "Map"])
                
                data.loc[(data['Radar Message'].str.len() != 27) | (data['Masked Status Byte'] == 0), 'Data State'] = 'Invalid'
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
                    chart_data = pd.DataFrame(data[["Latitude", "Longitude", "Data State"]].values.tolist(),
                                              columns=['lat', 'lon', 'ds'])
                    valid_data = chart_data[chart_data['ds'] == 'Valid']
                    valid_data = valid_data.dropna()

                    invalid_data = chart_data[chart_data['ds'] == 'Invalid']
                    invalid_data = invalid_data.dropna()

                    st.pydeck_chart(pdk.Deck(
                            map_provider="mapbox",
                            map_style="satellite",
                            initial_view_state=pdk.ViewState(
                            latitude=data[["Latitude", "Longitude"]].values.tolist()[0][0],
                            longitude=data[["Latitude", "Longitude"]].values.tolist()[0][1],
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
                            'html': '<b>Speed:</b> {{Speed}} <br> <b>Distance:</b> {{Speed}} <br> <b>RMS:</b> {{Speed}} <br>',
                            'style': {
                                'color': 'white'
                            }
                        }
                    ))

                data = data.dropna(axis=1, how="all")
                data = data.drop(["Masked Status Byte"], axis=1)
                data_first_dr42 = data_first_dr42.style.applymap(corrupt_data_drs42, props='background-color:#800000;',
                                                                 subset=["Radar Message"])
                st.dataframe(data, use_container_width=True)

                

            else:
                st.write("PLEASE LOAD A DR42 OR DR8 CSV FILE")

        except:
            st.write("PLEASE LOAD A DR42 OR DR8 CSV FILE")
            pass
