import pickle
from config import *
import os
import telebot
from utils import TipoSMS
from telebot.types import ReplyKeyboardMarkup
from telebot.types import ForceReply
from flask import Flask,request
from waitress import serve
from config import APP
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
import threading
import requests
import time
from os import remove
import cv2
import pytesseract
import platform

chunk_size=2000
N_RES_PAG=15
MAX_ANCHO_ROW=5
DIR={"Datos":"./Datos/","Documents":"./Datos/"}
for key in DIR:
    try:
        os.mkdir(key)
    except:
        pass
Users=[]
Items=[]
ItemSelect=[]


urlApi="https://18.214.100.229:7163"
#urlApi="https://localhost:7000"
headers = {"Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IkxvcmdpbyIsInJvbGUiOiJBZG1pbiIsIm5iZiI6MTczNTc5MTczMywiZXhwIjoxNzQ0NDMxNzMzLCJpYXQiOjE3MzU3OTE3MzN9.04qikq0cNa0TG0jcOdKv3aipqkydboQRwogOpO-_9mw",
#headers = {"Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IkxvcmdpbyIsInJvbGUiOiJBZG1pbiIsIm5iZiI6MTY4MjI3NzA0OCwiZXhwIjoxNjkwOTE3MDQ4LCJpYXQiOjE2ODIyNzcwNDh9.Rpo51395eitrx5DtRyMrgyhQutq8wwRgvUMG2K4ZLZk",
           "accept": "*/*",
           "Content-Type": "application/json"}

#region Inicio
bot = telebot.TeleBot(TELEGRAM_TOKEN)
valores ={}
web_server = Flask(__name__)

#region Configuracion
@web_server.route('/',methods=['POST'])
def webhook():
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK",200

def polling():
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()

def arrancar_web_server():
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f'https://{APP}.herokuapp.com')
    serve(web_server,host='0.0.0.0',port=int(os.environ.get("PORT",5000)))
#endregion

#endregion
def GetPDF(num):
    urlrquest=urlApi+f'/api/Buy/GetPDF/{num}'
    r = requests.get(urlrquest, headers=headers,verify=False, stream=True)

    with open(f'./Datos/Factura {num}.pdf', 'wb') as fd:
        for chunk in r.iter_content(chunk_size):
            fd.write(chunk)
    archivo = open(f'./Datos/Factura {num}.pdf','rb')
    return archivo
def QueryToApi(url,params,tipe):
    urlrquest=urlApi+url
    response = requests.request(tipe, urlrquest, headers=headers, json=params,verify=False)
    if response==None:
        return None
    try:
        jsonresult=response.json()
        if("status" in response and response["status"] >300):
            return None
        return jsonresult
    except:
        return response
    
def UpdatePago(id,double):
    return QueryToApi(f"/api/Buy/UpdatePago/{id}",double,"PATCH")

def UpdatePesosP(id,double):
    return QueryToApi(f"/api/Buy/UpdatePeso/{id}",double,"PATCH")

def CrearMensaje(Skus,Pesos):
    print(len(Skus), len(Pesos))
    Mensaje=""
    if(not (len(Skus)== len(Pesos))):
        Mensaje= "Tiene un error el proceso\n Por favor reenviarnos el mensaje arreglado sin estas linea, solo los sku y los pesos, Los datos son los siguientes: \n"
    else:
        Mensaje="Los Datos que actualizaremos seran los siguientes\n"
    for i in range(min(len(Skus),len(Pesos))):
        Mensaje+=(Skus[i]+" "+Pesos[i]+"\n")
    if(not (len(Skus)== len(Pesos))):
        if(len(Skus)>len(Pesos)):
            Mensaje+="Sobraron dichos Skus \n"
            for i in range(len(Pesos),len(Skus)):
                Mensaje+=(Skus[i]+"\n")
        else:
            Mensaje+="Sobraron dichos Pesos \n"
            for i in range(len(Skus),len(Pesos)):
                Mensaje+=(Pesos[i]+"\n")
    return Mensaje
def ActualizarDatos(message):
    if(message.text=="/no"):
        msg = bot.send_message(message.chat.id,"Esperamos su mensaje o /fin para terminar")
        bot.register_next_step_handler(msg,ActualizarBySMS)
        return
    chatid=message.chat.id
    data=pickle.load(open(f'{DIR["Datos"]}{chatid}','rb'))
    Skus=data["SKUS"]
    Pesos=data["Pesos"]
    Mensaje=""
    datos=[]
    for i in range(len(Skus)):
        datos.append({"sku":Skus[i],"peso":Pesos[i]})

    result = QueryToApi(f'/api/Item/UpdatePesos',datos,"POST")
    try:
        results= list(result)
        if(len(results)==0):
            bot.send_message(chatid,"Hubo Algun Error en la actualizacion")
            return
        for i in range(len(Skus)):
            Mensaje+=Skus[i]+" "+Pesos[i]+" "+str(results[i])+"\n"
        bot.send_message(chatid,Mensaje)
    except:        
        bot.send_message(chatid,"Hubo Algun Error en la actualizacion")
        return       
    
def ActualizarDatos2(Skus,Pesos,chatid):
    Mensaje=""
    datos=[]
    for i in range(len(Skus)):
        datos.append({"sku":Skus[i],"peso":Pesos[i]})

    result = QueryToApi(f'/api/Item/UpdatePesos',datos,"POST")
    try:
        results= list(result)
        if(len(results)==0):
            bot.send_message(chatid,"Hubo Algun Error en la actualizacion")
            return
        for i in range(len(Skus)):
            Mensaje+=Skus[i]+" "+Pesos[i]+" "+str(results[i])+"\n"
        bot.send_message(chatid,Mensaje)
    except:        
        bot.send_message(chatid,"Hubo Algun Error en la actualizacion")
        return
    
def ActualizarBySMS(message):
    if(message.text=='/fin'):
        return
    Skus=[]
    Pesos=[]

    for lin in message.text.split('\n'):
        datos = lin.split()
        Skus.append(datos[0])
        Pesos.append(datos[1])
    
    return ActualizarDatos2(Skus,Pesos,message.chat.id)

def LeerFoto2(message):
    if(message.text=='/stop'):
        return
    markup=ForceReply()
    try:
        if(message.text=="/fin"):
            return
        if(message.text=="/text"):
            msg = bot.send_message(message.chat.id,"Esperamos su mensaje o /fin para terminar",reply_markup=markup)
            bot.register_next_step_handler(msg,ActualizarBySMS)
    except:
        pass
    try:
        ruta=bot.get_file(message.document.file_id).file_path
        url=f'https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{ruta}'
        myfile = requests.get(url)
        open('./'+ruta, 'wb').write(myfile.content)

    # Cargar imagen
        img = cv2.imread('./'+ruta)

    # Convertir imagen a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aplicar umbral para convertir a imagen binaria
        threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        sistema = platform.system()
        if(sistema=="Windows"):
            pytesseract.pytesseract.tesseract_cmd = r'D:\Tessaract\tesseract.exe'

    # Pasar la imagen por pytesseract
        text = pytesseract.image_to_string(threshold_img)

        
        texts= text.split('\n')

        SKUS=[]
        Pesos=[]

        separadores=[')','}']
        for tex in texts:
            if "commodity" in tex.lower() or "skc" in tex.lower() or "sku" in tex.lower():
                SKUS.append(tex)
            if "product weight" in tex.lower() or "roduct weight" in tex.lower() or "peso del producto" in tex.lower() or "peso" in tex.lower() or "peso del prod" in tex.lower()  or "so del prod" in tex.lower() or "l product" in tex.lower()  or "del prod" in tex.lower() or "eza inic" in tex.lower() :
                Pesos.append(tex)

        def ObtenerLosSKU(skus):
            skusResults=[]
            for sku in skus:
                div=sku.split(':')
                if(len(div)==1):
                    div=div[0].split(')')
                if(len(div)==1):
                    div=div[0].split('}')
                if(len(div)==1):
                    continue
                else:
                    div=div[-1]
                SKUFINAL=""
                for i in range(len(div)):
                    num = ord(div[i])
                    if(div[i]==' ' and len(SKUFINAL)>=6):
                        break
                    if(num>=65 and num<=90 and len(SKUFINAL)>=6):
                        break
                    if((num>=48 and num <=57) or (num>=97 and num<=122)):
                        SKUFINAL=SKUFINAL+div[i]
                skusResults.append(SKUFINAL)
            return skusResults

        def ObtenerPesos(Pesos):
            PesosFinales=[]
            for peso in Pesos:
                div=peso.split(':')
                if(len(div)==1):
                    div=div[0].split(')')
                if(len(div)==1):
                    div=div[0].split('}')
                if(len(div)==1):
                    continue
                else:
                    div=div[-1]
                PesoFinal=""
                for i in range(len(div)):
                    num = ord(div[i])
                    if(div[i]==' ' and len(PesoFinal)>=1):
                        break
                    if(num>=65 and num<=90 and len(PesoFinal)>=1 and div[i]!='O'):
                        break
                    if((num>=48 and num <=57 and len(PesoFinal)<3)):
                        PesoFinal=PesoFinal+div[i]
                if(PesoFinal!="" and PesoFinal!=" "):
                    PesosFinales.append(PesoFinal)
            return PesosFinales

        #print(len(SKUS),len(Pesos))

        SKUS=ObtenerLosSKU(SKUS)
        Pesos=ObtenerPesos(Pesos)
        #print(SKUS)
        #print(Pesos)
        remove('./'+ruta)

        Mensaje=CrearMensaje(SKUS,Pesos)

        
        bot.send_message(message.chat.id,Mensaje)

        if(len(SKUS)!=len(Pesos)):
            msg = bot.send_message(message.chat.id,"Esperamos su mensaje o /fin para terminar",reply_markup=markup)
            bot.register_next_step_handler(msg,ActualizarBySMS)
        else:
            
            datos={"SKUS":SKUS,"Pesos":Pesos}
            pickle.dump(datos,open(f'{DIR["Datos"]}{message.chat.id}','wb'))
            msg = bot.send_message(message.chat.id,"Escriba /si Para Continuar y /no si requiere modificar algo",reply_markup=markup)
            bot.register_next_step_handler(msg,ActualizarDatos)

    except Exception as ex:
        msg = bot.send_message(message.chat.id,f"Hubo error {ex} con lo que envio Envie otra foto o escriba /text para enviarlo escrito o /fin para terminar",reply_markup=markup)
        bot.register_next_step_handler(msg,LeerFoto2)


def SearByText(message):
    if(message.text=='/stop'):
        return
    users = QueryToApi(f'/api/Buy/GetItemBuySKU/{message.text}',None,"GET")
    users = list(users)
    markup=ForceReply()
    if(len(users)==0):
        msg = bot.send_message(message.chat.id,"Escriba Otro Sku EsteTuvo Error",reply_markup=markup)
        bot.register_next_step_handler(msg,SearByText) 
    else:
        mensaje = "<b> Los Nombres Son: \n</b>"
        for user in users:
            di = dict(user)
            mensaje+= f'<b>{di["user"]["userName"]} </b> con la compra <b> {di["buyId"]}</b>\n'
        bot.reply_to(message,mensaje,parse_mode="html")
        msg = bot.send_message(message.chat.id,"Escriba Otro Sku",reply_markup=markup)
        bot.register_next_step_handler(msg,SearByText)

@bot.message_handler(commands=['getpdf'])
def cmd_GetPdf(message):
    if(not message.chat.id in IDS):
        bot.reply_to(message,"No Puede Usar Dicho Comando") 
        return
    num = " ".join(message.text.split()[1:])
    if num == '':
        bot.reply_to(message,"Dicho Comando Tiene Error Tiene que escribir el numero de la compra")
        return
    pdf = GetPDF(num)
    bot.send_document(message.chat.id,pdf,caption=f'Factura de la Compra num {str(num)}')
    pdf.close()
    remove(f'./Datos/Factura {str(num)}.pdf')

@bot.message_handler(commands=['updatepago'])
def cmd_updatepago(message):
    if(not message.chat.id in IDS):
        bot.reply_to(message,"No Puede Usar Dicho Comando") 
        return
    results= message.text.split()
    result = UpdatePago(int(results[1]),{"valor":float(results[2])})
    if(result==200):
        bot.send_message(message.chat.id,"Se Actualizo Correctamente")
    else:
        bot.send_message(message.chat.id,"No Se Actualizo Correctamente")

@bot.message_handler(commands=['updatepeso'])
def cmd_UpdatePesoP(message):
    if(not message.chat.id in IDS):
        bot.reply_to(message,"No Puede Usar Dicho Comando") 
        return
    results= message.text.split()
    result = UpdatePesosP(int(results[1]),float(results[2]))
    if(result==200):
        bot.send_message(message.chat.id,"Se Actualizo Correctamente")
    else:
        bot.send_message(message.chat.id,"No Se Actualizo Correctamente")

@bot.message_handler(commands=['pesosfotos'])
def cmd_UpdatePesos(message):
    if(not message.chat.id in IDS):
        bot.reply_to(message,"No Puede Usar Dicho Comando") 
        return
    mensaje="Envie una foto o escriba /fin para terminar"
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,mensaje,reply_markup=markup)
    bot.register_next_step_handler(msg,LeerFoto2)

@bot.message_handler(commands=['searchitem'])
def cmd_UpdatePesos(message):
    if(not message.chat.id in IDS):
        bot.reply_to(message,"No Puede Usar Dicho Comando") 
        return
    mensaje="Escriba el sku por favor"
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,mensaje,reply_markup=markup)
    bot.register_next_step_handler(msg,SearByText)

@bot.message_handler(commands=['start'])
def cmd_UpdatePesos(message):
    bot.reply_to(message,message.chat.id)

if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/stop","Para Parar Cualquier Secuencia de Ejecucuion"),
        telebot.types.BotCommand("/getpdf","Escriba el numero de la compra"),
        telebot.types.BotCommand("/updatepago","Escriba el numero de la compra y el pago separado por esapcios"),
        telebot.types.BotCommand("/updatepeso","Escriba el numero de la compra y el peso separado por esapcios"),
        telebot.types.BotCommand("/pesosfotos","Actualizar segun la foto de shein"),
        telebot.types.BotCommand("/searchitem","BuscarArticulo"),
        telebot.types.BotCommand("/start","Hola")
    ])
    print('Iniciando bot')
    if os.environ.get("DYNO_RAM"):
        hilo = threading.Thread(name="hilo_web_server",target=arrancar_web_server)
    else:
        hilo = threading.Thread(name="hilo_polling",target=polling)
    hilo.start()
    print("BOT INICIADO")
    #bot.remove_webhook()
    #time.sleep(1)
    #bot.infinity_polling()
    print('Fin')
