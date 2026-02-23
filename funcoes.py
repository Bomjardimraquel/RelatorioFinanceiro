import pandas as pd

def soma(df, categorias, tipo="Saída"):
    return df[(df["Categoria"].isin(categorias)) & (df["Tipo"] == tipo)]["Valor"].sum()

def soma_entradas(df, categorias):
    return df[(df["Categoria"].isin(categorias)) & (df["Tipo"] == "Entrada")]["Valor"].sum()
