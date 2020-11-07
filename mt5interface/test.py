import MetaTrader5 as mt5
from mt5interface.placingorders import *
import pytz
from datetime import datetime
import time


#Iniciar la plataforma con la informacion de cuenta del broker con quien quiero operar
#-------------------------------------------------------------------------------------
mt5.initialize(login=30383295, password="Pknrp2h8@", server="AdmiralMarkets-Live")

# account = mt5.account_info()
# print(account)


#Procedimiento para tratar con valores
#--------------------------------------

#primero localizo los símbolos que me interesan
# s = mt5.symbols_get("TEF")[0]
#luego los selecciono en la ventana MarketWatch, con ello ya puedo monitorizar el valor a los
#intervalos que me convengan
# res = mt5.symbol_select(s.name, True)

#Monitorizando el valor de un simbolo
#------------------------------------

#el terminal tarda unos segundos en cargar los datos por tanto es preciso
#precargar los valores en la ventana marketwatch

# while(True):
#     info = mt5.symbol_info('TEF')
#     print(str(info.bid) + "-" + str(info.ask))
#     time.sleep(5)


# generando requests y enviando ordenes buypending y cancelandolas
#-----------------------------------------------------------------

# req = getrequest_placeorderbuypendingexecution("TEF",10.00, 1.9)
# res = mt5.order_send(req)
# print(res)
#
# req = getrequest_cancelbuypendingexecution(res.order)
# res = mt5.order_send(req)
# print(res)

#consultando las posiciones abiertas
#--------------------------------------

# positions = mt5.positions_get()
# print(positions)

#consultando informacion historica
#ojo va con 2h de adelanto
# rates = getrates("TEF", mt5.TIMEFRAME_M1, "06-11-2020 07:00", "06-11-2020 21:00")
#
# for r in rates:
#     print(str(r) + str(datetime.fromtimestamp(r[0])))




mt5.shutdown()