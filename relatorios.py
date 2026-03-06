import pandas as pd
from funcoes import soma, soma_entradas

# Categorias que são despesas operacionais reais (aparecem na aba Despesas)
CATEGORIAS_DESPESA = [
    "Despesa Fixa",
    "Despesa Variável",
    "Despesa bancária",
    "Repasse",
    "Participação em contrato",
    "Folha de pagamento",
    "Impostos",
]

def gerar_relatorios(df, nome_arquivo="Relatorio_Completo.xlsx"):
    # ===== MAPA DE CATEGORIAS =====
    mapa_categorias = {
        "Honorários": "Receita Bruta",
        "Exito": "Receita Bruta",
        "Contratado": "Receita Bruta",
        "Partido": "Receita Bruta",
        "Sucumbencial": "Receita Bruta",
        "Compensação/liminar": "Receita Bruta",
        "Diversos": "Receita Bruta",                  # CORRIGIDO: entra na receita bruta
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

    # ===== Capturar categorias dinâmicas =====
    categorias_unicas = df["Categoria"].dropna().unique()
    valores_por_grupo = {}
    for cat in categorias_unicas:
        grupo = mapa_categorias.get(cat, "Outras")
        valores_por_grupo[grupo] = valores_por_grupo.get(grupo, 0) + df[df["Categoria"] == cat]["Valor"].sum()
    outras = valores_por_grupo.get("Outras", 0)

    # ===== DRE OPERACIONAL =====
    honorarios    = soma_entradas(df, ["Honorários"])
    exito         = soma_entradas(df, ["Exito"])
    contratado    = soma_entradas(df, ["Contratado", "Partido"])
    sucumbenciais = soma_entradas(df, ["Sucumbencial"])
    compensacoes  = soma_entradas(df, ["Compensação/liminar"])
    diversos      = soma_entradas(df, ["Diversos"])            # CORRIGIDO
    receita_bruta = honorarios + exito + contratado + sucumbenciais + compensacoes + diversos

    impostos      = soma(df, ["Impostos", "Despesa bancária"])
    folha         = soma(df, ["Folha de pagamento"])
    pro_labore    = df[(df["Descricao"].str.contains("pró labore", case=False, na=False))]["Valor"].sum()
    custos_folha  = folha + pro_labore

    despesas_fixas    = soma(df, ["Despesa Fixa"])
    despesas_variaveis = soma(df, ["Despesa Variável"])
    repasse_clientes  = soma(df, ["Repasse", "Participação em contrato"])

    receita_liquida      = receita_bruta + impostos
    lucro_bruto          = receita_liquida + custos_folha
    resultado_operacional = lucro_bruto + despesas_fixas + despesas_variaveis + repasse_clientes + outras

    dre_operacional = pd.DataFrame({
        "Conta": [
            "Receita Bruta", "Honorários", "Êxito", "Contratado/Partido",
            "Sucumbenciais", "Compensações", "Diversos",
            "(-) Impostos e Deduções", "Receita Líquida",
            "(-) Custos/Folha de Pagamento", "Salários", "Pró-labore",
            "Lucro Bruto", "(-) Despesas Fixas", "(-) Despesas Variáveis", "Repasse",
            "Outras Categorias", "Resultado Operacional"
        ],
        "Valor (R$)": [
            receita_bruta, honorarios, exito, contratado,
            sucumbenciais, compensacoes, diversos,
            impostos, receita_liquida,
            custos_folha, folha, pro_labore,
            lucro_bruto, despesas_fixas, despesas_variaveis, repasse_clientes,
            outras, resultado_operacional
        ]
    })

    # ===== DESTINAÇÃO DO LUCRO =====
    distribuicao_lucros  = soma(df, ["Distribuição de lucros"])
    participacao_vinicius = soma(df, ["Participação Vinicius Fraga"])
    total_destinacao     = distribuicao_lucros + participacao_vinicius

    destinacao = pd.DataFrame({
        "Conta": ["Distribuição de Lucros", "Participação Vinicius Fraga", "Total Destinação"],
        "Valor (R$)": [distribuicao_lucros, participacao_vinicius, total_destinacao]
    })

    # ===== RESUMO FINAL =====
    lucro_liquido_final = resultado_operacional + total_destinacao
    resumo = pd.DataFrame({
        "Indicador": ["Lucro Operacional", "Total Destinação", "Lucro Líquido após Destinação"],
        "Valor (R$)": [resultado_operacional, total_destinacao, lucro_liquido_final]
    })

    # ===== CONCILIAÇÃO =====
    receita_fixa       = df[(df["Tipo"] == "Entrada") & (df["Categoria"].str.contains("Partido", case=False, na=False))][["Data", "Descricao", "Valor"]]
    operacional_variavel = df[(df["Tipo"] == "Entrada") & (df["Categoria"].isin(["Honorários", "Exito", "Sucumbencial", "Compensação/liminar", "Diversos"]))][["Data", "Descricao", "Valor"]]
    nao_contabil       = df[(df["Tipo"] == "Entrada") & (df["Categoria"].isin(["Saldo inicial", "Transferência"]))][["Data", "Descricao", "Valor"]]

    total_fixa        = receita_fixa["Valor"].sum()
    total_variavel    = operacional_variavel["Valor"].sum()
    total_nao_contabil = nao_contabil["Valor"].sum()

    conciliacao = pd.concat([
        receita_fixa.rename(columns={"Descricao": "Conta", "Valor": "Valor (R$)"})[["Conta", "Valor (R$)"]],
        pd.DataFrame({"Conta": ["Total Receita Fixa"], "Valor (R$)": [total_fixa]}),
        operacional_variavel.rename(columns={"Descricao": "Conta", "Valor": "Valor (R$)"})[["Conta", "Valor (R$)"]],
        pd.DataFrame({"Conta": ["Total Receita Operacional Variável"], "Valor (R$)": [total_variavel]}),
        nao_contabil.rename(columns={"Descricao": "Conta", "Valor": "Valor (R$)"})[["Conta", "Valor (R$)"]],
        pd.DataFrame({"Conta": ["Total Movimento Não Contábil"], "Valor (R$)": [total_nao_contabil]}),
    ])
    conciliacao["Valor (R$)"] = pd.to_numeric(conciliacao["Valor (R$)"], errors="coerce")
    conciliacao = conciliacao[conciliacao["Conta"].notna() & (conciliacao["Conta"].str.strip() != "")]
    conciliacao = conciliacao.drop_duplicates().reset_index(drop=True)

    # ===== DESPESAS DETALHADAS =====
    # CORRIGIDO: só categorias operacionais, sem Transferência, Distribuição e Participação Vinicius
    despesas = df[
        (df["Tipo"] == "Saída") &
        (df["Categoria"].isin(CATEGORIAS_DESPESA))
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

    # ===== RELATÓRIO POR BANCOS =====
    bancos = df.groupby(["Conta Financeira", "Tipo"])["Valor"].sum().reset_index()
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
        df[df["Categoria"] == "Saldo inicial"]
        .groupby("Conta Financeira")["Valor"].sum().reset_index()
        .rename(columns={"Conta Financeira": "BANCO", "Valor": "Saldo Inicial (R$)"})
    )
    bancos_pivot = bancos_pivot.merge(saldo_inicial_por_banco, on="BANCO", how="left")
    bancos_pivot["Saldo Inicial (R$)"] = bancos_pivot["Saldo Inicial (R$)"].fillna(0)
    bancos_pivot["Saldo Final (R$)"] = bancos_pivot["Saldo Inicial (R$)"] + bancos_pivot["Saldo do Mês (R$)"]
    colunas = ["BANCO", "Saldo Inicial (R$)", "ENTRADAS (R$)", "SAÍDAS (R$)", "Saldo do Mês (R$)", "Saldo Final (R$)"]
    bancos_pivot = bancos_pivot[[c for c in colunas if c in bancos_pivot.columns]]

    # ===== EXPORTAR =====
    with pd.ExcelWriter(nome_arquivo) as writer:
        dre_operacional.to_excel(writer, sheet_name="DRE_Operacional", index=False)
        destinacao.to_excel(writer, sheet_name="Destinacao", index=False)
        resumo.to_excel(writer, sheet_name="Resumo", index=False)
        conciliacao.to_excel(writer, sheet_name="Conciliacao", index=False)
        despesas_detalhadas.to_excel(writer, sheet_name="Despesas", index=False)
        bancos_pivot.to_excel(writer, sheet_name="Bancos", index=False)

    return dre_operacional, destinacao, resumo, conciliacao, despesas_detalhadas, bancos_pivot
