from selenium import webdriver
from selenium.webdriver.firefox.options import Options
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
from globalutils import evaluate
from tickermanagement.utils import gettickersdictionary, INFOBOLSA
import defaults
from globalutils import mthprint, gettimestampfromfechatexto





def doimportinfobolsa(engine, iteracion):



    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-dev-shm-usage')
    if defaults.RUNNING_ON == "WINDOWS":
        browser = webdriver.Firefox(firefox_options=firefox_options)
    if defaults.RUNNING_ON == "UBUNTU":

        browser = webdriver.Firefox(executable_path=defaults.pathfirefoxdriver, firefox_options=firefox_options)

    succeeded = False
    while(not succeeded):
        try:
            browser.get('https://www.infobolsa.es/mercado-nacional/mercado-continuo')
            succeeded = True
        except BaseException:
            pass

    WebDriverWait(browser, 20).until(ExpectedConditions.presence_of_all_elements_located((By.CSS_SELECTOR,".fullTable tr")))

    buttonpressed = False
    while(buttonpressed==False):
        try:
            buttonEntendido = evaluate(lambda:browser.find_element_by_class_name("introjs-button"))
            buttonEntendido.click()
            buttonpressed = True
        except BaseException:
            time.sleep(2)

    #ahora puedo comenzar a extraer



    cotizaciones = []


    tabla = evaluate(lambda:browser.find_element_by_class_name("fullTable"))

    rows = evaluate(lambda:tabla.find_elements_by_tag_name("tr"))
    mthprint("INFOBOLSA:Importando...: Iteracion " + str(iteracion))
    for i in range(len(rows)):
        row = evaluate(lambda:rows[i])
        if (i >= 1):
            # browser.wait.until(ExpectedConditions.stalenessOf(row));


            cells = evaluate(lambda:row.find_elements_by_tag_name("td"))
            valor = {}

            valor["nombre"] = evaluate(lambda:cells[2].find_element_by_tag_name("a").get_property("text"))
            valor["ultimo"] = evaluate(lambda:cells[3].text)
            valor["percdiff"] = evaluate(lambda:cells[4].text)
            valor["max"] = evaluate(lambda:cells[5].text)
            valor["min"] = evaluate(lambda:cells[6].text)
            valor["vol"] = evaluate(lambda:cells[8].text)
            valor["efectivo"] = evaluate(lambda:cells[9].text)
            valor["fecha"] = evaluate(lambda:cells[10].text)
            dateTimeNow = datetime.datetime.now()
            valor["fecha"] = valor["fecha"]

            valor['hora'] = None

            # print(valor)

            cotizacionMc = CotizacionMC()
            cotizacionMc.iteracion = iteracion
            cotizaciones.append(cotizacionMc)
            cotizacionMc.nombre = valor["nombre"]
            cotizacionMc.nombre = ''.join(e for e in cotizacionMc.nombre if e.isalnum())
            cotizacionMc.ultimo = evaluate(lambda:str2float(valor['ultimo']))
            cotizacionMc.percdiff = evaluate(lambda:str2float(valor['percdiff']))
            cotizacionMc.max = evaluate(lambda:str2float(valor['max']))
            cotizacionMc.min = evaluate(lambda:str2float(valor['min']))
            cotizacionMc.vol = evaluate(lambda:str2float(valor['vol']))
            cotizacionMc.efectivo = evaluate(lambda:str2float(valor['efectivo']))
            cotizacionMc.ts = dateTimeNow
            cotizacionMc.fechaTexto = valor["fecha"]
            cotizacionMc.source = INFOBOLSA

            try:
                cotizacionMc.derivedsourcetimestamp = gettimestampfromfechatexto(INFOBOLSA, cotizacionMc)
            except:
                pass

            # tratamos de guardar un valor timestamp directamente
            try:
                cotizacionMc.derivedsourcetimestamp = gettimestampfromfechatexto(INFOBOLSA, cotizacionMc)
            except BaseException as be:
                pass

            tickerdict = gettickersdictionary(INFOBOLSA, engine)
            if cotizacionMc.nombre in tickerdict:
                cotizacionMc.ticker = tickerdict[cotizacionMc.nombre]

            Session = sessionmaker(bind=engine)
            session = Session()
            session.add(cotizacionMc)
            session.commit()


    browser.quit()









