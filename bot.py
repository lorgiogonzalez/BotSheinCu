from config import *
import telebot
from SheinScraping import Shein,TipoSMS,time
from SimpleInvoiceScraping import Simpleinvoice
from telebot.types import ReplyKeyboardMarkup
from telebot.types import ForceReply
from flask import Flask,request
from pyngrok import ngrok,conf
from waitress import serve


bot = telebot.TeleBot(TELEGRAM_TOKEN)
valores ={}
web_server = Flask(__name__)



shein = Shein()
invoice = Simpleinvoice()

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
        

@web_server.route('/',methods=['POST'])
def webhook():
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK",200




@bot.message_handler(commands=['AdminListSKU'])
def cmd_AdminListSKU(message):
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie el Link",reply_markup=markup)
    bot.register_next_step_handler(msg,AdminListSku)

@bot.message_handler(commands=['AdminCreateInvoice'])
def cmd_AdminCreateInvoice(message):
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie el Nombre de la Factura",reply_markup=markup)
    bot.register_next_step_handler(msg,GuardarNombre)

@bot.message_handler(commands=['CreateList'])
def cmd_AdminCreateList(message):
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie el Nombre de la Lista",reply_markup=markup)
    bot.register_next_step_handler(msg,GuardarNombreLista)

def AdminListSku(message):
    link,tipo = TipeMessage(message.text)
    if not tipo == TipoSMS.Lista:
        return shein.Error()
    shein.ScrapListSku(link)

def GuardarNombreLista(message):
    Name = message.text
    valores[message.chat.id]={}
    valores[message.chat.id]["ListLink"]=[]
    valores[message.chat.id]["NameList"]=Name
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie Los link de la lista",reply_markup=markup)
    bot.register_next_step_handler(msg,GuardarLinks)

def GuardarLinks(message):
    if(message.text.startswith('/')):
        nombre = valores[message.chat.id]["NameList"]
        links = valores[message.chat.id]["ListLink"]
        linksfinales=[]
        for link  in links:
            spl = link.split()
            for sp in spl:
                if 'http' in sp:
                    linksfinales.append(sp)
        shein.SaveLinksInLista(nombre,linksfinales)
        return
    link = message.text
    valores[message.chat.id]["ListLink"].append(link)
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie Los link de la lista",reply_markup=markup)
    bot.register_next_step_handler(msg,GuardarLinks)


def GuardarNombre(message):
    Name = message.text
    valores[message.chat.id]={}
    valores[message.chat.id]["Name"]=Name
    markup=ForceReply()
    msg = bot.send_message(message.chat.id,"Envie el link de la lista",reply_markup=markup)
    bot.register_next_step_handler(msg,AdminCreateInvoice)

def AdminCreateInvoice(message):
    result=message.text
    Name=valores[message.chat.id]["Name"]
    del valores[message.chat.id]
    link,tipo = TipeMessage(result)
    if not tipo == TipoSMS.Lista:
        return shein.Error()
    datos = shein.ScrapListDatos(link)
    print(len(datos))
    invoice.Login()
    invoice.CreateInvoice(Name,datos)
    
    

@bot.message_handler(content_types=["text"])
def cmd_message(message):
    url,tipo = TipeMessage(message.text)
    bot.reply_to(message,shein.ParserTipe(url,tipo))

if __name__ == '__main__':
    #bot.set_my_commands([
    #    telebot.types.BotCommand("/AdminListSKU","Solo Para Admin Listar SKU de una Lista de shein"),
    #    telebot.types.BotCommand("/AdminCreateInvoice","Solo Para Admin Crear una Factura de una Lista de shein"),
        #telebot.types.BotCommand("/Listas","Listar Articulos y Precios Final de una Lista de shein"),
        #telebot.types.BotCommand("/Articulo","De un Articulo de shein el Precio Final en Cuba")
    #])
    print('Iniciando bot')
    conf.get_default().config_path = "./config_ngrok.yml"
    conf.get_default().region="us"
    ngrok.set_auth_token(NGROK_TOKEN)
    ngrok_tunel=ngrok.connect(5000,bind_tls=True)
    ngrok_url=ngrok_tunel.public_url
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=ngrok_url)
    serve(web_server,host="0.0.0.0",port=5000)
    #web_server.run(host="0.0.0.0",port=5000)
    #bot.infinity_polling()
    print('Fin')


