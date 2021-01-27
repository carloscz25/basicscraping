import matplotlib.pyplot as plt
from mpl_candlestics.mpl_candlesticks import plot_candlesticks




class onda():
    impulsoraRegresora = None
    valorInicio, valorFin = None, None
    timestampInicio, timestampFin = None, None
    valorPI, timestampPI = None, None

    def __str__(self):
        s = "";
        if self.impulsoraRegresora==None:
            s += "Neutra"
        elif self.impulsoraRegresora == True:
            s += "Impulsora"
        elif self.impulsoraRegresora == False:
            s += "Regresora"
        s += "(" + str(self.valorInicio) + "-" + str(self.valorPI) + "-" + str(self.valorFin) + ")"
        return s

def concatena_segmentos_contiguos_de_igual_pendiente(timestamps, valores):
    """
    Metodo reduce array de timestamps y valores a segmentos lineales concatenados contiguos cuando
    la pendiente coincide. El resultado debería ser una secuencia de segmenos lineales, alternando la
    pendiente de los mismos positiva y negativa (+-+-+-+-+-+-+-)
    :param timestamps: array-like de timestamps
    :param valores: array-like de valores
    :return: sendos arrays de timestamps y valores reflejando la estructura alternada de segmentos
    positivos y negativos
    """
    c_ts = []
    c_v = []
    buffer = ""
    indexdesde, indexhasta = -1, -1
    for i in range(1,len(timestamps)):
        valorde, valora = valores[i-1], valores[i]
        pendienteactual = ""
        if valora > valorde:
            pendienteactual = "+"
        elif valora < valorde:
            pendienteactual = "-"
        else:
            pendienteactual = "="
        if (buffer == ""):
            buffer = pendienteactual
            indexdesde = i
            c_ts.append(timestamps[i-1])
            c_v.append(valores[i-1])
        else:
            if buffer == pendienteactual:
                pass
            else:
                c_ts.append(timestamps[i-1])
                c_v.append(valores[i-1])
                buffer = pendienteactual
    c_ts.append(timestamps[len(timestamps)-1])
    c_v.append(valores[len(valores) - 1])
    return c_ts, c_v

def transforma_segmentos_en_ondas_impulsoras_regresoras(timestamps, valores):
    """
    Transforma el array de timestamps y valores en array de ondas impulsoras-regresoras
    :param timestamps:
    :param valores:
    :return: array de instancias de clase onda
    """
    ondas = []
    curronda = None
    for i in range(1, len(timestamps)):
        valorde, valora = valores[i - 1], valores[i]
        if valora > valorde:
            curronda = onda()
            curronda.valorInicio = valorde
            curronda.valorPI = valora
            curronda.timestampInicio = timestamps[i-1]
            curronda.timestampPI = timestamps[i]
        elif curronda != None:
            curronda.valorFin = valora
            curronda.timestampFin = timestamps[i]
            if curronda.valorInicio < curronda.valorFin:
                curronda.impulsoraRegresora = True
            else:
                curronda.impulsoraRegresora = False
            ondas.append(curronda)

            curronda = None
    return ondas

def concatena_ondas_impulsoras_regresoras_de_igual_signo(ondas):
    """
    El metodo concatena aquellas ondas del mismo signo (impulsoras/regresoras) siempre y cuando sean
    contiguas, y devuelve la serie de ondas simplificada. Es decir solo concatena impulsora con impulsora
    y regresora con regresora. La concatenacion de 2 ondas del mismo signo es como resultado una onda que tiene
    su inicio en el punto inicial de la primera onda, el punto de inflexion en el mayor del punto de inflexion de ambas
    y el punto final en el punto final de la segunda onda.
    Con esta logica el resultado debería ser un array de ondas impulsoras/regresoras alternado
    :param ondas: array de ondas
    :return: array de ondas
    """
    resultantes = []
    currsigno = None #impulsora/regresora
    for o in ondas:
        if currsigno == None:
            resultantes.append(o)
            currsigno = o.impulsoraRegresora
        elif o.impulsoraRegresora == currsigno:
            #fusiono la onda actual con la ultima anexada
            #en la lista de resultantes
            oconcat = onda()
            oconcat.impulsoraRegresora = currsigno
            uonda = resultantes[len(resultantes)-1]
            oconcat.valorInicio, oconcat.timestampInicio = uonda.valorInicio, uonda.timestampInicio
            oconcat.valorFin, oconcat.timestampFin = o.valorFin, o.timestampFin
            if o.valorPI >= uonda.valorPI:
                oconcat.valorPI, oconcat.timestampPI = o.valorPI, o.timestampPI
            else:
                oconcat.valorPI, oconcat.timestampPI = uonda.valorPI, uonda.timestampPI
            resultantes[len(resultantes)-1] = oconcat
        elif o.impulsoraRegresora != currsigno:
            currsigno = o.impulsoraRegresora
            resultantes.append(o)
    return resultantes

def concatena_ondas_impulsoras_regresoras_de_signo_contrario(ondas):
    """
    Concatena ondas: concatena solo impulsora con regresora y regresora con impulsora. Debido a que el array
    resultante no guarda alternancia se deberá verificar y registrar si la onda resultante es impulsora o regresora
    :param ondas: array de ondas alternadas (I-R-I-R....)
    :return: array de ondas concatenadas que no tiene porque respetar alternancia
    """
    resultantes = []

    for i, o in enumerate(ondas):
        if o.impulsoraRegresora==False:
            if i > 0:
                # fusiono la onda actual con la onda anterior
                # y anexo en la lista de resultantes
                oconcat = onda()
                uonda = ondas[i-1]
                oconcat.valorInicio, oconcat.timestampInicio = uonda.valorInicio, uonda.timestampInicio
                oconcat.valorFin, oconcat.timestampFin = o.valorFin, o.timestampFin
                if o.valorPI >= uonda.valorPI:
                    oconcat.valorPI, oconcat.timestampPI = o.valorPI, o.timestampPI
                else:
                    oconcat.valorPI, oconcat.timestampPI = uonda.valorPI, uonda.timestampPI

                if oconcat.valorInicio>=oconcat.valorFin:
                    oconcat.impulsoraRegresora = True
                else:
                    oconcat.impulsoraRegresora = False

                resultantes.append(oconcat)
    return resultantes

def aplica_reduccion_de_ondas(ondas):
    o = concatena_ondas_impulsoras_regresoras_de_igual_signo(ondas)
    o = concatena_ondas_impulsoras_regresoras_de_signo_contrario(o)
    return o

def plot_ondas(ondas, ax):
    ttss = []
    valores = []
    for (index, onda) in enumerate(ondas):
        ttss.append(onda.timestampInicio)
        valores.append(onda.valorInicio)
        ttss.append(onda.timestampPI)
        valores.append(onda.valorPI)
    ttss.append(onda.timestampFin)
    valores.append(onda.valorFin)
    ax.plot(ttss, valores, linewidth=0.3, color='red')


import MetaTrader5 as mt5
import mt5interface.placingorders as mt5i

#probamos funcion con valores reales
mt5.initialize(login=30383295, password="Pknrp2h8@", server="AdmiralMarkets-Live")
df = mt5i.getratesaspandasdataframe("ALMSA", mt5.TIMEFRAME_M30, "12-08-2020 08:00", "18-01-2021 18:00")
timestamps = df["tts"].values
valores = df["close"].values
ts_c, v_c = concatena_segmentos_contiguos_de_igual_pendiente(timestamps, valores)
ondas = transforma_segmentos_en_ondas_impulsoras_regresoras(ts_c, v_c)

fig, (ax1, ax2) = plt.subplots(2,1, sharex=True)
# ax1.plot(timestamps, valores, linewidth=0.3)

plot_ondas(ondas, ax1)

o = aplica_reduccion_de_ondas(ondas)
o = aplica_reduccion_de_ondas(o)


plot_ondas(o, ax2)




plt.show()

y = 2
