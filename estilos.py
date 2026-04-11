import re

def auto_col_width(ws, df, extra=4):
    """Ajusta largura das colunas baseado no conteúdo."""
    for i, col in enumerate(df.columns):
        max_len = max(
            len(str(col)),
            df.iloc[:, i].astype(str).map(len).max() if len(df) > 0 else 0
        )
        ws.set_column(i, i, min(max_len + extra, 60))

def adicionar_titulo(ws, workbook, titulo, num_colunas):
    """Adiciona uma linha de título mesclada no topo da aba."""
    titulo_format = workbook.add_format({
        "bold": True,
        "font_size": 14,
        "font_name": "Calibri",
        "font_color": "white",
        "bg_color": "#1F3864",
        "align": "center",
        "valign": "vcenter",
        "border": 0
    })
    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, num_colunas - 1, titulo, titulo_format)

def aplicar_estilos(workbook, writer, dre_operacional, destinacao, resumo, despesas_detalhadas, conciliacao, bancos_pivot, mes_ano=""):
    moeda     = "R$ #,##0.00"
    fonte     = "Calibri"
    tam       = 10
    titulo_aba = f"Relatório Financeiro — {mes_ano}" if mes_ano else "Relatório Financeiro"

    def fmt(**kw):
        base = {"font_name": fonte, "font_size": tam}
        base.update(kw)
        return workbook.add_format(base)

    header_fmt   = fmt(bold=True, bg_color="#1F3864", font_color="white", align="center", valign="vcenter", border=1, font_size=11)
    neg_fmt      = fmt(font_color="#C00000", num_format=moeda)
    pos_fmt      = fmt(font_color="#375623", bold=True, num_format=moeda)
    total_fmt    = fmt(bold=True, font_color="#1F3864", num_format=moeda, bg_color="#D9E1F2", border=1)
    total_txt_fmt= fmt(bold=True, font_color="#1F3864", bg_color="#D9E1F2", border=1)
    default_fmt  = fmt(num_format=moeda)
    zebra_fmt    = fmt(bg_color="#EEF2F7", num_format=moeda)
    zebra_txt_fmt= fmt(bg_color="#EEF2F7")
    plain_fmt    = fmt()

    # ===== DRE_Operacional =====
    ws_dre = writer.sheets["DRE_Operacional"]
    ws_dre.set_row(1, 30)
    adicionar_titulo(ws_dre, workbook, titulo_aba, 2)

    for col_num, value in enumerate(dre_operacional.columns.values):
        ws_dre.write(2, col_num, value, header_fmt)
    ws_dre.set_row(2, 22)

    for row_num, conta in enumerate(dre_operacional["Conta"], start=3):
        valor = dre_operacional.loc[row_num-3, "Valor (R$)"]
        is_zebra = (row_num % 2 == 0)
        v_fmt = zebra_fmt if is_zebra else default_fmt
        t_fmt = zebra_txt_fmt if is_zebra else plain_fmt

        if "Lucro Bruto" in conta or "Lucro" in conta or "Resultado" in conta or "Receita Líquida" in conta:
            ws_dre.write(row_num, 0, conta, total_txt_fmt)
            ws_dre.write(row_num, 1, valor, total_fmt)
        elif valor < 0:
            ws_dre.write(row_num, 0, conta, t_fmt)
            ws_dre.write(row_num, 1, valor, neg_fmt)
        elif valor > 0:
            ws_dre.write(row_num, 0, conta, t_fmt)
            ws_dre.write(row_num, 1, valor, pos_fmt)
        else:
            ws_dre.write(row_num, 0, conta, t_fmt)
            ws_dre.write(row_num, 1, valor, v_fmt)

    linha_dest = len(dre_operacional) + 5
    for col_num, value in enumerate(destinacao.columns.values):
        ws_dre.write(linha_dest, col_num, value, header_fmt)
    ws_dre.set_row(linha_dest, 22)

    col_desc = "Descrição" if "Descrição" in destinacao.columns else "Conta"
    for row_num, conta in enumerate(destinacao[col_desc], start=linha_dest+1):
        valor = destinacao.loc[row_num-(linha_dest+1), "Valor (R$)"]
        is_zebra = (row_num % 2 == 0)
        v_fmt = zebra_fmt if is_zebra else default_fmt
        t_fmt = zebra_txt_fmt if is_zebra else plain_fmt
        if "Total" in str(conta):
            ws_dre.write(row_num, 0, conta, total_txt_fmt)
            ws_dre.write(row_num, 1, valor, total_fmt)
        elif valor < 0:
            ws_dre.write(row_num, 0, conta, t_fmt)
            ws_dre.write(row_num, 1, valor, neg_fmt)
        else:
            ws_dre.write(row_num, 0, conta, t_fmt)
            ws_dre.write(row_num, 1, valor, v_fmt)

    ws_dre.set_column(0, 0, 40)
    ws_dre.set_column(1, 1, 20)

    # ===== DESPESAS =====
    ws_desp = writer.sheets["Despesas"]
    adicionar_titulo(ws_desp, workbook, titulo_aba, 5)

    header_fmt2  = fmt(bold=True, bg_color="#1F3864", font_color="white", align="center", valign="vcenter", border=1, font_size=11)
    total_fmt2   = fmt(bold=True, bg_color="#D9E1F2", font_color="#1F3864", num_format=moeda, border=1)
    total_txt2   = fmt(bold=True, bg_color="#D9E1F2", font_color="#1F3864", border=1)
    neg_fmt2     = fmt(font_color="#C00000", num_format=moeda)
    zebra2       = fmt(bg_color="#EEF2F7")
    zebra_val2   = fmt(bg_color="#EEF2F7", num_format=moeda)
    plain_val2   = fmt(num_format=moeda)

    for col_num, value in enumerate(despesas_detalhadas.columns.values):
        ws_desp.write(2, col_num, value, header_fmt2)
    ws_desp.set_row(2, 22)

    for row_num, descricao in enumerate(despesas_detalhadas["DESCRIÇÃO"], start=3):
        valor = despesas_detalhadas.loc[row_num-3, "VALORES"]
        is_zebra = (row_num % 2 == 0)
        if str(descricao).startswith("TOTAL"):
            for c in range(5):
                ws_desp.write(row_num, c, None, total_txt2)
            ws_desp.write(row_num, 2, descricao, total_txt2)
            ws_desp.write(row_num, 4, valor, total_fmt2)
        else:
            row_data = despesas_detalhadas.loc[row_num-3]
            txt_f = zebra2 if is_zebra else plain_fmt
            val_f = zebra_val2 if is_zebra else plain_val2
            neg_f = fmt(font_color="#C00000", num_format=moeda, bg_color="#EEF2F7") if is_zebra else neg_fmt2
            ws_desp.write(row_num, 0, str(row_data["DATA"]) if row_data["DATA"] else "", txt_f)
            ws_desp.write(row_num, 1, row_data["PAGO PARA"] or "", txt_f)
            ws_desp.write(row_num, 2, descricao, txt_f)
            ws_desp.write(row_num, 3, row_data["CLASSIFICAÇÃO"] or "", txt_f)
            ws_desp.write(row_num, 4, valor, neg_f if valor < 0 else val_f)

    ws_desp.set_column(0, 0, 14)
    ws_desp.set_column(1, 1, 45)
    ws_desp.set_column(2, 2, 55)
    ws_desp.set_column(3, 3, 25)
    ws_desp.set_column(4, 4, 18)

    # ===== RECEITAS =====
    ws_conc = writer.sheets["Receitas"]
    adicionar_titulo(ws_conc, workbook, titulo_aba, 5)

    total_fmt3  = fmt(bold=True, bg_color="#D9E1F2", font_color="#1F3864", num_format=moeda, border=1)
    total_txt3  = fmt(bold=True, bg_color="#D9E1F2", font_color="#1F3864", border=1)
    pos_fmt3    = fmt(font_color="#375623", num_format=moeda)
    zebra3      = fmt(bg_color="#EEF2F7")
    zebra_val3  = fmt(bg_color="#EEF2F7", num_format=moeda)
    plain_val3  = fmt(num_format=moeda)

    for col_num, value in enumerate(conciliacao.columns.values):
        ws_conc.write(2, col_num, value, header_fmt)
    ws_conc.set_row(2, 22)

    for row_num, descricao in enumerate(conciliacao["DESCRIÇÃO"], start=3):
        valor = conciliacao.loc[row_num-3, "VALORES"]
        is_zebra = (row_num % 2 == 0)
        txt_f = zebra3 if is_zebra else plain_fmt
        val_f = zebra_val3 if is_zebra else plain_val3
        if str(descricao).startswith("TOTAL"):
            for c in range(5):
                ws_conc.write(row_num, c, None, total_txt3)
            ws_conc.write(row_num, 2, descricao, total_txt3)
            ws_conc.write(row_num, 4, valor, total_fmt3)
        else:
            row_data = conciliacao.loc[row_num-3]
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

    # ===== BANCOS =====
    ws_bancos = writer.sheets["Bancos"]
    adicionar_titulo(ws_bancos, workbook, titulo_aba, 6)

    entrada_fmt = fmt(font_color="#375623", bold=True, num_format=moeda)
    saida_fmt   = fmt(font_color="#C00000", bold=True, num_format=moeda)
    saldo_fmt   = fmt(bold=True, num_format=moeda, bg_color="#D9E1F2", border=1)
    banco_fmt   = fmt(bold=True)
    zebra_b     = fmt(bg_color="#EEF2F7")
    zebra_e     = fmt(bg_color="#EEF2F7", font_color="#375623", bold=True, num_format=moeda)
    zebra_s_neg = fmt(bg_color="#EEF2F7", font_color="#C00000", bold=True, num_format=moeda)

    for col_num, value in enumerate(bancos_pivot.columns.values):
        ws_bancos.write(2, col_num, value, header_fmt)
    ws_bancos.set_row(2, 22)

    for row_num in range(1, len(bancos_pivot)+1):
        r = row_num + 2
        is_zebra = (r % 2 == 0)
        banco         = bancos_pivot.loc[row_num-1, "BANCO"]
        saldo_inicial = bancos_pivot.loc[row_num-1, "Saldo Inicial (R$)"]
        entradas      = bancos_pivot.loc[row_num-1, "ENTRADAS (R$)"]
        saidas        = bancos_pivot.loc[row_num-1, "SAÍDAS (R$)"]
        saldo_mes     = bancos_pivot.loc[row_num-1, "Saldo do Mês (R$)"]
        saldo_final   = bancos_pivot.loc[row_num-1, "Saldo Final (R$)"]

        b_fmt = zebra_b if is_zebra else banco_fmt
        e_fmt = zebra_e if is_zebra else entrada_fmt
        s_fmt = zebra_s_neg if is_zebra else saida_fmt

        ws_bancos.write(r, 0, banco, b_fmt)
        ws_bancos.write(r, 1, saldo_inicial, saldo_fmt)
        ws_bancos.write(r, 2, entradas, e_fmt)
        ws_bancos.write(r, 3, saidas, s_fmt)
        ws_bancos.write(r, 4, saldo_mes, saldo_fmt)
        ws_bancos.write(r, 5, saldo_final, saldo_fmt)

    ws_bancos.set_column(0, 0, 30)
    ws_bancos.set_column(1, 5, 20)

    # ===== RANKING_CLIENTES =====
    ws_rank = writer.sheets["Ranking_Clientes"]
    adicionar_titulo(ws_rank, workbook, titulo_aba, 4)

    pct_fmt     = fmt(num_format="0.0\"%\"")
    pct_zebra   = fmt(bg_color="#EEF2F7", num_format="0.0\"%\"")
    pos_num_fmt = fmt(bold=True, align="center", font_color="#1F3864")
    pos_zebra   = fmt(bold=True, align="center", font_color="#1F3864", bg_color="#EEF2F7")

    headers_rank = ["POS.", "CLIENTE", "RECEITA (R$)", "PARTICIPAÇÃO (%)"]
    for c, h in enumerate(headers_rank):
        ws_rank.write(2, c, h, header_fmt)
    ws_rank.set_row(2, 22)

    ws_rank.set_column(0, 0, 6)
    ws_rank.set_column(1, 1, 45)
    ws_rank.set_column(2, 2, 18)
    ws_rank.set_column(3, 3, 18)

    # ===== CENTRO_CUSTOS =====
    ws_cc = writer.sheets["Centro_Custos"]
    adicionar_titulo(ws_cc, workbook, titulo_aba, 4)

    res_pos  = fmt(font_color="#375623", bold=True, num_format=moeda)
    res_neg  = fmt(font_color="#C00000", bold=True, num_format=moeda)
    res_pz   = fmt(bg_color="#EEF2F7", font_color="#375623", bold=True, num_format=moeda)
    res_nz   = fmt(bg_color="#EEF2F7", font_color="#C00000", bold=True, num_format=moeda)

    headers_cc = ["CENTRO DE CUSTO", "RECEITA (R$)", "DESPESA (R$)", "RESULTADO (R$)"]
    for c, h in enumerate(headers_cc):
        ws_cc.write(2, c, h, header_fmt)
    ws_cc.set_row(2, 22)

    ws_cc.set_column(0, 0, 28)
    ws_cc.set_column(1, 3, 18)

    return {
        "rank_fmts": {
            "pos_num": pos_num_fmt, "pos_zebra": pos_zebra,
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
