from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import time

from model import CotizacionMC, TickerMC
from globalutils import evaluate


def checktickers_bolsademadrid(engine):
    firefox_options = Options()
    # firefox_options.add_argument('--headless')
    # firefox_options.add_argument('--no-sandbox')
    # firefox_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Firefox(firefox_options=firefox_options)

    succeeded = False
    while (not succeeded):
        try:
            time.sleep(2)
            browser.get('https://www.bolsamadrid.es/esp/aspx/Mercados/Precios.aspx?indice=ESI100000000&punto=indice')
            succeeded = True
        except BaseException:
            pass


    select = Select(browser.find_element_by_id('SelMercado'))
    select.select_by_value('MC')

    button = browser.find_element_by_id("ctl00_Contenido_Consultar")
    button.click()

    #ahora puedo comenzar a extraer




    valores = []
    cotizaciones = []

    currrow = 1
    continuar = True
    # paginas a correr
    pagsacorrer = 0
    while(continuar):


        tabla = browser.find_element_by_id("ctl00_Contenido_tblAcciones")
        rows = tabla.find_elements_by_tag_name("tr")
        for i in range(len(rows)):
            if i < currrow:
                continue
            else:
                j = 0
                for j in range(pagsacorrer):
                    currrow = 1
                    try:
                        btnSiguientes = browser.find_element_by_id("ctl00_Contenido_SiguientesAbj")
                        if (btnSiguientes == None):
                            continuar = False
                        else:
                            btnSiguientes.click()
                    except NoSuchElementException:
                        continuar = False

                tabla = evaluate(lambda :browser.find_element_by_id("ctl00_Contenido_tblAcciones"))
                rows = evaluate(lambda :tabla.find_elements_by_tag_name("tr"))
                row = rows[i]


                cells = row.find_elements_by_tag_name("td")
                valor = {}
                nombrecell = cells[0].find_element_by_tag_name("a")
                nombre = nombrecell.text
                nombrecell.click()

                ticker = evaluate(lambda:browser.find_element_by_id("ctl00_Contenido_TickerDat").text.strip())

                Session = sessionmaker(bind=engine)
                session = Session()
                t = session.query(TickerMC).filter(TickerMC.ticker == ticker).first()
                if t==None:
                    t = TickerMC(ticker=ticker, bolsademadrid=nombre)
                    session.add(t)
                    session.commit()
                else:
                    if t.bolsademadrid == None:
                        t.bolsademadrid = nombre
                        session.append(t)
                        session.commit()
                session.close()
                print("Verificado ticker " + t.ticker)
                currrow = currrow + 1

                #rearrancando la navegacion
                succeeded = False
                while (not succeeded):
                    try:
                        time.sleep(2)
                        browser.get(
                            'https://www.bolsamadrid.es/esp/aspx/Mercados/Precios.aspx?indice=ESI100000000&punto=indice')
                        succeeded = True
                    except BaseException:
                        pass
                selectelement = evaluate(lambda:browser.find_element_by_id('SelMercado'))
                select = Select(selectelement)
                select.select_by_value('MC')

                button = browser.find_element_by_id("ctl00_Contenido_Consultar")
                button.click()
                #ahora ya vuelvo a estar en la pagina correcta y solo he de memorizar la fila

        # si descubro boton siguiente -> clickar y continuar
        currrow = 1
        pagsacorrer = pagsacorrer + 1
        if (pagsacorrer==3):
            print("Finalizada Verificacion Bolsa de Madrid")
            return

engine = create_engine("mysql+mysqlconnector://root:dtisat@localhost:3306/aitrader", poolclass=NullPool)
checktickers_bolsademadrid(engine)