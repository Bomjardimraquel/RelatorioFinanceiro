import pandas as pd
from funcoes import soma, soma_entradas

CATEGORIAS_DESPESA = [
    "Despesa do cliente", "Despesa Fixa", "Despesa Variável", "Despesa bancária",
    "Repasse", "Participação em contrato", "Folha de pagamento", "Impostos",
]

KEYWORDS_INVESTIMENTO = ["resultado de investimento", "resutado de investimento", "rendimento"]

def eh_investimento(descricao):
    if not descricao:
        return False
    return any(kw in str(descricao).lower() for kw in KEYWORDS_INVESTIMENTO)

def gerar_relatorios(df, provisao_vinicius=0.0):

    mask_invest     = (df["Categoria"] == "Diversos") & (df["Descricao"].apply(eh_investimento))
    df_investimento = df[mask_invest].copy()
    df_receita      = df[~mask_invest].copy()

    mask_dist  = df_receita["Categoria"] == "Distribuição de lucros"
    df_dist    = df_receita[mask_dist].copy()
    df_receita = df_receita[~mask_dist].copy()

    mask_cartao = (
        (df_receita["Categoria"] == "Transferência") &
        (df_receita["Tipo"] == "Saída") &
        (df_receita["Descricao"].str.contains("cartão|cartao|fatura", case=False, na=False))
    )
    df_cartao              = df_receita[mask_cartao].copy()
    df_cartao["Categoria"] = "Despesa Variável"
    df_receita             = pd.concat([df_receita[~mask_cartao], df_cartao], ignore_index=True)

    honorarios     = soma_entradas(df_receita, ["Honorários"])
    exito          = soma_entradas(df_receita, ["Exito"])
    contratado     = soma_entradas(df_receita, ["Contratado", "Partido"])
    sucumbenciais  = soma_entradas(df_receita, ["Sucumbencial"])
    compensacoes   = soma_entradas(df_receita, ["Compensação/liminar"])
    diversos_rec   = soma_entradas(df_receita, ["Diversos"])
    receita_bruta  = honorarios + exito + contratado + sucumbenciais + compensacoes + diversos_rec

    impostos           = soma(df_receita, ["Impostos"])
    folha              = soma(df_receita, ["Folha de pagamento"])
    desp_bancaria      = soma(df_receita, ["Despesa bancária"])
    despesas_fixas     = soma(df_receita, ["Despesa Fixa"])
    despesas_variaveis = soma(df_receita, ["Despesa Variável"])
    repasse            = soma(df_receita, ["Repasse"])
    participacao       = soma(df_receita, ["Participação em contrato"])
    desp_cliente       = soma(df_receita, ["Despesa do cliente"])
    repasse_clientes   = repasse + participacao
    provisao           = -abs(provisao_vinicius) if provisao_vinicius else 0.0

    receita_liquida       = receita_bruta + impostos
    lucro_bruto           = receita_liquida + folha
    resultado_operacional = lucro_bruto + desp_bancaria + desp_cliente + despesas_fixas + despesas_variaveis + repasse_clientes + provisao

    contas  = [
        "Receita Bruta", "Honorários", "Êxito", "Contratado/Partido",
        "Sucumbenciais", "Compensações", "Diversos",
        "(-) Impostos", "Receita Líquida",
        "(-) Folha de Pagamento",
        "Lucro Bruto", "(-) Despesa Bancária", "(-) Despesa do cliente", "(-) Despesas Fixas", "(-) Despesas Variáveis",
        "(-) Participação em Contratos", "(-) Repasse",
    ]
    valores = [
        receita_bruta, honorarios, exito, contratado,
        sucumbenciais, compensacoes, diversos_rec,
        impostos, receita_liquida,
        folha,
        lucro_bruto, desp_bancaria, desp_cliente, despesas_fixas, despesas_variaveis,
        participacao, repasse,
    ]
    if provisao_vinicius:
        contas.append("(-) Provisão Repasse Ex-Sócio")
        valores.append(provisao)
    contas.append("Resultado Operacional")
    valores.append(resultado_operacional)

    dre_operacional = pd.DataFrame({"Conta": contas, "Valor (R$)": valores})

    total_dist   = df_dist["Valor"].sum()
    total_invest = df_investimento[df_investimento["Tipo"] == "Entrada"]["Valor"].sum()

    nao_contabil = pd.DataFrame({
        "Descrição": ["Distribuição de Lucros", "Resultado de Investimentos", "Total Não Contábil"],
        "Valor (R$)": [total_dist, total_invest, total_dist + total_invest]
    })

    resumo = pd.DataFrame({
        "Indicador": ["Resultado Operacional", "Distribuição de Lucros", "Resultado de Investimentos"],
        "Valor (R$)": [resultado_operacional, total_dist, total_invest]
    })

    receita_fixa     = df_receita[(df_receita["Tipo"] == "Entrada") & (df_receita["Categoria"] == "Partido")][["Data", "Descricao", "Valor"]]
    receita_variavel = df_receita[(df_receita["Tipo"] == "Entrada") & (df_receita["Categoria"].isin(["Honorários", "Exito", "Sucumbencial", "Compensação/liminar", "Contratado", "Diversos"]))][["Data", "Descricao", "Valor"]]
    nc_entradas      = df_investimento[df_investimento["Tipo"] == "Entrada"][["Data", "Descricao", "Valor"]]
    nc_saidas        = df_dist[df_dist["Tipo"] == "Saída"][["Data", "Descricao", "Valor"]]

    conciliacao = pd.concat([
        receita_fixa.rename(columns={"Descricao": "Conta", "Valor": "Valor (R$)"})[["Conta", "Valor (R$)"]],
        pd.DataFrame({"Conta": ["Total Receita Fixa"], "Valor (R$)": [receita_fixa["Valor"].sum()]}),
        receita_variavel.rename(columns={"Descricao": "Conta", "Valor": "Valor (R$)"})[["Conta", "Valor (R$)"]],
        pd.DataFrame({"Conta": ["Total Receita Variável"], "Valor (R$)": [receita_variavel["Valor"].sum()]}),
        nc_entradas.rename(columns={"Descricao": "Conta", "Valor": "Valor (R$)"})[["Conta", "Valor (R$)"]],
        pd.DataFrame({"Conta": ["Total Resultado de Investimentos"], "Valor (R$)": [nc_entradas["Valor"].sum() if len(nc_entradas) else 0]}),
        nc_saidas.rename(columns={"Descricao": "Conta", "Valor": "Valor (R$)"})[["Conta", "Valor (R$)"]],
        pd.DataFrame({"Conta": ["Total Distribuição de Lucros"], "Valor (R$)": [nc_saidas["Valor"].sum() if len(nc_saidas) else 0]}),
    ])
    conciliacao["Valor (R$)"] = pd.to_numeric(conciliacao["Valor (R$)"], errors="coerce")
    conciliacao = conciliacao[conciliacao["Conta"].notna() & (conciliacao["Conta"].str.strip() != "")]
    conciliacao = conciliacao.drop_duplicates().reset_index(drop=True)

    despesas = df_receita[
        (df_receita["Tipo"] == "Saída") & (df_receita["Categoria"].isin(CATEGORIAS_DESPESA))
    ][["Data", "Pago para / Recebido de", "Descricao", "Categoria", "Valor"]]
    totais                           = despesas.groupby("Categoria")["Valor"].sum().reset_index()
    totais["Data"]                   = ""
    totais["Pago para / Recebido de"] = ""
    totais["Descricao"]              = "TOTAL " + totais["Categoria"]
    despesas_detalhadas              = pd.concat([despesas, totais], ignore_index=True)
    despesas_detalhadas              = despesas_detalhadas.rename(columns={
        "Data": "DATA", "Pago para / Recebido de": "PAGO PARA",
        "Descricao": "DESCRIÇÃO", "Categoria": "CLASSIFICAÇÃO", "Valor": "VALORES"
    })

    df_bancos    = pd.concat([df_receita, df_dist], ignore_index=True)
    bancos       = df_bancos.groupby(["Conta Financeira", "Tipo"])["Valor"].sum().reset_index()
    bancos_pivot = bancos.pivot_table(index="Conta Financeira", columns="Tipo", values="Valor", aggfunc="sum", fill_value=0).reset_index()
    bancos_pivot["Saldo do Mês (R$)"] = bancos_pivot.get("Entrada", 0) + bancos_pivot.get("Saída", 0)
    bancos_pivot = bancos_pivot.rename(columns={"Conta Financeira": "BANCO", "Entrada": "ENTRADAS (R$)", "Saída": "SAÍDAS (R$)"})
    saldo_ini    = df_receita[df_receita["Categoria"] == "Saldo inicial"].groupby("Conta Financeira")["Valor"].sum().reset_index().rename(columns={"Conta Financeira": "BANCO", "Valor": "Saldo Inicial (R$)"})
    bancos_pivot = bancos_pivot.merge(saldo_ini, on="BANCO", how="left")
    bancos_pivot["Saldo Inicial (R$)"] = bancos_pivot["Saldo Inicial (R$)"].fillna(0)
    bancos_pivot["Saldo Final (R$)"]   = bancos_pivot["Saldo Inicial (R$)"] + bancos_pivot["Saldo do Mês (R$)"]
    colunas      = ["BANCO", "Saldo Inicial (R$)", "ENTRADAS (R$)", "SAÍDAS (R$)", "Saldo do Mês (R$)", "Saldo Final (R$)"]
    bancos_pivot = bancos_pivot[[c for c in colunas if c in bancos_pivot.columns]]

    return dre_operacional, nao_contabil, resumo, conciliacao, despesas_detalhadas, bancos_pivot

def gerar_ranking_clientes(df):
    """Ranking de receita por cliente, excluindo movimentos não contábeis."""
    cats_receita = ["Honorários", "Exito", "Contratado", "Partido", "Sucumbencial",
                    "Compensação/liminar", "Diversos"]
    mask_invest = (df["Categoria"] == "Diversos") & (df["Descricao"].apply(eh_investimento))
    df_rec = df[~mask_invest]

    ranking = (
        df_rec[
            (df_rec["Tipo"] == "Entrada") &
            (df_rec["Categoria"].isin(cats_receita))
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
    """Receita e despesa por centro de custo."""
    cats_receita = ["Honorários", "Exito", "Contratado", "Partido", "Sucumbencial",
                    "Compensação/liminar", "Diversos"]
    cats_despesa = ["Despesa Fixa", "Despesa Variável", "Despesa bancária",
                    "Folha de pagamento", "Impostos"]

    mask_invest = (df["Categoria"] == "Diversos") & (df["Descricao"].apply(eh_investimento))
    df_clean = df[~mask_invest]

    receita = (
        df_clean[(df_clean["Tipo"] == "Entrada") & (df_clean["Categoria"].isin(cats_receita))]
        .groupby("Centro de custo")["Valor"].sum()
        .rename("RECEITA (R$)")
    )
    despesa = (
        df_clean[(df_clean["Tipo"] == "Saída") & (df_clean["Categoria"].isin(cats_despesa))]
        .groupby("Centro de custo")["Valor"].sum()
        .rename("DESPESA (R$)")
    )

    centro = pd.concat([receita, despesa], axis=1).fillna(0).reset_index()
    centro = centro.rename(columns={"Centro de custo": "CENTRO DE CUSTO"})
    centro["RESULTADO (R$)"] = centro["RECEITA (R$)"] + centro["DESPESA (R$)"]
    centro = centro.sort_values("RECEITA (R$)", ascending=False).reset_index(drop=True)

    total = pd.DataFrame([{
        "CENTRO DE CUSTO": "TOTAL",
        "RECEITA (R$)": centro["RECEITA (R$)"].sum(),
        "DESPESA (R$)": centro["DESPESA (R$)"].sum(),
        "RESULTADO (R$)": centro["RESULTADO (R$)"].sum(),
    }])
    centro = pd.concat([centro, total], ignore_index=True)
    return centro
