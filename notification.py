import http.client, urllib
conn = http.client.HTTPSConnection("api.pushover.net:443")
conn.request("POST", "/1/messages.json",
  urllib.parse.urlencode({
    "token": "axqckkgyrqa93b5d1d8ct5rdg567ix",
    "user": "uvq93ehr14f9o5ro7y6ht6az6pskh1",
    "message": "Ourdomain has new house alert",
  }), { "Content-type": "application/x-www-form-urlencoded" })
res = conn.getresponse()
print(res.status, res.msg)