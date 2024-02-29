import os
import sqlite3
import pandas as pd

def data_json():
    test_plan = {}
    clusters = os.listdir()
    clusters.sort(key=lambda modified: os.path.getmtime(modified), reverse=False)
    for cluster in clusters:
        if os.path.isdir(cluster):
            cluster_name =  cluster.replace('_Cluster_Test_Plan', '') \
                .replace('_Cluster_TestPlan', '') \
                .replace('_Cluster', '') \
                .replace('_cluster', '') \
                .replace('_Test_Plan', '')
            cluster_test_plan = []
            test_case_dbs = os.listdir(f"{cluster}/")
            test_case_dbs.sort(key=lambda modified: os.path.getmtime(os.path.join(f"{cluster}/",modified)), reverse=False)
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

                    test_case["PICS"] = []
                    if table == "Pics":
                        pics_data = conn.execute('''SELECT * FROM Pics''')
                        for pics in pics_data:
                            test_case["PICS"].append(pics[0])
                    else:
                        test_case["PICS"].append("Nil")

                    if table == "Precondition":
                        precondtion = pd.read_sql_query('''SELECT * FROM Precondition''', conn)
                        precondtion = precondtion.to_dict('list')
                        test_case["Pre-condition"] = precondtion
                    else:
                        test_case["Pre-condition"] = "Nil"

                    if table == "Test_procedure":
                        test_procedure = pd.read_sql_query('''SELECT * FROM Test_procedure''', conn)
                        test_procedure = test_procedure.to_dict('list')
                        test_case["Test Procedure"] = test_procedure
                cluster_test_plan.append(test_case)
                conn.close()
        test_plan[cluster_name] = cluster_test_plan

    return test_plan