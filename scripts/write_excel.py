import re
import openpyxl
from openpyxl import load_workbook
import sqlite3

def write_excel(test_plan):

    excel_file = f"test_plan_change.xlsx"

    try:
        workbook = load_workbook(excel_file)
    except FileNotFoundError:
        workbook = openpyxl.Workbook()

    sheet_names = workbook.sheetnames


    if "All_TC_Details" in sheet_names:
            workbook.remove(workbook["All_TC_Details"])
            workbook.create_sheet("All_TC_Details", 0)
            sheet1 = workbook["All_TC_Details"]

    else:
            sheet1 = workbook.active
            sheet1.title = "All_TC_Details"

    head = ["S.no" ,"Cluster Name","Test Case Name","Test Case ID"," Test Plan "]
    sheet1.append(head)
    conn = sqlite3.connect('all_tc_details.db')
    data = conn.execute('''SELECT * FROM Alltcdetails''')
    for line in data:
        sheet1.append(line)
    column_widths = {'A': 10, 'B': 20, 'C': 50 ,'D':30,'E':30}  # Specify the column widths as desired

    for column, width in column_widths.items():
                sheet1.column_dimensions[column].width = width
    workbook.save()

    data = conn.execute('''SELECT * FROM Test_plan_changes''')
    tc_changes = []
    for line in data:
         tc_changes.append(line)

    data = conn.execute('''SELECT * FROM Summary_changes''')
    summary_changes = []
    for line in data:
         summary_changes.append(line)
    conn.close()
    if "Test_Summary_Changes" not in sheet_names:

        sheet = workbook.create_sheet("Test_Summary_Changes",1)
        sheet.append(["Date of Run"	, "Cluster Name",	"Test Case Name",	"Test Case ID",	"Test Plan",	"Change Type"])

    else:
        sheet = workbook["Test_Summary_Changes"]

    for i in range(len(tc_changes)):
        for j, value in enumerate(tc_changes[i]):   
            sheet.insert_rows(2)                                                                              
            sheet.cell(row=i + 2, column=j + 1, value=value)
    column_widths = {'A': 10, 'B': 20, 'C': 50 ,'D':30,'E':30}  # Specify the column widths as desired

    for column, width in column_widths.items():
                sheet1.column_dimensions[column].width = width
    
    workbook.save()

    if "Test_plan_Changes" not in sheet_names:

        sheet = workbook.create_sheet("Test_plan_Changes",2)
        sheet.append(["Date of Run"," Commit","Cluster/Testcase","Changes","Column"])
    else:
        sheet = workbook["Test_plan_Changes"]

    for i in range(len(tc_changes)):
        for j, value in enumerate(tc_changes[i]):   
            sheet.insert_rows(2)                                                                              
            sheet.cell(row=i + 2, column=j + 1, value=value)

    column_widths = {'A': 10, 'B': 20, 'C': 50 ,'D':30,'E':30}  # Specify the column widths as desired

    for column, width in column_widths.items():
                sheet1.column_dimensions[column].width = width

    workbook.save()
         
    cluster_codes = []

    for test in test_plan:
            tcid = test_plan[test][0]["Test Case ID"]
            print(tcid)
            sh = re.search(r'-(.*?)-', tcid)
            code = sh.group(1)
            if code == 'LOWPOWER':
                code = 'MC'

            cluster_codes.append(code)

    for code in cluster_codes:
            if code in sheet_names:
                workbook.remove(workbook[code])
                workbook.create_sheet(code, sheet_names.index(code))
                

            else:
                workbook.create_sheet(code)

    tcsummary(workbook, test_plan)
    workbook.save()



def tcsummary(workbook, updated_data):
    clusters = list(updated_data.keys())
    for cluster in clusters:
        tcids = updated_data[cluster][0]["Test Case ID"]
        sh = re.search(r'-(.*?)-', tcids)
        code = sh.group(1)
        if code == 'LOWPOWER':
            code = 'MC'
        sheet = workbook[code]
        sheet.append([cluster])
        sheet.append([""])

        testcases = updated_data[cluster]
        for testcase in testcases:
            tcfn = testcase["Test Case Name"]
            sheet.append([tcfn])
            sheet.append([""])
            sheet.append(["Purpose"])
            sheet.append([testcase["Purpose"]])
            sheet.append([""])
            sheet.append(["PICS"])
            for pics in testcase["PICS"]:
                sheet.append([pics])
            sheet.append([""])
            sheet.append(["Pre-condition"])
            if testcase["Pre-condition"] == "Nil":
                sheet.append(["Nil"])
            else:
                head = list(testcase["Pre-condition"].keys())
                sheet.append(head)
                for i in range(len(list(testcase["Pre-condition"].values())[0])):
                    val =[]
                    for key, value in testcase["Pre-condition"].items():
                        if i < len(value):
                            val.append(value[i]) 
                    sheet.append(val)
            sheet.append([""])
            sheet.append(["Test Procedure"])
            keys = list(testcase["Test Procedure"].keys())
            sheet.append(keys)
            for i in range(len(list(testcase["Test Procedure"].values())[0])):
                val =[]
                for key, value in testcase["Test Procedure"].items():
                    if i < len(value):
                        val.append(value[i]) 
                sheet.append(val)
            sheet.append([""])
            sheet.append([""])
            sheet.append([""])
            
            workbook.save()
