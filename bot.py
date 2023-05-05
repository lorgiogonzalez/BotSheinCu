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
DIR={"Datos":"./Datos/","Documents":"./documents/"}
for key in DIR:
    try:
        os.mkdir(key)
    except:
        pass
Users=[]
Items=[]
ItemSelect=[]

urlApi="http://54.162.178.246:5163"
#urlApi="https://localhost:7000"
headers = {"Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IkxvcmdpbyIsInJvbGUiOiJBZG1pbiIsIm5iZiI6MTY4MjExMDExMCwiZXhwIjoxNjkwNzUwMTEwLCJpYXQiOjE2ODIxMTAxMTB9.2b1JcI9hki86F2O545tjmveG71QOGV89IUPOYi8eo38",
#headers = {"Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IkxvcmdpbyIsInJvbGUiOiJBZG1pbiIsIm5iZiI6MTY4MjI3NzA0OCwiZXhwIjoxNjkwOTE3MDQ4LCJpYXQiOjE2ODIyNzcwNDh9.Rpo51395eitrx5DtRyMrgyhQutq8wwRgvUMG2K4ZLZk",
           "accept": "*/*",
           "Content-Type": "application/json"}

#region Inicio
bot = telebot.TeleBot(TELEGRAM_TOKEN)
valores ={}
web_server = Flask(__name__)

#endregion





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



#region Message_Handlers

    #region Funciones Extras
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

    

def GetUsers(user_name):
    result = QueryToApi("/api/usuarios/AllUser",None,"GET")
    if result== None:
        return {}
    response = []
    alls = []

    for item in  list(result):
        itemdict= dict(item)
        if (not user_name == "") and user_name.lower() in itemdict["userName"].lower() or itemdict["userName"].lower() in user_name.lower():
            response.append(itemdict)
        alls.append(itemdict)
    if len(response) > 0:
        return response
    return alls

def CreateUser(message):
    if(message.text=='/stop'):
        return
    cid=message.chat.id
    result = QueryToApi("/api/usuarios/NewUsuarioPorDefecto",{"userName":message.text},"POST")
    if result == None:
        bot.send_message(cid,"ERROR AL CREAR USUARIO")
        return
    bot.send_message(message.chat.id,"USUARIO CREADO CORRECTAMENETE")
    datos=pickle.load(open(f'{DIR["Datos"]}{cid}','rb'))
    datos["result"]={}
    datos["result"]["user"]=result["id"]
    pickle.dump(datos,open(f'{DIR["Datos"]}{cid}','wb'))
    SelectUser(cid)
    return



def GetItems(linksfinales):
    result = QueryToApi("/api/Item/CreateListUrl",linksfinales,"POST")
    if result== None:
        return {}
    alls = []
    for item in  list(result):
        itemdict= dict(item)
        alls.append(itemdict)
    return alls

def Concluir(chatid):
    datos=pickle.load(open(f'{DIR["Datos"]}{chatid}','rb'))
    print(datos["result"]["user"])
    print(datos["result"]["items"])

    result = QueryToApi(f'/api/Buy/BuyItemsForUser/?userID={datos["result"]["user"]}',{"items":datos["result"]["items"],"discount":0},"POST")
    data={}
    pickle.dump(data,open(f'{DIR["Datos"]}{chatid}','wb'))
    if result== None:
        bot.send_message(chatid,"ERROR AL CREAR COMPRA")
    else:
        pdf = GetPDF(result)
        bot.send_document(chatid,pdf,caption=f'Factura de la Compra num {str(result)}')
        pdf.close()
        remove(f'./Datos/Factura {str(result)}.pdf')

def SelectUser(chatid):
    data=pickle.load(open(f'{DIR["Datos"]}{chatid}','rb'))
    markup=ForceReply()
    data["urls"]=[]
    pickle.dump(data,open(f'{DIR["Datos"]}{chatid}','wb'))
    msg = bot.send_message(chatid,"Envie Los link de la lista o escriba /fin para terminar",reply_markup=markup)
    bot.register_next_step_handler(msg,GuardarLinks)
def ProximoDesdeTipo(chatid):
    data=pickle.load(open(f'{DIR["Datos"]}{chatid}','rb'))
    item = data["items"][data["positem"]]
    if(item["tallas"]==None):
        ProximoDesdeTalla(chatid)
        return
    tallas = eval(item["tallas"])
    if(not tallas == None and len(tallas)>=2):
        markup = InlineKeyboardMarkup(row_width=MAX_ANCHO_ROW)
        botones=[]
        for tipo in list(tallas):
            botones.append(InlineKeyboardButton(tipo,callback_data=f'Select Talla {tipo}'))
        markup.add(*botones)
        bot.send_message(chatid,f'<b>{item["name"]}</b>',reply_markup=markup,parse_mode="html",disable_web_page_preview=True)
    else:
        ProximoDesdeTalla(chatid)
        
def ProximoDesdeTalla(chatid):
    markup=ForceReply()
    msg = bot.send_message(chatid,"Escriba La Cantidad(solo numero por favor)",reply_markup=markup)
    bot.register_next_step_handler(msg,ProximoDesdeCantidad)

def ProximoDesdeCantidad(message):
    if(message.text=='/stop'):
        return
    if(not str.isdigit(message.text)):
        ProximoDesdeTalla(message.chat.id)
    else:
        datos=pickle.load(open(f'{DIR["Datos"]}{message.chat.id}','rb'))  
        num = datos["num"]
        positem=datos["positem"]
        datos["result"]["items"][num]["cantidad"]=int(message.text)
        pickle.dump(datos,open(f'{DIR["Datos"]}{message.chat.id}','wb'))
        markup = InlineKeyboardMarkup(row_width=MAX_ANCHO_ROW)
        b_si=InlineKeyboardButton("SI",callback_data="SI")
        b_no= InlineKeyboardButton("NO",callback_data="NO")
        markup.row(b_si,b_no)
        bot.send_message(message.chat.id,f'<b> Va Realizar Alguna otra compra del articulo <b>{datos["items"][positem]["name"]}</b> en otra talla o tipo</b>',reply_markup=markup,parse_mode="html",disable_web_page_preview=True)


def EmpezarItem(chatid):
    datos=pickle.load(open(f'{DIR["Datos"]}{chatid}','rb'))
    positem=datos["positem"]
    if(positem>=len(datos["items"])):
        Concluir(chatid)
        return
    item=datos["items"][positem]
    markup=ForceReply()
    bot.send_message(chatid,f'<b>{item["name"]}</b> con id:{item["idShein"]}',parse_mode="html")
    if(item["tipos"]==None):
        ProximoDesdeTipo(chatid)
        return
    tipos = eval(item["tipos"])
    tipos= dict(tipos)
    if(len(tipos)>=2):
        markup = InlineKeyboardMarkup(row_width=MAX_ANCHO_ROW)
        botones=[]
        for tipo in tipos.keys():
            botones.append(InlineKeyboardButton(tipo,callback_data=f'Select Tipo {tipo}'))
        botones.append(InlineKeyboardButton("Default",callback_data='Select Tipo  '))
        markup.add(*botones)
        bot.send_message(chatid,f'Elija El Tipo',reply_markup=markup,parse_mode="html",disable_web_page_preview=True)
    else:
        ProximoDesdeTipo(chatid)

def GuardarPesos(message):
    if(message.text=='/stop'):
        return
    datos=[]
    texto=message.text.split('@')
    for text in texto:
        tex = text.split(' ')
        while tex.count(''):
            tex.remove('')
        datos.append({"palabraClave": tex[0],"peso": float(tex[1])})
    result = QueryToApi(f'/api/Item/UpdatePesosAproximados',datos,"POST")
    if (result==200):
        bot.reply_to(message,"Pesos Actualizados Correctamente")
        EmpezarItem(message.chat.id)
    else:
        bot.reply_to(message,"Los Pesos no se Actualizaron Correctamente")


def RevisarPesosAporximados(chatid,items):
    mensaje="Por Favor Devuelva un Mensaje donde Cada Pareja Este dividida por un @ una palabra clave y el peso promedio separado por espacio \n Por Ejemplo: \n Zapatos 0.50 @ Cartera 0.20\n Lor Articulos son:\n"
    pos=[]
    for i in range(len(items)):
        if(items[i]["weight"]==0):
            mensaje+=f'<b>{items[i]["name"]}</b> en {items[i]["category"]} cetegoria\n'
            pos.append(i)
    if len(pos)==0:
        EmpezarItem(chatid)
        return
    datos=pickle.load(open(f'{DIR["Datos"]}{chatid}','rb'))
    datos["Posiciones"]=pos
    pickle.dump(datos,open(f'{DIR["Datos"]}{chatid}','wb'))
    markup=ForceReply()
    msg = bot.send_message(chatid,mensaje,reply_markup=markup,parse_mode="html")
    bot.register_next_step_handler(msg,GuardarPesos)
    


def SeleccionarTiposyTallas(chatid,linksfinales,datos):
    items = GetItems(linksfinales)
    time.sleep(5)
    datos["items"]=items
    datos["result"]["items"]=[]
    for item in items:
        datos["result"]["items"].append({"itemId":item["idShein"],"cantidad":1,"tipo":"","talla":""})
    datos["num"]=0
    datos["positem"]=0
    pickle.dump(datos,open(f'{DIR["Datos"]}{chatid}','wb'))
    RevisarPesosAporximados(chatid,items)
    
    


def TipeMessage(Mesage:str):
    pos=Mesage.find("http")
    if(pos==-1):
        return(Mesage,TipoSMS.NoUrl)
    else:
        posFinal = Mesage.find(" ",pos)
        tipo = TipoSMS.Articulo
        if("wishlist" in Mesage):
            tipo = TipoSMS.Lista
        if(posFinal==-1):
            return (str(Mesage[pos:]),tipo)
        else:
            return (str(Mesage[pos:posFinal+1]),tipo)
        
def GuardarLinks(message):
    if(message.text=='/stop'):
        return
    datos=pickle.load(open(f'{DIR["Datos"]}{message.chat.id}','rb'))
    if(message.text.startswith('/')):
        if("stop" in message.text):
            bot.reply_to(message,"Parada La Ejecuion del ultimo Comando")
            return
        links = datos["urls"]
        linksfinales=[]
        for link  in links:
            spl = link.split()
            for sp in spl:
                if 'http' in sp:
                    sms,tipo = TipeMessage(sp)
                    if tipo == TipoSMS.Articulo:
                        linksfinales.append(sms)
       
            
        SeleccionarTiposyTallas(message.chat.id,linksfinales,datos)
        return
       
    link = message.text
    datos["urls"].append(link)
    pickle.dump(datos,open(f'{DIR["Datos"]}{message.chat.id}','wb'))
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie Los link de la lista o escriba /fin para terminar",reply_markup=markup)
    bot.register_next_step_handler(msg,GuardarLinks)

def SearByText(message):
    if(message.text=='/stop'):
        return
    users = QueryToApi(f'/api/Buy/GetItemBuySKU/{message.text}',None,"GET")
    users = list(users)
    markup=ForceReply()
    if(len(users)==0):
        msg = bot.send_message(message.chat.id,"Envie otra foto o escriba /text para enviarlo escrito o /fin para terminar porque ese sku no fue enconrado",reply_markup=markup)
        bot.register_next_step_handler(msg,LeerFoto) 
    else:
        mensaje = "<b> Los Nombres Son: \n</b>"
        for user in users:
            mensaje+= f'<b>{user}</b>\n'
        bot.reply_to(message,mensaje,parse_mode="html")
        msg = bot.send_message(message.chat.id,"Envie otra foto o escriba /text para enviarlo escrito o /fin para terminar",reply_markup=markup)
        bot.register_next_step_handler(msg,LeerFoto)

def LeerFoto(message):
    if(message.text=='/stop'):
        return
    markup=ForceReply()
    try:
        if(message.text=="/fin"):
            return
        if(message.text=="/text"):
            msg = bot.send_message(message.chat.id,"Escriba el sku por favor",reply_markup=markup)
            bot.register_next_step_handler(msg,SearByText)
            return            
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
        print(SKUFINAL)
        remove('./'+ruta)

        users = QueryToApi(f'/api/Buy/GetItemBuySKU/{SKUFINAL}',None,"GET")
        users = list(users)
        
        if(len(users)==0):
            msg = bot.send_message(message.chat.id,"Escriba el sku por favor de la foto no fue posible encontrarlo",reply_markup=markup)
            bot.register_next_step_handler(msg,SearByText) 
        else:
            mensaje = "<b> Los Nombres Son: \n</b>"
            for user in users:
                mensaje+= f'<b>{user}</b>\n'
            bot.reply_to(message,mensaje,parse_mode="html")
            msg = bot.send_message(message.chat.id,"Envie otra foto o escriba /text para enviarlo escrito o /fin para terminar",reply_markup=markup)
            bot.register_next_step_handler(msg,LeerFoto)
    except:
        msg = bot.send_message(message.chat.id,"Hubo error con lo que envio Envie otra foto o escriba /text para enviarlo escrito o /fin para terminar",reply_markup=markup)
        bot.register_next_step_handler(msg,LeerFoto)


def UpdatePago(id,double):
    return QueryToApi(f"/api/Buy/UpdatePago/{id}",double,"PATCH")

def UpdatePesosP(id,double):
    return QueryToApi(f"/api/Buy/UpdatePeso/{id}",double,"PATCH")






    #endregion

@bot.callback_query_handler(func=lambda x:True)
def respuesta_botones_inline(call):
    cid=call.from_user.id
    mid=call.message.id
    if call.data == "New User":
        bot.delete_message(cid,mid)
        markup=ForceReply()
        msg = bot.send_message(cid,"Escriba el nombre del usuario Nuevo",reply_markup=markup)
        bot.register_next_step_handler(msg,CreateUser)
        return
    datos=pickle.load(open(f'{DIR["Datos"]}{cid}','rb'))
    if call.data == "Users Anterior":
        if datos["pag"] == 0:
            bot.answer_callback_query(call.id,"Ya estan en la primera pagina")
        else:
            datos["pag"]-=1
            pickle.dump(datos,open(f'{DIR["Datos"]}{cid}_{mid}','wb'))
            MostrarPagina(datos["lista"],cid,datos["pag"],mid)
        return

    if call.data == "Users Siguiente":
        if (datos["pag"]+1)*N_RES_PAG>=len(datos["lista"]):
            bot.answer_callback_query(call.id,"Ya estas en la ultima pagina")
        else:
            datos["pag"]+=1
            pickle.dump(datos,open(f'{DIR["Datos"]}{cid}','wb'))
            MostrarPagina(datos["lista"],cid,datos["pag"],mid)
        return
    if "Select User" in call.data:
        datos["result"]={}
        datos["result"]["user"]=call.data.split()[2]
        pickle.dump(datos,open(f'{DIR["Datos"]}{cid}','wb'))
        SelectUser(cid)
        return

    if "Select Tipo" in call.data:
        num=datos["num"]
        valores = call.data.split()
        if(len(valores)==2):
            datos["result"]["items"][num]["tipo"]=''
        else:
            datos["result"]["items"][num]["tipo"]=" ".join(call.data.split()[2:])
        pickle.dump(datos,open(f'{DIR["Datos"]}{cid}','wb'))
        ProximoDesdeTipo(cid)
        return
    if "Select Talla"in call.data:
        num = datos["num"]
        datos["result"]["items"][num]["talla"]=" ".join(call.data.split()[2:])
        pickle.dump(datos,open(f'{DIR["Datos"]}{cid}','wb'))
        ProximoDesdeTalla(cid)
    if "Cantidad" in call.data:
        ProximoDesdeCantidad(cid)
        return
    if "NO" in call.data:
        datos["num"]+=1
        datos["positem"]+=1
        pickle.dump(datos,open(f'{DIR["Datos"]}{cid}','wb'))
        EmpezarItem(cid)
        return
    if "SI" in call.data:
        copy=datos["items"][datos["positem"]]
        datos["num"]+=1
        datos["result"]["items"].insert(datos["num"],{"itemId":copy["idShein"],"cantidad":1,"tipo":"","talla":""})
        pickle.dump(datos,open(f'{DIR["Datos"]}{cid}','wb'))
        EmpezarItem(cid)
        return
@bot.message_handler(commands=['createbuy'])
def cmd_CreateBuy(message):
    data={}
    pickle.dump(data,open(f'{DIR["Datos"]}{message.chat.id}','wb'))
    if(not message.chat.id in IDS):
        bot.reply_to(message,"No Puede Usar Dicho Comando") 
        return
    user_name = " ".join(message.text.split()[1:])
    Users = GetUsers(user_name)
    MostrarPagina(Users,message.chat.id)
    #msg = bot.send_message(message.chat.id,"Envie el Link",reply_markup=markup)
    #bot.register_next_step_handler(msg,AdminListSku)


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

@bot.message_handler(commands=['updatepesos'])
def cmd_UpdatePesos(message):
    if(not message.chat.id in IDS):
        bot.reply_to(message,"No Puede Usar Dicho Comando") 
        return
    mensaje="Por Favor Devuelva un Mensaje donde Cada Linea Abarque una palabra clave y el peso promedio separado por espacio \n Por Ejemplo: \n Zapatos 0.50\n Cartera 0.20"
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,mensaje,reply_markup=markup)
    bot.register_next_step_handler(msg,GuardarPesos)

@bot.message_handler(commands=['searchitem'])
def cmd_UpdatePesos(message):
    if(not message.chat.id in IDS):
        bot.reply_to(message,"No Puede Usar Dicho Comando") 
        return
    mensaje="Envie una foto o escriba /text para enviarlo escrito o /fin para terminar"
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,mensaje,reply_markup=markup)
    bot.register_next_step_handler(msg,LeerFoto)

@bot.message_handler(commands=['updatepago'])
def cmd_updatepago(message):
    if(not message.chat.id in IDS):
        bot.reply_to(message,"No Puede Usar Dicho Comando") 
        return
    results= message.text.split()
    result = UpdatePago(int(results[1]),float(results[2]))
    if(result==200):
        bot.send_message(message.chat.id,"Se Actualizo Correctamente")
    else:
        bot.send_message(message.chat.id,"No Se Actualizo Correctamente")

@bot.message_handler(commands=['updatepesop'])
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
    
def MostrarPagina(lista,cid,pag=0,mid=None):
    markup = InlineKeyboardMarkup(row_width=MAX_ANCHO_ROW)
    b_anterior= InlineKeyboardButton("<-",callback_data="Users Anterior")
    b_crearuser=InlineKeyboardButton("new user",callback_data="New User")
    b_siguiente= InlineKeyboardButton("->",callback_data="Users Siguiente")
    inicio = pag*N_RES_PAG
    fin=inicio+N_RES_PAG
    if fin>len(lista):
        fin=len(lista)
    n=1
    botones=[]
    mensaje = f'<i>Resultados {inicio+1}-{fin} de {len(lista)}</i>\n\n'
    for item in lista[inicio:fin]:
        botones.append(InlineKeyboardButton(str(n),callback_data=f'Select User {item["id"]}'))
        mensaje+= f'[<b>{n}</b>] {item["userName"]}\n'
        n+=1
    markup.add(*botones)
    markup.row(b_anterior,b_crearuser,b_siguiente)
    if mid:
        bot.edit_message_text(mensaje,cid,mid,reply_markup=markup,parse_mode="html",disable_web_page_preview=True)
    else:
        res=bot.send_message(cid,mensaje,reply_markup=markup,parse_mode="html",disable_web_page_preview=True)
        mid = res.message_id
        datos={"pag":0,"lista":lista}
        pickle.dump(datos,open(f'{DIR["Datos"]}{cid}','wb'))

@bot.message_handler(content_types=["text"])
def cmd_message(message):
    print(message.chat.id)

#endregion





if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/createbuy","CreateBuy"),
        telebot.types.BotCommand("/stop","Para Parar Cualquier Secuencia de Ejecucuion"),
        telebot.types.BotCommand("/updatepesos","Actualizar Pesos Aproximados"),
        telebot.types.BotCommand("/searchitem","BuscarArticulo"),
        telebot.types.BotCommand("/getpdf","Escriba el numero de la compra"),
        telebot.types.BotCommand("/updatepago","Escriba el numero de la compra y el pago separado por esapcios"),
        telebot.types.BotCommand("/updatepesop","Escriba el numero de la compra y el peso separado por esapcios")
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
