def adicionar_titulo(ws, workbook, titulo, num_colunas):
    titulo_format = workbook.add_format({
        "bold": True, "font_size": 14, "font_name": "Calibri",
        "font_color": "white", "bg_color": "#0C2340",
        "align": "center", "valign": "vcenter", "border": 0
    })
    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, num_colunas - 1, titulo, titulo_format)


BLOCOS_DRE = {
    "RECEITAS OPERACIONAIS": {"bg": "#185FA5", "fg": "white"},
    "CUSTOS DIRETOS":        {"bg": "#C55A11", "fg": "white"},
    "LUCRO BRUTO":           {"bg": "#0C2340", "fg": "#C9A84C"},
    "DESPESAS OPERACIONAIS": {"bg": "#7030A0", "fg": "white"},
    "RESULTADO OPERACIONAL": {"bg": "#0C2340", "fg": "white"},
    "IMPOSTOS":              {"bg": "#833C00", "fg": "white"},
    "LUCRO LÍQUIDO":         {"bg": "#C9A84C", "fg": "#0C2340"},
}


def aplicar_estilos(workbook, writer, dre_operacional, receita_financeira, societario,
                    emprestimos, transitorio, despesas_detalhadas, conciliacao,
                    ranking, centros, mes_ano=""):

    moeda  = "R$ #,##0.00"
    fonte  = "Calibri"
    tam    = 10
    titulo_aba = f"Relatório Financeiro — {mes_ano}" if mes_ano else "Relatório Financeiro"

    def fmt(**kw):
        base = {"font_name": fonte, "font_size": tam}
        base.update(kw)
        return workbook.add_format(base)

    header_fmt    = fmt(bold=True, bg_color="#0C2340", font_color="white",
                        align="center", valign="vcenter", border=1, font_size=11)
    neg_fmt       = fmt(font_color="#C00000", num_format=moeda)
    total_fmt     = fmt(bold=True, font_color="#0C2340", num_format=moeda, bg_color="#E6F1FB", border=1)
    total_txt_fmt = fmt(bold=True, font_color="#0C2340", bg_color="#E6F1FB", border=1)
    default_fmt   = fmt(num_format=moeda)
    zebra_fmt     = fmt(bg_color="#F0F6FC", num_format=moeda)
    zebra_txt_fmt = fmt(bg_color="#F0F6FC")
    plain_fmt     = fmt()

    # ── DRE_Operacional ──────────────────────────────────────────────────────
    ws_dre = writer.sheets["DRE_Operacional"]
    adicionar_titulo(ws_dre, workbook, titulo_aba, 2)
    ws_dre.set_row(1, 6)
    ws_dre.set_column(0, 0, 40)
    ws_dre.set_column(1, 1, 20)

    excel_row = 2
    for i, (conta, valor) in enumerate(zip(dre_operacional["Conta"], dre_operacional["Valor (R$)"])):
        conta_strip = conta.strip()
        is_bloco    = conta_strip in BLOCOS_DRE
        zebra       = (i % 2 == 0)

        if is_bloco:
            cores = BLOCOS_DRE[conta_strip]
            b_fmt = workbook.add_format({
                "font_name": fonte, "bold": True, "font_size": 11,
                "font_color": cores["fg"], "bg_color": cores["bg"],
                "valign": "vcenter",
                "bottom": 2 if conta_strip == "LUCRO LÍQUIDO" else 0,
                "top":    2 if conta_strip == "LUCRO LÍQUIDO" else 0,
            })
            bv_fmt = workbook.add_format({
                "font_name": fonte, "bold": True, "font_size": 11,
                "font_color": cores["fg"], "bg_color": cores["bg"],
                "num_format": moeda, "align": "right", "valign": "vcenter",
                "bottom": 2 if conta_strip == "LUCRO LÍQUIDO" else 0,
                "top":    2 if conta_strip == "LUCRO LÍQUIDO" else 0,
            })
            ws_dre.set_row(excel_row, 22)
            ws_dre.write(excel_row, 0, conta_strip, b_fmt)
            ws_dre.write(excel_row, 1, valor, bv_fmt)
        else:
            t_fmt = zebra_txt_fmt if zebra else plain_fmt
            if valor < 0:
                v_fmt = fmt(font_color="#C00000", num_format=moeda, bg_color="#F0F6FC") if zebra else neg_fmt
            elif valor > 0:
                v_fmt = fmt(font_color="#185FA5", num_format=moeda, bg_color="#F0F6FC") if zebra else default_fmt
            else:
                v_fmt = zebra_fmt if zebra else default_fmt
            ws_dre.set_row(excel_row, 17)
            ws_dre.write(excel_row, 0, conta, t_fmt)
            ws_dre.write(excel_row, 1, valor, v_fmt)

        excel_row += 1

    # ── Tabelas separadas ────────────────────────────────────────────────────
    sep_fmt = workbook.add_format({
        "font_name": fonte, "bold": True, "italic": True,
        "font_color": "#555555", "font_size": 9, "align": "center"
    })

    excel_row += 2
    ws_dre.merge_range(excel_row, 0, excel_row, 1, "MOVIMENTOS FORA DO DRE", sep_fmt)
    excel_row += 2

    def escrever_mini_tabela(df_mini, titulo, col_desc, bg_header):
        nonlocal excel_row
        h_fmt = workbook.add_format({
            "font_name": fonte, "bold": True, "font_size": 10,
            "font_color": "white", "bg_color": bg_header, "valign": "vcenter"
        })
        t_txt = workbook.add_format({
            "font_name": fonte, "bold": True, "font_size": 10,
            "font_color": "white", "bg_color": bg_header
        })
        t_val = workbook.add_format({
            "font_name": fonte, "bold": True, "font_size": 10,
            "font_color": "white", "bg_color": bg_header,
            "num_format": moeda, "align": "right"
        })
        ws_dre.set_row(excel_row, 20)
        ws_dre.write(excel_row, 0, titulo, h_fmt)
        ws_dre.write(excel_row, 1, "", h_fmt)
        excel_row += 1

        for j, row_data in df_mini.iterrows():
            desc  = row_data[col_desc]
            valor = row_data["Valor (R$)"]
            zebra = (j % 2 == 0)
            is_total = str(desc).startswith("TOTAL") or str(desc).startswith("SALDO")
            if is_total:
                ws_dre.set_row(excel_row, 20)
                ws_dre.write(excel_row, 0, desc, t_txt)
                ws_dre.write(excel_row, 1, valor, t_val)
            else:
                t_f = zebra_txt_fmt if zebra else plain_fmt
                v_f = (fmt(font_color="#C00000", num_format=moeda, bg_color="#F0F6FC")
                       if (valor < 0 and zebra) else
                       neg_fmt if valor < 0 else
                       zebra_fmt if zebra else default_fmt)
                ws_dre.set_row(excel_row, 17)
                ws_dre.write(excel_row, 0, desc, t_f)
                ws_dre.write(excel_row, 1, valor, v_f)
            excel_row += 1
        excel_row += 1

    escrever_mini_tabela(receita_financeira, "RECEITA FINANCEIRA",        "Descrição", "#185FA5")
    escrever_mini_tabela(societario,         "MOVIMENTOS SOCIETÁRIOS",    "Descrição", "#0C2340")
    escrever_mini_tabela(emprestimos,        "EMPRÉSTIMOS/FINANCIAMENTOS","Descrição", "#833C00")
    escrever_mini_tabela(transitorio,        "VALORES TRANSITÓRIOS",      "Descrição", "#375623")

    # ── Despesas ─────────────────────────────────────────────────────────────
    ws_desp = writer.sheets["Despesas"]
    adicionar_titulo(ws_desp, workbook, titulo_aba, 5)
    neg_fmt2   = fmt(font_color="#C00000", num_format=moeda)
    zebra2     = fmt(bg_color="#F0F6FC")
    zebra_val2 = fmt(bg_color="#F0F6FC", num_format=moeda)
    plain_val2 = fmt(num_format=moeda)
    total_fmt2 = fmt(bold=True, bg_color="#E6F1FB", font_color="#0C2340", num_format=moeda, border=1)
    total_txt2 = fmt(bold=True, bg_color="#E6F1FB", font_color="#0C2340", border=1)

    for col_num, value in enumerate(despesas_detalhadas.columns.values):
        ws_desp.write(2, col_num, value, header_fmt)
    ws_desp.set_row(2, 22)

    for row_num, descricao in enumerate(despesas_detalhadas["DESCRIÇÃO"], start=3):
        valor    = despesas_detalhadas.loc[row_num - 3, "VALORES"]
        is_zebra = (row_num % 2 == 0)
        if str(descricao).startswith("TOTAL"):
            for c in range(5):
                ws_desp.write(row_num, c, None, total_txt2)
            ws_desp.write(row_num, 2, descricao, total_txt2)
            ws_desp.write(row_num, 4, valor, total_fmt2)
        else:
            row_data = despesas_detalhadas.loc[row_num - 3]
            txt_f = zebra2 if is_zebra else plain_fmt
            neg_f = fmt(font_color="#C00000", num_format=moeda, bg_color="#F0F6FC") if is_zebra else neg_fmt2
            val_f = zebra_val2 if is_zebra else plain_val2
            ws_desp.write(row_num, 0, str(row_data["DATA"]) if row_data["DATA"] else "", txt_f)
            ws_desp.write(row_num, 1, row_data["PAGO PARA"] or "", txt_f)
            ws_desp.write(row_num, 2, descricao, txt_f)
            ws_desp.write(row_num, 3, str(row_data["CLASSIFICAÇÃO"]) or "", txt_f)
            ws_desp.write(row_num, 4, valor, neg_f if valor < 0 else val_f)

    ws_desp.set_column(0, 0, 14)
    ws_desp.set_column(1, 1, 45)
    ws_desp.set_column(2, 2, 55)
    ws_desp.set_column(3, 3, 25)
    ws_desp.set_column(4, 4, 18)

    # ── Receitas ─────────────────────────────────────────────────────────────
    ws_conc = writer.sheets["Receitas"]
    adicionar_titulo(ws_conc, workbook, titulo_aba, 5)
    total_fmt3 = fmt(bold=True, bg_color="#E6F1FB", font_color="#0C2340", num_format=moeda, border=1)
    total_txt3 = fmt(bold=True, bg_color="#E6F1FB", font_color="#0C2340", border=1)
    pos_fmt3   = fmt(font_color="#185FA5", num_format=moeda)
    zebra3     = fmt(bg_color="#F0F6FC")
    zebra_val3 = fmt(bg_color="#F0F6FC", num_format=moeda)
    plain_val3 = fmt(num_format=moeda)

    for col_num, value in enumerate(conciliacao.columns.values):
        ws_conc.write(2, col_num, value, header_fmt)
    ws_conc.set_row(2, 22)

    for row_num, descricao in enumerate(conciliacao["DESCRIÇÃO"], start=3):
        valor    = conciliacao.loc[row_num - 3, "VALORES"]
        is_zebra = (row_num % 2 == 0)
        txt_f    = zebra3 if is_zebra else plain_fmt
        val_f    = zebra_val3 if is_zebra else plain_val3
        if str(descricao).startswith("TOTAL"):
            for c in range(5):
                ws_conc.write(row_num, c, None, total_txt3)
            ws_conc.write(row_num, 2, descricao, total_txt3)
            ws_conc.write(row_num, 4, valor, total_fmt3)
        else:
            row_data = conciliacao.loc[row_num - 3]
            ws_conc.write(row_num, 0, str(row_data["DATA"]) if row_data["DATA"] else "", txt_f)
            ws_conc.write(row_num, 1, row_data["CLIENTE"] or "", txt_f)
            ws_conc.write(row_num, 2, descricao, txt_f)
            ws_conc.write(row_num, 3, row_data["CLASSIFICAÇÃO"] or "", txt_f)
            ws_conc.write(row_num, 4, valor, pos_fmt3 if valor > 0 else val_f)

    ws_conc.set_column(0, 0, 14)
    ws_conc.set_column(1, 1, 45)
    ws_conc.set_column(2, 2, 55)
    ws_conc.set_column(3, 3, 25)
    ws_conc.set_column(4, 4, 18)

    # ── Ranking_Clientes ─────────────────────────────────────────────────────
    ws_rank = writer.sheets["Ranking_Clientes"]
    adicionar_titulo(ws_rank, workbook, titulo_aba, 4)
    pct_fmt   = fmt(num_format="0.0\"%\"")
    pct_zebra = fmt(bg_color="#F0F6FC", num_format="0.0\"%\"")
    pos_num   = fmt(bold=True, align="center", font_color="#0C2340")
    pos_zebra = fmt(bold=True, align="center", font_color="#0C2340", bg_color="#F0F6FC")
    for c, h in enumerate(["POS.", "CLIENTE", "RECEITA (R$)", "PARTICIPAÇÃO (%)"]):
        ws_rank.write(2, c, h, header_fmt)
    ws_rank.set_row(2, 22)
    ws_rank.set_column(0, 0, 6)
    ws_rank.set_column(1, 1, 45)
    ws_rank.set_column(2, 2, 18)
    ws_rank.set_column(3, 3, 18)

    # ── Centro_Custos ─────────────────────────────────────────────────────────
    ws_cc = writer.sheets["Centro_Custos"]
    adicionar_titulo(ws_cc, workbook, titulo_aba, 4)
    res_pos = fmt(font_color="#185FA5", bold=True, num_format=moeda)
    res_neg = fmt(font_color="#C00000", bold=True, num_format=moeda)
    res_pz  = fmt(bg_color="#F0F6FC", font_color="#185FA5", bold=True, num_format=moeda)
    res_nz  = fmt(bg_color="#F0F6FC", font_color="#C00000", bold=True, num_format=moeda)
    for c, h in enumerate(["CENTRO DE CUSTO", "RECEITA (R$)", "DESPESA (R$)", "RESULTADO (R$)"]):
        ws_cc.write(2, c, h, header_fmt)
    ws_cc.set_row(2, 22)
    ws_cc.set_column(0, 0, 28)
    ws_cc.set_column(1, 3, 18)

    # ── Dashboard (gráficos) ─────────────────────────────────────────────────
    ws_dash = writer.sheets["Dashboard"]
    ws_dash.set_tab_color("#0C2340")
    ws_dash.hide_gridlines(2)
    ws_dash.set_column(0, 0, 2)   # margem esquerda
    ws_dash.set_column(1, 8, 10)
    ws_dash.set_column(9, 9, 2)   # margem direita

    # Título do dashboard
    titulo_dash_fmt = workbook.add_format({
        "bold": True, "font_size": 16, "font_name": "Calibri",
        "font_color": "#0C2340", "align": "left", "valign": "vcenter"
    })
    sub_dash_fmt = workbook.add_format({
        "font_size": 10, "font_name": "Calibri",
        "font_color": "#888780", "align": "left"
    })
    ws_dash.set_row(1, 28)
    ws_dash.write(1, 1, f"Dashboard Financeiro — {mes_ano}", titulo_dash_fmt)
    ws_dash.write(2, 1, "Visão executiva gerada automaticamente", sub_dash_fmt)

    # ── Dados auxiliares para os gráficos (escritos em área fora da vista) ──
    # Usamos colunas K+ (col 10+) como área de dados oculta

    # 1. Dados DRE resumida (col 10-11)
    dre_labels = ["Receita Bruta", "Custos Diretos", "Desp. Operacionais", "Lucro Líquido"]
    dre_contas_map = {
        "Receita Bruta":       "RECEITAS OPERACIONAIS",
        "Custos Diretos":      "CUSTOS DIRETOS",
        "Desp. Operacionais":  "DESPESAS OPERACIONAIS",
        "Lucro Líquido":       "LUCRO LÍQUIDO",
    }
    dre_data_row_start = 1
    for i, label in enumerate(dre_labels):
        conta = dre_contas_map[label]
        val = dre_operacional.loc[dre_operacional["Conta"] == conta, "Valor (R$)"]
        valor = abs(val.values[0]) if len(val) > 0 else 0
        ws_dash.write(dre_data_row_start + i, 10, label)
        ws_dash.write(dre_data_row_start + i, 11, valor)

    # 2. Dados ranking top 8 (col 13-14)
    ranking_top = ranking.head(8).reset_index()
    rank_data_row_start = 1
    for i, row in ranking_top.iterrows():
        ws_dash.write(rank_data_row_start + i, 13, row["CLIENTE"])
        ws_dash.write(rank_data_row_start + i, 14, row["RECEITA (R$)"])

    # 3. Dados despesas operacionais top 8 (col 16-17)
    from relatorios import CATS_DESPESA_OP
    desp_data_row_start = 1
    desp_vals = []
    for cat in CATS_DESPESA_OP:
        from relatorios import soma as _soma
        # pega do despesas_detalhadas — linhas TOTAL
        mask = despesas_detalhadas["DESCRIÇÃO"] == f"TOTAL {cat.replace('DES | ', '')}"
        v = despesas_detalhadas.loc[mask, "VALORES"]
        val = abs(v.values[0]) if len(v) > 0 else 0
        if val > 0:
            desp_vals.append((cat.replace("DES | ", ""), val))
    desp_vals.sort(key=lambda x: x[1], reverse=True)
    for i, (label, val) in enumerate(desp_vals[:8]):
        ws_dash.write(desp_data_row_start + i, 16, label)
        ws_dash.write(desp_data_row_start + i, 17, val)

    # 4. Dados centro de custos (col 19-21, sem linha TOTAL)
    cc_data_row_start = 1
    centros_sem_total = centros[centros["CENTRO DE CUSTO"] != "TOTAL"].reset_index(drop=True)
    for i, row in centros_sem_total.iterrows():
        ws_dash.write(cc_data_row_start + i, 19, row["CENTRO DE CUSTO"])
        ws_dash.write(cc_data_row_start + i, 20, row["RECEITA (R$)"])
        ws_dash.write(cc_data_row_start + i, 21, abs(row["DESPESA (R$)"]))

    n_dre     = len(dre_labels)
    n_rank    = len(ranking_top)
    n_desp    = len(desp_vals[:8])
    n_cc      = len(centros_sem_total)

    # ── Gráfico 1: DRE resumida (barras verticais) ───────────────────────────
    chart_dre = workbook.add_chart({"type": "column"})
    chart_dre.add_series({
        "name":       "Valor",
        "categories": ["Dashboard", dre_data_row_start, 10, dre_data_row_start + n_dre - 1, 10],
        "values":     ["Dashboard", dre_data_row_start, 11, dre_data_row_start + n_dre - 1, 11],
        "fill":       {"colors": ["#185FA5", "#C55A11", "#7030A0", "#C9A84C"]},
        "data_labels": {"value": True, "num_format": "R$ #,##0", "font": {"size": 8, "color": "#0C2340"}},
        "gap": 80,
    })
    chart_dre.set_title({"name": "DRE Resumida", "name_font": {"size": 11, "bold": True, "color": "#0C2340"}})
    chart_dre.set_legend({"none": True})
    chart_dre.set_chartarea({"border": {"none": True}, "fill": {"color": "#F7F5F0"}})
    chart_dre.set_plotarea({"border": {"none": True}, "fill": {"color": "#F7F5F0"}})
    chart_dre.set_x_axis({"line": {"none": True}, "major_gridlines": {"visible": False},
                           "num_font": {"size": 8, "color": "#5F5E5A"}})
    chart_dre.set_y_axis({"line": {"none": True}, "major_gridlines": {"visible": True,
                           "line": {"color": "#E0DEDD", "dash_type": "dash"}},
                           "num_font": {"size": 8, "color": "#5F5E5A"},
                           "num_format": "R$ #,##0"})
    chart_dre.set_size({"width": 380, "height": 240})
    ws_dash.insert_chart("B5", chart_dre, {"x_offset": 5, "y_offset": 5})

    # ── Gráfico 2: Ranking de clientes (barras horizontais) ──────────────────
    chart_rank = workbook.add_chart({"type": "bar"})
    chart_rank.add_series({
        "name":       "Receita",
        "categories": ["Dashboard", rank_data_row_start, 13, rank_data_row_start + n_rank - 1, 13],
        "values":     ["Dashboard", rank_data_row_start, 14, rank_data_row_start + n_rank - 1, 14],
        "fill":       {"color": "#185FA5"},
        "data_labels": {"value": True, "num_format": "R$ #,##0", "font": {"size": 8, "color": "#0C2340"}},
        "gap": 60,
    })
    chart_rank.set_title({"name": "Ranking de Clientes", "name_font": {"size": 11, "bold": True, "color": "#0C2340"}})
    chart_rank.set_legend({"none": True})
    chart_rank.set_chartarea({"border": {"none": True}, "fill": {"color": "#F7F5F0"}})
    chart_rank.set_plotarea({"border": {"none": True}, "fill": {"color": "#F7F5F0"}})
    chart_rank.set_x_axis({"line": {"none": True}, "major_gridlines": {"visible": True,
                            "line": {"color": "#E0DEDD", "dash_type": "dash"}},
                            "num_font": {"size": 8}, "num_format": "R$ #,##0"})
    chart_rank.set_y_axis({"line": {"none": True}, "major_gridlines": {"visible": False},
                            "num_font": {"size": 8, "color": "#5F5E5A"}, "reverse": True})
    chart_rank.set_size({"width": 380, "height": 240})
    ws_dash.insert_chart("F5", chart_rank, {"x_offset": 5, "y_offset": 5})

    # ── Gráfico 3: Despesas operacionais (barras horizontais) ────────────────
    chart_desp = workbook.add_chart({"type": "bar"})
    chart_desp.add_series({
        "name":       "Despesa",
        "categories": ["Dashboard", desp_data_row_start, 16, desp_data_row_start + n_desp - 1, 16],
        "values":     ["Dashboard", desp_data_row_start, 17, desp_data_row_start + n_desp - 1, 17],
        "fill":       {"color": "#7030A0"},
        "data_labels": {"value": True, "num_format": "R$ #,##0", "font": {"size": 8, "color": "#0C2340"}},
        "gap": 60,
    })
    chart_desp.set_title({"name": "Despesas Operacionais", "name_font": {"size": 11, "bold": True, "color": "#0C2340"}})
    chart_desp.set_legend({"none": True})
    chart_desp.set_chartarea({"border": {"none": True}, "fill": {"color": "#F7F5F0"}})
    chart_desp.set_plotarea({"border": {"none": True}, "fill": {"color": "#F7F5F0"}})
    chart_desp.set_x_axis({"line": {"none": True}, "major_gridlines": {"visible": True,
                            "line": {"color": "#E0DEDD", "dash_type": "dash"}},
                            "num_font": {"size": 8}, "num_format": "R$ #,##0"})
    chart_desp.set_y_axis({"line": {"none": True}, "major_gridlines": {"visible": False},
                            "num_font": {"size": 8, "color": "#5F5E5A"}, "reverse": True})
    chart_desp.set_size({"width": 380, "height": 240})
    ws_dash.insert_chart("B20", chart_desp, {"x_offset": 5, "y_offset": 5})

    # ── Gráfico 4: Centro de custos (barras agrupadas) ────────────────────────
    chart_cc = workbook.add_chart({"type": "column"})
    chart_cc.add_series({
        "name":       "Receita",
        "categories": ["Dashboard", cc_data_row_start, 19, cc_data_row_start + n_cc - 1, 19],
        "values":     ["Dashboard", cc_data_row_start, 20, cc_data_row_start + n_cc - 1, 20],
        "fill":       {"color": "#185FA5"},
        "gap": 60,
    })
    chart_cc.add_series({
        "name":       "Despesa",
        "categories": ["Dashboard", cc_data_row_start, 19, cc_data_row_start + n_cc - 1, 19],
        "values":     ["Dashboard", cc_data_row_start, 21, cc_data_row_start + n_cc - 1, 21],
        "fill":       {"color": "#C9A84C"},
        "gap": 60,
    })
    chart_cc.set_title({"name": "Centro de Custos", "name_font": {"size": 11, "bold": True, "color": "#0C2340"}})
    chart_cc.set_legend({"font": {"size": 8, "color": "#5F5E5A"}})
    chart_cc.set_chartarea({"border": {"none": True}, "fill": {"color": "#F7F5F0"}})
    chart_cc.set_plotarea({"border": {"none": True}, "fill": {"color": "#F7F5F0"}})
    chart_cc.set_x_axis({"line": {"none": True}, "major_gridlines": {"visible": False},
                          "num_font": {"size": 8, "color": "#5F5E5A"}})
    chart_cc.set_y_axis({"line": {"none": True}, "major_gridlines": {"visible": True,
                          "line": {"color": "#E0DEDD", "dash_type": "dash"}},
                          "num_font": {"size": 8}, "num_format": "R$ #,##0"})
    chart_cc.set_size({"width": 380, "height": 240})
    ws_dash.insert_chart("F20", chart_cc, {"x_offset": 5, "y_offset": 5})

    return {
        "rank_fmts": {
            "pos_num": pos_num, "pos_zebra": pos_zebra,
            "plain": plain_fmt, "zebra_txt": zebra_txt_fmt,
            "moeda": default_fmt, "zebra_val": zebra_fmt,
            "pct": pct_fmt, "pct_zebra": pct_zebra,
            "total_txt": total_txt_fmt, "total_val": total_fmt,
            "header": header_fmt,
        },
        "cc_fmts": {
            "plain": plain_fmt, "zebra_txt": zebra_txt_fmt,
            "moeda": default_fmt, "zebra_val": zebra_fmt,
            "neg": neg_fmt, "zebra_neg": fmt(bg_color="#F0F6FC", font_color="#C00000", num_format=moeda),
            "res_pos": res_pos, "res_neg": res_neg,
            "res_pz": res_pz, "res_nz": res_nz,
            "total_txt": total_txt_fmt, "total_val": total_fmt,
            "header": header_fmt,
        }
    }