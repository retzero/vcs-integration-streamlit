import streamlit as st
from utils.db_handler import get_target_server_ratio
import plotly.express as px
from pprint import pprint
import pandas as pd

def run():

    with st.container(border=True):
        st.subheader("Overview")
        records = get_target_server_ratio()
        df = pd.DataFrame(records, columns=['target_server', 'count'])
        fig = px.pie(df, 'target_server', 'count', title='🎯 Target 형상 서버 이전 비율')
        st.plotly_chart(fig)



