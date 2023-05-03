from lib.extrahop_api import ExtrahopApi
import json


API = ExtrahopApi()



payload = {}

r = API.get_info("detections")
print(r.json())

with open("test.json", "w") as fw:
    json.dump(r.json(), fw, indent=4)

r = API.post_info("detections", payload=payload)
print(r.json())

r = API.post_info("detections", payload=payload)
print(r.status_code)


