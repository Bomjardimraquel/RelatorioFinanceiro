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

TODAS_CATEGORIAS_CONHECIDAS = (
    CATS_RECEITA + CATS_CUSTO_DIRETO + CATS_DESPESA_OP +
    CATS_RESULTADO_FIN + CATS_IMPOSTO + CATS_RECEITA_FIN +
    CATS_SOCIETARIO + CATS_EMPRESTIMO + CATS_TRANSITORIO +
    ["Transferência", "Despesa do cliente", "Saldo inicial"]
)


def gerar_relatorios(df, provisao_vinicius=0.0):

    rec_avulso     = soma_entradas(df, ["REC | Honorário Avulso"])
    rec_contratado = soma_entradas(df, ["REC | Honorário Contratado"])
    rec_partido    = soma_entradas(df, ["REC | Honorário Partido"])
    rec_sucumb     = soma_entradas(df, ["REC | Honorário Sucumbencial"])
    rec_exito      = soma_entradas(df, ["REC | Honorário Êxito"])
    rec_comp       = soma_entradas(df, ["REC | Honorário Compensação/liminar"])
    total_receita  = rec_avulso + rec_contratado + rec_partido + rec_sucumb + rec_exito + rec_comp

    cus_parceiro = soma(df, ["CUS | Parceiro Jurídico"])
    cus_part     = soma(df, ["CUS | Participação contrato"])
    cus_dilig    = soma(df, ["CUS | Diligencia"])
    cus_vini     = soma(df, ["CUS | Participação Vinicius Fraga"])
    desp_cliente = soma(df, ["Despesa do cliente"])
    total_custos = cus_parceiro + cus_part + cus_dilig + cus_vini + desp_cliente

    lucro_bruto = total_receita + total_custos

    des_values = {cat: soma(df, [cat]) for cat in CATS_DESPESA_OP}
    provisao = -abs(provisao_vinicius) if provisao_vinicius else 0.0
    total_despesas_op = sum(des_values.values()) + provisao

    resultado_operacional = lucro_bruto + total_despesas_op

    imp_simples = soma(df, ["IMP | Simples Nacional"])
    imp_iptu    = soma(df, ["IMP | IPTU"])
    imp_inss    = soma(df, ["IMP | INSS"])
    total_imp   = imp_simples + imp_iptu + imp_inss

    lucro_liquido = resultado_operacional + total_imp

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
        ("Parceiro Jurídico",           cus_parceiro),
        ("Participação em Contrato",    cus_part),
        ("Diligência",                  cus_dilig),
        ("Participação Vinicius Fraga", cus_vini),
        ("Despesa do Cliente",          desp_cliente),
    ]:
        contas.append(f"  {label}")
        valores.append(val)

    contas  += ["LUCRO BRUTO"]
    valores += [lucro_bruto]

    contas  += ["DESPESAS OPERACIONAIS"]
    valores += [total_despesas_op]
    for cat, val in des_values.items():
        contas.append(f"  {cat.replace('DES | ', '')}")
        valores.append(val)
    if provisao_vinicius:
        contas.append("  Provisão Repasse Ex-Sócio")
        valores.append(provisao)

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

    contas  += ["LUCRO LÍQUIDO"]
    valores += [lucro_liquido]

    dre_operacional = pd.DataFrame({"Conta": contas, "Valor (R$)": valores})

    rec_fin_val = soma_entradas(df, ["REC | Receita Financeira"])
    venda_ativo = soma_entradas(df, ["REC | Venda ativo"])
    receita_financeira = pd.DataFrame({
        "Descrição": ["Receita Financeira", "Venda de Ativo", "TOTAL"],
        "Valor (R$)": [rec_fin_val, venda_ativo, rec_fin_val + venda_ativo]
    })

    soc_dist  = df[df["Categoria"] == "SOC | Distribuição Lucros"]["Valor"].sum()
    soc_aport = df[df["Categoria"] == "SOC | Aporte Sócio"]["Valor"].sum()
    societario = pd.DataFrame({
        "Descrição": ["Distribuição de Lucros", "Aporte de Sócio", "SALDO SOCIETÁRIO"],
        "Valor (R$)": [soc_dist, soc_aport, soc_dist + soc_aport]
    })

    emp_pag   = df[df["Categoria"].isin(["FIN | Empréstimo Bancário", "FIN | Empréstimo bancário", "FIN | Pagamento Empréstimo"])]["Valor"].sum()
    cons_prin = df[df["Categoria"] == "FIN | Consórcio Principal"]["Valor"].sum()
    juros     = df[df["Categoria"].isin(["FIN | Juros Bancários", "FIN | Juros bancários"])]["Valor"].sum()
    emprestimos = pd.DataFrame({
        "Descrição": ["Empréstimo Bancário", "Consórcio Principal", "Juros Bancários", "TOTAL"],
        "Valor (R$)": [emp_pag, cons_prin, juros, emp_pag + cons_prin + juros]
    })

    rep_cliente_val = df[df["Categoria"] == "REP | Repasse Cliente"]["Valor"].sum()
    val_tr_e = df[(df["Categoria"] == "REP | Valores transitórios") & (df["Tipo"] == "Entrada")]["Valor"].sum()
    val_tr_s = df[(df["Categoria"] == "REP | Valores transitórios") & (df["Tipo"] == "Saída")]["Valor"].sum()
    transitorio = pd.DataFrame({
        "Descrição": ["Repasse Cliente", "Entradas Transitórias", "Saídas Transitórias", "SALDO TRANSITÓRIO"],
        "Valor (R$)": [rep_cliente_val, val_tr_e, val_tr_s, rep_cliente_val + val_tr_e + val_tr_s]
    })

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

    CATS_DESPESA_DETALHE = CATS_CUSTO_DIRETO + CATS_DESPESA_OP + CATS_IMPOSTO
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
        df[(df["Tipo"] == "Saída") & (df["Categoria"].isin(CATS_DESPESA_OP + CATS_IMPOSTO))]
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
