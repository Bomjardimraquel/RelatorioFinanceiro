import pandas as pd
from funcoes import soma, soma_entradas

# ── Categorias do Astrea (prefixos novos) ────────────────────────────────────

CATS_RECEITA = [
    "REC | Honorário Avulso",
    "REC | Honorário Contratado",
    "REC | Honorário Partido",
    "REC | Honorário Sucumbencial",
    "REC | Honorário Êxito",
    "REC | Honorário Compensação/liminar",
]

CATS_CUSTO_DIRETO = [
    "CUS | Parceiro Jurídico",
    "CUS | Participação contrato",
    "REP | Repasse Cliente",
    "Despesa do cliente",
]

CATS_DESPESA_OP = [
    "DES | Aluguel",
    "DES | Assinaturas Jurídicas",
    "DES | Condomínio",
    "DES | Contabilidade",
    "DES | Copa/Cozinha",
    "DES | Cursos/Especializações",
    "DES | Estagiários",
    "DES | Energia",
    "DES | Folha Pagamento",
    "DES | Hospedagem/Site",
    "DES | Limpeza",
    "DES | Marketing",
    "DES | OAB/Anuidade",
    "DES | Pró-Labore",
    "DES | Software Jurídico",
    "DES | Telefonia",
    "DES | Uber/Combustível",
]

CATS_RESULTADO_FIN = [
    "DES | Despesa Bancária",
]

CATS_IMPOSTO = [
    "IMP | Simples Nacional",
    "IMP | IPTU",
]

CATS_RECEITA_FIN = [
    "REC | Receita Financeira",
]

CATS_SOCIETARIO = [
    "SOC | Distribuição Lucros",
    "SOC | Aporte Sócio",
]

CATS_EMPRESTIMO = [
    "FIN | Pagamento Empréstimo",
    "FIN | Consórcio Principal",
]

CATS_TRANSITORIO = [
    "REP | Valores transitórios",
]

# Todas as categorias conhecidas (para aviso de desconhecidas no app.py)
TODAS_CATEGORIAS_CONHECIDAS = (
    CATS_RECEITA + CATS_CUSTO_DIRETO + CATS_DESPESA_OP +
    CATS_RESULTADO_FIN + CATS_IMPOSTO + CATS_RECEITA_FIN +
    CATS_SOCIETARIO + CATS_EMPRESTIMO + CATS_TRANSITORIO +
    ["Transferência", "Despesa do cliente"]
)


def gerar_relatorios(df, provisao_vinicius=0.0):

    # Reclassifica fatura de cartão (Transferência → DES | Uber/Combustível ou similar)
    mask_cartao = (
        (df["Categoria"] == "Transferência") &
        (df["Tipo"] == "Saída") &
        (df["Descricao"].str.contains("cartão|cartao|fatura", case=False, na=False))
    )
    df = df.copy()
    df.loc[mask_cartao, "Categoria"] = "DES | Uber/Combustível"

    # ── RECEITAS OPERACIONAIS ────────────────────────────────────────────────
    rec_avulso     = soma_entradas(df, ["REC | Honorário Avulso"])
    rec_contratado = soma_entradas(df, ["REC | Honorário Contratado"])
    rec_partido    = soma_entradas(df, ["REC | Honorário Partido"])
    rec_sucumb     = soma_entradas(df, ["REC | Honorário Sucumbencial"])
    rec_exito      = soma_entradas(df, ["REC | Honorário Êxito"])
    rec_comp       = soma_entradas(df, ["REC | Honorário Compensação/liminar"])
    total_receita  = rec_avulso + rec_contratado + rec_partido + rec_sucumb + rec_exito + rec_comp

    # ── CUSTOS DIRETOS ───────────────────────────────────────────────────────
    cus_parceiro  = soma(df, ["CUS | Parceiro Jurídico"])
    cus_part      = soma(df, ["CUS | Participação contrato"])
    rep_cliente   = soma(df, ["REP | Repasse Cliente"])
    desp_cliente  = soma(df, ["Despesa do cliente"])
    total_custos  = cus_parceiro + cus_part + rep_cliente + desp_cliente

    lucro_bruto   = total_receita + total_custos

    # ── DESPESAS OPERACIONAIS ────────────────────────────────────────────────
    des_values = {cat: soma(df, [cat]) for cat in CATS_DESPESA_OP}
    # adiciona provisão se informada
    provisao = -abs(provisao_vinicius) if provisao_vinicius else 0.0
    total_despesas_op = sum(des_values.values()) + provisao

    resultado_operacional = lucro_bruto + total_despesas_op

    # ── RESULTADO FINANCEIRO (só despesa bancária) ───────────────────────────
    desp_bancaria   = soma(df, ["DES | Despesa Bancária"])
    total_fin       = desp_bancaria

    # ── IMPOSTOS ────────────────────────────────────────────────────────────
    imp_simples  = soma(df, ["IMP | Simples Nacional"])
    imp_iptu     = soma(df, ["IMP | IPTU"])
    total_imp    = imp_simples + imp_iptu

    lucro_liquido = resultado_operacional + total_fin + total_imp

    # ── Monta DataFrame do DRE ───────────────────────────────────────────────
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

    contas  += ["CUSTOS DIRETOS"]
    valores += [total_custos]
    for label, val in [
        ("Parceiro Jurídico",       cus_parceiro),
        ("Participação em Contrato", cus_part),
        ("Repasse Cliente",         rep_cliente),
        ("Despesa do Cliente",      desp_cliente),
    ]:
        contas.append(f"  {label}")
        valores.append(val)

    contas  += ["LUCRO BRUTO"]
    valores += [lucro_bruto]

    contas  += ["DESPESAS OPERACIONAIS"]
    valores += [total_despesas_op]
    for cat, val in des_values.items():
        label = cat.replace("DES | ", "")
        contas.append(f"  {label}")
        valores.append(val)
    if provisao_vinicius:
        contas.append("  Provisão Repasse Ex-Sócio")
        valores.append(provisao)

    contas  += ["RESULTADO OPERACIONAL"]
    valores += [resultado_operacional]

    contas  += ["RESULTADO FINANCEIRO"]
    valores += [total_fin]
    contas.append("  Despesa Bancária")
    valores.append(desp_bancaria)

    contas  += ["IMPOSTOS"]
    valores += [total_imp]
    for label, val in [("Simples Nacional", imp_simples), ("IPTU", imp_iptu)]:
        contas.append(f"  {label}")
        valores.append(val)

    contas  += ["LUCRO LÍQUIDO"]
    valores += [lucro_liquido]

    dre_operacional = pd.DataFrame({"Conta": contas, "Valor (R$)": valores})

    # Tabelas separadas ─────────────────────────────────────

    # Receita financeira
    rec_fin = soma_entradas(df, ["REC | Receita Financeira"])
    receita_financeira = pd.DataFrame({
        "Descrição": ["Receita Financeira", "TOTAL"],
        "Valor (R$)": [rec_fin, rec_fin]
    })

    # Societário
    soc_dist  = df[df["Categoria"] == "SOC | Distribuição Lucros"]["Valor"].sum()
    soc_aport = df[df["Categoria"] == "SOC | Aporte Sócio"]["Valor"].sum()
    societario = pd.DataFrame({
        "Descrição": ["Distribuição de Lucros", "Aporte de Sócio", "SALDO SOCIETÁRIO"],
        "Valor (R$)": [soc_dist, soc_aport, soc_dist + soc_aport]
    })

    # Empréstimos
    emp_pag   = df[df["Categoria"] == "FIN | Pagamento Empréstimo"]["Valor"].sum()
    cons_prin = df[df["Categoria"] == "FIN | Consórcio Principal"]["Valor"].sum()
    emprestimos = pd.DataFrame({
        "Descrição": ["Pagamento de Empréstimo", "Consórcio Principal", "TOTAL"],
        "Valor (R$)": [emp_pag, cons_prin, emp_pag + cons_prin]
    })

    # Valores transitórios
    val_tr_e = df[(df["Categoria"] == "REP | Valores transitórios") & (df["Tipo"] == "Entrada")]["Valor"].sum()
    val_tr_s = df[(df["Categoria"] == "REP | Valores transitórios") & (df["Tipo"] == "Saída")]["Valor"].sum()
    transitorio = pd.DataFrame({
        "Descrição": ["Entradas Transitórias", "Saídas Transitórias", "SALDO TRANSITÓRIO"],
        "Valor (R$)": [val_tr_e, val_tr_s, val_tr_e + val_tr_s]
    })

    # Aba Receitas (listagem detalhada) ────────────────────────────────────
    CATS_RECEITA_ORDEM = [
        ("REC | Honorário Avulso",              "Honorário Avulso"),
        ("REC | Honorário Contratado",           "Honorário Contratado"),
        ("REC | Honorário Partido",              "Honorário Partido"),
        ("REC | Honorário Sucumbencial",         "Honorário Sucumbencial"),
        ("REC | Honorário Êxito",                "Honorário Êxito"),
        ("REC | Honorário Compensação/liminar",  "Compensação/Liminar"),
        ("REC | Receita Financeira",             "Receita Financeira"),
    ]

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

    # ── Aba Despesas (listagem detalhada) ────────────────────────────────────
    CATS_DESPESA_DETALHE = CATS_CUSTO_DIRETO + CATS_DESPESA_OP + CATS_RESULTADO_FIN + CATS_IMPOSTO
    despesas = df[
        (df["Tipo"] == "Saída") & (df["Categoria"].isin(CATS_DESPESA_DETALHE))
    ][["Data", "Pago para / Recebido de", "Descricao", "Categoria", "Valor"]].copy()

    totais = despesas.groupby("Categoria")["Valor"].sum().reset_index()
    totais["Data"] = ""
    totais["Pago para / Recebido de"] = ""
    totais["Descricao"] = "TOTAL " + totais["Categoria"].str.replace(r"^[A-Z]{2,3} \| ", "", regex=True)
    despesas_detalhadas = pd.concat([despesas, totais], ignore_index=True)
    despesas_detalhadas = despesas_detalhadas.rename(columns={
        "Data": "DATA", "Pago para / Recebido de": "PAGO PARA",
        "Descricao": "DESCRIÇÃO", "Categoria": "CLASSIFICAÇÃO", "Valor": "VALORES"
    })

    # ── Bancos (mantido) ─────────────────────────────────────────────────────
    bancos = df.groupby(["Conta Financeira", "Tipo"])["Valor"].sum().reset_index()
    bancos_pivot = bancos.pivot_table(
        index="Conta Financeira", columns="Tipo",
        values="Valor", aggfunc="sum", fill_value=0
    ).reset_index()
    bancos_pivot["Saldo do Mês (R$)"] = bancos_pivot.get("Entrada", 0) + bancos_pivot.get("Saída", 0)
    bancos_pivot = bancos_pivot.rename(columns={
        "Conta Financeira": "BANCO",
        "Entrada": "ENTRADAS (R$)",
        "Saída": "SAÍDAS (R$)"
    })
    saldo_ini = (
        df[df["Categoria"] == "Saldo inicial"]
        .groupby("Conta Financeira")["Valor"].sum()
        .reset_index()
        .rename(columns={"Conta Financeira": "BANCO", "Valor": "Saldo Inicial (R$)"})
    )
    bancos_pivot = bancos_pivot.merge(saldo_ini, on="BANCO", how="left")
    bancos_pivot["Saldo Inicial (R$)"] = bancos_pivot["Saldo Inicial (R$)"].fillna(0)
    bancos_pivot["Saldo Final (R$)"]   = bancos_pivot["Saldo Inicial (R$)"] + bancos_pivot["Saldo do Mês (R$)"]
    colunas_banco = ["BANCO", "Saldo Inicial (R$)", "ENTRADAS (R$)", "SAÍDAS (R$)", "Saldo do Mês (R$)", "Saldo Final (R$)"]
    bancos_pivot  = bancos_pivot[[c for c in colunas_banco if c in bancos_pivot.columns]]

    return (
        dre_operacional,
        receita_financeira,
        societario,
        emprestimos,
        transitorio,
        conciliacao,
        despesas_detalhadas,
        bancos_pivot,
    )


def gerar_ranking_clientes(df):
    ranking = (
        df[
            (df["Tipo"] == "Entrada") &
            (df["Categoria"].isin(CATS_RECEITA))
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
    receita = (
        df[(df["Tipo"] == "Entrada") & (df["Categoria"].isin(CATS_RECEITA))]
        .groupby("Centro de custo")["Valor"].sum()
        .rename("RECEITA (R$)")
    )
    despesa = (
        df[(df["Tipo"] == "Saída") & (df["Categoria"].isin(CATS_DESPESA_OP + CATS_RESULTADO_FIN + CATS_IMPOSTO))]
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
