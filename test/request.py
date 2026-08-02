# import http.client
# conn = http.client.HTTPSConnection("localhost", 4443)
# conn.request("GET", "/")
# r1 = conn.getresponse()
# print(r1.status, r1.reason)

import requests
with requests.get("https://localhost:4443") as r:
    print(r.status_code)
    print(r.content)
