def auto_col_width(ws, df, extra=4):
    for i, col in enumerate(df.columns):
        max_len = max(
            len(str(col)),
            df.iloc[:, i].astype(str).map(len).max() if len(df) > 0 else 0
        )
        ws.set_column(i, i, min(max_len + extra, 60))

def adicionar_titulo(ws, workbook, titulo, num_colunas):
    titulo_format = workbook.add_format({
        "bold": True, "font_size": 14, "font_name": "Calibri",
        "font_color": "white", "bg_color": "#1F3864",
        "align": "center", "valign": "vcenter", "border": 0
    })
    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, num_colunas - 1, titulo, titulo_format)


# ── Cores dos blocos do DRE ──────────────────────────────────────────────────
BLOCOS_DRE = {
    "RECEITAS OPERACIONAIS":  {"bg": "#2E75B6", "fg": "white"},
    "CUSTOS DIRETOS":         {"bg": "#C55A11", "fg": "white"},
    "LUCRO BRUTO":            {"bg": "#1a7a4a", "fg": "white"},
    "DESPESAS OPERACIONAIS":  {"bg": "#7030A0", "fg": "white"},
    "RESULTADO OPERACIONAL":  {"bg": "#1F3864", "fg": "white"},
    "RESULTADO FINANCEIRO":   {"bg": "#375623", "fg": "white"},
    "IMPOSTOS":               {"bg": "#833C00", "fg": "white"},
    "LUCRO LÍQUIDO":          {"bg": "#1a7a4a", "fg": "white"},
}

TOTAIS_INTERMEDIARIOS = {
    "RECEITAS OPERACIONAIS", "CUSTOS DIRETOS", "LUCRO BRUTO",
    "DESPESAS OPERACIONAIS", "RESULTADO OPERACIONAL",
    "RESULTADO FINANCEIRO", "IMPOSTOS", "LUCRO LÍQUIDO",
}


def aplicar_estilos(workbook, writer, dre_operacional, receita_financeira, societario,
                    emprestimos, transitorio, despesas_detalhadas, conciliacao,
                    bancos_pivot, mes_ano=""):

    moeda  = "R$ #,##0.00"
    fonte  = "Calibri"
    tam    = 10
    titulo_aba = f"Relatório Financeiro — {mes_ano}" if mes_ano else "Relatório Financeiro"

    def fmt(**kw):
        base = {"font_name": fonte, "font_size": tam}
        base.update(kw)
        return workbook.add_format(base)

    header_fmt    = fmt(bold=True, bg_color="#1F3864", font_color="white",
                        align="center", valign="vcenter", border=1, font_size=11)
    neg_fmt       = fmt(font_color="#C00000", num_format=moeda)
    pos_fmt       = fmt(font_color="#375623", bold=True, num_format=moeda)
    total_fmt     = fmt(bold=True, font_color="#1F3864", num_format=moeda, bg_color="#D9E1F2", border=1)
    total_txt_fmt = fmt(bold=True, font_color="#1F3864", bg_color="#D9E1F2", border=1)
    default_fmt   = fmt(num_format=moeda)
    zebra_fmt     = fmt(bg_color="#EEF2F7", num_format=moeda)
    zebra_txt_fmt = fmt(bg_color="#EEF2F7")
    plain_fmt     = fmt()

    # ── DRE_Operacional ──────────────────────────────────────────────────────
    ws_dre = writer.sheets["DRE_Operacional"]
    adicionar_titulo(ws_dre, workbook, titulo_aba, 2)
    ws_dre.set_row(1, 6)  # espaço após título
    ws_dre.set_column(0, 0, 40)
    ws_dre.set_column(1, 1, 20)

    excel_row = 2  # começa na linha 3 do Excel (0-indexed = 2)

    for i, (conta, valor) in enumerate(zip(dre_operacional["Conta"], dre_operacional["Valor (R$)"])):
        conta_strip = conta.strip()
        is_bloco    = conta_strip in BLOCOS_DRE
        is_subitem  = conta.startswith("  ")
        zebra       = (i % 2 == 0)

        if is_bloco:
            cores  = BLOCOS_DRE[conta_strip]
            b_fmt  = workbook.add_format({
                "font_name": fonte, "bold": True, "font_size": 11,
                "font_color": cores["fg"], "bg_color": cores["bg"],
                "valign": "vcenter",
                "bottom": 1 if conta_strip == "LUCRO LÍQUIDO" else 0,
                "top":    1 if conta_strip == "LUCRO LÍQUIDO" else 0,
            })
            bv_fmt = workbook.add_format({
                "font_name": fonte, "bold": True, "font_size": 11,
                "font_color": cores["fg"], "bg_color": cores["bg"],
                "num_format": moeda, "align": "right", "valign": "vcenter",
                "bottom": 1 if conta_strip == "LUCRO LÍQUIDO" else 0,
                "top":    1 if conta_strip == "LUCRO LÍQUIDO" else 0,
            })
            ws_dre.set_row(excel_row, 22)
            ws_dre.write(excel_row, 0, conta_strip, b_fmt)
            ws_dre.write(excel_row, 1, valor, bv_fmt)

        else:
            # subitem
            t_fmt = zebra_txt_fmt if zebra else plain_fmt
            if valor < 0:
                v_fmt = fmt(font_color="#C00000", num_format=moeda,
                            bg_color="#EEF2F7") if zebra else neg_fmt
            elif valor > 0:
                v_fmt = fmt(font_color="#375623", bold=False, num_format=moeda,
                            bg_color="#EEF2F7") if zebra else default_fmt
            else:
                v_fmt = zebra_fmt if zebra else default_fmt

            ws_dre.set_row(excel_row, 17)
            ws_dre.write(excel_row, 0, conta, t_fmt)
            ws_dre.write(excel_row, 1, valor, v_fmt)

        excel_row += 1

    # ── Tabelas separadas na mesma aba ───────────────────────────────────────
    sep_fmt = workbook.add_format({
        "font_name": fonte, "bold": True, "italic": True,
        "font_color": "#555555", "font_size": 9, "align": "center"
    })
    mini_header = workbook.add_format({
        "font_name": fonte, "bold": True, "font_size": 10,
        "font_color": "white", "bg_color": "#1F3864",
        "valign": "vcenter", "left": 0
    })
    mini_total_txt = workbook.add_format({
        "font_name": fonte, "bold": True, "font_size": 10,
        "font_color": "white", "bg_color": "#2E75B6"
    })
    mini_total_val = workbook.add_format({
        "font_name": fonte, "bold": True, "font_size": 10,
        "font_color": "white", "bg_color": "#2E75B6",
        "num_format": moeda, "align": "right"
    })

    def mini_headers_colors():
        return {
            "Receita Financeira":         "#375623",
            "Movimentos Societários":     "#1F3864",
            "Empréstimos/Financiamentos": "#833C00",
            "Valores Transitórios":       "#375623",
        }

    excel_row += 2
    ws_dre.merge_range(excel_row, 0, excel_row, 1,
                       "MOVIMENTOS FORA DO DRE", sep_fmt)
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
                v_f = (fmt(font_color="#C00000", num_format=moeda, bg_color="#EEF2F7")
                       if (valor < 0 and zebra) else
                       neg_fmt if valor < 0 else
                       zebra_fmt if zebra else default_fmt)
                ws_dre.set_row(excel_row, 17)
                ws_dre.write(excel_row, 0, desc, t_f)
                ws_dre.write(excel_row, 1, valor, v_f)
            excel_row += 1
        excel_row += 1  # espaço entre tabelas

    escrever_mini_tabela(receita_financeira, "RECEITA FINANCEIRA",       "Descrição", "#375623")
    escrever_mini_tabela(societario,         "MOVIMENTOS SOCIETÁRIOS",   "Descrição", "#1F3864")
    escrever_mini_tabela(emprestimos,        "EMPRÉSTIMOS/FINANCIAMENTOS","Descrição", "#833C00")
    escrever_mini_tabela(transitorio,        "VALORES TRANSITÓRIOS",     "Descrição", "#375623")

    # ── Despesas ─────────────────────────────────────────────────────────────
    ws_desp = writer.sheets["Despesas"]
    adicionar_titulo(ws_desp, workbook, titulo_aba, 5)

    neg_fmt2   = fmt(font_color="#C00000", num_format=moeda)
    zebra2     = fmt(bg_color="#EEF2F7")
    zebra_val2 = fmt(bg_color="#EEF2F7", num_format=moeda)
    plain_val2 = fmt(num_format=moeda)
    total_fmt2 = fmt(bold=True, bg_color="#D9E1F2", font_color="#1F3864", num_format=moeda, border=1)
    total_txt2 = fmt(bold=True, bg_color="#D9E1F2", font_color="#1F3864", border=1)

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
            neg_f = fmt(font_color="#C00000", num_format=moeda,
                        bg_color="#EEF2F7") if is_zebra else neg_fmt2
            val_f = zebra_val2 if is_zebra else plain_val2
            ws_desp.write(row_num, 0, str(row_data["DATA"]) if row_data["DATA"] else "", txt_f)
            ws_desp.write(row_num, 1, row_data["PAGO PARA"] or "", txt_f)
            ws_desp.write(row_num, 2, descricao, txt_f)
            ws_desp.write(row_num, 3, str(row_data["CLASSIFICAÇÃO"]).replace(r"^[A-Z]{2,3} \| ", "") or "", txt_f)
            ws_desp.write(row_num, 4, valor, neg_f if valor < 0 else val_f)

    ws_desp.set_column(0, 0, 14)
    ws_desp.set_column(1, 1, 45)
    ws_desp.set_column(2, 2, 55)
    ws_desp.set_column(3, 3, 25)
    ws_desp.set_column(4, 4, 18)

    # ── Receitas ─────────────────────────────────────────────────────────────
    ws_conc = writer.sheets["Receitas"]
    adicionar_titulo(ws_conc, workbook, titulo_aba, 5)

    total_fmt3 = fmt(bold=True, bg_color="#D9E1F2", font_color="#1F3864", num_format=moeda, border=1)
    total_txt3 = fmt(bold=True, bg_color="#D9E1F2", font_color="#1F3864", border=1)
    pos_fmt3   = fmt(font_color="#375623", num_format=moeda)
    zebra3     = fmt(bg_color="#EEF2F7")
    zebra_val3 = fmt(bg_color="#EEF2F7", num_format=moeda)
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

    # ── Bancos ───────────────────────────────────────────────────────────────
    ws_bancos = writer.sheets["Bancos"]
    adicionar_titulo(ws_bancos, workbook, titulo_aba, 6)

    entrada_fmt  = fmt(font_color="#375623", bold=True, num_format=moeda)
    saida_fmt    = fmt(font_color="#C00000", bold=True, num_format=moeda)
    saldo_fmt    = fmt(bold=True, num_format=moeda, bg_color="#D9E1F2", border=1)
    banco_fmt    = fmt(bold=True)
    zebra_b      = fmt(bg_color="#EEF2F7")
    zebra_e      = fmt(bg_color="#EEF2F7", font_color="#375623", bold=True, num_format=moeda)
    zebra_s_neg  = fmt(bg_color="#EEF2F7", font_color="#C00000", bold=True, num_format=moeda)

    for col_num, value in enumerate(bancos_pivot.columns.values):
        ws_bancos.write(2, col_num, value, header_fmt)
    ws_bancos.set_row(2, 22)

    for row_num in range(len(bancos_pivot)):
        r        = row_num + 3
        is_zebra = (r % 2 == 0)
        row_data = bancos_pivot.loc[row_num]
        b_fmt    = zebra_b if is_zebra else banco_fmt
        e_fmt    = zebra_e if is_zebra else entrada_fmt
        s_fmt    = zebra_s_neg if is_zebra else saida_fmt
        ws_bancos.write(r, 0, row_data["BANCO"],            b_fmt)
        ws_bancos.write(r, 1, row_data.get("Saldo Inicial (R$)", 0), saldo_fmt)
        ws_bancos.write(r, 2, row_data.get("ENTRADAS (R$)", 0),      e_fmt)
        ws_bancos.write(r, 3, row_data.get("SAÍDAS (R$)", 0),        s_fmt)
        ws_bancos.write(r, 4, row_data.get("Saldo do Mês (R$)", 0),  saldo_fmt)
        ws_bancos.write(r, 5, row_data.get("Saldo Final (R$)", 0),   saldo_fmt)

    ws_bancos.set_column(0, 0, 30)
    ws_bancos.set_column(1, 5, 20)

    # ── Ranking_Clientes e Centro_Custos (estrutura igual — retorna fmts) ────
    ws_rank = writer.sheets["Ranking_Clientes"]
    adicionar_titulo(ws_rank, workbook, titulo_aba, 4)
    pct_fmt   = fmt(num_format="0.0\"%\"")
    pct_zebra = fmt(bg_color="#EEF2F7", num_format="0.0\"%\"")
    pos_num   = fmt(bold=True, align="center", font_color="#1F3864")
    pos_zebra = fmt(bold=True, align="center", font_color="#1F3864", bg_color="#EEF2F7")
    for c, h in enumerate(["POS.", "CLIENTE", "RECEITA (R$)", "PARTICIPAÇÃO (%)"]):
        ws_rank.write(2, c, h, header_fmt)
    ws_rank.set_row(2, 22)
    ws_rank.set_column(0, 0, 6)
    ws_rank.set_column(1, 1, 45)
    ws_rank.set_column(2, 2, 18)
    ws_rank.set_column(3, 3, 18)

    ws_cc = writer.sheets["Centro_Custos"]
    adicionar_titulo(ws_cc, workbook, titulo_aba, 4)
    res_pos = fmt(font_color="#375623", bold=True, num_format=moeda)
    res_neg = fmt(font_color="#C00000", bold=True, num_format=moeda)
    res_pz  = fmt(bg_color="#EEF2F7", font_color="#375623", bold=True, num_format=moeda)
    res_nz  = fmt(bg_color="#EEF2F7", font_color="#C00000", bold=True, num_format=moeda)
    for c, h in enumerate(["CENTRO DE CUSTO", "RECEITA (R$)", "DESPESA (R$)", "RESULTADO (R$)"]):
        ws_cc.write(2, c, h, header_fmt)
    ws_cc.set_row(2, 22)
    ws_cc.set_column(0, 0, 28)
    ws_cc.set_column(1, 3, 18)

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
            "neg": neg_fmt, "zebra_neg": fmt(bg_color="#EEF2F7", font_color="#C00000", num_format=moeda),
            "res_pos": res_pos, "res_neg": res_neg,
            "res_pz": res_pz, "res_nz": res_nz,
            "total_txt": total_txt_fmt, "total_val": total_fmt,
            "header": header_fmt,
        }
    }
