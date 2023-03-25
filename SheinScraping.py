from Scraping import Scraping,time,EC,TimeoutException,webdriver
from selenium.webdriver.common.by import By
from utils import TipoSMS,ListadeArticulos,PrecioxLibra
from config import USERSEHIN,PASSWORSEHIN
class Shein(Scraping):
    def __init__(self) -> None:
        super().__init__()

    def Login(self):
        self.SetUrl("https://us.shein.com/user/auth/login?direction=nav&from=navTop")
        self.LoginBase(By.CSS_SELECTOR,By.CSS_SELECTOR,
                       "body > div.c-outermost-ctn.j-outermost-ctn > div.container-fluid-1200.j-login-container.she-v-cloak-none > div > div > div > div:nth-child(2) > div.page-login__container > div:nth-child(1) > div > div.page__login_mergeLoginItem > div:nth-child(1) > div > div.input_filed-wrapper > div > div > input",
                        "body > div.c-outermost-ctn.j-outermost-ctn > div.container-fluid-1200.j-login-container.she-v-cloak-none > div > div > div > div:nth-child(2) > div.page-login__container > div:nth-child(1) > div > div.page__login_mergeLoginItem > div:nth-child(2) > div > div > input",
                        USERSEHIN,PASSWORSEHIN,By.CSS_SELECTOR,
                        "body > div.c-outermost-ctn.j-outermost-ctn > div.container-fluid-1200.j-login-container.she-v-cloak-none > div > div > div > div:nth-child(2) > div.page-login__container > div:nth-child(1) > div > div.page__login_mergeLoginItem > div.actions > div:nth-child(1) > button"
                       )
        time.sleep(1)
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"div.skip")))
        except:
            print(self.Error()) 
        self.driver.find_element(By.CSS_SELECTOR,"div.skip").find_element(By.CSS_SELECTOR,'span').click()
        


    def ScrapArticulo(self,url):
        self.SetUrl(url)
        params=[(By.CSS_SELECTOR,"h1.product-intro__head-name"),(By.CSS_SELECTOR,"div.original"),(By.CSS_SELECTOR,"div.discount"),(By.CSS_SELECTOR,"div.product-intro__head-sku"),(By.CSS_SELECTOR,"div.bread-crumb.j-bread-crumb")]
        result=self.ScrapingUnicElement(params)
        nombre = result[0]
        precioOriginal=result[1]
        precioDes=result[2]
        Sku=result[3]
        guia=result[4]
        pesoProp = 0
        mark=False
        for nombres, peso in ListadeArticulos:
            if mark:
                break
            for nombrex in nombres:
                if nombrex in guia.lower():
                    pesoProp=peso
                    mark=True
                    break
        if not mark:
            pesoProp =0.5

        if(nombre is None or (precioOriginal is None and precioDes is None) or Sku is None):
            return self.Error()
        else:
            precio = precioOriginal if(precioDes is None) else precioDes
            precioFinal= round(float(precio[1:]) + (pesoProp* PrecioxLibra) ,2)
            if mark:
                return  f"El Nombre es:{nombre} \n"\
                    f"El Precio del Articulo es:{precio} \n"\
                    f"El Peso Promedio es :{pesoProp}\n"\
                    f"Para un Valor Total de: ${precioFinal}" 
            return  f"El Nombre es:{nombre} \n"\
                    f"El Precio del Articulo es:{precio} \n"\
                    f"El Peso Promedio No lo tenemos registrado y le asignamos :{pesoProp}\n"\
                    f"Para un Valor Total de: ${precioFinal}" 
                    

  #<a class="S-product-item__img-container j-expose__product-item-img" href="/LED-Water-Resistant-Electronic-Watch-p-12791872-cat-3301.html?mallCode=1" 
  # tabindex="0" aria-label="LED Water Resistant Electronic Watch" target="_self" da-event-click="2-3-1" da-event-expose="2-3-2" index="0" data-spu="" 
  # data-sku="sj2301146633329596" data-id="12791872" data-title="LED Water Resistant Electronic Watch" data-cat_id="3301" data-rec_mark="" data-extra_mark="" 
  # data-other_ext_mark="" data-other_d_ext_mark="" data-us-price="1.90" data-price="1.90" data-us-origin-price="1.90" data-series-brand="" data-discount="" 
  # data-label="" data-brand="" data-brand-code="" data-page="" data-show-exclusive-price="" data-video="" data-spu-img="" data-mall_tag_code="3,4_1" 
  # data-store_code="" data-promotion-id="169208" data-type-id="29" data-quickship="" data-best-deal="" data-promo-label="" data-badges="" da-eid="x3m60duj6v">
   
    def ScrapList(self,url):
        results = self.ScrapListDatos(url)
        for res in results:
            result = result + res[0] +" " + res[1] + "\n"
        return result
    
    def ScrapListDatos(self,url):
        self.SetUrl(url)
        results = self.ScrapingOnePageAllElemet((By.CSS_SELECTOR,"a.S-product-item__img-container"),["aria-label","data-us-price"])
 
        for i in range(len(results)):
            results[i][1]= float(results[i][1])

        return results

    def ScrapListSku(self,url):
        try:
            self.SetUrl(url)
            nombres= self.ScrapingUnicElement([(By.CSS_SELECTOR,"div.group-user-info")])[0]
            results = self.ScrapingOnePageAllElemet((By.CSS_SELECTOR,"a.S-product-item__img-container"),["aria-label"])
            result = nombres+"\n"
            for res in results:
                if res[0]==None:
                    result = result + "NONE" +"\n"
                    continue
                result = result + res[0]+ "\n"
            return result
        except Exception as e:
            return "Hubo Algun Error" + str(e)
    
    def ParserTipe(self,url,tipe):
        if(tipe==TipoSMS.Articulo):
            return self.ScrapArticulo(url)
        elif(tipe == TipoSMS.Lista):
            return self.ScrapListSku(url)
        return self.Error()
    
    def IraListas(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"a.header-wishlist")))
        except:
            print(self.Error()+ " AQUIII")
        self.driver.find_element(By.CSS_SELECTOR,"a.header-wishlist").click()
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"body > div.c-outermost-ctn.j-outermost-ctn > div.container-fluid-1200 > div > div.j-wish-list > div > div.tabbar > div:nth-child(2)")))
        except TimeoutException:
            return self.Error()
        self.driver.find_element(By.CSS_SELECTOR,"body > div.c-outermost-ctn.j-outermost-ctn > div.container-fluid-1200 > div > div.j-wish-list > div > div.tabbar > div:nth-child(2)").click()

    def GetNameList(self):
        self.IraListas()
        #self.SetUrl("https://us.shein.com/user/wishlist?_t=1679458937056&activeTab=2&pf=topbar")
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"div.board__card.j-board__card")))
        except TimeoutException:
            return self.Error()
        results = self.driver.find_elements(By.CSS_SELECTOR,"div.board__card.j-board__card")
        texts=[]
        for result in results:
            texts.append(result.text)
            print(result.text)
        return texts


    def CreateList(self,name):
        self.IraListas()
        #self.SetUrl("https://us.shein.com/user/wishlist?_t=1679458937056&activeTab=2&pf=topbar")
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"div.board__create")))
        except TimeoutException:
            return self.Error()
        self.driver.find_element(By.CSS_SELECTOR,"div.board__create").click()
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"input.name-input")))
        except TimeoutException:
            return self.Error()
        self.driver.find_element(By.CSS_SELECTOR,"input.name-input").send_keys(name)
        self.driver.find_element(By.CSS_SELECTOR,"body > div.c-outermost-ctn.j-outermost-ctn > div.container-fluid-1200 > div > div.j-wish-list > div > div.dialog-group > div.dialog-group__board > div > div > div.sui-dialog__footer > button").click()     

    def AdditemToList(self,urlItem,nameList):
        self.SetUrl(urlItem)
        
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"body > div.j-popup-us > div > div > div.c-modal > div > div > div.modal-header > i")))
            self.driver.find_element(By.CSS_SELECTOR,"body > div.j-popup-us > div > div > div.c-modal > div > div > div.modal-header > i").click()
        except:
            pass
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"body > div.c-outermost-ctn.j-outermost-ctn > div.j-goods-detail-v2 > div > div.goods-detailv2__media > div > div.product-intro > div.product-intro__info > div > div.product-intro__add > div.she-clearfix.product-intro__add-wrap > div > span > div.product-intro__add-like")))
        except:
            print(self.Error())
        like=self.driver.find_element(By.CSS_SELECTOR,"body > div.c-outermost-ctn.j-outermost-ctn > div.j-goods-detail-v2 > div > div.goods-detailv2__media > div > div.product-intro > div.product-intro__info > div > div.product-intro__add > div.she-clearfix.product-intro__add-wrap > div > span > div.product-intro__add-like")
        try:
            like.find_element(By.CSS_SELECTOR,"i.suiiconfont.sui_icon_save_completed_32px.hovertips")
            self.driver.find_element(By.CSS_SELECTOR,"body > div.c-outermost-ctn.j-outermost-ctn > div.j-goods-detail-v2 > div > div.goods-detailv2__media > div > div.product-intro > div.product-intro__info > div > div.product-intro__add > div.she-clearfix.product-intro__add-wrap > div > span > div.product-intro__add-like").click()
            time.sleep(1)
        except:
            pass
            
        self.driver.find_element(By.CSS_SELECTOR,"body > div.c-outermost-ctn.j-outermost-ctn > div.j-goods-detail-v2 > div > div.goods-detailv2__media > div > div.product-intro > div.product-intro__info > div > div.product-intro__add > div.she-clearfix.product-intro__add-wrap > div > span > div.product-intro__add-like").click()
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"div.product-intro__add-group")))
        except:
            print(self.Error())
        elemento = self.driver.find_element(By.CSS_SELECTOR,"div.product-intro__add-group").click()
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"ul.group-no-empty")))
        except:
            print(self.Error())
        elemento = self.driver.find_element(By.CSS_SELECTOR,"ul.group-no-empty")
        lists= elemento.find_elements(By.CSS_SELECTOR,"li")

        for lista in lists:
            if lista.find_element(By.CSS_SELECTOR,"div.right-title").text == nameList:
                but=lista.find_element(By.CSS_SELECTOR,"button")

                actions = webdriver.ActionChains(self.driver)
                actions.move_to_element(lista).perform()
                time.sleep(1)
                but.click()

    def SaveLinksInLista(self,nameList,linkList):
        self.Login()
        listasexistentes= self.GetNameList()
        if not nameList in listasexistentes:
            self.CreateList(nameList)
        for link in linkList:
            self.AdditemToList(link,nameList)
        
        

        
#
#she= Shein()
#she.Login()
#she.CreateList("Hola")
#she.AdditemToList("https://us.shein.com/SHEIN-SXY-Solid-Drawstring-Ruched-Crop-Top-p-7643727-cat-1733.html?mallCode=1","test")
#time.sleep(10)


  