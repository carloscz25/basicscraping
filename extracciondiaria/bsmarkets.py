from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from model import CotizacionMC
import datetime
import time
from globalutils import str2float
from globalutils import isopentime
from globalutils import evaluate, gettimestampfromfechatexto
from tickermanagement.utils import BSMARKETS

from extracciondiaria.main import *
import defaults

#primera tanda
#1/1/2018-30/8/2020 - Completada
#1/1/2012-31/12/2017 - Completada
#1/1/2010-31/12/2011 - Completada

def doimportbsmarkets(engine, iteracion):

    starturl = "https://www.bsmarkets.com/cs/Satellite?cid=1191407147971&pagename=BSMarkets2%2FPage%2FPage_Interna_WFG_Template&language=es_ES"

    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-dev-shm-usage')
    if defaults.RUNNING_ON == "WINDOWS":
        browser = webdriver.Firefox(firefox_options=firefox_options)
    if defaults.RUNNING_ON == "UBUNTU":
        browser = webdriver.Firefox(defaults.pathfirefoxdriver, firefox_options=firefox_options)


    succeeded = False
    while (not succeeded):
        try:
            browser.get(starturl)
            succeeded = True
        except BaseException:
            pass

    table = evaluate(lambda:browser.find_element_by_id("ls_table_constituyentes"))
    rows = evaluate(lambda:table.find_elements_by_css_selector(".wfg_cursorMano"))

    cotizaciones = []
    mthprint("BSMARKETS:Importando...: Iteracion " + str(iteracion))
    for row in rows:


        cells = evaluate(lambda:row.find_elements_by_css_selector("td"))

        nombre = evaluate(lambda:cells[0].text)
        ticker = evaluate(lambda:cells[1].text)
        ultimo = evaluate(lambda:str2float(cells[3].text))
        percdiff = evaluate(lambda:str2float(cells[4].text))
        max = evaluate(lambda:str2float(cells[6].text))
        min = evaluate(lambda:str2float(cells[7].text))
        vol = evaluate(lambda:str2float(cells[8].text))
        hora = evaluate(lambda:cells[9].text)

        cotizacion = CotizacionMC()
        cotizacion.iteracion = iteracion
        cotizacion.ticker = ticker
        cotizacion.nombre = nombre
        cotizacion.ultimo = ultimo
        cotizacion.percdiff = percdiff
        cotizacion.max = max
        cotizacion.min = min
        cotizacion.vol = vol
        cotizacion.fechaTexto = hora
        cotizacion.ts = datetime.datetime.now()
        cotizacion.source = BSMARKETS

        # tratamos de guardar un valor timestamp directamente
        try:
            cotizacion.derivedsourcetimestamp = gettimestampfromfechatexto(BSMARKETS, cotizacion)
        except:
            pass

        cotizaciones.append(cotizacion)

    Session = sessionmaker(bind=engine)
    session = Session()
    for c in cotizaciones:
        session.add(c)
    session.commit()
    browser.quit()


