RUNNING_ON = "UBUNTU" #WINDOWS-UBUNTU
databasedriver = "pymysql" #pymysql - mysqlconnector
server = "localhost"
port = 3306
databasename = "aitrader"
user = "root"
if RUNNING_ON == "UBUNTU":
    pwd = "Pknrp2h8#"
else:
    pwd = "dtisat"
# pwd = "dtisat"
path = "/home/carlosconti/Projects/basicscraping"
# path = "/home/ubuntucontisola/aitrader/basicscraping/basicscraping "
# path = "C:\\Users\\Carlos Conti\\PycharmProjects\\basicscraping"
pathchromedriver = "/home/carlosconti/aitrader/chromedriver"
# pathfirefoxdriver = "/home/carlosconti/Projects/geckodriver"
pathfirefoxdriver = "/usr/bin/geckodriver"