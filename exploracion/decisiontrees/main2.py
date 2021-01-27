import sklearn.tree as tree
import os
path = os.getcwd() + "\\files\\ALMSA.csv"
import matplotlib.pyplot as plt
import pandas as pandas

df = pandas.read_csv(path)
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
Y = df2["session_has_above_4perc_returns"].tolist()
df2.drop(["session_has_above_4perc_returns"], axis=1, inplace=True)
fn = df2.columns.values.tolist()
X = df2.values.tolist()

y = 2

clf = tree.DecisionTreeClassifier()

DTclf = clf.fit(X,Y)

tree.export_graphviz(clf,
                     out_file="ALMSA.dot",
                     feature_names = fn,
                     class_names=["TRUE","FALSE"],
                     filled = True)

