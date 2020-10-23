from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from model import CotizazionHistMC
import datetime
import time
from globalutils import str2float
from globalutils import isopentime
from globalutils import evaluate



def doimport(engine):

    starturl = "https://www.bsmarkets.com/cs/Satellite?cid=1191407147971&pagename=BSMarkets2%2FPage%2FPage_Interna_WFG_Template&language=es_ES"

    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(chrome_options=chrome_options)


    succeeded = False
    while (not succeeded):
        try:
            browser.get(starturl)
            succeeded = True
        except BaseException:
            pass

    currrow = 0



    table = browser.find_element_by_id("ls_table_constituyentes")
    rows = table.find_elements_by_css_selector(".wfg_cursorMano")

    cotizaciones = []

    for currrow in range(len(rows)):
        row = rows[currrow]
        cells = row.find_elements_by_css_selector("td")

        nombre = cells[0].text
        ticker = cells[1].text
        precio = cells[3].text
        varperc = cells[4].text
        vareur = cells[5].text
        max = cells[6].text
        min = cells[7].text
        vol = cells[8].text

        fecha = datetime.datetime.now().strftime("%d-%m-%Y")

        cotizacionhist = CotizazionHistMC(nombre=nombre, ticker=ticker, valorcierre=precio, fechatexto=fecha,
                                          percdiff=varperc)
        cotizaciones.append(cotizacionhist)

    Session = sessionmaker(bind=engine)
    session = Session()
    for c in cotizaciones:
        session.add(c)
    session.commit()




from model import getaitraderengine

engine = getaitraderengine()
doimport(engine)