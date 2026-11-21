"""
Testes unitários — qualidade.py
Cobre: grafia das categorias, categorias desconhecidas, sugestões e avisos do arquivo.
"""
import pandas as pd
import pytest

from qualidade import (
    analisar_qualidade, canonizar_categorias, categorias_nao_reconhecidas,
    chave_categoria, sugerir_cadastro,
)

CATS = {
    "CATS_RECEITA": ["REC | Honorário Partido"],
    "CATS_RECEITA_FIN": ["REC | Resultado de Investimento"],
    "CATS_DESPESA_OP": ["DES | Folha Pagamento", "DES | Aluguel"],
}
CADASTRADAS = [n for ns in CATS.values() for n in ns]


def _df(*linhas):
    cols = ["Data", "Descricao", "Categoria", "Centro de custo", "Pago para / Recebido de", "Valor", "Tipo"]
    return pd.DataFrame(linhas, columns=cols)


# ── chave_categoria ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("a,b", [
    ("DES | Folha Pagamento", "des | folha pagamento"),
    ("DES| Folha Pagamento", "DES | Folha Pagamento"),
    ("DES  |  Folha   Pagamento ", "DES | Folha Pagamento"),
])
def test_chave_ignora_caixa_e_espacos(a, b):
    assert chave_categoria(a) == chave_categoria(b)


def test_chave_nao_ignora_acento():
    assert chave_categoria("DES | Folha Pagamento") != chave_categoria("DES | Folha Pagamentó")


# ── canonizar_categorias ──────────────────────────────────────────────────────

def test_canonizar_usa_grafia_cadastrada():
    df = _df(("01/09/2026", "x", "REC | Resultado de investimento", "", "A", 100.0, "Entrada"))
    novo, ajustes = canonizar_categorias(df, CADASTRADAS)
    assert novo["Categoria"].iloc[0] == "REC | Resultado de Investimento"
    assert ajustes == [{"arquivo": "REC | Resultado de investimento", "cadastrada": "REC | Resultado de Investimento"}]
    # o original não é alterado
    assert df["Categoria"].iloc[0] == "REC | Resultado de investimento"


def test_canonizar_sem_mudanca_nao_gera_ajuste():
    df = _df(("01/09/2026", "x", "DES | Aluguel", "", "A", -50.0, "Saída"))
    novo, ajustes = canonizar_categorias(df, CADASTRADAS)
    assert novo["Categoria"].iloc[0] == "DES | Aluguel"
    assert ajustes == []


def test_canonizar_duas_cadastradas_iguais_vale_a_primeira():
    df = _df(("01/09/2026", "x", "rec | compensação/liminar", "", "A", 10.0, "Entrada"))
    novo, _ = canonizar_categorias(df, ["REC | Compensação/Liminar", "REC | Compensação/liminar"])
    assert novo["Categoria"].iloc[0] == "REC | Compensação/Liminar"


def test_canonizar_mantem_vazios():
    df = _df(("01/09/2026", "x", None, "", "A", 10.0, "Entrada"))
    novo, ajustes = canonizar_categorias(df, CADASTRADAS)
    assert pd.isna(novo["Categoria"].iloc[0]) and ajustes == []


# ── categorias_nao_reconhecidas ───────────────────────────────────────────────

def test_nao_reconhecidas_ignora_vazias_e_cadastradas():
    df = _df(
        ("01/09/2026", "a", "DES | Aluguel", "", "A", -1.0, "Saída"),
        ("01/09/2026", "b", "DES | Nova", "", "A", -1.0, "Saída"),
        ("01/09/2026", "c", "", "", "A", -1.0, "Saída"),
        ("01/09/2026", "d", None, "", "A", -1.0, "Saída"),
    )
    assert categorias_nao_reconhecidas(df, CADASTRADAS) == ["DES | Nova"]


# ── sugerir_cadastro ──────────────────────────────────────────────────────────

def test_sugestao_parecida_sem_acento():
    r = sugerir_cadastro("DES | Folha Pagamentó", CATS)
    assert r == {"parecidaCom": "DES | Folha Pagamento", "grupoSugerido": "CATS_DESPESA_OP"}


def test_sugestao_parecida_com_letra_trocada():
    r = sugerir_cadastro("REC | Honorario Partidoo", CATS)
    assert r["parecidaCom"] == "REC | Honorário Partido"
    assert r["grupoSugerido"] == "CATS_RECEITA"


@pytest.mark.parametrize("cat,grupo", [
    ("DES | Algo totalmente novo", "CATS_DESPESA_OP"),
    ("CUS | Outro custo qualquer", "CATS_CUSTO_DIRETO"),
    ("IMP | ISS", "CATS_IMPOSTO"),
    ("SOC | Pró-labore sócio", "CATS_SOCIETARIO"),
    ("FIN | Financiamento", "CATS_EMPRESTIMO"),
    ("REP | Repasse", "CATS_TRANSITORIO"),
])
def test_sugestao_por_prefixo(cat, grupo):
    r = sugerir_cadastro(cat, CATS)
    assert r == {"parecidaCom": None, "grupoSugerido": grupo}


def test_sugestao_sem_prefixo_conhecido():
    assert sugerir_cadastro("Qualquer coisa", CATS) == {"parecidaCom": None, "grupoSugerido": None}


# ── analisar_qualidade ────────────────────────────────────────────────────────

OPERACIONAIS = ["REC | Honorário Partido", "DES | Folha Pagamento", "DES | Aluguel"]


def test_qualidade_arquivo_limpo():
    df = _df(
        ("01/09/2026", "a", "DES | Aluguel", "Escritório", "Imob", -3000.0, "Saída"),
        ("02/09/2026", "b", "REC | Honorário Partido", "Civil", "Cli", 5000.0, "Entrada"),
    )
    a = analisar_qualidade(df, OPERACIONAIS)
    assert a["semCategoria"]["qtd"] == 0
    assert a["semCentroCusto"]["qtd"] == 0
    assert a["valorInvalido"]["qtd"] == 0
    assert a["possiveisDuplicadas"] == {"grupos": 0, "qtd": 0, "exemplos": []}


def test_qualidade_sem_centro_so_conta_categorias_operacionais():
    df = _df(
        ("01/09/2026", "aluguel", "DES | Aluguel", None, "Imob", -3000.0, "Saída"),
        ("02/09/2026", "folha", "DES | Folha Pagamento", "  ", "Func", -1000.0, "Saída"),
        ("03/09/2026", "transf", "Transferência", None, "CEF", -80000.0, "Saída"),  # não é operacional
    )
    a = analisar_qualidade(df, OPERACIONAIS)
    assert a["semCentroCusto"] == {"qtd": 2, "valor": 4000.0}


def test_qualidade_sem_categoria():
    df = _df(
        ("01/09/2026", "a", None, "Civil", "X", -10.0, "Saída"),
        ("02/09/2026", "b", " ", "Civil", "X", 25.5, "Entrada"),
    )
    assert analisar_qualidade(df, OPERACIONAIS)["semCategoria"] == {"qtd": 2, "valor": 35.5}


def test_qualidade_valor_invalido():
    df = _df(("01/09/2026", "a", "DES | Aluguel", "Civil", "X", None, "Saída"))
    assert analisar_qualidade(df, OPERACIONAIS)["valorInvalido"]["qtd"] == 1


def test_qualidade_possiveis_duplicadas():
    linha = ("04/09/2026", "SALÁRIO", "DES | Folha Pagamento", "Tributário", "PHILLIPE", -4000.0, "Saída")
    df = _df(linha, linha, ("05/09/2026", "outra", "DES | Aluguel", "Civil", "Imob", -1.0, "Saída"))
    d = analisar_qualidade(df, OPERACIONAIS)["possiveisDuplicadas"]
    assert d["grupos"] == 1 and d["qtd"] == 2
    assert d["exemplos"] == [{"data": "04/09/2026", "descricao": "SALÁRIO", "valor": -4000.0, "vezes": 2}]


def test_qualidade_exemplos_limitados_a_cinco():
    linhas = []
    for i in range(8):
        l = ("01/09/2026", f"desc {i}", "DES | Aluguel", "Civil", "X", -float(i + 1), "Saída")
        linhas += [l, l]
    d = analisar_qualidade(_df(*linhas), OPERACIONAIS)["possiveisDuplicadas"]
    assert d["grupos"] == 8 and len(d["exemplos"]) == 5