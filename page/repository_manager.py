import streamlit as st
from utils.db_handler import get_repos
from streamlit_tree_select import tree_select
import collections
from pprint import pprint
from collections import defaultdict
import datetime
import os

def build_directory_tree_with_value(data):

    def nested_dict():
        return defaultdict(nested_dict)

    tree_store = nested_dict()
    size_map = defaultdict(int)

    for item in data:
        _, origin_server, repository_path, size, _, _ = item
        full_path = f"{origin_server}/{repository_path}"
        parts = full_path.split('/')
        for i in range(1, len(parts) + 1):
            parent_path = '/'.join(parts[:i])
            size_map[parent_path] += size
        current = tree_store
        for part in parts:
            current = current[part]

    def size_into_readible(size):
        if size > 1024 * 1024 * 1024:
            return f'{int(size/1024/1024/1024)} GB'
        if size > 1024 * 1024:
            return f'{int(size/1024/1024)} MB'
        if size > 1024:
            return f'{int(size/1024)} KB'
        return f'{size} bytes'

    def format_tree(node, current_path=""):
        result = []
        for label, children_node in node.items():
            new_path = f"{current_path}/{label}" if current_path else label
            total_size = size_map.get(new_path, 0)
            formatted_children = format_tree(children_node, new_path)
            item = {
                "label": f'{label} ({size_into_readible(total_size)})',
                "value": new_path, # 요청된 value 필드 추가
                "total_directory_size": total_size,
                "children": formatted_children
            }
            result.append(item)
        return result

    final_tree = format_tree(tree_store)
    return final_tree


def construct_repo_tree(columns, repos):

    result_tree = build_directory_tree_with_value(repos)
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
