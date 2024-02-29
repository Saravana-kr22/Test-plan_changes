import re
import datetime


def test_plan_changes(existing_data, updated_data):
    new_cluster_list = list(updated_data.keys())
    old_cluster_list = list(existing_data.keys())

    added_cluster = list(set(new_cluster_list).difference(set(old_cluster_list)))
    removed_cluster = list(set(old_cluster_list).difference(set(new_cluster_list)))
    testcase_changes = {}
    new_testcase =[]
    removed_testcase =[]

    for cluster in new_cluster_list:
        if cluster in added_cluster + removed_cluster:
            continue
        newcluster = updated_data[cluster]
        oldcluster = existing_data[cluster]
        if newcluster == oldcluster:
            print(f"No changes in {cluster} cluster")
            continue
        
        if len(newcluster) >  len(oldcluster):
            for testcase in newcluster:
                if testcase not in old_cluster_list:
                    new_testcase.append(testcase) 
                    newcluster.pop(newcluster.index(testcase))
            

        elif len(newcluster) <  len(oldcluster):
            for testcase in oldcluster:
                if testcase not in newcluster:
                    removed_testcase.append(testcase) 
                    oldcluster.pop(oldcluster.index(testcase))

        for i in range(len(newcluster)):
                if newcluster[i] == oldcluster[i]:
                    print(f"{newcluster[i]['Test Case ID']} has no change ")
                else:
                    changes =[]
                    #testcase_changes.append(a[i]['Test Case ID'])
                    keys = list(newcluster[i].keys())
                    for k in keys:
                        if newcluster[i][k] == oldcluster[i][k]:
                            print(f"{newcluster[i]['Test Case ID']} {k} has no change ")
                        elif k == "Test Procedure":
                            tp = list(newcluster[i][k].keys())
                            print(tp)

                            for t in tp :
                                if newcluster[i][k][t] == oldcluster[i][k][t]:
                                    print(f"{newcluster[i]['Test Case ID']} {t} has no change ")
                                else:
                                        changes.append(f"Test procedure({t})")
                        elif k == "Test Case Name":
                            atci  = re.search(r'\[(.*?)\]\s*(.*)', newcluster[i][k])
                            atc ='[' + atci.group(1) + '] ' + atci.group(2)
                            btci  = re.search(r'\[(.*?)\]\s*(.*)', oldcluster[i][k])
                            btc ='[' + btci.group(1) + '] ' + btci.group(2)
                            if atc != btc:
                               changes.append(k) 
                        else:
                            changes.append(k)
                    testcase_changes[newcluster[i]['Test Case ID']]   = changes                  


    dif = {}
    dif = {"addedcluster": added_cluster, "removedcluster": removed_cluster, "chagedtc" : testcase_changes, "addedtc" : new_testcase,"removedtc": removed_testcase}

    return (dif)


def sumary_change(dif , version):
    diff = []
    date = datetime.date.today().strftime('%Y-%m-%d')
    if dif["chagedtc"]:
        keys = list(dif["chagedtc"].keys())
        for k in keys:
            for change in dif["chagedtc"][k]:
                if change in ["Test Case Name","Test Case ID"]:
                    diff.append((date,version, k,f"{change} is modified"))
    if dif["addedcluster"]:
        for i in dif["addedcluster"]:
            diff.append((date, version, i, "newly added cluster"))
    if dif["removedcluster"]:
        for i in dif["removedcluster"]:
            diff.append((date,version, i,"this cluster is removed"))
    if dif["addedtc"]:
        for i in dif["addedtc"]:
            diff.append((date,version, i,"new testcase is added to this cluster"))
    if dif["removedtc"]:
        for i in dif["removedtc"]:
            diff.append((date,version, i,"Testcase is removed from this cluster"))

    if not diff:
        diff.append((date,version,"Nil", f"No changes on {date} "))
    return diff

def list_of_changes(dif , version):
    diff = []
    date = datetime.date.today().strftime('%Y-%m-%d')
  
    if dif["chagedtc"]:
        keys = list(dif["chagedtc"].keys())
        for k in keys:
            for change in dif["chagedtc"][k]:
                diff.append((date,version, k,f"{change} is modified"))
    if dif["addedcluster"]:
        for i in dif["addedcluster"]:
            diff.append((date, version, i, "newly added cluster"))
    if dif["removedcluster"]:
        for i in dif["removedcluster"]:
            diff.append((date,version, i,"this cluster is removed"))
    if dif["addedtc"]:
        for i in dif["addedtc"]:
            diff.append((date,version, i,"new testcase is added to this cluster"))
    if dif["removedtc"]:
        for i in dif["removedtc"]:
            diff.append((date,version, i,"Testcase is removed from this cluster"))

    if not diff:
        diff.append((date,version,"Nil", f"No changes on {date} "))
    return diff