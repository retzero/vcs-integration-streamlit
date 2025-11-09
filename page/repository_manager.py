import streamlit as st
from utils.db_handler import get_repos
from streamlit_tree_select import tree_select
import collections
from pprint import pprint
from collections import defaultdict
import datetime
import os
import math

def format_bytes(bytes_value):
    """바이트 값을 KB, MB, GB 등으로 보기 좋게 변환합니다."""
    if bytes_value < 1024:
        return f"{bytes_value} bytes"
    # 1024를 기준으로 로그를 취하여 단위를 결정 (KB, MB, GB)
    unit_labels = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    # math.floor를 사용하여 정확한 단위 인덱스 계산
    unit_index = math.floor(math.log(bytes_value, 1024))
    # 인덱스가 리스트 범위를 초과하지 않도록 보장
    unit_index = min(unit_index, len(unit_labels) - 1)
    
    converted_value = bytes_value / (1024 ** unit_index)
    unit = unit_labels[unit_index]
    
    return f"{converted_value:.2f} {unit}"


def build_directory_tree_with_value_and_size(data):
    def nested_dict():
        return defaultdict(nested_dict)
    
    tree_store = nested_dict()
    size_map = defaultdict(int)
    target_server_map = {}
    # 경로별 마지막 커밋 날짜를 저장할 맵 추가 (리프 노드 기준)
    last_commit_date_map = {}

    for item in data:
        _, origin_server, repository_path, size, _, last_commit_date, target_server = item
        
        full_path = f"{origin_server}/{repository_path}"
        parts = full_path.split('/')
        
        for i in range(1, len(parts) + 1):
            parent_path = '/'.join(parts[:i])
            size_map[parent_path] += size
        
        current = tree_store
        for part in parts:
            current = current[part]
        
        target_server_map[full_path] = target_server
        # 리프 노드의 날짜 저장
        last_commit_date_map[full_path] = last_commit_date.strftime('%Y-%m-%d')


    def format_tree_with_labels_and_size(node, current_path=""):
        result = []
        all_descendant_servers = set()
        # 모든 자손 노드의 날짜를 저장할 리스트 (최신 날짜 검색용)
        all_descendant_dates = []

        for label, children_node in node.items():
            new_path = f"{current_path}/{label}" if current_path else label
            
            # 자식 노드 재귀 호출 및 정보 수집
            formatted_children, children_servers, children_dates = format_tree_with_labels_and_size(children_node, new_path)
            
            all_descendant_servers.update(children_servers)
            all_descendant_dates.extend(children_dates)

            current_node_size = size_map.get(new_path, 0)
            formatted_size = format_bytes(current_node_size)
            
            # 1. Target Server 정보 결정 (이전과 동일)
            server_info_suffix = ""
            if not formatted_children:
                server_val = target_server_map.get(new_path, 'Unknown')
                server_info_suffix = f"{server_val}"
                all_descendant_servers.add(server_val)
            else:
                if len(children_servers) == 1:
                    server_info_suffix = list(children_servers)[0] # 집합에서 값 추출
                elif len(children_servers) > 1:
                    server_info_suffix = "Multi"
            
            # 2. Date 정보 결정
            date_info = ""
            if not formatted_children: # 리프 노드인 경우
                date_info = last_commit_date_map.get(new_path, 'Unknown Date')
                all_descendant_dates.append(date_info) # 리프 날짜를 부모로 전달하기 위해 추가
            else: # 부모 노드인 경우: 수집된 자식 날짜 중 가장 최근 날짜 사용
                if all_descendant_dates:
                    # 문자열 날짜를 datetime 객체로 변환하여 최대값 찾기
                    latest_date_obj = max([datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in all_descendant_dates])
                    date_info = latest_date_obj.strftime('%Y-%m-%d')
                else:
                    date_info = 'No Date'

            # 레이블 형식: label (size, <target-server>, date)
            item = {
                "label": f"{label} ({formatted_size}, {server_info_suffix}, {date_info})",
                "value": new_path,
                "total_directory_size": current_node_size
            }
            if formatted_children:
                item["children"] = formatted_children
            result.append(item)
        
        # 현재 레벨의 모든 날짜 정보를 반환하여 상위 부모가 사용하도록 함
        return result, all_descendant_servers, all_descendant_dates

    # 최상위 레벨 트리 생성 및 불필요한 반환값 무시
    final_tree, _, _ = format_tree_with_labels_and_size(tree_store)
    return final_tree


def construct_repo_tree(columns, repos):

    result_tree = build_directory_tree_with_value_and_size(repos)
    return result_tree


def run():

    st.title("🐙 Streamlit-tree-select")
    st.subheader("A simple and elegant checkbox tree for Streamlit.")

    if st.button("Reset"):
        st.rerun()

    columns, repos = get_repos()
    repo_tree = construct_repo_tree(columns, repos)
    return_select = tree_select(repo_tree, checked=[], expanded=[])
    st.write(return_select)

    if repos:
        st.table(repos)
