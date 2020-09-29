import pandas
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

engine = create_engine("mysql+mysqlconnector://root:dtisat@localhost:3306/aitrader")

sql = "select ts, ultimo from cotizacionesconsolidadas_mc where ticker like 'ITX' and day(ts)=4 and month(ts)=9;"

reedf = pandas.read_sql(sql, engine)



reedf.plot(x='ts', y='ultimo', linewidth=1.0)
print(reedf)
y = 2
