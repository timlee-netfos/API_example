from lib.extrahop_api import ExtrahopApi
from termcolor import colored
import openpyxl
import pandas as pd




API = ExtrahopApi()

df = pd.read_excel("./create_devicegroup.xlsx")
df = df.fillna("")
print(df)
wb = openpyxl.load_workbook("./create_devicegroup.xlsx")
ws = wb["工作表1"]
ws.delete_rows(2, df.shape[0])
wb.save("./create_devicegroup.xlsx")

for i in range(df.shape[0]):
    ips = {}
    name = df.iloc[i, 0]
    description = df.iloc[i, 1]
    filters = []
    # ips = df.iloc[i, 2].replace(" ", "").split(",")
    # for ip in ips:
    #     filters.append({
    #         "field": "ipaddr",
    #         "operator": "=",
    #         "operand": ip
    # })
    ips[f"ip_addr_{i+1}"] = df.iloc[i, 2].replace(" ", "").split(",")
    for key in ips.keys():
        for ip in ips[key]:
            filters.append({
                "field": "ipaddr",
                "operator": "=",
                "operand": ip
            })
    payload = {
        "name": name, 
        "description": description,
        "dynamic": True,
        "filter":{
            "rules": filters,
            "operator": "or"
        }
    }
    r = API.post_info("devicegroups", payload)
    if r.status_code == 201:
        print(colored(f"{name}: Done!", "green"))
    else:
        print(colored(f"{name}: Failed!", "red"))