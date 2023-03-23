from Scraping import Scraping,By,time,EC,TimeoutException
from selenium.webdriver.common.keys import Keys
from utils import Comentario,ImportantWordsGroup
from config import USERINVOICE,PASSWORDINVOICE

class Simpleinvoice(Scraping):
    def __init__(self) -> None:
        super().__init__()
    
    def Login(self):
        self.SetUrl("https://simpleinvoiceweb.com/#/login")
        
        self.LoginBase(By.CSS_SELECTOR,By.CSS_SELECTOR,"input[name='email']","input[name='password']",USERINVOICE,PASSWORDINVOICE,By.CSS_SELECTOR,"button.btn-done")

    def CreateInvoice(self,client,items):
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"a.lw-cursor-pointer.waves-effect")))
        except TimeoutException:
            print(self.Error()) 
        self.driver.find_elements(By.CSS_SELECTOR,"a.lw-cursor-pointer.waves-effect")[0].click()
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH,"//a[contains(text(),'Agregar nueva factura')]")))
        except TimeoutException:
            print(self.Error())
        self.driver.find_element(By.XPATH,"//a[contains(text(),'Agregar nueva factura')]").click()

        
        
        self.driver.find_element(By.ID,"lwAddClient").send_keys(client)
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"span.mat-option-text")))
        except TimeoutException:
            print(self.Error())
        self.driver.find_elements(By.CSS_SELECTOR,"span.mat-option-text")[1].click()

        total=0.0
        for itemName,itemValue in items:
            total=total+itemValue
            try:
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"input[name='itemQuantity']")))
            except TimeoutException:
                print(self.Error())
                
            self.driver.find_element(By.CSS_SELECTOR,"input[name='itemQuantity']").send_keys(1)
            self.driver.find_element(By.CSS_SELECTOR,"input[name='itemName']").send_keys(itemName)
            self.driver.find_element(By.CSS_SELECTOR,"input[name='itemAmount']").send_keys(itemValue)
            
            #button=self.driver.find_element(By.XPATH,"//button[contains(text(),'Añadir artículo')]")
            mark=True
            mark2=True
            while mark:
                time.sleep(1)
                try:
                    if mark2:
                        self.wait.until(EC.visibility_of_element_located((By.XPATH,"//button[contains(text(),'Añadir artículo')]")))
                        mark2=False
                    ok=self.driver.find_element(By.XPATH,"//button[contains(text(),'Añadir artículo')]")
                    ok.click()
                    mark=False
                except:
                    pass
            try:
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"mat-dialog-actions.mat-dialog-actions")))
                ok=self.driver.find_element(By.CSS_SELECTOR,"mat-dialog-actions.mat-dialog-actions")
                ok.find_element(By.CSS_SELECTOR,"button.btn-done").click()
            except:
                print(self.Error())
            time.sleep(1)

        time.sleep(3) 
        self.driver.find_element(By.CSS_SELECTOR,"input[name='itemQuantity']").send_keys(1)
        self.driver.find_element(By.CSS_SELECTOR,"input[name='itemName']").send_keys("Tasa de venta de shein")
        self.driver.find_element(By.CSS_SELECTOR,"input[name='itemAmount']").send_keys(round(total*0.07,2))
        self.driver.find_element(By.XPATH,"//button[contains(text(),'Añadir artículo')]").click()
        self.driver.find_element(By.XPATH,"//button[contains(text(),'Guardar factura')]").click()
        time.sleep(3)
        self.driver.find_element(By.CSS_SELECTOR,"button.btn.new-acc-btn.me-2").click()
        time.sleep(3)

#sim = Simpleinvoice()
#sim.Login()
#sim.CreateInvoice("Hanny",[("AAAAAAAAAAA",10.2)])
#time.sleep(10)
        
            
            

        
        
        
