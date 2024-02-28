import os
import sqlite3
import pandas as pd

def data_json():
    test_plan = {}
    clusters = os.listdir()
    for cluster in clusters:
        cluster_name =  cluster.replace('_Cluster_Test_Plan', '') \
            .replace('_Cluster_TestPlan', '') \
            .replace('_Cluster', '') \
            .replace('_cluster', '') \
            .replace('_Test_Plan', '')
        cluster_test_plan = []
        test_case_dbs = os.listdir(f"{cluster}/")
        for test_case_db in test_case_dbs:
            test_case = {}
            conn = sqlite3.connect(f'{cluster}/{test_case_db}')
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cur.fetchall()
            for table in tables:
                table = table[0]
                if table == "Info":
                    tc_info = conn.execute('''SELECT * FROM Info''')
                    for info in tc_info:
                        test_case["Test Case Name"] = info[0]
                        test_case["Test Case ID"] = info[1]
                        test_case["Test Plan"]  = info[2]
                if table == "Purpose":
                    purpose_data = conn.execute('''SELECT * FROM Purpose''')
                    for purpose in purpose_data:
                        test_case["Purpose"] = purpose[0]
                if table == "Pics":
                    test_case["PICS"] = []
                    pics_data = conn.execute('''SELECT * FROM Pics''')
                    for pics in pics_data:
                        test_case["PICS"].append(pics[0])
                if table == "Precondition":
                    precondtion = pd.read_sql_table('''SELECT * FROM Precondition''', conn)
                    precondtion = precondtion.to_dict('list')
                    test_case["Pre-condition"] = precondtion

                if table == "Test_procedure":
                    test_procedure = pd.read_sql_query('''SELECT * FROM Test_procedure''', conn)
                    test_procedure = test_procedure.to_dict('list')
                    test_case["Test Procedure"] = test_procedure
                cluster_test_plan.append(test_case)
            conn.close()
        test_plan[cluster_name] = cluster_test_plan

    return test_plan