import json
import pandas as pd
from pathlib import Path
from funcoes import soma, soma_entradas

# ── Categorias base (hardcoded) ───────────────────────────────────────────────

CATS_RECEITA = [
    "REC | Honorário Avulso",
    "REC | Honorário Contratado",
    "REC | Honorário Partido",
    "REC | Honorário Sucumbencial",
    "REC | Honorário Êxito",
    "REC | Honorário Compensação/liminar",
    "REC | Reembolso cliente",
]

CATS_CUSTO_DIRETO = [
    "CUS | Parceiro Jurídico",
    "CUS | Participação contrato",
    "CUS | Diligencia",
    "CUS | Participação Vinicius Fraga",
    "Despesa do cliente",
]

CATS_DESPESA_OP = [
    "DES | Aluguel",
    "DES | Assinaturas Jurídicas",
    "DES | Bancaria",
    "DES | Certificado digital",
    "DES | Condomínio",
    "DES | Consultoria",
    "DES | Contabilidade",
    "DES | Copa/Cozinha",
    "DES | Cursos/Especializações",
    "DES | Estagiários",
    "DES | Energia",
    "DES | Folha Pagamento",
    "DES | Hospedagem/Site",
    "DES | Internet",
    "DES | Limpeza",
    "DES | Manutenção",
    "DES | Marketing",
    "DES | Material Escritório",
    "DES | Não Classificado",
    "DES | OAB/Anuidade",
    "DES | Pró-Labore",
    "DES | Segurança",
    "DES | Software Jurídico",
    "DES | Telefonia",
    "DES | Token/OAB",
    "DES | Tráfego pago",
    "DES | Uber/Combustível",
    "DES | Despesa Bancária",
    "DES | Bancária",
]

CATS_RESULTADO_FIN = []

CATS_IMPOSTO = [
    "IMP | Simples Nacional",
    "IMP | IPTU",
    "IMP | INSS",
]

CATS_RECEITA_FIN = [
    "REC | Receita Financeira",
    "REC | Venda ativo",
]

CATS_SOCIETARIO = [
    "SOC | Distribuição Lucros",
    "SOC | Aporte Sócio",
]

CATS_EMPRESTIMO = [
    "FIN | Empréstimo Bancário",
    "FIN | Empréstimo bancário",
    "FIN | Pagamento Empréstimo",
    "FIN | Consórcio Principal",
    "FIN | Juros Bancários",
    "FIN | Juros bancários",
]

CATS_TRANSITORIO = [
    "REP | Valores transitórios",
    "REP | Repasse Cliente",
]

# ── Categorias via banco de dados ─────────────────────────────────────────────

CATS_FILE = Path(__file__).parent / "categorias.json"

def _carregar_cats():
    """Carrega todas as categorias do banco. Fallback para hardcoded."""
    try:
        import os
        if os.environ.get("DATABASE_URL"):
            import psycopg2
            conn = psycopg2.connect(os.environ["DATABASE_URL"])
            with conn.cursor() as cur:
                cur.execute("SELECT grupo, nome FROM categorias ORDER BY id")
                rows = cur.fetchall()
            conn.close()
            result = {}
            for grupo, nome in rows:
                result.setdefault(grupo, []).append(nome)
            return result
    except Exception:
        pass
    # Fallback: listas vazias (sem banco disponível)
    return {
        "CATS_RECEITA":      [],
        "CATS_CUSTO_DIRETO": [],
        "CATS_DESPESA_OP":   [],
        "CATS_IMPOSTO":      [],
        "CATS_RECEITA_FIN":  [],
        "CATS_SOCIETARIO":   [],
        "CATS_EMPRESTIMO":   [],
        "CATS_TRANSITORIO":  [],
    }

def get_cats_receita():
    return _carregar_cats().get("CATS_RECEITA", CATS_RECEITA)

def get_cats_custo_direto():
    return _carregar_cats().get("CATS_CUSTO_DIRETO", CATS_CUSTO_DIRETO)

def get_cats_despesa_op():
    return _carregar_cats().get("CATS_DESPESA_OP", CATS_DESPESA_OP)

def get_cats_imposto():
    return _carregar_cats().get("CATS_IMPOSTO", CATS_IMPOSTO)

def get_cats_receita_fin():
    return _carregar_cats().get("CATS_RECEITA_FIN", CATS_RECEITA_FIN)

def get_cats_societario():
    return _carregar_cats().get("CATS_SOCIETARIO", CATS_SOCIETARIO)

def get_cats_emprestimo():
    return _carregar_cats().get("CATS_EMPRESTIMO", CATS_EMPRESTIMO)

def get_cats_transitorio():
    return _carregar_cats().get("CATS_TRANSITORIO", CATS_TRANSITORIO)


def get_todas_categorias_conhecidas():
    cats = _carregar_cats()
    todas = []
    for lista in cats.values():
        todas.extend(lista)
    todas += ["Transferência", "Despesa do cliente", "Saldo inicial"]
    return list(set(todas))

# Categorias com linha própria fixa no DRE — mantidas para layout do relatório
_RECEITA_LINHA_FIXA = {
    "REC | Honorário Avulso",
    "REC | Honorário Contratado",
    "REC | Honorário Partido",
    "REC | Honorário Sucumbencial",
    "REC | Honorário Êxito",
    "REC | Honorário Compensação/liminar",
}

_CUSTO_LINHA_FIXA = {
    "CUS | Parceiro Jurídico",
    "CUS | Participação contrato",
    "CUS | Diligencia",
    "CUS | Participação Vinicius Fraga",
    "Despesa do cliente",
}

_IMPOSTO_LINHA_FIXA = {
    "IMP | Simples Nacional",
    "IMP | IPTU",
    "IMP | INSS",
}


def gerar_relatorios(df, provisao_vinicius=0.0):

    # Carrega listas do banco (ou fallback hardcoded)
    cats_receita      = get_cats_receita()
    cats_custo_direto = get_cats_custo_direto()
    cats_despesa_op   = get_cats_despesa_op()
    cats_imposto      = get_cats_imposto()

    # ── Receitas ──────────────────────────────────────────────────────────────
    # Linhas fixas do DRE (sempre aparecem com label próprio)
    rec_avulso     = soma_entradas(df, ["REC | Honorário Avulso"])
    rec_contratado = soma_entradas(df, ["REC | Honorário Contratado"])
    rec_partido    = soma_entradas(df, ["REC | Honorário Partido"])
    rec_sucumb     = soma_entradas(df, ["REC | Honorário Sucumbencial"])
    rec_exito      = soma_entradas(df, ["REC | Honorário Êxito"])
    rec_comp       = soma_entradas(df, ["REC | Honorário Compensação/liminar"])

    # Categorias extras (não têm linha fixa no DRE)
    rec_extras = {
        cat: soma_entradas(df, [cat])
        for cat in cats_receita
        if cat not in _RECEITA_LINHA_FIXA
    }

    total_receita = (
        rec_avulso + rec_contratado + rec_partido +
        rec_sucumb + rec_exito + rec_comp +
        sum(rec_extras.values())
    )

    # ── Custos diretos ────────────────────────────────────────────────────────
    cus_parceiro = soma(df, ["CUS | Parceiro Jurídico"])
    cus_dilig    = soma(df, ["CUS | Diligencia"])
    cus_vini     = soma(df, ["CUS | Participação Vinicius Fraga"])
    desp_cliente = soma(df, ["Despesa do cliente"])

    part_df        = df[df["Categoria"] == "CUS | Participação contrato"].copy()
    cus_part_total = part_df["Valor"].sum()

    cus_extras = {
        cat: soma(df, [cat])
        for cat in cats_custo_direto
        if cat not in _CUSTO_LINHA_FIXA
    }

    provisao     = -abs(provisao_vinicius) if provisao_vinicius else 0.0
    total_custos = (
        cus_parceiro + cus_part_total + cus_dilig +
        cus_vini + desp_cliente + provisao +
        sum(cus_extras.values())
    )

    lucro_bruto = total_receita + total_custos

    # ── Despesas operacionais ─────────────────────────────────────────────────
    des_values        = {cat: soma(df, [cat]) for cat in cats_despesa_op}
    total_despesas_op = sum(des_values.values())
    resultado_operacional = lucro_bruto + total_despesas_op

    # ── Impostos ──────────────────────────────────────────────────────────────
    imp_simples = soma(df, ["IMP | Simples Nacional"])
    imp_iptu    = soma(df, ["IMP | IPTU"])
    imp_inss    = soma(df, ["IMP | INSS"])

    imp_extras = {
        cat: soma(df, [cat])
        for cat in cats_imposto
        if cat not in _IMPOSTO_LINHA_FIXA
    }

    total_imp     = imp_simples + imp_iptu + imp_inss + sum(imp_extras.values())
    lucro_liquido = resultado_operacional + total_imp

    # ── Monta DRE ─────────────────────────────────────────────────────────────
    contas  = ["RECEITAS OPERACIONAIS"]
    valores = [total_receita]
    for label, val in [
        ("Honorário Avulso",              rec_avulso),
        ("Honorário Contratado",          rec_contratado),
        ("Honorário Partido",             rec_partido),
        ("Honorário Sucumbencial",        rec_sucumb),
        ("Honorário Êxito",               rec_exito),
        ("Honorário Compensação/Liminar", rec_comp),
    ]:
        contas.append(f"  {label}")
        valores.append(val)
    # Receitas dinâmicas extras
    for cat, val in rec_extras.items():
        contas.append(f"  {cat.replace('REC | ', '')}")
        valores.append(val)

    contas  += ["CUSTOS DIRETOS"]
    valores += [total_custos]
    contas.append("  Parceiro Jurídico")
    valores.append(cus_parceiro)
    # Participação em Contrato — apenas total (sem detalhamento por beneficiário)
    contas.append("  Participação em Contrato")
    valores.append(cus_part_total)
    for label, val in [
        ("Diligência",                  cus_dilig),
        ("Participação Vinicius Fraga", cus_vini),
        ("Despesa do Cliente",          desp_cliente),
    ]:
        contas.append(f"  {label}")
        valores.append(val)
    # Custos diretos dinâmicos extras
    for cat, val in cus_extras.items():
        contas.append(f"  {cat.replace('CUS | ', '')}")
        valores.append(val)
    if provisao_vinicius:
        contas.append("  Provisão Repasse Ex-Sócio")
        valores.append(provisao)

    contas  += ["LUCRO BRUTO"]
    valores += [lucro_bruto]

    contas  += ["DESPESAS OPERACIONAIS"]
    valores += [total_despesas_op]
    for cat, val in des_values.items():
        contas.append(f"  {cat.replace('DES | ', '')}")
        valores.append(val)

    contas  += ["RESULTADO OPERACIONAL"]
    valores += [resultado_operacional]

    contas  += ["IMPOSTOS"]
    valores += [total_imp]
    for label, val in [
        ("Simples Nacional", imp_simples),
        ("IPTU",             imp_iptu),
        ("INSS",             imp_inss),
    ]:
        contas.append(f"  {label}")
        valores.append(val)
    # Impostos dinâmicos extras
    for cat, val in imp_extras.items():
        contas.append(f"  {cat.replace('IMP | ', '')}")
        valores.append(val)

    contas  += ["LUCRO LÍQUIDO"]
    valores += [lucro_liquido]

    dre_operacional = pd.DataFrame({"Conta": contas, "Valor (R$)": [round(v, 2) for v in valores]})

    # ── Tabelas laterais ──────────────────────────────────────────────────────

    # Receita Financeira — categorias fixas + dinâmicas
    cats_receita_fin = get_cats_receita_fin()
    _rec_fin_fixas = {
        "REC | Receita Financeira": "Receita Financeira",
        "REC | Venda ativo":        "Venda de Ativo",
    }
    rec_fin_rows = {label: soma_entradas(df, [cat]) for cat, label in _rec_fin_fixas.items()}
    for cat in cats_receita_fin:
        if cat not in _rec_fin_fixas:
            rec_fin_rows[cat.replace("REC | ", "")] = soma_entradas(df, [cat])
    rec_fin_total = sum(rec_fin_rows.values())
    receita_financeira = pd.DataFrame({
        "Descrição": list(rec_fin_rows.keys()) + ["TOTAL"],
        "Valor (R$)": list(rec_fin_rows.values()) + [rec_fin_total],
    })

    # Societário — categorias fixas + dinâmicas
    cats_societario = get_cats_societario()
    _soc_fixas = {
        "SOC | Distribuição Lucros": "Distribuição de Lucros",
        "SOC | Aporte Sócio":        "Aporte de Sócio",
    }
    soc_rows = {label: df[df["Categoria"] == cat]["Valor"].sum() for cat, label in _soc_fixas.items()}
    for cat in cats_societario:
        if cat not in _soc_fixas:
            soc_rows[cat.replace("SOC | ", "")] = df[df["Categoria"] == cat]["Valor"].sum()
    soc_total = sum(soc_rows.values())
    societario = pd.DataFrame({
        "Descrição": list(soc_rows.keys()) + ["SALDO SOCIETÁRIO"],
        "Valor (R$)": list(soc_rows.values()) + [soc_total],
    })

    # Empréstimos — categorias fixas + dinâmicas
    cats_emprestimo = get_cats_emprestimo()
    _emp_fixas = {
        "Empréstimo Bancário": ["FIN | Empréstimo Bancário", "FIN | Empréstimo bancário", "FIN | Pagamento Empréstimo"],
        "Consórcio Principal": ["FIN | Consórcio Principal"],
        "Juros Bancários":     ["FIN | Juros Bancários", "FIN | Juros bancários"],
    }
    _emp_fixas_cats = {cat for cats in _emp_fixas.values() for cat in cats}
    emp_rows = {label: df[df["Categoria"].isin(cats)]["Valor"].sum() for label, cats in _emp_fixas.items()}
    for cat in cats_emprestimo:
        if cat not in _emp_fixas_cats:
            emp_rows[cat.replace("FIN | ", "")] = df[df["Categoria"] == cat]["Valor"].sum()
    emp_total = sum(emp_rows.values())
    emprestimos = pd.DataFrame({
        "Descrição": list(emp_rows.keys()) + ["TOTAL"],
        "Valor (R$)": list(emp_rows.values()) + [emp_total],
    })

    # Transitório — categorias fixas + dinâmicas
    cats_transitorio = get_cats_transitorio()
    _trans_fixas = {"REP | Repasse Cliente", "REP | Valores transitórios"}
    rep_cliente_val = df[df["Categoria"] == "REP | Repasse Cliente"]["Valor"].sum()
    val_tr_e = df[(df["Categoria"] == "REP | Valores transitórios") & (df["Tipo"] == "Entrada")]["Valor"].sum()
    val_tr_s = df[(df["Categoria"] == "REP | Valores transitórios") & (df["Tipo"] == "Saída")]["Valor"].sum()
    trans_rows = {
        "Repasse Cliente":      rep_cliente_val,
        "Entradas Transitórias": val_tr_e,
        "Saídas Transitórias":   val_tr_s,
    }
    for cat in cats_transitorio:
        if cat not in _trans_fixas:
            trans_rows[cat.replace("REP | ", "")] = df[df["Categoria"] == cat]["Valor"].sum()
    trans_total = sum(trans_rows.values())
    transitorio = pd.DataFrame({
        "Descrição": list(trans_rows.keys()) + ["SALDO TRANSITÓRIO"],
        "Valor (R$)": list(trans_rows.values()) + [trans_total],
    })

    # ── Aba Receitas ──────────────────────────────────────────────────────────
    # Lista base + dinâmicas extras (sem duplicar as fixas já mapeadas)
    CATS_RECEITA_ORDEM = [
        ("REC | Honorário Avulso",             "Honorário Avulso"),
        ("REC | Honorário Contratado",          "Honorário Contratado"),
        ("REC | Honorário Partido",             "Honorário Partido"),
        ("REC | Honorário Sucumbencial",        "Honorário Sucumbencial"),
        ("REC | Honorário Êxito",               "Honorário Êxito"),
        ("REC | Honorário Compensação/liminar", "Compensação/Liminar"),
        ("REC | Reembolso cliente",             "Reembolso Cliente"),
        ("REC | Receita Financeira",            "Receita Financeira"),
        ("REC | Venda ativo",                   "Venda de Ativo"),
    ]
    _cats_receita_ordem_keys = {c for c, _ in CATS_RECEITA_ORDEM}
    for cat in cats_receita:
        if cat not in _cats_receita_ordem_keys:
            CATS_RECEITA_ORDEM.append((cat, cat.replace("REC | ", "")))

    blocos = []
    for cat, label in CATS_RECEITA_ORDEM:
        bloco = df[
            (df["Tipo"] == "Entrada") & (df["Categoria"] == cat)
        ][["Data", "Pago para / Recebido de", "Descricao", "Categoria", "Valor"]].copy()
        if bloco.empty:
            continue
        total = pd.DataFrame([{
            "Data": "", "Pago para / Recebido de": "",
            "Descricao": f"TOTAL {label.upper()}",
            "Categoria": cat, "Valor": bloco["Valor"].sum()
        }])
        blocos.append(bloco)
        blocos.append(total)
    conciliacao = pd.concat(blocos, ignore_index=True) if blocos else pd.DataFrame(
        columns=["Data", "Pago para / Recebido de", "Descricao", "Categoria", "Valor"]
    )
    conciliacao = conciliacao.rename(columns={
        "Data": "DATA", "Pago para / Recebido de": "CLIENTE",
        "Descricao": "DESCRIÇÃO", "Categoria": "CLASSIFICAÇÃO", "Valor": "VALORES"
    })

    # ── Aba Despesas ──────────────────────────────────────────────────────────
    CATS_DESPESA_DETALHE = cats_custo_direto + cats_despesa_op + cats_imposto
    CATS_LABELS = {}
    for c in cats_custo_direto:
        CATS_LABELS[c] = c.replace("CUS | ", "")
    for c in cats_despesa_op:
        CATS_LABELS[c] = c.replace("DES | ", "")
    for c in cats_imposto:
        CATS_LABELS[c] = c.replace("IMP | ", "")
    CATS_LABELS["Despesa do cliente"] = "Despesa do Cliente"

    blocos_desp = []
    for cat in CATS_DESPESA_DETALHE:
        bloco = df[
            (df["Tipo"] == "Saída") & (df["Categoria"] == cat)
        ][["Data", "Pago para / Recebido de", "Descricao", "Categoria", "Valor"]].copy()
        if bloco.empty:
            continue
        label = CATS_LABELS.get(cat, cat)
        total = pd.DataFrame([{
            "Data": "", "Pago para / Recebido de": "",
            "Descricao": f"TOTAL {label.upper()}",
            "Categoria": cat, "Valor": bloco["Valor"].sum()
        }])
        blocos_desp.append(bloco)
        blocos_desp.append(total)

    despesas_detalhadas = pd.concat(blocos_desp, ignore_index=True) if blocos_desp else pd.DataFrame(
        columns=["Data", "Pago para / Recebido de", "Descricao", "Categoria", "Valor"]
    )
    despesas_detalhadas = despesas_detalhadas.rename(columns={
        "Data": "DATA", "Pago para / Recebido de": "PAGO PARA",
        "Descricao": "DESCRIÇÃO", "Categoria": "CLASSIFICAÇÃO", "Valor": "VALORES"
    })

    return (
        dre_operacional,
        receita_financeira,
        societario,
        emprestimos,
        transitorio,
        conciliacao,
        despesas_detalhadas,
    )


def gerar_ranking_clientes(df):
    cats_receita = get_cats_receita()
    ranking = (
        df[
            (df["Tipo"] == "Entrada") &
            (df["Categoria"].isin(cats_receita))
        ]
        .groupby("Pago para / Recebido de")["Valor"]
        .sum()
        .reset_index()
        .rename(columns={"Pago para / Recebido de": "CLIENTE", "Valor": "RECEITA (R$)"})
        .sort_values("RECEITA (R$)", ascending=False)
        .reset_index(drop=True)
    )
    ranking.index += 1
    ranking.index.name = "POS."
    total = ranking["RECEITA (R$)"].sum()
    ranking["PARTICIPAÇÃO (%)"] = (ranking["RECEITA (R$)"] / total * 100).round(1)
    return ranking


def gerar_centro_custos(df):
    cats_receita    = get_cats_receita()
    cats_despesa_op = get_cats_despesa_op()
    cats_imposto    = get_cats_imposto()
    cats_custo      = get_cats_custo_direto()

    receita = (
        df[(df["Tipo"] == "Entrada") & (df["Categoria"].isin(cats_receita))]
        .groupby("Centro de custo")["Valor"].sum()
        .rename("RECEITA (R$)")
    )
    todas_saidas = cats_custo + cats_despesa_op + cats_imposto
    despesa = (
        df[(df["Tipo"] == "Saída") & (df["Categoria"].isin(todas_saidas))]
        .groupby("Centro de custo")["Valor"].sum()
        .rename("DESPESA (R$)")
    )
    centro = pd.concat([receita, despesa], axis=1).fillna(0).reset_index()
    centro = centro.rename(columns={"Centro de custo": "CENTRO DE CUSTO"})
    centro["RESULTADO (R$)"] = centro["RECEITA (R$)"] + centro["DESPESA (R$)"]
    centro = centro.sort_values("RECEITA (R$)", ascending=False).reset_index(drop=True)
    total = pd.DataFrame([{
        "CENTRO DE CUSTO": "TOTAL",
        "RECEITA (R$)":    centro["RECEITA (R$)"].sum(),
        "DESPESA (R$)":    centro["DESPESA (R$)"].sum(),
        "RESULTADO (R$)":  centro["RESULTADO (R$)"].sum(),
    }])
    return pd.concat([centro, total], ignore_index=True)
