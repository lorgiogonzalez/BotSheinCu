from Scraping import Scraping,time

class Revolico(Scraping):
    def __init__(self) -> None:
        super().__init__()
    
    def Test(self):
        self.SetUrl("https://www.revolico.com/insertar-anuncio.html")

rev =Revolico()
rev.Test()
time.sleep(10)

