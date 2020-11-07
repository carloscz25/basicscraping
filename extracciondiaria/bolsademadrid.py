from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from model import CotizacionMC
from globalutils import str2float, isopentime
import datetime, time
from globalutils import evaluate, gettimestampfromfechatexto
from tickermanagement.utils import gettickersdictionary, BOLSADEMADRID

from extracciondiaria.main import *
import defaults

def doimportbolsademadrid(engine, iteracion):

    try:
    
        firefox_options = Options()
        firefox_options.add_argument('--headless')
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('--disable-dev-shm-usage')
        if defaults.RUNNING_ON == "WINDOWS":
            browser = webdriver.Firefox(firefox_options=firefox_options)
        if defaults.RUNNING_ON == "UBUNTU":
            browser = webdriver.Firefox(executable_path=defaults.pathfirefoxdriver, firefox_options=firefox_options)
        succeeded = False
        while (not succeeded):
            try:
                browser.get('https://www.bolsamadrid.es/esp/aspx/Mercados/Precios.aspx?indice=ESI100000000&punto=indice')
                succeeded = True
            except BaseException:
                pass

        selectelement = evaluate(lambda:browser.find_element_by_id('SelMercado'))
        select = Select(selectelement)
        select.select_by_value('MC')

        button = evaluate(lambda:browser.find_element_by_id("ctl00_Contenido_Consultar"))
        button.click()

        #ahora puedo comenzar a extraer


        valores = []
        cotizaciones = []


        continuar = True
        while(continuar):
            tabla = evaluate(lambda:browser.find_element_by_id("ctl00_Contenido_tblAcciones"))
            rows = evaluate(lambda:tabla.find_elements_by_tag_name("tr"))
            mthprint("BOLSADEMADRID:Importando...: Iteracion " + str(iteracion))
            for i in range(len(rows)):
                row = rows[i]
                if (i >= 1):
                    cells = evaluate(lambda:row.find_elements_by_tag_name("td"))
                    valor = {}
                    valor["nombre"] = evaluate(lambda:cells[0].find_element_by_tag_name("a").get_property("text"))
                    valor["ultimo"] = evaluate(lambda:cells[1].text)
                    valor["percdiff"] = evaluate(lambda:cells[2].text)
                    valor["max"] = evaluate(lambda:cells[3].text)
                    valor["min"] = evaluate(lambda:cells[4].text)
                    valor["vol"] = evaluate(lambda:cells[5].text)
                    valor["efectivo"] = evaluate(lambda:cells[6].text)
                    valor["fecha"] = evaluate(lambda:cells[7].text)

                    try:
                        if (valor['fecha'].index("Suspendido")!=-1):
                            valor['fecha'] = valor['fecha'][10:]
                    except ValueError:
                        pass
                    if (len(cells)==9):
                        valor["hora"] = cells[8].text
                        if (valor["hora"]=='Cierre'):
                            valor['hora'] = '17:00'
                    else:
                        valor["hora"] = None
                    # print(valor)

                    cotizacionMc = CotizacionMC()
                    cotizacionMc.iteracion = iteracion
                    cotizaciones.append(cotizacionMc)
                    cotizacionMc.nombre = valor["nombre"]
                    cotizacionMc.ultimo = evaluate(lambda:str2float(valor['ultimo']))
                    cotizacionMc.percdiff = evaluate(lambda:str2float(valor['percdiff']))
                    cotizacionMc.max = evaluate(lambda:str2float(valor['max']))
                    cotizacionMc.min = evaluate(lambda:str2float(valor['min']))
                    cotizacionMc.vol = evaluate(lambda:str2float(valor['vol']))
                    cotizacionMc.efectivo = evaluate(lambda:str2float(valor['efectivo']))
                    cotizacionMc.ts = datetime.datetime.now()
                    cotizacionMc.source = BOLSADEMADRID
                    #tratamos de guardar un valor timestamp directamente
                    try:
                        cotizacionMc.derivedsourcetimestamp = gettimestampfromfechatexto(BOLSADEMADRID, cotizacionMc)
                    except:
                        pass

                    if (valor['hora']!=None):
                        cotizacionMc.fechaTexto = valor["fecha"] + " " + valor["hora"]
                    else:
                        cotizacionMc.fechaTexto = valor["fecha"]


                    tickerdict = gettickersdictionary(BOLSADEMADRID, engine)
                    if cotizacionMc.nombre in tickerdict:
                        cotizacionMc.ticker = tickerdict[cotizacionMc.nombre]

                    #parsing timestamp


                    Session = sessionmaker(bind=engine)
                    session = Session()
                    session.add(cotizacionMc)
                    session.commit()


                    valores.append(valor)
            #si descubro boton siguiente -> clickar y continuar
            try:
                btnSiguientes = browser.find_element_by_id("ctl00_Contenido_SiguientesAbj")
                if (btnSiguientes == None):
                    continuar = False
                else:
                    btnSiguientes.click()
            except NoSuchElementException:
                continuar = False

        browser.quit()
    except Exception as e:
        browser.quit()
        raise e





