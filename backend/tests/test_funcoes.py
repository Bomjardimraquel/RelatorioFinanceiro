"""
Testes unitários — funcoes.py
"""
import pandas as pd
import pytest
from funcoes import soma, soma_entradas


@pytest.fixture
def df_base():
    """DataFrame base reutilizável nos testes."""
    return pd.DataFrame([
        {"Categoria": "REC | Honorário Avulso",    "Tipo": "Entrada", "Valor": 5000.0},
        {"Categoria": "REC | Honorário Contratado","Tipo": "Entrada", "Valor": 10000.0},
        {"Categoria": "CUS | Parceiro Jurídico",   "Tipo": "Saída",   "Valor": -2000.0},
        {"Categoria": "DES | Aluguel",             "Tipo": "Saída",   "Valor": -3000.0},
        {"Categoria": "IMP | Simples Nacional",    "Tipo": "Saída",   "Valor": -1500.0},
        {"Categoria": "REC | Honorário Avulso",    "Tipo": "Entrada", "Valor": 2000.0},
    ])


# ── soma_entradas ─────────────────────────────────────────────────────────────

def test_soma_entradas_categoria_unica(df_base):
    resultado = soma_entradas(df_base, ["REC | Honorário Avulso"])
    assert resultado == 7000.0

def test_soma_entradas_multiplas_categorias(df_base):
    resultado = soma_entradas(df_base, ["REC | Honorário Avulso", "REC | Honorário Contratado"])
    assert resultado == 17000.0

def test_soma_entradas_categoria_inexistente(df_base):
    resultado = soma_entradas(df_base, ["REC | Categoria Fantasma"])
    assert resultado == 0.0

def test_soma_entradas_nao_soma_saidas(df_base):
    """Garante que soma_entradas ignora lançamentos do tipo Saída."""
    resultado = soma_entradas(df_base, ["CUS | Parceiro Jurídico"])
    assert resultado == 0.0


# ── soma ──────────────────────────────────────────────────────────────────────

def test_soma_saida_padrao(df_base):
    resultado = soma(df_base, ["DES | Aluguel"])
    assert resultado == -3000.0

def test_soma_multiplas_categorias_saida(df_base):
    resultado = soma(df_base, ["DES | Aluguel", "IMP | Simples Nacional"])
    assert resultado == -4500.0

def test_soma_categoria_inexistente(df_base):
    resultado = soma(df_base, ["DES | Categoria Fantasma"])
    assert resultado == 0.0

def test_soma_nao_soma_entradas(df_base):
    """Garante que soma (tipo Saída) ignora lançamentos de Entrada."""
    resultado = soma(df_base, ["REC | Honorário Avulso"])
    assert resultado == 0.0

def test_soma_tipo_entrada_explicito(df_base):
    """soma aceita tipo='Entrada' explicitamente."""
    resultado = soma(df_base, ["REC | Honorário Avulso"], tipo="Entrada")
    assert resultado == 7000.0