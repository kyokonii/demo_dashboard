import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime

def app():

    df= pd.read_csv("./data/data.csv")

    product_names =df["product_name"].unique()

    def plot_production():
        fig = px.bar(
            df, x="Datetime", y="Production", color="product_name", title="生産数", text_auto=True
            )

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="直近1ヶ月", step="month", stepmode="backward"),
                    dict(count=1, label="今月", step="month", stepmode="todate"),
                    dict(count=6, label="直近6ヶ月", step="month", stepmode="backward"),
                    dict(count=1, label="今年", step="year", stepmode="todate"),
                    dict(count=1, label="直近1年", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    def plot_defeat_rate():
        fig = px.line(df, x="Datetime", y="Failure rate", color="product_name",)
        st.plotly_chart(fig, use_container_width=True )

    # st.set_page_config(layout="wide")
    st.title('QCDの見える化')
    st.sidebar.write("FilterBox")
    st.sidebar.selectbox("test",product_names)

    d = st.date_input(
        "When's your birthday",
        datetime.date(2022, 4, 1))
    st.write(d)

    plot_production()
    plot_defeat_rate()

    st.table(df.head())