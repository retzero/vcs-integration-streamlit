import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import bcrypt
import re
import pandas as pd
import numpy as np
from pprint import pprint
from datetime import datetime, timedelta
from random import randint

load_dotenv()

# Database connection parameters
db_params = {
    "dbname":  os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

'''
1) THE CSV FILE SHOULD HAVE BELOW COLUMNS...
   rel_path, git_size, author_email, committer_email, commit_date 
2) The CSV file name should ends with _XXX.csv where XXX is the server identifier.
   repos_commits_179.csv
'''


def read_data_files(input_file: str = None):

    print('*********')
    print(input_file)
    report = []

    default_report_path = 'reports'
    if input_file:
        file_list = [input_file]
    else:
        file_list = []
        for _fname in os.listdir(default_report_path):
            file_list.append(os.path.join(default_report_path, _fname))

    print(f'Go with {file_list}')

    for fname in file_list:
        if not os.path.isfile(fname):
            continue
        if not fname.endswith('.csv'):
            continue

        origin_server = fname.split('_')[-1].replace('.csv', '')

        df = pd.read_csv(fname)

        for index, row in df.iterrows():
            repo_name = row['repository_name']
            git_size = row['git_size']
            commit_date = row['commit_date']
            if pd.isna(repo_name) or pd.isna(git_size) or pd.isna(commit_date):
                print(f'Mal-formatted data: {row}')
                continue
            git_size = ''.join(git_size.lower().split())
            git_size_digit, git_size_unit = re.search(r'(\d+)(.*)', git_size).groups()
            git_size_digit = int(git_size_digit)
            if git_size_unit == 'bytes':
                git_size_digit = git_size_digit * 1
            elif git_size_unit == 'kb':
                git_size_digit = git_size_digit * 1024
            elif git_size_unit == 'mb':
                git_size_digit = git_size_digit * 1024 * 1024
            elif git_size_unit == 'gb':
                git_size_digit = git_size_digit * 1024 * 1024 * 1024
            elif git_size_unit == 'tb':
                git_size_digit = git_size_digit * 1024 * 1024 * 1024 * 1024
            else:
                print(f'Fail to parse git size... [{git_size}]')
            report.append({
                'origin_server': origin_server,
                'repo_name': repo_name,
                'git_size': git_size_digit,
                'commit_date': commit_date
            })

    return report


def fill_repository_table(input_file: str = None):

    records = read_data_files(input_file)

    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    for item in records:
        _fake_date = datetime.now() + timedelta(days=randint(-365, 365))
        try:
            cur.execute(f"""
                INSERT INTO repository (origin_server, repository_path, size_in_bytes, last_commit_date)
                VALUES('{item.get("origin_server")}', '{item.get("repo_name")}', {item.get("git_size")}, '{_fake_date}');
            """)
            conn.commit()
        except Exception as err:
            print(repr(err))
            conn.rollback()
    
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":

    #try:
        fill_repository_table()
        print("Item inserted successfully.")
    #except psycopg2.Error as e:
    #    print(f"Error inserting items: {e}")
