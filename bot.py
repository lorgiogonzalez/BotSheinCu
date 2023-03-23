from config import *
import os
import telebot
from SheinScraping import Shein,TipoSMS,time
from SimpleInvoiceScraping import Simpleinvoice
from telebot.types import ReplyKeyboardMarkup
from telebot.types import ForceReply
from flask import Flask,request
from waitress import serve
from config import APP
import threading

#region Inicio
bot = telebot.TeleBot(TELEGRAM_TOKEN)
valores ={}
web_server = Flask(__name__)
shein = Shein()
invoice = Simpleinvoice()
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
def TipeMessage(Mesage:str):
    pos=Mesage.rfind("http")
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

def AdminListSku(message):
    if("/stop" in message.text):
        bot.reply_to(message,"Parada La Ejecuion del ultimo Comando")
        return
    link,tipo = TipeMessage(message.text)
    if not tipo == TipoSMS.Lista:
        bot.reply_to(message,shein.Error()) 
    bot.reply_to(message,shein.ScrapListSku(link)) 

def GuardarNombreLista(message):
    if("/stop" in message.text):
        bot.reply_to(message,"Parada La Ejecuion del ultimo Comando")
        return
    Name = message.text
    valores[message.chat.id]={}
    valores[message.chat.id]["ListLink"]=[]
    valores[message.chat.id]["NameList"]=Name
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie Los link de la lista",reply_markup=markup)
    bot.register_next_step_handler(msg,GuardarLinks)

def GuardarLinks(message):
    if(message.text.startswith('/')):
        if("stop" in message.text):
            bot.reply_to(message,"Parada La Ejecuion del ultimo Comando")
            return
        nombre = valores[message.chat.id]["NameList"]
        links = valores[message.chat.id]["ListLink"]
        linksfinales=[]
        for link  in links:
            spl = link.split()
            for sp in spl:
                if 'http' in sp:
                    linksfinales.append(sp)
        try:
            shein.SaveLinksInLista(nombre,linksfinales)
            bot.send_message(message.chat.id,"Guardada Correctamente")
        except Exception as e:
            bot.send_message(message.chat.id,"Hubo Algun Error "+ e)
        return
    link = message.text
    valores[message.chat.id]["ListLink"].append(link)
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie Los link de la lista",reply_markup=markup)
    bot.register_next_step_handler(msg,GuardarLinks)

def GuardarNombre(message):
    if("/stop" in message.text):
        bot.reply_to(message,"Parada La Ejecuion del ultimo Comando")
        return
    Name = message.text
    valores[message.chat.id]={}
    valores[message.chat.id]["Name"]=Name
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie el link de la lista",reply_markup=markup)
    bot.register_next_step_handler(msg,AdminCreateInvoice)

def AdminCreateInvoice(message):
    if("/stop" in message.text):
        bot.reply_to(message,"Parada La Ejecuion del ultimo Comando")
        return
    result=message.text
    Name=valores[message.chat.id]["Name"]
    del valores[message.chat.id]
    link,tipo = TipeMessage(result)
    if not tipo == TipoSMS.Lista:
        return shein.Error()
    
    try:
        datos = shein.ScrapListDatos(link)
        invoice.Login()
        invoice.CreateInvoice(Name,datos)
        bot.send_message(message.chat.id,"Creado Correctamente")
    except Exception as e:
        bot.send_message(message.chat.id,"Hubo Algun Error "+ e)
    return
    #endregion


@bot.message_handler(commands=['adminlistsku'])
def cmd_AdminListSKU(message):
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie el Link",reply_markup=markup)
    bot.register_next_step_handler(msg,AdminListSku)

@bot.message_handler(commands=['admincreateinvoice'])
def cmd_AdminCreateInvoice(message):
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie el Nombre de la Factura",reply_markup=markup)
    bot.register_next_step_handler(msg,GuardarNombre)

@bot.message_handler(commands=['admincreatelist'])
def cmd_AdminCreateList(message):
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie el Nombre de la Lista",reply_markup=markup)
    bot.register_next_step_handler(msg,GuardarNombreLista)

@bot.message_handler(content_types=["text"])
def cmd_message(message):
    if("/stop" in message.text):
        bot.reply_to(message,"No Hay Un Anterior Comando Ejecutandose")
        return
    url,tipo = TipeMessage(message.text)
    bot.reply_to(message,shein.ParserTipe(url,tipo))


#endregion





if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/adminlistsku","Solo Para Admin Listar SKU de una Lista de shein"),
        telebot.types.BotCommand("/admincreateinvoice","Solo Para Admin Crear una Factura de una Lista de shein"),
        telebot.types.BotCommand("/admincreatelist","Solo Para Admin Crear una lista de articulos"),
        telebot.types.BotCommand("/stop","Para Parar Cualquier Secuencia de Ejecucuion")
    ])
    print('Iniciando bot')
    if os.environ.get("DYNO_RAM"):
        hilo = threading.Thread(name="hilo_web_server",target=arrancar_web_server)
    else:
        hilo = threading.Thread(name="hilo_polling",target=polling)
    hilo.start()
    print("BOT INICIADO")
    print('Fin')
