import streamlit as st
from utils.db_handler import get_repos
from datetime import datetime, time, timedelta
from pprint import pprint
import pandas as pd
import plotly.express as px

def run():

    my_container = st.container(border=True)

    # 세션 상태 초기화
    if 'selected_start_time' not in st.session_state:
        st.session_state['selected_start_time'] = None

    # 버튼 클릭 시 실행될 콜백 함수
    def apply_selection_and_plot(df):
        st.session_state['selected_start_time'] = st.session_state['slider_key']

        if st.session_state['selected_start_time'] is not None:
            cutoff_date = st.session_state['selected_start_time']
            
            # 상태 컬럼을 미리 계산합니다.
            df['state'] = df['last_commit_date'].apply(lambda x: '이후' if x > cutoff_date else '이전')

            with my_container:
                st.subheader(f"통계 결과 (기준일: {cutoff_date.strftime('%Y-%m-%d')})")
                
                # 그룹형 바 차트 호출
                st.markdown("#### 📊 서버별 커밋 갯수 및 용량 통계 (그룹 바 차트)")
                plot_counts(df.copy(), cutoff_date) # copy()를 사용하여 원본 DF에 영향 방지
                plot_size_totals(df.copy(), cutoff_date)

                # 파이 차트 호출
                st.markdown("#### 🥧 전체 합산 비율 통계 (파이 차트)")
                col1, col2 = st.columns(2)
                with col1:
                    plot_pie_counts(df.copy(), cutoff_date)
                with col2:
                    plot_pie_sizes(df.copy(), cutoff_date)

    # (이전의 plot_counts, plot_size_totals 함수는 생략하거나 위에 그대로 유지)
    def plot_counts(df, cutoff_date):
        # df는 이미 state 컬럼을 가지고 있다고 가정합니다 (콜백에서 생성했으므로).
        counts_df = df.groupby(['origin_server', 'state']).size().reset_index(name='count')
        fig = px.bar(counts_df, x="origin_server", y="count", color="state", barmode='group', labels={'count': '저장소 수', 'origin_server': 'Origin Server'}, height=400)
        st.plotly_chart(fig, use_container_width=True)

    def plot_size_totals(df, cutoff_date):
        # df는 이미 state 컬럼을 가지고 있다고 가정합니다.
        totals_df = df.groupby(['origin_server', 'state'])['size_in_bytes'].sum().reset_index(name='total_bytes')
        fig = px.bar(totals_df, x="origin_server", y="total_bytes", color="state", barmode='group', labels={'total_bytes': '총 용량 (Bytes)', 'origin_server': 'Origin Server'}, height=400)
        st.plotly_chart(fig, use_container_width=True)


    # 새로 추가된 파이 차트 함수들
    def plot_pie_counts(df, cutoff_date):
        # 전체 서버 합산이므로 origin_server 그룹핑이 필요 없습니다.
        # df는 이미 state 컬럼을 가지고 있다고 가정합니다.
        total_counts_df = df.groupby('state').size().reset_index(name='count')

        fig = px.pie(total_counts_df, 
                    values='count', 
                    names='state', 
                    title=f'전체 저장소 갯수 비율',
                    hole=.3 # 도넛 차트 형태로 표시 (선택 사항)
                    )
        st.plotly_chart(fig, use_container_width=True)

    def plot_pie_sizes(df, cutoff_date):
        # 전체 서버 합산 및 size_in_bytes 합계
        # df는 이미 state 컬럼을 가지고 있다고 가정합니다.
        total_sizes_df = df.groupby('state')['size_in_bytes'].sum().reset_index(name='total_bytes')

        fig = px.pie(total_sizes_df, 
                    values='total_bytes', 
                    names='state', 
                    title=f'전체 저장소 총 용량 비율',
                    hole=.3
                    )
        st.plotly_chart(fig, use_container_width=True)


    # --- Streamlit UI ---
    with my_container:
        st.subheader("⌚ Date 조정하면서 형상 서버 통계 확인하기")
        st.write("실제 데이터는 변경되지 않습니다.")
        
        columns, records = get_repos() # 데이터프레임 가져오기
        df = pd.DataFrame(records, columns=columns)

        start_date = df['last_commit_date'].min()
        end_date = df['last_commit_date'].max()

        # Date and Time Slider
        st.slider(
            "구분 할 날자를 선택해 주세요.",
            value=start_date + (end_date - start_date)/2,
            min_value=start_date,
            max_value=end_date,
            format="YYYY-MM-DD",
            key='slider_key' 
        )

        # 버튼 추가 (콜백 함수에 인자 전달)
        st.button("적용하기", on_click=apply_selection_and_plot, args=(df.copy(),)) # df 복사본 전달

        # 결과 출력
        if st.session_state['selected_start_time'] is not None:
            st.write("Selected start time (적용됨):", st.session_state['selected_start_time'])
        else:
            st.write("날짜를 선택하고 '적용하기' 버튼을 눌러주세요.")