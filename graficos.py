def criar_graficos(workbook, worksheet, df, despesas_detalhadas, dre_operacional, destinacao, resumo, writer):
    # ===== Gráfico 1: Despesas por categoria =====
    despesas_por_categoria = df[df["Tipo"]=="Saída"].groupby("Categoria")["Valor"].sum().reset_index()
    linha_inicio = len(despesas_detalhadas) + 3

    # escreve os dados na aba "Despesas"
    despesas_por_categoria.to_excel(writer, sheet_name="Despesas", index=False, startrow=linha_inicio)

    chart1 = workbook.add_chart({"type": "pie"})
    chart1.add_series({
        "name": "Distribuição das Despesas",
        "categories": ["Despesas", linha_inicio+1, 0, linha_inicio+len(despesas_por_categoria), 0],
        "values":     ["Despesas", linha_inicio+1, 1, linha_inicio+len(despesas_por_categoria), 1],
        "data_labels": {"percentage": True}
    })
    chart1.set_title({"name": "Distribuição das Despesas"})
    worksheet.insert_chart("A1", chart1)

    # ===== Gráfico 2: Receitas por categoria =====
    receitas_por_categoria = df[df["Tipo"]=="Entrada"].groupby("Categoria")["Valor"].sum().reset_index()
    linha_inicio_receitas = len(dre_operacional) + len(destinacao) + len(resumo) + 10

    # escreve os dados na aba "DRE_Operacional"
    receitas_por_categoria.to_excel(writer, sheet_name="DRE_Operacional", index=False, startrow=linha_inicio_receitas)

    chart2 = workbook.add_chart({"type": "pie"})
    chart2.add_series({
        "name": "Distribuição das Receitas",
        "categories": ["DRE_Operacional", linha_inicio_receitas+1, 0, linha_inicio_receitas+len(receitas_por_categoria), 0],
        "values":     ["DRE_Operacional", linha_inicio_receitas+1, 1, linha_inicio_receitas+len(receitas_por_categoria), 1],
        "data_labels": {"percentage": True}
    })
    chart2.set_title({"name": "Distribuição das Receitas"})
    worksheet.insert_chart("A20", chart2)

