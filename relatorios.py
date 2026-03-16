import pandas as pd
from funcoes import soma, soma_entradas

CATEGORIAS_DESPESA = [
    "Despesa Fixa",
    "Despesa Variável",
    "Despesa bancária",
    "Repasse",
    "Participação em contrato",
    "Folha de pagamento",
    "Impostos",
]

KEYWORDS_INVESTIMENTO = ["resultado de investimento", "resutado de investimento", "rendimento"]

def eh_investimento(descricao):
    if not descricao:
        return False
    return any(kw in str(descricao).lower() for kw in KEYWORDS_INVESTIMENTO)

def gerar_relatorios(df, nome_arquivo="Relatorio_Completo.xlsx"):

    mapa_categorias = {
        "Honorários": "Receita Bruta",
        "Exito": "Receita Bruta",
        "Contratado": "Receita Bruta",
        "Partido": "Receita Bruta",
        "Sucumbencial": "Receita Bruta",
        "Compensação/liminar": "Receita Bruta",
        "Diversos": "Receita Bruta",
        "Impostos": "Impostos e Deduções",
        "Despesa bancária": "Impostos e Deduções",
        "Despesa Fixa": "Despesas Fixas",
        "Despesa Variável": "Despesas Variáveis",
        "Repasse": "Repasse",
        "Participação em contrato": "Repasse",
        "Folha de pagamento": "Folha",
        "Distribuição de lucros": "Destinação",
        "Participação Vinicius Fraga": "Destinação"
    }

    mask_investimento = (df["Categoria"] == "Diversos") & (df["Descricao"].apply(eh_investimento))
    df_investimento   = df[mask_investimento].copy()
    df_receita        = df[~mask_investimento].copy()  # tudo exceto investimentos

    mask_cartao = (
        (df_receita["Categoria"] == "Transferência") &
        (df_receita["Tipo"] == "Saída") &
        (df_receita["Descricao"].str.contains("cartão|cartao|fatura", case=False, na=False))
    )
    df_cartao = df_receita[mask_cartao].copy()
    df_cartao["Categoria"] = "Despesa Variável"  
    df_receita = df_receita[~mask_cartao].copy()
    df_receita = pd.concat([df_receita, df_cartao], ignore_index=True)

    
    honorarios     = soma_entradas(df_receita, ["Honorários"])
    exito          = soma_entradas(df_receita, ["Exito"])
    contratado     = soma_entradas(df_receita, ["Contratado", "Partido"])
    sucumbenciais  = soma_entradas(df_receita, ["Sucumbencial"])
    compensacoes   = soma_entradas(df_receita, ["Compensação/liminar"])
    diversos_rec   = soma_entradas(df_receita, ["Diversos"])  
    receita_bruta  = honorarios + exito + contratado + sucumbenciais + compensacoes + diversos_rec

    impostos       = soma(df_receita, ["Impostos"])
    folha          = soma(df_receita, ["Folha de pagamento"])  
    custos_folha   = folha

    despesas_fixas     = soma(df_receita, ["Despesa Fixa", "Despesa bancária"])
    despesas_variaveis = soma(df_receita, ["Despesa Variável"])  
    repasse_clientes   = soma(df_receita, ["Repasse", "Participação em contrato"])

    receita_liquida       = receita_bruta + impostos
    lucro_bruto           = receita_liquida + custos_folha
    resultado_operacional = lucro_bruto + despesas_fixas + despesas_variaveis + repasse_clientes

    dre_operacional = pd.DataFrame({
        "Conta": [
            "Receita Bruta", "Honorários", "Êxito", "Contratado/Partido",
            "Sucumbenciais", "Compensações", "Diversos",
            "(-) Impostos", "Receita Líquida",
            "(-) Folha de Pagamento",
            "Lucro Bruto", "(-) Despesas Fixas", "(-) Despesas Variáveis", "Repasse",
            "Resultado Operacional"
        ],
        "Valor (R$)": [
            receita_bruta, honorarios, exito, contratado,
            sucumbenciais, compensacoes, diversos_rec,
            impostos, receita_liquida,
            custos_folha,
            lucro_bruto, despesas_fixas, despesas_variaveis, repasse_clientes,
            resultado_operacional
        ]
    })

    distribuicao_lucros   = soma(df_receita, ["Distribuição de lucros"])
    participacao_vinicius = soma(df_receita, ["Participação Vinicius Fraga"])
    total_destinacao      = distribuicao_lucros + participacao_vinicius

    destinacao = pd.DataFrame({
        "Conta": ["Distribuição de Lucros", "Participação Vinicius Fraga", "Total Destinação"],
        "Valor (R$)": [distribuicao_lucros, participacao_vinicius, total_destinacao]
    })

    lucro_liquido_final = resultado_operacional + total_destinacao
    resumo = pd.DataFrame({
        "Indicador": ["Resultado Operacional", "Total Destinação", "Lucro Líquido após Destinação"],
        "Valor (R$)": [resultado_operacional, total_destinacao, lucro_liquido_final]
    })

    receita_fixa        = df_receita[(df_receita["Tipo"] == "Entrada") & (df_receita["Categoria"] == "Partido")][["Data", "Descricao", "Valor"]]
    receita_variavel    = df_receita[(df_receita["Tipo"] == "Entrada") & (df_receita["Categoria"].isin(["Honorários", "Exito", "Sucumbencial", "Compensação/liminar", "Contratado", "Diversos"]))][["Data", "Descricao", "Valor"]]
    nao_contabil        = df_investimento[df_investimento["Tipo"] == "Entrada"][["Data", "Descricao", "Valor"]]

    total_fixa          = receita_fixa["Valor"].sum()
    total_variavel      = receita_variavel["Valor"].sum()
    total_nao_contabil  = nao_contabil["Valor"].sum()

    conciliacao = pd.concat([
        receita_fixa.rename(columns={"Descricao": "Conta", "Valor": "Valor (R$)"})[["Conta", "Valor (R$)"]],
        pd.DataFrame({"Conta": ["Total Receita Fixa"], "Valor (R$)": [total_fixa]}),
        receita_variavel.rename(columns={"Descricao": "Conta", "Valor": "Valor (R$)"})[["Conta", "Valor (R$)"]],
        pd.DataFrame({"Conta": ["Total Receita Variável"], "Valor (R$)": [total_variavel]}),
        nao_contabil.rename(columns={"Descricao": "Conta", "Valor": "Valor (R$)"})[["Conta", "Valor (R$)"]],
        pd.DataFrame({"Conta": ["Total Movimento Não Contábil"], "Valor (R$)": [total_nao_contabil]}),
    ])
    conciliacao["Valor (R$)"] = pd.to_numeric(conciliacao["Valor (R$)"], errors="coerce")
    conciliacao = conciliacao[conciliacao["Conta"].notna() & (conciliacao["Conta"].str.strip() != "")]
    conciliacao = conciliacao.drop_duplicates().reset_index(drop=True)

    despesas = df_receita[
        (df_receita["Tipo"] == "Saída") &
        (df_receita["Categoria"].isin(CATEGORIAS_DESPESA))
    ][["Data", "Pago para / Recebido de", "Descricao", "Categoria", "Valor"]]

    totais = despesas.groupby("Categoria")["Valor"].sum().reset_index()
    totais["Data"] = ""
    totais["Pago para / Recebido de"] = ""
    totais["Descricao"] = "TOTAL " + totais["Categoria"]
    despesas_detalhadas = pd.concat([despesas, totais], ignore_index=True)
    despesas_detalhadas = despesas_detalhadas.rename(columns={
        "Data": "DATA",
        "Pago para / Recebido de": "PAGO PARA",
        "Descricao": "DESCRIÇÃO",
        "Categoria": "CLASSIFICAÇÃO",
        "Valor": "VALORES"
    })

    bancos = df_receita.groupby(["Conta Financeira", "Tipo"])["Valor"].sum().reset_index()
    bancos_pivot = bancos.pivot_table(
        index="Conta Financeira", columns="Tipo", values="Valor", aggfunc="sum", fill_value=0
    ).reset_index()
    bancos_pivot["Saldo do Mês (R$)"] = bancos_pivot.get("Entrada", 0) + bancos_pivot.get("Saída", 0)
    bancos_pivot = bancos_pivot.rename(columns={
        "Conta Financeira": "BANCO",
        "Entrada": "ENTRADAS (R$)",
        "Saída": "SAÍDAS (R$)"
    })
    saldo_inicial_por_banco = (
        df_receita[df_receita["Categoria"] == "Saldo inicial"]
        .groupby("Conta Financeira")["Valor"].sum().reset_index()
        .rename(columns={"Conta Financeira": "BANCO", "Valor": "Saldo Inicial (R$)"})
    )
    bancos_pivot = bancos_pivot.merge(saldo_inicial_por_banco, on="BANCO", how="left")
    bancos_pivot["Saldo Inicial (R$)"] = bancos_pivot["Saldo Inicial (R$)"].fillna(0)
    bancos_pivot["Saldo Final (R$)"] = bancos_pivot["Saldo Inicial (R$)"] + bancos_pivot["Saldo do Mês (R$)"]
    colunas = ["BANCO", "Saldo Inicial (R$)", "ENTRADAS (R$)", "SAÍDAS (R$)", "Saldo do Mês (R$)", "Saldo Final (R$)"]
    bancos_pivot = bancos_pivot[[c for c in colunas if c in bancos_pivot.columns]]

    return dre_operacional, destinacao, resumo, conciliacao, despesas_detalhadas, bancos_pivot
