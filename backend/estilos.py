"""
estilos.py — Ledra Financial Reports
Paleta: #0C2340 (azul escuro) | #185FA5 (azul médio) | #C9A84C (dourado)
        #3B6D11 (verde) | #A32D2D (vermelho) | #F7F5F0 (off-white)
"""

# ── Paleta ────────────────────────────────────────────────────────────────────
AZUL_ESCURO  = "#0C2340"
AZUL_MEDIO   = "#185FA5"
AZUL_CLARO   = "#B5D4F4"
AZUL_BG      = "#E6F1FB"
DOURADO      = "#C9A84C"
DOURADO_BG   = "#FBF6E9"
VERDE        = "#3B6D11"
VERDE_BG     = "#EBF5E1"
VERMELHO     = "#A32D2D"
VERMELHO_BG  = "#FDEAEA"
ROXO         = "#5C2D91"
ROXO_BG      = "#F3EEFB"
MARROM       = "#7B3F00"
MARROM_BG    = "#FDF0E6"
OFF_WHITE    = "#F7F5F0"
CINZA_BORDA  = "#D3D1C7"
CINZA_TEXT   = "#5F5E5A"
BRANCO       = "#FFFFFF"

FONTE = "Calibri"
MOEDA = 'R$ #,##0.00'
MOEDA_NEG = 'R$ #,##0.00;[Red]-R$ #,##0.00'
PCT = '0.0"%"'


def _f(wb, **kw):
    base = {"font_name": FONTE, "font_size": 10}
    base.update(kw)
    return wb.add_format(base)


def aplicar_estilos(workbook, writer, dre_operacional, receita_financeira, societario,
                    emprestimos, transitorio, despesas_detalhadas, conciliacao,
                    ranking, centros, mes_ano=""):

    titulo_aba = f"Ledra — Relatório Financeiro {mes_ano}".strip(" —")

    # ═══════════════════════════════════════════════════════════════════════════
    # ABA: DRE_Operacional
    # ═══════════════════════════════════════════════════════════════════════════
    ws = writer.sheets["DRE_Operacional"]
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 36)   # Conta
    ws.set_column(1, 1, 18)   # Valor
    ws.set_column(2, 2, 3)    # espaço
    ws.set_column(3, 4, 20)   # tabela 1 direita
    ws.set_column(5, 5, 3)    # espaço
    ws.set_column(6, 7, 20)   # tabela 2 direita

    # Título
    titulo_fmt = _f(workbook, bold=True, font_size=13, font_color=BRANCO,
                    bg_color=AZUL_ESCURO, align="center", valign="vcenter", border=0)
    ws.set_row(0, 28)
    ws.merge_range(0, 0, 0, 7, titulo_aba, titulo_fmt)
    ws.set_row(1, 6)

    BLOCOS = {
        "RECEITAS OPERACIONAIS": (AZUL_MEDIO,   BRANCO,    14),
        "CUSTOS DIRETOS":        (MARROM,        BRANCO,    13),
        "LUCRO BRUTO":           (AZUL_ESCURO,   DOURADO,   13),
        "DESPESAS OPERACIONAIS": (ROXO,          BRANCO,    13),
        "RESULTADO OPERACIONAL": (AZUL_ESCURO,   BRANCO,    13),
        "IMPOSTOS":              (VERMELHO,      BRANCO,    12),
        "LUCRO LÍQUIDO":         (DOURADO,       AZUL_ESCURO, 14),
    }

    excel_row = 2
    for i, (conta, valor) in enumerate(zip(dre_operacional["Conta"], dre_operacional["Valor (R$)"])):
        conta_strip = conta.strip()
        is_bloco = conta_strip in BLOCOS

        if is_bloco:
            bg, fg, fs = BLOCOS[conta_strip]
            h = 24 if fs >= 14 else 21
            ws.set_row(excel_row, h)
            b_fmt = _f(workbook, bold=True, font_size=fs, font_color=fg, bg_color=bg,
                       valign="vcenter", left=2, left_color=CINZA_BORDA,
                       bottom=1, bottom_color=CINZA_BORDA)
            v_fmt = _f(workbook, bold=True, font_size=fs, font_color=fg, bg_color=bg,
                       num_format=MOEDA, align="right", valign="vcenter",
                       right=2, right_color=CINZA_BORDA,
                       bottom=1, bottom_color=CINZA_BORDA)
            ws.write(excel_row, 0, conta_strip, b_fmt)
            ws.write(excel_row, 1, valor, v_fmt)
        else:
            zebra = (i % 2 == 0)
            bg_z = OFF_WHITE if zebra else BRANCO
            t_fmt = _f(workbook, bg_color=bg_z, indent=1)
            if valor < 0:
                v_fmt = _f(workbook, bg_color=bg_z, font_color=VERMELHO, num_format=MOEDA)
            elif valor > 0:
                v_fmt = _f(workbook, bg_color=bg_z, font_color=AZUL_MEDIO, num_format=MOEDA)
            else:
                v_fmt = _f(workbook, bg_color=bg_z, font_color=CINZA_TEXT, num_format=MOEDA)
            ws.set_row(excel_row, 17)
            ws.write(excel_row, 0, conta, t_fmt)
            ws.write(excel_row, 1, valor, v_fmt)
        excel_row += 1

    # ── Tabelas laterais (colunas D/E e G/H) ──────────────────────────────────
    def mini_tabela_lateral(ws, workbook, df_mini, titulo, col_desc, bg_header, start_row, col_start):
        h_fmt = _f(workbook, bold=True, font_size=11, font_color=BRANCO, bg_color=bg_header,
                   valign="vcenter", border=1, border_color=bg_header)
        hv_fmt = _f(workbook, bold=True, font_size=11, font_color=BRANCO, bg_color=bg_header,
                    num_format=MOEDA, align="right", valign="vcenter",
                    border=1, border_color=bg_header)
        ws.set_row(start_row, 22)
        ws.write(start_row, col_start, titulo, h_fmt)
        ws.write(start_row, col_start + 1, "", h_fmt)
        r = start_row + 1
        for j, row_data in df_mini.iterrows():
            desc = row_data[col_desc]
            val  = row_data["Valor (R$)"]
            zebra = (j % 2 == 0)
            bg_z = OFF_WHITE if zebra else BRANCO
            is_total = str(desc).startswith("TOTAL") or str(desc).startswith("SALDO")
            if is_total:
                tt = _f(workbook, bold=True, bg_color=AZUL_BG, font_color=AZUL_ESCURO,
                        border=1, border_color=CINZA_BORDA)
                tv = _f(workbook, bold=True, bg_color=AZUL_BG, font_color=AZUL_ESCURO,
                        num_format=MOEDA, align="right", border=1, border_color=CINZA_BORDA)
                ws.write(r, col_start, desc, tt)
                ws.write(r, col_start + 1, val, tv)
            else:
                tf = _f(workbook, bg_color=bg_z, indent=1,
                        bottom=1, bottom_color=CINZA_BORDA)
                if val < 0:
                    vf = _f(workbook, bg_color=bg_z, font_color=VERMELHO, num_format=MOEDA,
                             bottom=1, bottom_color=CINZA_BORDA)
                elif val > 0:
                    vf = _f(workbook, bg_color=bg_z, font_color=AZUL_MEDIO, num_format=MOEDA,
                             bottom=1, bottom_color=CINZA_BORDA)
                else:
                    vf = _f(workbook, bg_color=bg_z, font_color=CINZA_TEXT, num_format=MOEDA,
                             bottom=1, bottom_color=CINZA_BORDA)
                ws.write(r, col_start, desc, tf)
                ws.write(r, col_start + 1, val, vf)
            r += 1
        return r + 1  # linha após a tabela

    r1 = mini_tabela_lateral(ws, workbook, receita_financeira, "RECEITA FINANCEIRA",
                              "Descrição", AZUL_MEDIO, 2, 3)
    r1 = mini_tabela_lateral(ws, workbook, emprestimos, "EMPRÉSTIMOS / FINANCIAMENTOS",
                              "Descrição", MARROM, r1, 3)
    mini_tabela_lateral(ws, workbook, societario, "MOVIMENTOS SOCIETÁRIOS",
                        "Descrição", AZUL_ESCURO, 2, 6)
    mini_tabela_lateral(ws, workbook, transitorio, "VALORES TRANSITÓRIOS",
                        "Descrição", VERDE, 2 + len(societario) + 3, 6)

    # ═══════════════════════════════════════════════════════════════════════════
    # ABA: Receitas
    # ═══════════════════════════════════════════════════════════════════════════
    ws_rec = writer.sheets["Receitas"]
    ws_rec.hide_gridlines(2)
    ws_rec.set_column(0, 0, 14)
    ws_rec.set_column(1, 1, 40)
    ws_rec.set_column(2, 2, 50)
    ws_rec.set_column(3, 3, 28)
    ws_rec.set_column(4, 4, 18)

    titulo_fmt2 = _f(workbook, bold=True, font_size=13, font_color=BRANCO,
                     bg_color=AZUL_MEDIO, align="center", valign="vcenter")
    ws_rec.set_row(0, 28)
    ws_rec.merge_range(0, 0, 0, 4, titulo_aba, titulo_fmt2)
    ws_rec.set_row(1, 6)

    hdr = _f(workbook, bold=True, font_size=10, font_color=BRANCO, bg_color=AZUL_ESCURO,
             align="center", valign="vcenter", border=1, border_color=AZUL_ESCURO)
    for c, h in enumerate(["DATA", "CLIENTE", "DESCRIÇÃO", "CLASSIFICAÇÃO", "VALORES"]):
        ws_rec.write(2, c, h, hdr)
    ws_rec.set_row(2, 22)

    # Tabela com filtro
    n_rec = len(conciliacao)
    if n_rec > 0:
        ws_rec.add_table(2, 0, 2 + n_rec, 4, {
            "name": "TabelaReceitas",
            "style": "Table Style Light 2",
            "columns": [
                {"header": "DATA"},
                {"header": "CLIENTE"},
                {"header": "DESCRIÇÃO"},
                {"header": "CLASSIFICAÇÃO"},
                {"header": "VALORES"},
            ]
        })

    for row_num, row_data in conciliacao.iterrows():
        r = row_num + 3
        zebra = (row_num % 2 == 0)
        bg_z = OFF_WHITE if zebra else BRANCO
        desc = row_data["DESCRIÇÃO"]
        val  = row_data["VALORES"]
        is_total = str(desc).startswith("TOTAL")

        if is_total:
            tt = _f(workbook, bold=True, bg_color=DOURADO_BG, font_color=AZUL_ESCURO,
                    top=1, top_color=DOURADO, bottom=2, bottom_color=DOURADO)
            tv = _f(workbook, bold=True, bg_color=DOURADO_BG, font_color=AZUL_ESCURO,
                    num_format=MOEDA, align="right",
                    top=1, top_color=DOURADO, bottom=2, bottom_color=DOURADO)
            for c in range(5):
                ws_rec.write(r, c, "", tt)
            ws_rec.write(r, 2, desc, tt)
            ws_rec.write(r, 4, val, tv)
        else:
            tf = _f(workbook, bg_color=bg_z)
            vf = _f(workbook, bg_color=bg_z, font_color=AZUL_MEDIO, num_format=MOEDA)
            ws_rec.write(r, 0, str(row_data["DATA"]) if row_data["DATA"] else "", tf)
            ws_rec.write(r, 1, row_data["CLIENTE"] or "", tf)
            ws_rec.write(r, 2, desc, tf)
            ws_rec.write(r, 3, row_data["CLASSIFICAÇÃO"] or "", tf)
            ws_rec.write(r, 4, val, vf)

    # ═══════════════════════════════════════════════════════════════════════════
    # ABA: Despesas
    # ═══════════════════════════════════════════════════════════════════════════
    ws_desp = writer.sheets["Despesas"]
    ws_desp.hide_gridlines(2)
    ws_desp.set_column(0, 0, 14)
    ws_desp.set_column(1, 1, 40)
    ws_desp.set_column(2, 2, 50)
    ws_desp.set_column(3, 3, 28)
    ws_desp.set_column(4, 4, 18)

    titulo_fmt3 = _f(workbook, bold=True, font_size=13, font_color=BRANCO,
                     bg_color=ROXO, align="center", valign="vcenter")
    ws_desp.set_row(0, 28)
    ws_desp.merge_range(0, 0, 0, 4, titulo_aba, titulo_fmt3)
    ws_desp.set_row(1, 6)

    for c, h in enumerate(["DATA", "PAGO PARA", "DESCRIÇÃO", "CLASSIFICAÇÃO", "VALORES"]):
        ws_desp.write(2, c, h, hdr)
    ws_desp.set_row(2, 22)

    n_desp = len(despesas_detalhadas)
    if n_desp > 0:
        ws_desp.add_table(2, 0, 2 + n_desp, 4, {
            "name": "TabelaDespesas",
            "style": "Table Style Light 6",
            "columns": [
                {"header": "DATA"},
                {"header": "PAGO PARA"},
                {"header": "DESCRIÇÃO"},
                {"header": "CLASSIFICAÇÃO"},
                {"header": "VALORES"},
            ]
        })

    for row_num, row_data in despesas_detalhadas.iterrows():
        r = row_num + 3
        zebra = (row_num % 2 == 0)
        bg_z = OFF_WHITE if zebra else BRANCO
        desc = row_data["DESCRIÇÃO"]
        val  = row_data["VALORES"]
        is_total = str(desc).startswith("TOTAL")

        if is_total:
            tt = _f(workbook, bold=True, bg_color=VERMELHO_BG, font_color=VERMELHO,
                    top=1, top_color=VERMELHO, bottom=2, bottom_color=VERMELHO)
            tv = _f(workbook, bold=True, bg_color=VERMELHO_BG, font_color=VERMELHO,
                    num_format=MOEDA, align="right",
                    top=1, top_color=VERMELHO, bottom=2, bottom_color=VERMELHO)
            for c in range(5):
                ws_desp.write(r, c, "", tt)
            ws_desp.write(r, 2, desc, tt)
            ws_desp.write(r, 4, val, tv)
        else:
            tf = _f(workbook, bg_color=bg_z)
            vf = _f(workbook, bg_color=bg_z, font_color=VERMELHO, num_format=MOEDA)
            ws_desp.write(r, 0, str(row_data["DATA"]) if row_data["DATA"] else "", tf)
            ws_desp.write(r, 1, row_data["PAGO PARA"] or "", tf)
            ws_desp.write(r, 2, desc, tf)
            ws_desp.write(r, 3, str(row_data["CLASSIFICAÇÃO"]) or "", tf)
            ws_desp.write(r, 4, val, vf)

    # ═══════════════════════════════════════════════════════════════════════════
    # ABA: Ranking_Clientes
    # ═══════════════════════════════════════════════════════════════════════════
    ws_rank = writer.sheets["Ranking_Clientes"]
    ws_rank.hide_gridlines(2)
    ws_rank.set_column(0, 0, 6)
    ws_rank.set_column(1, 1, 45)
    ws_rank.set_column(2, 2, 18)
    ws_rank.set_column(3, 3, 18)

    titulo_fmt4 = _f(workbook, bold=True, font_size=13, font_color=BRANCO,
                     bg_color=AZUL_ESCURO, align="center", valign="vcenter")
    ws_rank.set_row(0, 28)
    ws_rank.merge_range(0, 0, 0, 3, titulo_aba, titulo_fmt4)
    ws_rank.set_row(1, 6)

    for c, h in enumerate(["POS.", "CLIENTE", "RECEITA (R$)", "PARTICIPAÇÃO (%)"]):
        ws_rank.write(2, c, h, hdr)
    ws_rank.set_row(2, 22)

    n_rank = len(ranking)
    if n_rank > 0:
        ws_rank.add_table(2, 0, 2 + n_rank + 1, 3, {
            "name": "TabelaRanking",
            "style": "Table Style Light 2",
            "columns": [
                {"header": "POS."},
                {"header": "CLIENTE"},
                {"header": "RECEITA (R$)"},
                {"header": "PARTICIPAÇÃO (%)"},
            ]
        })

    rank_reset = ranking.reset_index()
    for i, row in rank_reset.iterrows():
        r = i + 3
        zebra = (i % 2 == 0)
        bg_z = OFF_WHITE if zebra else BRANCO
        pos_fmt = _f(workbook, bold=True, align="center", font_color=AZUL_ESCURO,
                     bg_color=bg_z, font_size=11)
        txt_fmt = _f(workbook, bg_color=bg_z)
        val_fmt = _f(workbook, bg_color=bg_z, font_color=AZUL_MEDIO, num_format=MOEDA)
        pct_fmt = _f(workbook, bg_color=bg_z, font_color=CINZA_TEXT, num_format=PCT)
        ws_rank.write(r, 0, row["POS."], pos_fmt)
        ws_rank.write(r, 1, row["CLIENTE"], txt_fmt)
        ws_rank.write(r, 2, row["RECEITA (R$)"], val_fmt)
        ws_rank.write(r, 3, row["PARTICIPAÇÃO (%)"] / 100, pct_fmt)

    total_r = n_rank + 3
    tt = _f(workbook, bold=True, bg_color=AZUL_BG, font_color=AZUL_ESCURO,
            top=2, top_color=AZUL_MEDIO)
    tv = _f(workbook, bold=True, bg_color=AZUL_BG, font_color=AZUL_ESCURO,
            num_format=MOEDA, top=2, top_color=AZUL_MEDIO)
    ws_rank.write(total_r, 0, "", tt)
    ws_rank.write(total_r, 1, "TOTAL", tt)
    ws_rank.write(total_r, 2, ranking["RECEITA (R$)"].sum(), tv)
    ws_rank.write(total_r, 3, 1.0, _f(workbook, bold=True, bg_color=AZUL_BG,
                                       font_color=AZUL_ESCURO, num_format=PCT,
                                       top=2, top_color=AZUL_MEDIO))

    # ═══════════════════════════════════════════════════════════════════════════
    # ABA: Centro_Custos
    # ═══════════════════════════════════════════════════════════════════════════
    ws_cc = writer.sheets["Centro_Custos"]
    ws_cc.hide_gridlines(2)
    ws_cc.set_column(0, 0, 28)
    ws_cc.set_column(1, 3, 18)

    titulo_fmt5 = _f(workbook, bold=True, font_size=13, font_color=BRANCO,
                     bg_color=VERDE, align="center", valign="vcenter")
    ws_cc.set_row(0, 28)
    ws_cc.merge_range(0, 0, 0, 3, titulo_aba, titulo_fmt5)
    ws_cc.set_row(1, 6)

    for c, h in enumerate(["CENTRO DE CUSTO", "RECEITA (R$)", "DESPESA (R$)", "RESULTADO (R$)"]):
        ws_cc.write(2, c, h, hdr)
    ws_cc.set_row(2, 22)

    n_cc = len(centros)
    if n_cc > 0:
        ws_cc.add_table(2, 0, 2 + n_cc, 3, {
            "name": "TabelaCentroCustos",
            "style": "Table Style Light 9",
            "columns": [
                {"header": "CENTRO DE CUSTO"},
                {"header": "RECEITA (R$)"},
                {"header": "DESPESA (R$)"},
                {"header": "RESULTADO (R$)"},
            ]
        })

    for i, row in centros.iterrows():
        r = i + 3
        zebra = (i % 2 == 0)
        bg_z = OFF_WHITE if zebra else BRANCO
        is_total = str(row["CENTRO DE CUSTO"]) == "TOTAL"
        res = row["RESULTADO (R$)"]

        if is_total:
            tf = _f(workbook, bold=True, bg_color=AZUL_BG, font_color=AZUL_ESCURO,
                    top=2, top_color=AZUL_MEDIO)
            rf = _f(workbook, bold=True, bg_color=AZUL_BG, font_color=AZUL_MEDIO,
                    num_format=MOEDA, top=2, top_color=AZUL_MEDIO)
            df2 = _f(workbook, bold=True, bg_color=AZUL_BG, font_color=VERMELHO,
                     num_format=MOEDA, top=2, top_color=AZUL_MEDIO)
            res_f = _f(workbook, bold=True, bg_color=AZUL_BG,
                       font_color=VERDE if res >= 0 else VERMELHO,
                       num_format=MOEDA, top=2, top_color=AZUL_MEDIO)
        else:
            tf  = _f(workbook, bg_color=bg_z)
            rf  = _f(workbook, bg_color=bg_z, font_color=AZUL_MEDIO, num_format=MOEDA)
            df2 = _f(workbook, bg_color=bg_z, font_color=VERMELHO, num_format=MOEDA)
            res_f = _f(workbook, bg_color=bg_z,
                       font_color=VERDE if res >= 0 else VERMELHO, num_format=MOEDA)

        ws_cc.write(r, 0, row["CENTRO DE CUSTO"], tf)
        ws_cc.write(r, 1, row["RECEITA (R$)"], rf)
        ws_cc.write(r, 2, row["DESPESA (R$)"], df2)
        ws_cc.write(r, 3, res, res_f)

    # ═══════════════════════════════════════════════════════════════════════════
    # ABA: Movimentos (filtro automático)
    # ═══════════════════════════════════════════════════════════════════════════
    ws_mov = writer.sheets["Movimentos"]
    ws_mov.hide_gridlines(2)
    ws_mov.set_row(0, 22)
    for c, w in enumerate([12, 25, 45, 28, 25, 35, 30, 15, 25, 15, 14, 10, 12]):
        ws_mov.set_column(c, c, w)
    ws_mov.autofilter(0, 0, 0, 12)

    # ═══════════════════════════════════════════════════════════════════════════
    # ABA: Dashboard
    # ═══════════════════════════════════════════════════════════════════════════
    ws_dash = writer.sheets["Dashboard"]
    ws_dash.set_tab_color(AZUL_ESCURO)
    ws_dash.hide_gridlines(2)
    ws_dash.set_zoom(90)

    # Layout: col A=margem(2), B-E=conteúdo esq(10 cada), F=gap(2), G-J=conteúdo dir(10 cada), K=margem(2)
    ws_dash.set_column(0, 0, 2)
    ws_dash.set_column(1, 4, 11)
    ws_dash.set_column(5, 5, 2)
    ws_dash.set_column(6, 9, 11)
    ws_dash.set_column(10, 10, 2)

    # ── Cabeçalho ─────────────────────────────────────────────────────────────
    cab_fmt = _f(workbook, bold=True, font_size=18, font_color=BRANCO,
                 bg_color=AZUL_ESCURO, valign="vcenter")
    sub_fmt = _f(workbook, font_size=10, font_color=AZUL_CLARO,
                 bg_color=AZUL_ESCURO, valign="vcenter")
    ws_dash.set_row(0, 36)
    ws_dash.set_row(1, 18)
    ws_dash.merge_range(0, 0, 0, 10, f"  Dashboard Financeiro — {mes_ano}", cab_fmt)
    ws_dash.merge_range(1, 0, 1, 10, "  Visão executiva gerada automaticamente pelo Ledra", sub_fmt)
    ws_dash.set_row(2, 8)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    receita_bruta  = dre_operacional.loc[dre_operacional["Conta"] == "RECEITAS OPERACIONAIS", "Valor (R$)"].values[0]
    lucro_liquido  = dre_operacional.loc[dre_operacional["Conta"] == "LUCRO LÍQUIDO", "Valor (R$)"].values[0]
    total_despesas = dre_operacional.loc[dre_operacional["Conta"] == "DESPESAS OPERACIONAIS", "Valor (R$)"].values[0]
    lucro_bruto    = dre_operacional.loc[dre_operacional["Conta"] == "LUCRO BRUTO", "Valor (R$)"].values[0]
    resultado_op   = dre_operacional.loc[dre_operacional["Conta"] == "RESULTADO OPERACIONAL", "Valor (R$)"].values[0]

    kpis = [
        ("RECEITA BRUTA",        receita_bruta,  AZUL_MEDIO,   AZUL_BG,     1, 4),
        ("DESPESAS OP.",         total_despesas, VERMELHO,     VERMELHO_BG, 1, 4),
        ("RESULTADO OP.",        resultado_op,   ROXO,         ROXO_BG,     6, 4),
        ("LUCRO LÍQUIDO",        lucro_liquido,  VERDE if lucro_liquido >= 0 else VERMELHO, VERDE_BG if lucro_liquido >= 0 else VERMELHO_BG, 6, 4),
    ]

    def kpi_card(row, col_s, col_e, label, valor, cor, bg):
        lbl_fmt = _f(workbook, font_size=9, font_color=cor, bg_color=bg,
                     bold=True, align="center",
                     top=3, top_color=cor,
                     left=1, left_color=CINZA_BORDA,
                     right=1, right_color=CINZA_BORDA)
        val_fmt = _f(workbook, font_size=16, font_color=cor, bg_color=bg,
                     bold=True, align="center", valign="vcenter",
                     num_format=MOEDA,
                     bottom=1, bottom_color=CINZA_BORDA,
                     left=1, left_color=CINZA_BORDA,
                     right=1, right_color=CINZA_BORDA)
        ws_dash.set_row(row, 18)
        ws_dash.set_row(row + 1, 28)
        ws_dash.merge_range(row, col_s, row, col_e, label, lbl_fmt)
        ws_dash.merge_range(row + 1, col_s, row + 1, col_e, valor, val_fmt)

    kpi_card(3, 1, 4, "RECEITA BRUTA",   receita_bruta,  AZUL_MEDIO, AZUL_BG)
    kpi_card(3, 6, 9, "DESPESAS OP.",    abs(total_despesas), VERMELHO, VERMELHO_BG)
    kpi_card(6, 1, 4, "RESULTADO OP.",   resultado_op,   ROXO if resultado_op >= 0 else VERMELHO,
             ROXO_BG if resultado_op >= 0 else VERMELHO_BG)
    kpi_card(6, 6, 9, "LUCRO LÍQUIDO",  lucro_liquido,
             VERDE if lucro_liquido >= 0 else VERMELHO,
             VERDE_BG if lucro_liquido >= 0 else VERMELHO_BG)
    ws_dash.set_row(9, 12)

    # ── Dados auxiliares para gráficos (colunas L+ ocultas) ───────────────────
    dre_labels = ["Receita Bruta", "Lucro Bruto", "Resultado Op.", "Lucro Líquido"]
    dre_vals   = [receita_bruta, lucro_bruto, resultado_op, lucro_liquido]
    for i, (l, v) in enumerate(zip(dre_labels, dre_vals)):
        ws_dash.write(i, 11, l)
        ws_dash.write(i, 12, abs(v))

    ranking_top = ranking.head(8).reset_index()
    for i, row in ranking_top.iterrows():
        ws_dash.write(i, 14, row["CLIENTE"][:22])
        ws_dash.write(i, 15, row["RECEITA (R$)"])

    desp_cats = dre_operacional[
        dre_operacional["Conta"].str.startswith("  ") &
        ~dre_operacional["Conta"].str.contains("Provisão", na=False)
    ].copy()
    desp_cats = desp_cats[desp_cats["Valor (R$)"] < 0].nsmallest(8, "Valor (R$)")
    for i, (_, row) in enumerate(desp_cats.iterrows()):
        ws_dash.write(i, 17, row["Conta"].strip()[:18])
        ws_dash.write(i, 18, abs(row["Valor (R$)"]))

    centros_graf = centros[centros["CENTRO DE CUSTO"] != "TOTAL"].reset_index(drop=True)
    for i, row in centros_graf.iterrows():
        ws_dash.write(i, 20, row["CENTRO DE CUSTO"])
        ws_dash.write(i, 21, row["RECEITA (R$)"])
        ws_dash.write(i, 22, abs(row["DESPESA (R$)"]))

    # Oculta colunas auxiliares
    ws_dash.set_column(11, 25, None, None, {"hidden": True})

    n_dre  = len(dre_labels)
    n_rank = len(ranking_top)
    n_desp = len(desp_cats)
    n_cc   = len(centros_graf)

    def base_chart(cor_area=OFF_WHITE):
        return {
            "chartarea": {"border": {"none": True}, "fill": {"color": cor_area}},
            "plotarea":  {"border": {"none": True}, "fill": {"color": BRANCO}},
        }

    # ── Gráfico 1: DRE ────────────────────────────────────────────────────────
    CORES_DRE = [AZUL_MEDIO, AZUL_ESCURO, ROXO, VERDE if lucro_liquido >= 0 else VERMELHO]
    chart1 = workbook.add_chart({"type": "column"})
    chart1.add_series({
        "name": "Valor",
        "categories": ["Dashboard", 0, 11, n_dre - 1, 11],
        "values":     ["Dashboard", 0, 12, n_dre - 1, 12],
        "fill":       {"colors": CORES_DRE},
        "gap": 70,
    })
    chart1.set_title({"name": "① DRE Resumida",
                      "name_font": {"size": 11, "bold": True, "color": AZUL_ESCURO}})
    chart1.set_legend({"none": True})
    chart1.set_x_axis({"line": {"none": True}, "major_gridlines": {"visible": False},
                        "num_font": {"size": 9, "color": CINZA_TEXT}})
    chart1.set_y_axis({"line": {"none": True},
                        "major_gridlines": {"visible": True, "line": {"color": "#E0DEDD", "dash_type": "dash"}},
                        "num_font": {"size": 9, "color": CINZA_TEXT}, "num_format": 'R$ #,##0'})
    chart1.set_chartarea({"border": {"none": True}, "fill": {"color": OFF_WHITE}})
    chart1.set_plotarea({"border": {"none": True}, "fill": {"color": BRANCO}})
    chart1.set_size({"width": 360, "height": 220})
    ws_dash.insert_chart("B11", chart1, {"x_offset": 4, "y_offset": 4})

    # ── Gráfico 2: Ranking ────────────────────────────────────────────────────
    chart2 = workbook.add_chart({"type": "bar"})
    chart2.add_series({
        "name": "Receita",
        "categories": ["Dashboard", 0, 14, n_rank - 1, 14],
        "values":     ["Dashboard", 0, 15, n_rank - 1, 15],
        "fill":       {"color": AZUL_MEDIO},
        "gap": 50,
    })
    chart2.set_title({"name": "② Ranking de Clientes",
                      "name_font": {"size": 11, "bold": True, "color": AZUL_ESCURO}})
    chart2.set_legend({"none": True})
    chart2.set_x_axis({"line": {"none": True},
                        "major_gridlines": {"visible": True, "line": {"color": "#E0DEDD", "dash_type": "dash"}},
                        "num_font": {"size": 9, "color": CINZA_TEXT}, "num_format": 'R$ #,##0'})
    chart2.set_y_axis({"line": {"none": True}, "major_gridlines": {"visible": False},
                        "num_font": {"size": 9, "color": CINZA_TEXT}, "reverse": True})
    chart2.set_chartarea({"border": {"none": True}, "fill": {"color": OFF_WHITE}})
    chart2.set_plotarea({"border": {"none": True}, "fill": {"color": BRANCO}})
    chart2.set_size({"width": 360, "height": 220})
    ws_dash.insert_chart("G11", chart2, {"x_offset": 4, "y_offset": 4})

    # ── Gráfico 3: Despesas ───────────────────────────────────────────────────
    chart3 = workbook.add_chart({"type": "bar"})
    chart3.add_series({
        "name": "Despesa",
        "categories": ["Dashboard", 0, 17, n_desp - 1, 17],
        "values":     ["Dashboard", 0, 18, n_desp - 1, 18],
        "fill":       {"color": ROXO},
        "gap": 50,
    })
    chart3.set_title({"name": "③ Despesas Operacionais",
                      "name_font": {"size": 11, "bold": True, "color": AZUL_ESCURO}})
    chart3.set_legend({"none": True})
    chart3.set_x_axis({"line": {"none": True},
                        "major_gridlines": {"visible": True, "line": {"color": "#E0DEDD", "dash_type": "dash"}},
                        "num_font": {"size": 9, "color": CINZA_TEXT}, "num_format": 'R$ #,##0'})
    chart3.set_y_axis({"line": {"none": True}, "major_gridlines": {"visible": False},
                        "num_font": {"size": 9, "color": CINZA_TEXT}, "reverse": True})
    chart3.set_chartarea({"border": {"none": True}, "fill": {"color": OFF_WHITE}})
    chart3.set_plotarea({"border": {"none": True}, "fill": {"color": BRANCO}})
    chart3.set_size({"width": 360, "height": 220})
    ws_dash.insert_chart("B27", chart3, {"x_offset": 4, "y_offset": 4})

    # ── Gráfico 4: Centro de Custos ───────────────────────────────────────────
    chart4 = workbook.add_chart({"type": "column"})
    chart4.add_series({
        "name": "Receita",
        "categories": ["Dashboard", 0, 20, n_cc - 1, 20],
        "values":     ["Dashboard", 0, 21, n_cc - 1, 21],
        "fill":       {"color": AZUL_MEDIO},
        "gap": 60,
    })
    chart4.add_series({
        "name": "Despesa",
        "categories": ["Dashboard", 0, 20, n_cc - 1, 20],
        "values":     ["Dashboard", 0, 22, n_cc - 1, 22],
        "fill":       {"color": DOURADO},
        "gap": 60,
    })
    chart4.set_title({"name": "④ Centro de Custos",
                      "name_font": {"size": 11, "bold": True, "color": AZUL_ESCURO}})
    chart4.set_legend({"font": {"size": 9, "color": CINZA_TEXT}})
    chart4.set_x_axis({"line": {"none": True}, "major_gridlines": {"visible": False},
                        "num_font": {"size": 9, "color": CINZA_TEXT}})
    chart4.set_y_axis({"line": {"none": True},
                        "major_gridlines": {"visible": True, "line": {"color": "#E0DEDD", "dash_type": "dash"}},
                        "num_font": {"size": 9, "color": CINZA_TEXT}, "num_format": 'R$ #,##0'})
    chart4.set_chartarea({"border": {"none": True}, "fill": {"color": OFF_WHITE}})
    chart4.set_plotarea({"border": {"none": True}, "fill": {"color": BRANCO}})
    chart4.set_size({"width": 360, "height": 220})
    ws_dash.insert_chart("G27", chart4, {"x_offset": 4, "y_offset": 4})

    # Retorna formatos para uso externo (Ranking e Centro de Custos já aplicados acima)
    plain = _f(workbook)
    moeda_fmt = _f(workbook, num_format=MOEDA)
    return {
        "rank_fmts": {
            "pos_num":   _f(workbook, bold=True, align="center", font_color=AZUL_ESCURO, font_size=11),
            "pos_zebra": _f(workbook, bold=True, align="center", font_color=AZUL_ESCURO, font_size=11, bg_color=OFF_WHITE),
            "plain":     plain,
            "zebra_txt": _f(workbook, bg_color=OFF_WHITE),
            "moeda":     moeda_fmt,
            "zebra_val": _f(workbook, bg_color=OFF_WHITE, num_format=MOEDA),
            "pct":       _f(workbook, num_format=PCT),
            "pct_zebra": _f(workbook, bg_color=OFF_WHITE, num_format=PCT),
            "total_txt": _f(workbook, bold=True, bg_color=AZUL_BG, font_color=AZUL_ESCURO,
                            top=2, top_color=AZUL_MEDIO),
            "total_val": _f(workbook, bold=True, bg_color=AZUL_BG, font_color=AZUL_ESCURO,
                            num_format=MOEDA, top=2, top_color=AZUL_MEDIO),
            "header":    _f(workbook, bold=True, font_color=BRANCO, bg_color=AZUL_ESCURO,
                            align="center", valign="vcenter", border=1),
        },
        "cc_fmts": {
            "plain":     plain,
            "zebra_txt": _f(workbook, bg_color=OFF_WHITE),
            "moeda":     moeda_fmt,
            "zebra_val": _f(workbook, bg_color=OFF_WHITE, num_format=MOEDA),
            "neg":       _f(workbook, font_color=VERMELHO, num_format=MOEDA),
            "zebra_neg": _f(workbook, bg_color=OFF_WHITE, font_color=VERMELHO, num_format=MOEDA),
            "res_pos":   _f(workbook, font_color=VERDE, bold=True, num_format=MOEDA),
            "res_neg":   _f(workbook, font_color=VERMELHO, bold=True, num_format=MOEDA),
            "res_pz":    _f(workbook, bg_color=OFF_WHITE, font_color=VERDE, bold=True, num_format=MOEDA),
            "res_nz":    _f(workbook, bg_color=OFF_WHITE, font_color=VERMELHO, bold=True, num_format=MOEDA),
            "total_txt": _f(workbook, bold=True, bg_color=AZUL_BG, font_color=AZUL_ESCURO,
                            top=2, top_color=AZUL_MEDIO),
            "total_val": _f(workbook, bold=True, bg_color=AZUL_BG, font_color=AZUL_ESCURO,
                            num_format=MOEDA, top=2, top_color=AZUL_MEDIO),
            "header":    _f(workbook, bold=True, font_color=BRANCO, bg_color=AZUL_ESCURO,
                            align="center", valign="vcenter", border=1),
        }
    }
