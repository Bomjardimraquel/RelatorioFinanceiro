"""
Testes unitários — relatorios.py
Cobre: DRE, categorias dinâmicas, ranking, centro de custos.
"""
import json
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch


# ── Fixture base ──────────────────────────────────────────────────────────────

@pytest.fixture
def df_completo():
    """DataFrame realista cobrindo todas as categorias do DRE."""
    return pd.DataFrame([
        # Receitas
        {"Data": "01/06/2026", "Categoria": "REC | Honorário Avulso",             "Tipo": "Entrada", "Valor": 5000.0,  "Pago para / Recebido de": "Cliente A", "Centro de custo": "Civil",           "Descricao": "Honorário Avulso"},
        {"Data": "02/06/2026", "Categoria": "REC | Honorário Contratado",          "Tipo": "Entrada", "Valor": 10000.0, "Pago para / Recebido de": "Cliente B", "Centro de custo": "Trabalhista",     "Descricao": "Honorário Contratado"},
        {"Data": "03/06/2026", "Categoria": "REC | Honorário Êxito",               "Tipo": "Entrada", "Valor": 8000.0,  "Pago para / Recebido de": "Cliente A", "Centro de custo": "Civil",           "Descricao": "Honorário Êxito"},
        {"Data": "04/06/2026", "Categoria": "REC | Honorário Partido",             "Tipo": "Entrada", "Valor": 6000.0,  "Pago para / Recebido de": "Cliente C", "Centro de custo": "Trabalhista",     "Descricao": "Honorário Partido"},
        {"Data": "05/06/2026", "Categoria": "REC | Honorário Sucumbencial",        "Tipo": "Entrada", "Valor": 4000.0,  "Pago para / Recebido de": "Cliente D", "Centro de custo": "Civil",           "Descricao": "Honorário Sucumbencial"},
        {"Data": "06/06/2026", "Categoria": "REC | Honorário Compensação/liminar", "Tipo": "Entrada", "Valor": 3000.0,  "Pago para / Recebido de": "Cliente E", "Centro de custo": "Tributário",      "Descricao": "Honorário Compensação"},
        # Custos diretos
        {"Data": "07/06/2026", "Categoria": "CUS | Parceiro Jurídico",             "Tipo": "Saída",   "Valor": -2000.0, "Pago para / Recebido de": "Parceiro X", "Centro de custo": "Civil",          "Descricao": "Repasse parceiro"},
        {"Data": "08/06/2026", "Categoria": "CUS | Participação contrato",         "Tipo": "Saída",   "Valor": -1500.0, "Pago para / Recebido de": "Parceiro Y", "Centro de custo": "Trabalhista",    "Descricao": "Participação contrato"},
        {"Data": "09/06/2026", "Categoria": "CUS | Diligencia",                    "Tipo": "Saída",   "Valor": -300.0,  "Pago para / Recebido de": "Cartório",   "Centro de custo": "Civil",          "Descricao": "Diligência cartório"},
        {"Data": "10/06/2026", "Categoria": "Despesa do cliente",                  "Tipo": "Saída",   "Valor": -500.0,  "Pago para / Recebido de": "TJ",         "Centro de custo": "Civil",          "Descricao": "Custas judiciais"},
        # Despesas operacionais
        {"Data": "11/06/2026", "Categoria": "DES | Aluguel",                       "Tipo": "Saída",   "Valor": -3000.0, "Pago para / Recebido de": "Imobiliária","Centro de custo": "Administrativo", "Descricao": "Aluguel junho"},
        {"Data": "12/06/2026", "Categoria": "DES | Folha Pagamento",               "Tipo": "Saída",   "Valor": -5000.0, "Pago para / Recebido de": "Funcionários","Centro de custo": "Administrativo","Descricao": "Folha junho"},
        {"Data": "13/06/2026", "Categoria": "DES | Pró-Labore",                    "Tipo": "Saída",   "Valor": -4000.0, "Pago para / Recebido de": "Sócios",      "Centro de custo": "Administrativo","Descricao": "Pró-labore junho"},
        # Impostos
        {"Data": "20/06/2026", "Categoria": "IMP | Simples Nacional",              "Tipo": "Saída",   "Valor": -2500.0, "Pago para / Recebido de": "Receita Federal","Centro de custo": "Administrativo","Descricao": "Simples Nacional"},
        {"Data": "21/06/2026", "Categoria": "IMP | INSS",                          "Tipo": "Saída",   "Valor": -800.0,  "Pago para / Recebido de": "Receita Federal","Centro de custo": "Administrativo","Descricao": "INSS junho"},
    ])


# ── gerar_relatorios ──────────────────────────────────────────────────────────

def test_dre_total_receita(df_completo):
    from relatorios import gerar_relatorios
    dre, *_ = gerar_relatorios(df_completo)
    total = dre.loc[dre["Conta"] == "RECEITAS OPERACIONAIS", "Valor (R$)"].values[0]
    assert total == 36000.0

def test_dre_total_custos(df_completo):
    from relatorios import gerar_relatorios
    dre, *_ = gerar_relatorios(df_completo)
    total = dre.loc[dre["Conta"] == "CUSTOS DIRETOS", "Valor (R$)"].values[0]
    assert total == -4300.0

def test_dre_lucro_bruto(df_completo):
    from relatorios import gerar_relatorios
    dre, *_ = gerar_relatorios(df_completo)
    lucro_bruto = dre.loc[dre["Conta"] == "LUCRO BRUTO", "Valor (R$)"].values[0]
    assert lucro_bruto == 31700.0

def test_dre_total_despesas_op(df_completo):
    from relatorios import gerar_relatorios
    dre, *_ = gerar_relatorios(df_completo)
    total = dre.loc[dre["Conta"] == "DESPESAS OPERACIONAIS", "Valor (R$)"].values[0]
    assert total == -12000.0

def test_dre_resultado_operacional(df_completo):
    from relatorios import gerar_relatorios
    dre, *_ = gerar_relatorios(df_completo)
    resultado = dre.loc[dre["Conta"] == "RESULTADO OPERACIONAL", "Valor (R$)"].values[0]
    assert resultado == 19700.0

def test_dre_total_impostos(df_completo):
    from relatorios import gerar_relatorios
    dre, *_ = gerar_relatorios(df_completo)
    total = dre.loc[dre["Conta"] == "IMPOSTOS", "Valor (R$)"].values[0]
    assert total == -3300.0

def test_dre_lucro_liquido(df_completo):
    from relatorios import gerar_relatorios
    dre, *_ = gerar_relatorios(df_completo)
    lucro = dre.loc[dre["Conta"] == "LUCRO LÍQUIDO", "Valor (R$)"].values[0]
    assert lucro == 16400.0

def test_dre_valores_arredondados(df_completo):
    """Garante que nenhum valor tem mais de 2 casas decimais."""
    from relatorios import gerar_relatorios
    dre, *_ = gerar_relatorios(df_completo)
    for val in dre["Valor (R$)"]:
        assert round(val, 2) == val

def test_dre_sem_detalhe_participacao_contrato(df_completo):
    """Garante que beneficiários de Participação em Contrato não aparecem no DRE."""
    from relatorios import gerar_relatorios
    dre, *_ = gerar_relatorios(df_completo)
    assert not any("Parceiro Y" in str(c) for c in dre["Conta"])

def test_dre_provisao_vinicius(df_completo):
    """Provisão deve reduzir o lucro bruto."""
    from relatorios import gerar_relatorios
    dre_sem, *_ = gerar_relatorios(df_completo)
    dre_com, *_ = gerar_relatorios(df_completo, provisao_vinicius=1000.0)
    lucro_sem = dre_sem.loc[dre_sem["Conta"] == "LUCRO BRUTO", "Valor (R$)"].values[0]
    lucro_com = dre_com.loc[dre_com["Conta"] == "LUCRO BRUTO", "Valor (R$)"].values[0]
    assert lucro_com == lucro_sem - 1000.0


# ── Categorias dinâmicas ──────────────────────────────────────────────────────

def test_merge_cats_sem_json():
    """Sem banco disponível, retorna as listas hardcoded."""
    from relatorios import get_cats_receita, CATS_RECEITA
    with patch("relatorios._carregar_cats", return_value={}):
        resultado = get_cats_receita()
    assert resultado == CATS_RECEITA

def test_merge_cats_com_json(tmp_path):
    """Categorias do banco são retornadas corretamente."""
    from relatorios import get_cats_receita
    cats_banco = {"CATS_RECEITA": ["REC | GANHO", "REC | Honorário Avulso"]}
    with patch("relatorios._carregar_cats", return_value=cats_banco):
        resultado = get_cats_receita()
    assert "REC | GANHO" in resultado
    assert resultado.count("REC | Honorário Avulso") == 1

def test_categoria_dinamica_entra_no_dre(df_completo, tmp_path):
    """Categoria adicionada via banco aparece no DRE e entra no total."""
    from relatorios import gerar_relatorios, CATS_RECEITA
    df = df_completo.copy()
    df = pd.concat([df, pd.DataFrame([{
        "Data": "15/06/2026", "Categoria": "REC | GANHO", "Tipo": "Entrada",
        "Valor": 5000.0, "Pago para / Recebido de": "Cliente Z",
        "Centro de custo": "Civil", "Descricao": "Ganho"
    }])], ignore_index=True)
    cats_banco = {"CATS_RECEITA": CATS_RECEITA + ["REC | GANHO"],
                  "CATS_CUSTO_DIRETO": [], "CATS_DESPESA_OP": [],
                  "CATS_IMPOSTO": [], "CATS_RECEITA_FIN": [],
                  "CATS_SOCIETARIO": [], "CATS_EMPRESTIMO": [], "CATS_TRANSITORIO": []}
    with patch("relatorios._carregar_cats", return_value=cats_banco):
        dre, *_ = gerar_relatorios(df)
    total = dre.loc[dre["Conta"] == "RECEITAS OPERACIONAIS", "Valor (R$)"].values[0]
    assert total == 41000.0
    assert any("GANHO" in str(c) for c in dre["Conta"])


# ── gerar_ranking_clientes ────────────────────────────────────────────────────

def test_ranking_ordenado_por_receita(df_completo):
    from relatorios import gerar_ranking_clientes
    ranking = gerar_ranking_clientes(df_completo)
    valores = ranking["RECEITA (R$)"].tolist()
    assert valores == sorted(valores, reverse=True)

def test_ranking_participacao_soma_100(df_completo):
    from relatorios import gerar_ranking_clientes
    ranking = gerar_ranking_clientes(df_completo)
    assert abs(ranking["PARTICIPAÇÃO (%)"].sum() - 100.0) < 0.1

def test_ranking_nao_inclui_saidas(df_completo):
    from relatorios import gerar_ranking_clientes
    ranking = gerar_ranking_clientes(df_completo)
    assert "Parceiro X" not in ranking["CLIENTE"].values
    assert "Cartório" not in ranking["CLIENTE"].values


# ── gerar_centro_custos ───────────────────────────────────────────────────────

def test_centro_custos_tem_linha_total(df_completo):
    from relatorios import gerar_centro_custos
    centros = gerar_centro_custos(df_completo)
    assert "TOTAL" in centros["CENTRO DE CUSTO"].values

def test_centro_custos_resultado_correto(df_completo):
    from relatorios import gerar_centro_custos
    centros = gerar_centro_custos(df_completo)
    total = centros.loc[centros["CENTRO DE CUSTO"] == "TOTAL", "RESULTADO (R$)"].values[0]
    receita_total = centros.loc[centros["CENTRO DE CUSTO"] == "TOTAL", "RECEITA (R$)"].values[0]
    despesa_total = centros.loc[centros["CENTRO DE CUSTO"] == "TOTAL", "DESPESA (R$)"].values[0]
    assert round(total, 2) == round(receita_total + despesa_total, 2)
