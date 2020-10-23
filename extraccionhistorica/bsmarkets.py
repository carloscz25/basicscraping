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

#primera tanda
#1/1/2018-30/8/2020 - Completada
#1/1/2012-31/12/2017 - Completada
#1/1/2010-31/12/2011 - Completada

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

    while(True):

        table = browser.find_element_by_id("ls_table_constituyentes")
        rows = table.find_elements_by_css_selector(".wfg_cursorMano")

        cotizaciones = []

        row = rows[currrow]
        cells = row.find_elements_by_css_selector("td")

        nombre = cells[0].text
        ticker = cells[1].text

        print("Importando historico para " + nombre + " (" + str(currrow) + ")")

        linktoissuer = cells[0].find_element_by_tag_name("a")
        linktoissuer.click()



        WebDriverWait(browser, 20).until(
            ExpectedConditions.presence_of_element_located((By.ID, "wfg_enlaceHistoCSV")))

        buttonhistorico = browser.find_element_by_id("wfg_enlaceHistoCSV")
        buttonhistorico.click()
        txtFechaDesde = evaluate(lambda: browser.find_element_by_name("txtDescargaDesde"))
        txtFechaDesde.clear()
        txtFechaDesde.send_keys("22/10/2020")
        txtFechaHasta = evaluate(lambda: browser.find_element_by_name("txtDescargaHasta"))
        txtFechaHasta.clear()
        txtFechaHasta.send_keys("22/10/2020")
        txtFechaHasta.send_keys(Keys.ENTER)

        #inicio extraccion
        continuar = True
        npagina = 0
        while(continuar==True):
            print("Pagina " + str(npagina))
            tablahistorico = browser.find_element_by_css_selector("table[summary='Listado de histórico de precios']")
            rowshistorico = tablahistorico.find_elements_by_css_selector(".wfg_cursorMano")
            for j in range(len(rowshistorico)):
                cellshistorico = rowshistorico[j].find_elements_by_tag_name("td")
                fecha = cellshistorico[0].text
                try:
                    valor = float(cellshistorico[1].text.replace(",","."))
                except:
                    valor = None
                try:
                    percdiff = float(cellshistorico[2].text.replace(",",".").replace("%",""))
                except:
                    percdiff = None
                #guardando datos
                cotizacionhist = CotizazionHistMC(nombre=nombre, ticker=ticker, valorcierre=valor, fechatexto=fecha, percdiff=percdiff )
                cotizaciones.append(cotizacionhist)
            try:
                linksiguientes = browser.find_element_by_css_selector("a[title='150 Siguientes'")
                linksiguientes.click()
                npagina = npagina + 1
            except BaseException:
                #guardando el contenido de la list cotizaciones
                Session = sessionmaker(bind=engine)
                session = Session()
                for c in cotizaciones:
                    session.add(c)
                session.commit()

                continuar = False
                currrow = currrow + 1
                succeeded = False
                while (not succeeded):
                    try:
                        browser.get(starturl)
                        succeeded = True
                    except BaseException:
                        pass


engine = create_engine("mysql+mysqlconnector://root:dtisat@localhost:3306/aitrader")
doimport(engine)