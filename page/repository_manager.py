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

    for item in data:
        _, origin_server, repository_path, size, _, _, target_server = item
        
        full_path = f"{origin_server}/{repository_path}"
        parts = full_path.split('/')
        
        for i in range(1, len(parts) + 1):
            parent_path = '/'.join(parts[:i])
            size_map[parent_path] += size
        
        current = tree_store
        for part in parts:
            current = current[part]
        
        target_server_map[full_path] = target_server

    def format_tree_with_labels_and_size(node, current_path=""):
        result = []
        all_descendant_servers = set()

        for label, children_node in node.items():
            new_path = f"{current_path}/{label}" if current_path else label
            
            formatted_children, children_servers = format_tree_with_labels_and_size(children_node, new_path)
            all_descendant_servers.update(children_servers)

            current_node_size = size_map.get(new_path, 0)
            formatted_size = format_bytes(current_node_size) # 보기 좋은 형식으로 변환
            
            server_info_suffix = ""
            if not formatted_children:
                server_val = target_server_map.get(new_path, 'Unknown')
                server_info_suffix = f"{server_val}"
                all_descendant_servers.add(server_val)
            else:
                if len(children_servers) == 1:
                    # 집합의 유일한 요소 추출 시 list 변환 후 인덱싱
                    server_info_suffix = list(children_servers)[0]
                elif len(children_servers) > 1:
                    server_info_suffix = "Multi"

            # 레이블 형식: label (size, <target-server>)
            item = {
                "label": f"{label} ({formatted_size}, {server_info_suffix})",
                "value": new_path,
                "total_directory_size": current_node_size, # 원본 바이트 사이즈 유지
                "children": formatted_children
            }
            result.append(item)
        
        return result, all_descendant_servers

    # 최상위 레벨 트리 생성
    final_tree, _ = format_tree_with_labels_and_size(tree_store)
    return final_tree


def construct_repo_tree(columns, repos):

    result_tree = build_directory_tree_with_value_and_size(repos)
    pprint(result_tree)
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
