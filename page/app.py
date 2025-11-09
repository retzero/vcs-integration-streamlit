import streamlit as st
from utils.db_handler import get_users
from utils.init_session import reset_session
from datetime import datetime
import os
import pandas as pd

from page.repository_manager import run as repo_view

from db.insert_repo_data import fill_repository_table
from utils.db_handler import delete_repository_table



# 파일 업로드 함수
# 디렉토리 이름, 파일을 주면 해당 디렉토리에 파일을 저장해주는 함수
def save_uploaded_file(directory, file):
    # 1. 저장할 디렉토리(폴더) 있는지 확인
    #   없다면 디렉토리를 먼저 만든다.
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # 2. 디렉토리가 있으니, 파일 저장
    with open(os.path.join(directory, file.name), 'wb') as f:
        f.write(file.getbuffer())
    return st.success('파일 업로드 성공!')

def app_page():
    with st.sidebar:
        if st.session_state['guest_mode']:
            st.subheader("Guest Mode")
            if st.button("Login"):
                reset_session()
                st.rerun()
        else:
            if st.button("Logout"):
                reset_session()
                st.rerun()

        if True:
            st.subheader('CSV 파일 추가')
            st.write('( 예시 파일명: repos_commits_179.csv )')
            csv_file = st.file_uploader('⚠️ 동일한 형상서버에 해당하는 데이터가 갱신됩니다. Ex) 179 서버 데이터 삭제 후 재 생성됨.', type=['csv'])
            print(csv_file.name if csv_file else None)
            if csv_file is not None:
                save_uploaded_file('reports', csv_file)
                delete_repository_table(origin_server=csv_file.name.split('_')[-1].split('.')[0])
                fill_repository_table('reports/'+csv_file.name)
                #reset_session()
                #st.rerun()

    st.title("App Page")
    st.write("Hello World")
    users = get_users()
    if users:
        st.table(users)
    
    #repos = get_repos()
    #if repos:
    #    st.table(repos)
    repo_view()
    

