import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff

import numpy as np
import pandas as pd
import datetime
import math


st.markdown("# Microver :train2:")
st.write("Load your data for visualization")


uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
for uploaded_file in uploaded_files:
    try:
        data = pd.read_csv(uploaded_file)
        st.write("filename:", uploaded_file.name)

        data["Speed"] = 0
        data["Distance"] = 0
        data["Status Byte"] = 0

        data = data.drop("Unnamed: 2", axis=1)

        for i in range(len(data)):
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

            data["Status Byte"][i] = res

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


        tab1, tab2 = st.tabs(["Speed Over Time", "Distance Over Time"])



        fig = px.scatter(data,
                         x='Timestamp',
                         y='Speed',
                         color='Status Byte',
                         hover_data=['Status Byte'],
                         labels={
                             "Speed": "Speed (km/h)",
                             "Timestamp": "Date",

                         }, )
        fig.update_traces(mode="lines")

        with tab1:
            st.plotly_chart(fig, use_container_width=True)
        with tab2:
            fig = px.scatter(data,
                             x='Timestamp',
                             y='Distance',
                             color='Status Byte',
                             hover_data=['Status Byte'],
                             labels={
                                 "Distance": "Distance (meter)",
                                 "Timestamp": "Date",
                             },
                             )
            fig.update_traces(mode="lines")
            st.plotly_chart(fig, use_container_width=True)
    except:
        st.write("PLEASE LOAD A SUITABLE CSV FILE.")