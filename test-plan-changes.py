from bs4 import BeautifulSoup
from scripts.make_json import *
from scripts.changes import *
from scripts.write_excel import *
import pandas as pd
import shutil
import json
import sqlite3
import re
import os

json_file = "../TC_Summary.json"

app = "/home/grl/Downloads/allclusters (1).html"
main = "/home/grl/Downloads/index (1).html"

def tc_id (head):
    testcase1 = re.search(r'\[(.*?)\]',head)
    if testcase1:
        matched_str = testcase1.group()  # Extract the matched substring
        testcase = re.sub(r'\[|\]', '', matched_str)

    return testcase

def create_df(table):
    rows = table.find_all('tr')
    data = []
    col_spans = []
    row_spans = []
    # to find the rowspan and colspan
    for i, row in enumerate(rows):
        cells = row.find_all(['th', 'td'])
        row_data = []
        for j, cell in enumerate(cells):
            if cell.has_attr('colspan'):
                col_spans.append((i, j, int(cell['colspan'])))
            if cell.has_attr('rowspan'):
                row_spans.append((i, j, int(cell['rowspan'])))
            row_data.append(cell.get_text(strip=True))
        data.append(row_data)
    # Apply colspans to data
    for span in col_spans:
        i, j, span_size = span
        for r in range(1, span_size):
            data[i].insert(j+1, '')
    # Apply rowspans to data
    for span in row_spans:
        i, j, span_size = span
        for r in range(1, span_size):
            data[i+r].insert(j, '')

    # Convert the data into a pandas dataframe
    df = pd.DataFrame(data[1:], columns=data[0])

    # Replace any None values with an empty string
    df = df.fillna('')
    # convert the dataframe to dict
    data_dict = {}
    # convert the dataframe to dict
    data_dict = df.to_dict('list')
    return(df)

def scrap(soup):
    header = soup.find ('div', id='header')
    test_plan_tag= header.find('h1').text
    versiontag = header.find ('div', class_='details')
    versiont = versiontag.find('span', id = "revnumber")
    version = versiont.text

    if test_plan_tag == "Matter Application Clusters Test Plan":
        testplan = "App testcase"
    else:
        testplan = "Core testcase"

    h1_tags1 = soup.find_all('h1', {'id': True}) 
    h1_tags1t = []

    for tag in h1_tags1:
        tag_text = tag.text
        if tag_text != "MCORE PICS Definition":
            h1_tags1t.append(tag_text)

    cluster_divs = []

    divs = h1_tags1[0].find_all_next('div', class_="sect1")
    for div in divs:
        h2_tag =div.find_next('h2', {'id': True}).text
        if re.sub(r'^\d+\.\s*', '', h2_tag) == "Test Cases":
            cluster_divs.append(div)


    cluster_folders = os.listdir()
    conn_alltc = sqlite3.connect('all_tc_details.db')
    if "all_tc_details.db" not in cluster_folders:
        conn_alltc.execute('''CREATE TABLE Alltcdetails (Cluster_Name VARCHAR, Test_case_name VARCHAR, Test_case_id VARCHAR, Test_plan VARCHAR);''')
        conn_alltc.commit()

    alltc_query = """INSERT INTO Alltcdetails (Cluster_Name, Test_case_name, Test_case_id, Test_plan) VALUES (?, ?, ?, ?)"""  
    work_dir = os.getcwd()

    for cluster, tpdiv in zip(h1_tags1t, cluster_divs):
        
        cluster_name = cluster.replace(" ","_")\
                            .replace("/", "")
        os.mkdir(os.path.join(os.getcwd(),cluster_name))
        os.chdir(cluster_name)
        #testcases = tpdiv.find_all(['h4','h5','h6'], {'id': lambda x: x and x.startswith('_tc')})
        tcdivs = tpdiv.find_all('div', class_ = "sect3")
        for tcdiv in tcdivs:
            testcase = tcdiv.find(['h4','h5','h6'], {'id': lambda x: x and x.startswith('_tc')})
            try:
                testcase_id = tc_id(testcase.text)
            except AttributeError:
                testcase = tcdiv.find(['h4','h5','h6'], {'id': lambda x: x and x.startswith('ref_TC')})
                testcase_id = tc_id(testcase.text)
            testcase_id_name = testcase_id.replace(".","_")
            alltc_values = (cluster, testcase.text , testcase_id, testplan)
            info_value = (testcase.text , testcase_id, testplan)
            conn_alltc.execute(alltc_query, alltc_values)
            conn_alltc.commit()
            conn_tc = sqlite3.connect(f'{testcase_id_name}.db')
            cursor = conn_tc.cursor()
            tc_info_query = '''INSERT INTO Info (Test_case_name, Test_case_id, Test_plan) VALUES (?,?,?)'''
            conn_tc.execute('''CREATE TABLE Info (Test_case_name VARCHAR, Test_case_id VARCHAR, Test_plan VARCHAR)''')
            cursor.execute(tc_info_query, info_value)
            conn_tc.commit()

            data_divs = tcdiv.find_all('div', class_=["sect4", "sect5"])
            print(testcase_id_name)
            for data_div in data_divs:
                test_key = data_div.find(['h7','h5','h6'], {'id': lambda x: x and x.startswith('_')}).text
                if test_key == "Purpose":
                    try:
                        purpose = data_div.find('p').text
                        purpose_query ='''INSERT INTO Purpose(Purpose) VALUES (?)'''
                        conn_tc.execute('''CREATE TABLE Purpose (Purpose TEXT)''')
                        cursor.execute(purpose_query, (purpose,))
                        conn_tc.commit()
                    except:
                        pass
                elif test_key =="PICS":
                    pics_div = data_div.find('div', class_="ulist")
                    pics_tag = pics_div.find_all('p')
                    pics_query = '''INSERT INTO Pics(Pics) VALUES (?)'''
                    conn_tc.execute('''CREATE TABLE Pics (Pics VARCHAR)''')
                    for pics in pics_tag:
                        cursor.execute(pics_query,(pics.text,))
                    conn_tc.commit()
                elif test_key =="Preconditions":
                    precondition_table = data_div.find('table')
                    precondition_df = create_df(precondition_table)
                    precondition_df.to_sql('Precondition', conn_tc, index = False)
                    conn_tc.commit()
                elif test_key =="Test Procedure":
                    test_table = data_div.find('table')
                    test_df = create_df(test_table)
                    test_df.to_sql('Test_procedure', conn_tc, index = False)
                    conn_tc.commit()
            
            conn_tc.close()
        os.chdir(work_dir)

    conn_alltc.close()
        

if __name__ == '__main__':
    folders = os.listdir()  
    if 'test-plan-db' in folders:
        shutil.rmtree('test-plan-db')
    os.mkdir(os.path.join(os.getcwd(), 'test-plan-db'))
    os.chdir("test-plan-db")
    with open (app) as f:
        soup1 = BeautifulSoup(f, 'lxml')
    f.close()

    scrap(soup1)
    header = soup1.find ('div', id='header')
    test_plan_tag= header.find('h1').text
    versiontag = header.find ('div', class_='details')
    versiont = versiontag.find('span', id = "revnumber")
    version = versiont.text

    with open (main) as f2:
        soup2 = BeautifulSoup(f2, 'lxml')
    f2.close()
    scrap(soup2)

    current_test_plan = data_json()



    changes=0
    try:
        with open(json_file, 'r') as file:
            existing_test_plan = json.load(file)
        changes = test_plan_changes(existing_test_plan, current_test_plan)
        
    except FileNotFoundError:
            existing_test_plan = {}

    with open(json_file, 'w') as file:
        json.dump(current_test_plan, file, indent=4)

    if changes:
        conn = sqlite3.connect('all_tc_details.db')
        conn.execute('''CREATE TABLE Test_plan_changes (Date VARCHAR, "Commit" VARCHAR, Testcase VARCHAR, Changes VARCHAR);''')
        tcchange_query = """INSERT INTO Test_plan_changes (Date, "Commit", Testcase, Changes) VALUES (?, ?, ?, ?)"""
        tp_diff = list_of_changes(changes, version)
        for tp_change in tp_diff:
            print(tp_change)
            conn.execute(tcchange_query, tp_change)
        conn.commit()
        conn.execute('''CREATE TABLE Summary_changes (Date VARCHAR, "Commit" VARCHAR, Testcase VARCHAR, Changes VARCHAR);''')
        summarychange_query = """INSERT INTO Summary_changes (Date, "Commit", Testcase, Changes) VALUES (?, ?, ?, ?)"""
        summary_diff = sumary_change(changes, version)
        for summary_change in summary_diff:
            conn.execute(summarychange_query, summary_change)
        conn.commit()
        conn.close()
    write_excel(current_test_plan)



