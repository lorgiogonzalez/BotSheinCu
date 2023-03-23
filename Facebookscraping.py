from Scraping import Scraping,By,time,EC,TimeoutException
from selenium.webdriver.common.keys import Keys
from utils import Comentario,ImportantWordsGroup
from config import USERFACEBOOK,PASSWORDFACEBOOK
class Facebook(Scraping):
    def __init__(self) -> None:
        super().__init__()

    def Coment(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.NAME,"Más")))
        except :
            print(self.Error())
        self.driver.find_element(By.NAME,"Más").click()
        try:
            elemento= self.wait.until(EC.visibility_of_element_located((By.XPATH,"//div[contains(text(),'Grup')]")))
        except :
            print(self.Error())
        elemento.click()
        time.sleep(3)
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH,"//a[contains(text(),'Grup')]")))
        except :
            print(self.Error())
        self.driver.find_elements(By.XPATH,"//a[contains(text(),'Grup')]")[1].click()
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH,"//div[contains(text(),'Others')]")))
        except :
            print(self.Error())
        grupos=[]
        elements=self.driver.find_elements(By.CSS_SELECTOR,"a._7hkg")
        nombres=[]
        for element in elements:
            nombres.append(element.text)
        for i in range(len(nombres)):
            mark=False
            for word in ImportantWordsGroup:
                if word in nombres[i].lower():
                    mark=True
            if mark:
                grupos.append(elements[i].get_attribute('href'))
        grupos=grupos[6:]
        for group in grupos:
            self.ComentEachGroup(group)


    def Login(self):
        self.SetUrl("https://m.facebook.com/")
        self.LoginBase(By.ID,By.ID,"m_login_email","m_login_password",USERFACEBOOK,PASSWORDFACEBOOK,By.CSS_SELECTOR,"#login_password_step_element > button")
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"button[type='submit']")))
        except :
            print(self.Error()) 
        self.driver.find_element(By.CSS_SELECTOR,"button[type='submit']").click()

    def ComentEachGroup(self,group):
        time.sleep(3)
        self.SetUrl(group)
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH,"//a[contains(text(),'Escribe algo...')]")))
        except :
            print(self.Error())
        photos=self.driver.find_elements(By.XPATH,"//a[contains(text(),'Comentar')]")
        comentarrr=[]
        for photo in photos:
            comentarrr.append(photo.get_attribute("href"))
        #Likes=self.driver.find_elements(By.XPATH,"//a[contains(text(),'Me gusta')]")
        #i=0
        #for like in Likes:
        #    like.click()
        #    time.sleep(3)
        #    if i == 5:
        #        break
        #    i=i+1
        for coment in comentarrr:
            self.ComentEachPhoto(coment)

            
            
    
    def ComentEachPhoto(self,photo):
        self.SetUrl(photo)
        time.sleep(3)
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"p.xdj266r")))
        except :
            print(self.Error())
        hola=self.driver.find_element(By.CSS_SELECTOR,"p.xdj266r")
        hola.send_keys(Comentario)
        hola.send_keys(Keys.ENTER)
        time.sleep(5)
        
        

    def Responder():
        pass


fa = Facebook()
fa.Login()
fa.Coment()
time.sleep(10)
