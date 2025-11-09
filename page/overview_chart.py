import streamlit as st
from utils.db_handler import get_target_server_ratio
import plotly.express as px
from pprint import pprint
import pandas as pd

def run():

    with st.container(border=True):
        st.subheader("Overview")
        records = get_target_server_ratio()
        df = pd.DataFrame(records, columns=['target_server', 'count', 'sum'])

        col1, col2 = st.columns(2, vertical_alignment="center")
        with col1:
            with st.container(border=True):
                fig1 = px.pie(df, 'target_server', 'count', title='🎯 Target 형상 서버 이전 비율 (갯수)')
                st.plotly_chart(fig1)
        with col2:
            with st.container(border=True):
                fig2 = px.pie(df, 'target_server', 'sum', title='🎯 Target 형상 서버 이전 비율 (사이즈)')
                st.plotly_chart(fig2)



