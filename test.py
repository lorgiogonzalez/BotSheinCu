#import certifi
#import urllib3
#http = urllib3.PoolManager(
#    cert_reqs='CERT_REQUIRED',
#    ca_certs=certifi.where()
#)
#import requests


#urlApi="http://54.162.178.246:5163/api/Buy/GetAll"
#headers = {"accept": "*/*","Content-Type": "application/json","Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IkxvcmdpbyIsInJvbGUiOiJBZG1pbiIsIm5iZiI6MTY4MjExMDExMCwiZXhwIjoxNjkwNzUwMTEwLCJpYXQiOjE2ODIxMTAxMTB9.2b1JcI9hki86F2O545tjmveG71QOGV89IUPOYi8eo38"}
#params={
#  "userName": "Lorgio",
#  "password": "Lorgio.1998"
#}
#response = requests.request("GET", urlApi, headers=headers,verify=False)

#json=response.json()


#print(json)

import cv2
import pytesseract

# Cargar imagen
img = cv2.imread("imagen_ejemplo.jpg")

# Convertir imagen a escala de grises
#gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Aplicar umbral para convertir a imagen binaria
#threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
pytesseract.pytesseract.tesseract_cmd = r'D:\Tessaract\tesseract.exe'
# Pasar la imagen por pytesseract
text = pytesseract.image_to_string(img)

texts= text.split()

SKU=""

for tex in texts:
    if len(text)>=16:
        SKU=tex

SKUFINAL=""
for i in range(len(SKU)):
    num = ord(SKU[i])
    if((num>=48 and num <=57) or (num>=65 and num<=90 ) or (num>=97 and num<=122)):
      SKUFINAL=SKUFINAL+SKU[i]


# Imprimir el texto extraído
print(SKUFINAL)