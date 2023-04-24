import certifi
import urllib3
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()
)
import requests


urlApi="http://54.162.178.246:5163/api/Buy/GetAll"
headers = {"accept": "*/*","Content-Type": "application/json","Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IkxvcmdpbyIsInJvbGUiOiJBZG1pbiIsIm5iZiI6MTY4MjExMDExMCwiZXhwIjoxNjkwNzUwMTEwLCJpYXQiOjE2ODIxMTAxMTB9.2b1JcI9hki86F2O545tjmveG71QOGV89IUPOYi8eo38"}
params={
  "userName": "Lorgio",
  "password": "Lorgio.1998"
}
response = requests.request("GET", urlApi, headers=headers,verify=False)

json=response.json()


print(json)