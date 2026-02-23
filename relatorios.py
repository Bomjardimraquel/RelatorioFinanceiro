import pandas as pd
from funcoes import soma, soma_entradas

def gerar_relatorios(df):
    mapa_categorias = {
        "Honorários": "Receita Bruta",
        "Exito": "Receita Bruta",
        "Contratado": "Receita Bruta",
        "Partido": "Receita Bruta",
        "Sucumbencial": "Receita Bruta",
        "Compensação/liminar": "Receita Bruta",
        "Impostos": "Impostos e Deduções",
        "Despesa bancária": "Impostos e Deduções",
        "Despesa Fixa": "Despesas Fixas",
        "Despesa Variável": "Despesas Variáveis",
        "Repasse": "Repasse",
        "Distribuição de lucros": "Destinação",
        "Participação Vinicius Fraga": "Destinação"
    }

    categorias_unicas = df["Categoria"].dropna().unique()
    valores_por_grupo = {}

    for cat in categorias_unicas:
        grupo = mapa_categorias.get(cat, "Outras")
        valores_por_grupo[grupo] = valores_por_grupo.get(grupo, 0) + df[df["Categoria"] == cat]["Valor"].sum()

    outras = valores_por_grupo.get("Outras", 0)

    honorarios = soma_entradas(df, ["Honorários"])
    exito = soma_entradas(df, ["Exito"])
    contratado = soma_entradas(df, ["Contratado", "Partido"])
    sucumbenciais = soma_entradas(df, ["Sucumbencial"])
    compensacoes = soma_entradas(df, ["Compensação/liminar"])
    receita_bruta = honorarios + exito + contratado + sucumbenciais + compensacoes

    impostos = soma(df, ["Impostos", "Despesa bancária"])
    folha = df[(df["Descricao"].str.contains("salário", case=False, na=False))]["Valor"].sum()
    pro_labore = df[(df["Descricao"].str.contains("pró labore", case=False, na=False))]["Valor"].sum()
    custos_folha = folha + pro_labore
    despesas_fixas = soma(df, ["Despesa Fixa"])
    despesas_variaveis = soma(df, ["Despesa Variável"])
    repasse_clientes = soma(df, ["Repasse"])

    receita_liquida = receita_bruta + impostos
    lucro_bruto = receita_liquida + custos_folha
    resultado_operacional = lucro_bruto + despesas_fixas + despesas_variaveis + repasse_clientes + outras

    dre_operacional = pd.DataFrame({
        "Conta": [
            "Receita Bruta","Honorários","Êxito","Contratado/Partido",
            "Sucumbenciais","Compensações",
            "(-) Impostos e Deduções","Receita Líquida",
            "(-) Custos/Folha de Pagamento","Salários","Pró-labore",
            "Lucro Bruto","(-) Despesas Fixas","(-) Despesas Variáveis","Repasse",
            "Outras Categorias","Resultado Operacional"
        ],
        "Valor (R$)": [
            receita_bruta,honorarios,exito,contratado,
            sucumbenciais,compensacoes,
            impostos,receita_liquida,
            custos_folha,folha,pro_labore,
            lucro_bruto,despesas_fixas,despesas_variaveis,repasse_clientes,
            outras,resultado_operacional
        ]
    })

    distribuicao_lucros = soma(df, ["Distribuição de lucros"])
    participacao_vinicius = soma(df, ["Participação Vinicius Fraga"])
    total_destinacao = distribuicao_lucros + participacao_vinicius

    destinacao = pd.DataFrame({
        "Conta":["Distribuição de Lucros","Participação Vinicius Fraga","Total Destinação"],
        "Valor (R$)":[distribuicao_lucros,participacao_vinicius,total_destinacao]
    })

    lucro_liquido_final = resultado_operacional + total_destinacao
    resumo = pd.DataFrame({
        "Indicador":["Lucro Operacional","Total Destinação","Lucro Líquido após Destinação"],
        "Valor (R$)":[resultado_operacional,total_destinacao,lucro_liquido_final]
    })

    receita_fixa = df[(df["Tipo"]=="Entrada") & (df["Categoria"].str.contains("Partido", case=False, na=False))][["Data","Descricao","Valor"]]
    operacional_variavel = df[(df["Tipo"]=="Entrada") & (df["Categoria"].isin(["Honorários","Exito","Sucumbencial","Compensação/liminar"]))][["Data","Descricao","Valor"]]
    nao_contabil = df[(df["Tipo"]=="Entrada") & (df["Categoria"].isin(["Saldo inicial","Transferência"]))][["Data","Descricao","Valor"]]

    total_fixa = receita_fixa["Valor"].sum()
    total_variavel = operacional_variavel["Valor"].sum()
    total_nao_contabil = nao_contabil["Valor"].sum()

    conciliacao = pd.concat([
        receita_fixa.rename(columns={"Descricao":"Conta","Valor":"Valor (R$)"})[["Conta","Valor (R$)"]],
        pd.DataFrame({"Conta":["Total Receita Fixa"],"Valor (R$)":[total_fixa]}),
        operacional_variavel.rename(columns={"Descricao":"Conta","Valor":"Valor (R$)"})[["Conta","Valor (R$)"]],
        pd.DataFrame({"Conta":["Total Receita Operacional Variável"],"Valor (R$)":[total_variavel]}),
        nao_contabil.rename(columns={"Descricao":"Conta","Valor":"Valor (R$)"})[["Conta","Valor (R$)"]],
        pd.DataFrame({"Conta":["Total Movimento Não Contábil"],"Valor (R$)":[total_nao_contabil]}),
    ])

    conciliacao["Valor (R$)"] = pd.to_numeric(conciliacao["Valor (R$)"], errors="coerce")
    conciliacao = conciliacao[conciliacao["Conta"].notna() & (conciliacao["Conta"].str.strip() != "")]
    conciliacao = conciliacao.drop_duplicates().reset_index(drop=True)

    despesas = df[df["Tipo"]=="Saída"][["Data","Pago para / Recebido de","Descricao","Categoria","Valor"]]
    totais = despesas.groupby("Categoria")["Valor"].sum().reset_index()
    totais["Data"] = ""
    totais["Pago para / Recebido de"] = ""
    totais["Descricao"] = "TOTAL " + totais["Categoria"]
    despesas_detalhadas = pd.concat([despesas, totais], ignore_index=True)
    despesas_detalhadas = despesas_detalhadas.rename(columns={
        "Data":"DATA",
        "Pago para / Recebido de":"PAGO PARA",
        "Descricao":"DESCRIÇÃO",
        "Categoria":"CLASSIFICAÇÃO",
        "Valor":"VALORES"
    })

    bancos = df.groupby(["Conta Financeira","Tipo"])["Valor"].sum().reset_index()
    bancos_pivot = bancos.pivot_table(index="Conta Financeira", columns="Tipo", values="Valor", aggfunc="sum", fill_value=0).reset_index()
    bancos_pivot["Saldo (R$)"] = bancos_pivot.get("Entrada",0) + bancos_pivot.get("Saída",0)
    bancos_pivot = bancos_pivot.rename(columns={"Conta Financeira":"BANCO","Entrada":"ENTRADAS (R$)","Saída":"SAÍDAS (R$)"})

    return dre_operacional, destinacao, resumo, conciliacao, despesas_detalhadas, bancos_pivot

