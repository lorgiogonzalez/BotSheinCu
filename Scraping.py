from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium_stealth import stealth
from shutil import which
from utils import *

class Scraping:

    def __init__(self) -> None:
        
        #self.ruta = ChromeDriverManager(path="./cromedriver").install()
        options = Options()
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        options.add_argument(f"user-agent={user_agent}")
        #options.add_argument("--headless")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-certificate-errors")
        options.add_argument("--no-sandbox")
        options.add_argument("--log-level=3")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--no-default-broswer-check")
        options.add_argument("--no-first-run")
        options.add_argument("--no-proxy-server")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-blink-features=AutomationControlled")
        exp_opt=[
        'enable-automation',
        'ignore-certificate-errors',
        'enable-logging'
        ]
        options.add_experimental_option("excludeSwitches",exp_opt)
        service= Service(which("chromedriver"))
        self.driver= webdriver.Chrome(service=service,options=options)
        stealth(
            self.driver,
            languages=["es-Es","es"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        self.wait=WebDriverWait(self.driver,10)
        self.url = None


    def SetUrl(self,url) -> None:
        self.url=url
        self.driver.get(url)
        
    
    def Error(self):
        texto="Hola%20Este%20Url%20no%20me%20funciono%20Gracias"
        return "Por Favor Este Enlace tuvo error Comunicarse con\n" + f"https://wa.me/{NumWhatSapp}/?text={texto}"
    
    def ScrapingUnicElement(self,params)-> list:
        try:
            self.wait.until(EC.visibility_of_element_located(params[0]))
        except TimeoutException:
            return self.Error()
        result = []
        for tipo,elemento in params:
            try:
                result.append(self.driver.find_element(tipo,elemento).text)
            except:
                result.append(None)
        return result
    
    def ScrapingOnePageAllElemet(self,Principal,atributs)-> list:
        Elementos = []
        tipoPrincipal,elementPrincipal=Principal
        disable=None
        while disable==None:
            mark=False
            try:
                self.wait.until(EC.visibility_of_element_located(Principal))
            except TimeoutException:
                return self.Error()
            try:
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"body > div.j-popup-us > div > div > div.c-modal > div > div > div.modal-header > i")))
            except TimeoutException:
                mark=True
                print("No Salio")
            if not mark:
                self.driver.find_element(By.CSS_SELECTOR,"body > div.j-popup-us > div > div > div.c-modal > div > div > div.modal-header > i").click()
            try:
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"span.sui-pagination__next.sui-pagination__btn")))
                prox = self.driver.find_element(By.CSS_SELECTOR,"span.sui-pagination__next.sui-pagination__btn")
                disable= prox.get_attribute("disabled")
                try:
                    self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"span.sui-pagination__next.sui-pagination__btn.sui-pagination__hover")))
                except TimeoutException:
                    disable="true"
            except TimeoutException:
                disable="true"
            

            elements=self.driver.find_elements(tipoPrincipal,elementPrincipal)
            for element in elements:
                partes= []
                for atribut in atributs:
                    try:
                        partes.append(element.get_attribute(atribut))
                    except:
                        partes.append(None)
                Elementos.append(partes)
            if disable==None:
                prox.click()
        return Elementos

    def LoginBase(self,typeUser,typePasword,ByIdUser,ByIdPassword,User,Password,typeSub,submit):
        try:
            self.wait.until(EC.visibility_of_element_located((typeUser,ByIdUser)))
        except TimeoutException:
            return self.Error()
        self.driver.find_element(typeUser,ByIdUser).send_keys(User)
        time.sleep(1)
        try:
            self.wait.until(EC.visibility_of_element_located((typePasword,ByIdPassword)))
        except TimeoutException:
            return self.Error()
        self.driver.find_element(typePasword,ByIdPassword).send_keys(Password)
        time.sleep(1)
        self.driver.find_element(typeSub,submit).click()
        

