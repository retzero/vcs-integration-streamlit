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
    def format_tree(node, current_path=""):
        result = []
        child_target_servers = set()
        for label, children_node in node.items():
            new_path = f"{current_path}/{label}" if current_path else label
            total_size = size_map.get(new_path, 0)
            formatted_children, children_servers = format_tree(children_node, new_path)
            child_target_servers.update(children_servers)
            item = {
                "label": label,
                "value": new_path,
                "total_directory_size": total_size,
                "children": formatted_children
            }
            result.append(item)
        for item in result:
            current_item_path = item["value"]
            if current_item_path in target_server_map:
                server_val = target_server_map[current_item_path]
                item["label"] = f"{item['label']} ({server_val})"
                child_target_servers.add(server_val)
            else:
                current_children_servers = set()
                pass # 아래 최종 로직에서 처리
        return result, child_target_servers
    def format_tree_with_labels(node, current_path=""):
        result = []
        all_descendant_servers = set()
        for label, children_node in node.items():
            new_path = f"{current_path}/{label}" if current_path else label
            total_size = size_map.get(new_path, 0)
            formatted_children, children_servers = format_tree_with_labels(children_node, new_path)
            all_descendant_servers.update(children_servers)
            server_info_suffix = ""
            if not formatted_children: # 리프 노드인 경우
                server_val = target_server_map.get(new_path, 'Unknown')
                server_info_suffix = f" ({server_val})"
                all_descendant_servers.add(server_val)
            else: # 부모 노드인 경우
                if len(children_servers) == 1:
                    server_info_suffix = f" ({list(children_servers)[0]})"
                elif len(children_servers) > 1:
                    server_info_suffix = " (Multi)"
            item = {
                "label": f"{label}{server_info_suffix}",
                "value": new_path,
                "total_directory_size": total_size,
                "children": formatted_children
            }
            result.append(item)
        return result, all_descendant_servers
    final_tree, _ = format_tree_with_labels(tree_store)
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
