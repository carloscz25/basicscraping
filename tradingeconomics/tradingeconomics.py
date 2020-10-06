from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import defaults
import datetime, time
from datetime import timedelta
from globalutils import evaluate
from model import MacroDataItem
from sqlalchemy.orm import sessionmaker, Session


def doextractday(day, pattern, engine):
    url = "https://tradingeconomics.com/calendar#"
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    if defaults.RUNNING_ON == "WINDOWS":
        browser = webdriver.Chrome(chrome_options=chrome_options)
    if defaults.RUNNING_ON == "UBUNTU":
        browser = webdriver.Chrome(defaults.pathchromedriver, chrome_options=chrome_options)
    succeeded = False
    while (not succeeded):
        try:
            browser.get(url)
            succeeded = True
        except BaseException:
            pass

    btnDates = browser.find_elements_by_css_selector("button[onclick^='toggleMainCountrySelection(']")[1]
    btnDates.click()

    anchorcustom = browser.find_elements_by_css_selector("ul.dropdown-menu")[5].find_elements_by_css_selector("i.glyphicon-pencil")[0].click()


    dateday = datetime.datetime.strptime(day, pattern)
    dateformatted = dateday.strftime("%m-%d-%Y")

    txtstartdate = evaluate(lambda:browser.find_elements_by_id("startDate")[0])
    txtstartdate.clear()
    txtstartdate.send_keys(dateformatted)
    txtenddate = evaluate(lambda: browser.find_elements_by_id("endDate")[0])
    txtenddate.clear()
    txtenddate.send_keys(dateformatted)
    btnsubmit = evaluate(lambda:browser.find_elements_by_css_selector("button[onclick='setCustomDates(event);'")[0])
    btnsubmit.click()


    rows = evaluate(lambda: browser.find_elements_by_css_selector("#calendar>tbody>tr"))

    for row in rows:

        time = row.find_elements_by_css_selector("td[style='white-space: nowrap;']")[0].text
        country = row.find_elements_by_css_selector("td[class='calendar-item']")[0].text
        item = row.find_elements_by_css_selector("td")[4].text

        actual = row.find_elements_by_css_selector("td[class^='calendar-item']")[1].text
        previous = row.find_elements_by_css_selector("td[class^='calendar-item']")[2].text
        consensus = row.find_elements_by_css_selector("td[class~='calendar-item']")[3].text
        forecast = row.find_elements_by_css_selector("td[class~='calendar-item']")[4].text

        print((time, country, item, actual, previous, consensus, forecast))
        mdi = MacroDataItem(source="tradingeconomics")
        mdi.time = time
        mdi.country = country
        mdi.title = item
        mdi.actual = actual
        mdi.previous = previous
        mdi.consensus = consensus
        mdi.forecast = forecast
        mdi.date = datetime.datetime.strptime(day, pattern)

        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(mdi)
        session.commit()


    y = 2

    y = 2

import model
engine = model.getaitraderengine()
pattern = "%d/%m/%Y"
datefromstr = "27/05/2020"
datetostr = "04/10/2020"
datefrom = datetime.datetime.strptime(datefromstr, pattern)
dateto = datetime.datetime.strptime(datetostr, pattern)
currdate = datefrom
while(currdate.strftime(pattern)!=datetostr):
    if (currdate.weekday() in (0,1,2,3,4)):
        print(currdate.strftime(pattern))
        doextractday(currdate.strftime(pattern), pattern, engine)
    currdate = currdate + timedelta(days=1)
    time.sleep(5)


