import streamlit as st
from utils.db_handler import get_users
from utils.init_session import reset_session
from datetime import datetime
import os
import pandas as pd
from pprint import pprint

from page.repository_manager import run as repo_view
from page.overview_chart import run as overview_chart
from page.slider_view import run as slider_view

from db.insert_repo_data import fill_repository_table
from utils.db_handler import delete_repository_table, get_target_servers, create_target_server



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
        '''
        if st.session_state['guest_mode']:
            st.subheader("Guest Mode")
            if st.button("Login"):
                reset_session()
                st.rerun()
        else:
            if st.button("Logout"):
                reset_session()
                st.rerun()
        '''

        with st.container(border=True):
            st.subheader('CSV 파일 추가')
            st.write('( 예시 파일명: repos_commits_179.csv )')
            with st.form(key='csv_upload_form', clear_on_submit=True):
                csv_file = st.file_uploader('⚠️ 동일한 형상서버에 해당하는 데이터가 갱신됩니다. Ex) 179 서버 데이터 삭제 후 재 생성됨.', type=['csv'])
                csv_submit_button = st.form_submit_button(label='업로드 하기')
            if csv_submit_button and csv_file is not None:
                print(f'CSV File to upload: {csv_file.name if csv_file else None}')
                # Your file processing logic here
                save_uploaded_file('reports', csv_file)
                delete_repository_table(origin_server=csv_file.name.split('_')[-1].split('.')[0])
                fill_repository_table('reports/'+csv_file.name)
                #reset_session()
                st.rerun()

        with st.container(border=True):
            st.subheader("이전 할 대상 서버 목록")
            st.table(get_target_servers())

            with st.form("add_new_target_server_form", clear_on_submit=True):
                target_server_name_to_save = st.text_input("대상 서버를 추가하시려면 아래 텍스트 박스에 입력 후 Enter 눌러 주세요.")
                target_server_submit_button = st.form_submit_button("생성")
                if target_server_submit_button and target_server_name_to_save is not None:
                    print(f'Adding Target Server Name: {target_server_name_to_save}')
                    create_target_server(target_server_name_to_save)
                    #target_server_name_to_save = None
                    #reset_session()
                    st.rerun()


    slider_view()
    st.divider()
    overview_chart()
    st.divider()
    repo_view()

