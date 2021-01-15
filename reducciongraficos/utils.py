import matplotlib.pyplot as plt


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
        s += "(" + self.valorInicio + "-" + self.valorPI + "-" + self.valorFin + ")"

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
    ax.plot(ttss, valores, linewidth=0.3)


import MetaTrader5 as mt5
import mt5interface.placingorders as mt5i

#probamos funcion con valores reales
mt5.initialize(login=30383295, password="Pknrp2h8@", server="AdmiralMarkets-Live")
df = mt5i.getratesaspandasdataframe("FDR", mt5.TIMEFRAME_H1, "01-12-2020 08:00", "14-12-2020 18:00")
timestamps = df["tts"].values
valores = df["close"].values
ts_c, v_c = concatena_segmentos_contiguos_de_igual_pendiente(timestamps, valores)
ondas = transforma_segmentos_en_ondas_impulsoras_regresoras(ts_c, v_c)

fig, (ax1, ax2, ax3) = plt.subplots(3,1, sharex=True)
ax1.plot(timestamps, valores, linewidth=0.3)
ax2.plot(ts_c, v_c, linewidth=0.3)
plot_ondas(ondas, ax3)

plt.show()

y = 2
