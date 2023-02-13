import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
from PIL import Image
import numpy as np
import pandas as pd
import datetime
import math

st.set_page_config(layout="wide")

st.markdown( f"""
<style>
	.css-1dp5vir {{
    position: absolute;
    top: 0px;
    right: 0px;
    left: 0px;
    height: 0.125rem;
    background-image: linear-gradient(90deg, rgba(40,94,174,255), rgba(20,190,241,255));
    z-index: 999990;
}}
</style>
""", unsafe_allow_html=True)

holland_logo = Image.open('./images/holland.png')


st.image(holland_logo, width=300)


st.text("")
drs05_tab, dr42_tab = st.tabs(["DRS05", "DR42"])

with drs05_tab:
    uploaded_files_drs05 = st.file_uploader("Load a DRS05 CSV file for visualization", accept_multiple_files=True)
    for uploaded_file_drs05 in uploaded_files_drs05:
        try:
            data = pd.read_csv(uploaded_file_drs05)
            st.write("filename:", uploaded_file_drs05.name)

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


            speed_tab, distance_tab = st.tabs(["Speed Over Time", "Distance Over Time"])



            fig = px.scatter(data,
                             x='Timestamp',
                             y='Speed',
                             hover_data=['Status Byte'],
                             labels={
                                 "Speed": "Speed (km/h)",
                                 "Timestamp": "Date",

                             }, )
            fig.update_traces(mode="lines")

            with speed_tab:
                st.plotly_chart(fig, use_container_width=True)
            with distance_tab:
                fig = px.scatter(data,
                                 x='Timestamp',
                                 y='Distance',
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

with dr42_tab:
    uploaded_files_dr42 = st.file_uploader("Load a DR42 CSV file for visualization", accept_multiple_files=True)
    for uploaded_file_dr42 in uploaded_files_dr42:
        try:
            data = pd.read_csv(uploaded_file_dr42)
            st.write("filename:", uploaded_file_dr42.name)

            data["Speed"] = 0
            data["Distance"] = 0
            data["Status Byte"] = 0

            for i in range(len(data)):
                speed = data["Radar Message"][i][5:9]
                speed = int(speed, base=16)

                speed = (speed * 600) / 65535

                data["Speed"][i] = speed

                distance_counter = data["Radar Message"][i][9:13]
                distance_counter = int(distance_counter, base=16)
                distance_counter = distance_counter / 10
                data["Distance"][i] = distance_counter

                status_byte = data["Radar Message"][i][23:25]
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

            speed_tab, distance_tab = st.tabs(["Speed Over Time", "Distance Over Time"])

            fig = px.scatter(data,
                             x='Timestamp',
                             y='Speed',
                             hover_data=['Status Byte'],
                             labels={
                                 "Speed": "Speed (km/h)",
                                 "Timestamp": "Date",

                             }, )
            fig.update_traces(mode="lines")

            with speed_tab:
                st.plotly_chart(fig, use_container_width=True)
            with distance_tab:
                fig = px.scatter(data,
                                 x='Timestamp',
                                 y='Distance',
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