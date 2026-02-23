def aplicar_estilos(workbook, writer, dre_operacional, destinacao, resumo, despesas_detalhadas, conciliacao, bancos_pivot):
    # ===== Estilos para DRE_Operacional =====
    ws_dre = writer.sheets["DRE_Operacional"]

    header_format = workbook.add_format({"bold": True, "bg_color": "#4F81BD", "font_color": "white", "align": "center", "border": 1})
    negative_format = workbook.add_format({"font_color": "red"})
    positive_format = workbook.add_format({"font_color": "green", "bold": True})
    total_format = workbook.add_format({"bold": True, "font_color": "green"})

    # Cabeçalho da primeira tabela
    for col_num, value in enumerate(dre_operacional.columns.values):
        ws_dre.write(0, col_num, value, header_format)

    for row_num, conta in enumerate(dre_operacional["Conta"], start=1):
        valor = dre_operacional.loc[row_num-1, "Valor (R$)"]
        if "Lucro bruto" in conta:
            ws_dre.write(row_num, 0, conta, total_format)
            ws_dre.write(row_num, 1, valor, total_format)
        elif valor > 0 and "Lucro" not in conta:
            ws_dre.set_row(row_num, None, positive_format)
        elif valor < 0:
            ws_dre.set_row(row_num, None, negative_format)
        elif "Lucro" in conta or "Resultado" in conta:
            ws_dre.set_row(row_num, None, total_format)

    # Cabeçalho da segunda tabela (destinacao)
    linha_destinacao = len(dre_operacional) + 3
    for col_num, value in enumerate(destinacao.columns.values):
        ws_dre.write(linha_destinacao, col_num, value, header_format)

    for row_num, conta in enumerate(destinacao["Conta"], start=linha_destinacao+1):
        valor = destinacao.loc[row_num-(linha_destinacao+1), "Valor (R$)"]
        if valor < 0:
            ws_dre.set_row(row_num, None, negative_format)
        elif "Total" in conta:
            ws_dre.set_row(row_num, None, total_format)

    # Cabeçalho da terceira tabela (resumo)
    linha_resumo = linha_destinacao + len(destinacao) + 3
    for col_num, value in enumerate(resumo.columns.values):
        ws_dre.write(linha_resumo, col_num, value, header_format)

    for row_num, conta in enumerate(resumo["Indicador"], start=linha_resumo+1):
        valor = resumo.loc[row_num-(linha_resumo+1), "Valor (R$)"]
        if "Lucro" in conta and valor > 0:
            ws_dre.set_row(row_num, None, positive_format)
        elif valor < 0:
            ws_dre.set_row(row_num, None, negative_format)
        elif "Total" in conta:
            ws_dre.set_row(row_num, None, total_format)

    # ===== Estilos para Despesas =====
    ws_despesas = writer.sheets["Despesas"]
    header_format = workbook.add_format({"bold": True, "bg_color": "#4F81BD", "font_color": "white", "align": "center", "border": 1})
    alt_row_format = workbook.add_format({"bg_color": "#F2F2F2"})
    total_format = workbook.add_format({"bold": True, "bg_color": "#D9E1F2"})
    negative_format = workbook.add_format({"font_color": "red"})

    for col_num, value in enumerate(despesas_detalhadas.columns.values):
        ws_despesas.write(0, col_num, value, header_format)

    for row_num, descricao in enumerate(despesas_detalhadas["DESCRIÇÃO"], start=1):
        valor = despesas_detalhadas.loc[row_num-1, "VALORES"]
        if row_num % 2 == 0:
            ws_despesas.set_row(row_num, None, alt_row_format)
        if str(descricao).startswith("TOTAL"):
            ws_despesas.write(row_num, 2, descricao, total_format)
            ws_despesas.write(row_num, 4, valor, total_format)
        elif valor < 0:
            ws_despesas.write(row_num, 4, valor, negative_format)

    # ===== Estilos para Conciliação =====
    ws_conciliacao = writer.sheets["Conciliacao"]
    header_format = workbook.add_format({"bold": True, "bg_color": "#4F81BD", "font_color": "white", "align": "center", "border": 1})
    alt_row_format = workbook.add_format({"bg_color": "#F9F9F9"})
    total_format = workbook.add_format({"bold": True, "bg_color": "#D9E1F2"})
    positive_format = workbook.add_format({"font_color": "green"})
    negative_format = workbook.add_format({"font_color": "red"})

    for col_num, value in enumerate(conciliacao.columns.values):
        ws_conciliacao.write(0, col_num, value, header_format)

    for row_num, conta in enumerate(conciliacao["Conta"], start=1):
        valor = conciliacao.loc[row_num-1, "Valor (R$)"]
        if row_num % 2 == 0:
            ws_conciliacao.set_row(row_num, None, alt_row_format)
        if str(conta).startswith("Total"):
            ws_conciliacao.write(row_num, 0, conta, total_format)
            ws_conciliacao.write(row_num, 1, valor, total_format)
        elif valor > 0:
            ws_conciliacao.write(row_num, 1, valor, positive_format)
        elif valor < 0:
            ws_conciliacao.write(row_num, 1, valor, negative_format)

    # ===== Estilos para Bancos =====
    ws_bancos = writer.sheets["Bancos"]
    header_format = workbook.add_format({"bold": True, "bg_color": "#4F81BD", "font_color": "white", "align": "center", "border": 1})
    entrada_format = workbook.add_format({"font_color": "green"})
    saida_format = workbook.add_format({"font_color": "red"})
    saldo_format = workbook.add_format({"bold": True})

    for col_num, value in enumerate(bancos_pivot.columns.values):
        ws_bancos.write(0, col_num, value, header_format)

    for row_num in range(1, len(bancos_pivot)+1):
        banco = bancos_pivot.loc[row_num-1, "BANCO"]
        entradas = bancos_pivot.loc[row_num-1, "ENTRADAS (R$)"]
        saidas = bancos_pivot.loc[row_num-1, "SAÍDAS (R$)"]
        saldo = bancos_pivot.loc[row_num-1, "Saldo (R$)"]

        ws_bancos.write(row_num, 0, banco)
        ws_bancos.write(row_num, 1, entradas, entrada_format)
        ws_bancos.write(row_num, 2, saidas, saida_format)
        ws_bancos.write(row_num, 3, saldo, saldo_format)
