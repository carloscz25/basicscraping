from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import defaults
from globalutils import evaluate
import datetime
import time

url = "https://www.cnmv.es/ipps/default.aspx"

year = datetime.datetime.now().year
year = 2020
ejercicios = [i for i in range(year, 2004,-1)]
ejercicios = [2019]

firefox_options = Options()
# firefox_options.add_argument('--headless')
# firefox_options.add_argument('--no-sandbox')
# firefox_options.add_argument('--disable-dev-shm-usage')
if defaults.RUNNING_ON == "WINDOWS":
    browser = webdriver.Firefox(firefox_options=firefox_options)
if defaults.RUNNING_ON == "UBUNTU":
    browser = webdriver.Firefox(defaults.pathfirefoxdriver, firefox_options=firefox_options)

succeeded = False
while (not succeeded):
    try:
        browser.get(url)
        succeeded = True
    except BaseException:
        pass



lkdescarga = evaluate(lambda: browser.find_element_by_id("lkDescarga"))
lkdescarga.click()

optentidades = evaluate(lambda:browser.find_element_by_id("wDescargas_rbTipoBusqueda_3"))
optentidades.click()

selentidades = evaluate(lambda:browser.find_element_by_id("wDescargas_drpEntidades"))
selentidades = Select(selentidades)
options = selentidades.options


for k in ejercicios:
    for i in range(1, len(options)):
        print("option " + str(i))
        for j in (2,4):

            selentidades = evaluate(lambda: browser.find_element_by_id("wDescargas_drpEntidades"))
            selentidades = Select(selentidades)
            selentidades.select_by_index(i)

            selperiodos = evaluate(lambda: browser.find_element_by_id("wDescargas_drpPeriodos"))
            selperiodos = Select(selperiodos)
            selperiodos.select_by_value(str(j))

            selejercicio = evaluate(lambda: browser.find_element_by_id("wDescargas_drpEjercicios"))
            selejercicio = Select(selejercicio)
            selejercicio.select_by_value(str(k))

            btndescarga = evaluate(lambda:browser.find_element_by_id("wDescargas_btnBuscar"))
            btndescarga.click()

            try:
                divnoelements = browser.find_element_by_id("wDescargas_Listado_pnlNoHayDatos")
            except NoSuchElementException:
                #se ha hallado link de descarga
                btndescargafichero = evaluate(lambda:browser.find_element_by_id("wDescargas_Listado_btnDescargar"))
                btndescargafichero.click()
                time.sleep(30)
            y=2

    y=2




y=2

