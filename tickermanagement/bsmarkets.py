from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from model import CotizazionHistMC, TickerMC
import datetime
import time
from globalutils import str2float
from globalutils import isopentime
from globalutils import evaluate


def checktickers_bsmarkets(engine):

    starturl = "https://www.bsmarkets.com/cs/Satellite?cid=1191407147971&pagename=BSMarkets2%2FPage%2FPage_Interna_WFG_Template&language=es_ES"

    firefox_options = Options()
    # firefox_options.add_argument('--headless')
    # firefox_options.add_argument('--no-sandbox')
    # firefox_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Firefox(firefox_options=firefox_options)


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

        t = TickerMC()
        t.bsmarkets = nombre
        t.ticker = ticker

        Session = sessionmaker(bind=engine)
        session = Session()
        t = session.query(TickerMC).filter(TickerMC.ticker == ticker).first()
        if t == None:
            t = TickerMC()
            t.ticker = ticker
            t.bsmarkets = nombre
            session.add(t)
            session.commit()
        else:
            if t.bsmarkets == None:
                t.bsmarkets = nombre
                session.add(t)
                session.commit()
        session.close()
        currrow = currrow + 1
    print("Tickers BSMarkets verificados!")



engine = create_engine("mysql+mysqlconnector://root:dtisat@localhost:3306/aitrader")
checktickers_bsmarkets(engine)