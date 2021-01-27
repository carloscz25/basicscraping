import csv
import pandas
import numpy

def read_csv(filepath):
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data


def prepare_data(data, numericColumnLabels=None):
    if numericColumnLabels is not None and len(numericColumnLabels) > 0:
        numericColumnIndexes = [data[0].index(label) for label in
                                numericColumnLabels]
        for rowIndex, row in enumerate(data):
            if rowIndex == 0:
                continue
            for numericIndex in numericColumnIndexes:
                f = float(data[rowIndex][numericIndex]) if len(
                    data[rowIndex][numericIndex]) > 0 else 0
                i = int(f)
                data[rowIndex][numericIndex] = i if i == f else f
    return data

def dataframe2datafordecisiontree(df):
    """Conversion function to turn a dataframe in to a data array processable by the DTree class"""
    cols = df.columns.values
    data = df.to_numpy()
    data2 = numpy.insert(data, 0, cols, axis=0)
    return data2
import os
df = pandas.read_csv(os.getcwd() + "\\files\\TEF.csv")
df2 = pandas.DataFrame()
df2["session_has_above_4perc_returns"] = df["session_has_above_4perc_returns"]
df2["rsi_14"] = df["rsi_14"]
df2["rsi_28"] = df["rsi_28"]
df2["rsi_42"] = df["rsi_42"]
df2["rsi_56"] = df["rsi_56"]
df2["rsi_70"] = df["rsi_70"]
df2["rsi_84"] = df["rsi_84"]
df2["rsi_98"] = df["rsi_98"]
df2 = df2.loc[df2["rsi_98"].notna()]
data = dataframe2datafordecisiontree(df2)
data = data.tolist()
from exploracion.decisiontrees.dtree import build
tree = build(data, 'session_has_above_4perc_returns',continuousAttributes=["rsi_14","rsi_28","rsi_42","rsi_56","rsi_70","rsi_84","rsi_98"])
print(tree)
y = 2