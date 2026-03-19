import streamlit as st
import pandas as pd
from relatorios import gerar_relatorios, gerar_ranking_clientes, gerar_centro_custos
from estilos import aplicar_estilos

st.set_page_config(page_title="Relatório Financeiro", page_icon="🗂️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main, .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        background: #0a0f1a !important;
    }

    section[data-testid="stSidebar"] { display: none; }

    .hero-nav {
        display: flex; align-items: center; justify-content: space-between;
        padding: 16px 48px; border-bottom: 0.5px solid rgba(255,255,255,0.08);
    }
    .hero-logo { display: flex; align-items: center; gap: 10px; }
    .hero-logo-icon {
        width: 28px; height: 28px; border-radius: 6px; background: #378ADD;
        display: flex; align-items: center; justify-content: center;
    }
    .hero-logo-text { color: white; font-size: 14px; font-weight: 500; }
    .hero-nav-links { display: flex; gap: 24px; }
    .hero-nav-links span { color: rgba(255,255,255,0.45); font-size: 12px; cursor: pointer; }
    .hero-cta {
        background: #378ADD; border: none; color: white; font-size: 12px;
        font-weight: 500; padding: 8px 16px; border-radius: 6px; cursor: pointer;
    }

    .hero-grid {
        display: grid; grid-template-columns: 1fr 1fr;
        min-height: 420px; padding: 0 48px;
    }
    .hero-left { padding: 56px 32px 48px 0; display: flex; flex-direction: column; justify-content: center; }
    .hero-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(55,138,221,0.15); border: 0.5px solid rgba(55,138,221,0.3);
        border-radius: 20px; padding: 4px 12px; margin-bottom: 24px; width: fit-content;
    }
    .hero-badge-dot { width: 6px; height: 6px; border-radius: 50%; background: #378ADD; }
    .hero-badge-text { font-size: 11px; color: #378ADD; font-weight: 500; }
    .hero-title { color: white; font-size: 36px; font-weight: 500; line-height: 1.2; margin: 0 0 16px; }
    .hero-title span { color: #378ADD; }
    .hero-subtitle { color: rgba(255,255,255,0.5); font-size: 14px; line-height: 1.7; margin: 0 0 32px; }
    .hero-buttons { display: flex; gap: 12px; }
    .btn-primary {
        background: #378ADD; border: none; color: white; font-size: 13px;
        font-weight: 500; padding: 12px 24px; border-radius: 8px; cursor: pointer;
    }
    .btn-secondary {
        background: transparent; border: 0.5px solid rgba(255,255,255,0.2);
        color: rgba(255,255,255,0.7); font-size: 13px; padding: 12px 24px;
        border-radius: 8px; cursor: pointer;
    }

    .hero-right { padding: 48px 0 48px 32px; display: flex; flex-direction: column; gap: 10px; justify-content: center; }
    .feature-card {
        background: rgba(255,255,255,0.04); border: 0.5px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 14px 18px; display: flex; align-items: center; gap: 14px;
    }
    .feature-card-bi {
        background: rgba(243,120,32,0.08); border: 0.5px solid rgba(243,120,32,0.25);
        border-radius: 12px; padding: 14px 18px; display: flex; align-items: center; gap: 14px;
    }
    .feature-icon {
        width: 34px; height: 34px; border-radius: 8px;
        display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .feature-title { color: white; font-size: 13px; font-weight: 500; margin: 0 0 2px; }
    .feature-title-bi { color: #F37820; font-size: 13px; font-weight: 500; margin: 0 0 2px; }
    .feature-desc { color: rgba(255,255,255,0.4); font-size: 11px; margin: 0; }
    .feature-desc-bi { color: rgba(243,120,32,0.6); font-size: 11px; margin: 0; }

    .bi-card {
        margin: 0 48px 32px;
        background: rgba(243,120,32,0.06); border: 0.5px solid rgba(243,120,32,0.2);
        border-radius: 12px; padding: 20px 24px;
        display: flex; align-items: center; gap: 20px;
    }
    .bi-card-icon {
        width: 44px; height: 44px; border-radius: 10px; background: rgba(243,120,32,0.15);
        display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .bi-card-title { color: #F37820; font-size: 13px; font-weight: 500; margin: 0 0 4px; }
    .bi-card-desc { color: rgba(255,255,255,0.4); font-size: 12px; margin: 0; line-height: 1.6; }
    .bi-badge {
        background: rgba(243,120,32,0.15); border: 0.5px solid rgba(243,120,32,0.3);
        border-radius: 20px; padding: 4px 12px; flex-shrink: 0;
    }
    .bi-badge span { font-size: 11px; color: #F37820; font-weight: 500; }

    .upload-section {
        margin: 0 48px 32px; padding: 32px;
        background: rgba(255,255,255,0.02); border: 0.5px solid rgba(255,255,255,0.08);
        border-radius: 16px;
    }
    .upload-title { color: white; font-size: 16px; font-weight: 500; margin: 0 0 24px; }

    .resumo-grid {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;
    }
    .resumo-metric {
        background: rgba(255,255,255,0.04); border-radius: 10px; padding: 16px;
    }
    .resumo-label { font-size: 10px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 6px; }
    .resumo-value { font-size: 18px; font-weight: 500; margin: 0; }
    .value-blue { color: #378ADD; }
    .value-red { color: #E24B4A; }
    .value-green { color: #1D9E75; }

    .download-btn {
        width: 100%; padding: 14px; border-radius: 8px; background: #378ADD;
        border: none; color: white; font-size: 14px; font-weight: 500; cursor: pointer;
    }

    .footer {
        padding: 16px 48px; border-top: 0.5px solid rgba(255,255,255,0.06);
        display: flex; justify-content: space-between; align-items: center;
    }
    .footer-text { color: rgba(255,255,255,0.25); font-size: 11px; margin: 0; }

    /* Streamlit overrides */
    .stFileUploader > div { background: rgba(255,255,255,0.03) !important; border: 1.5px dashed rgba(255,255,255,0.15) !important; border-radius: 10px !important; }
    .stFileUploader label { color: rgba(255,255,255,0.6) !important; }
    .stNumberInput label { color: rgba(255,255,255,0.6) !important; font-size: 13px !important; }
    .stNumberInput input { background: rgba(255,255,255,0.05) !important; border: 0.5px solid rgba(255,255,255,0.15) !important; color: white !important; border-radius: 8px !important; }
    .stSuccess, .stWarning, .stError, .stInfo { border-radius: 8px !important; }
    .stDownloadButton > button {
        width: 100% !important; padding: 14px !important; border-radius: 8px !important;
        background: #378ADD !important; border: none !important; color: white !important;
        font-size: 14px !important; font-weight: 500 !important;
    }
    footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="hero-nav">
        <div class="hero-logo">
            <div class="hero-logo-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                </svg>
            </div>
            <span class="hero-logo-text">Relatório Financeiro</span>
        </div>
        <div class="hero-nav-links">
            <span>Início</span>
            <span>Como funciona</span>
            <span>Contato</span>
        </div>
        <button class="hero-cta">Gerar relatório</button>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="hero-grid">
        <div class="hero-left">
            <div class="hero-badge">
                <div class="hero-badge-dot"></div>
                <span class="hero-badge-text">Compatível com arquivo Excel</span>
            </div>
            <h1 class="hero-title">Relatórios financeiros<br><span>em segundos</span></h1>
            <p class="hero-subtitle">Transforme seu export financeiro em DRE, ranking de clientes e análise por área — sem planilhas manuais.</p>
        </div>
        <div class="hero-right">
            <div class="feature-card">
                <div class="feature-icon" style="background: rgba(55,138,221,0.15);">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#378ADD" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
                </div>
                <div>
                    <p class="feature-title">DRE operacional</p>
                    <p class="feature-desc">Resultado do mês com todas as linhas</p>
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-icon" style="background: rgba(29,158,117,0.15);">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1D9E75" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                </div>
                <div>
                    <p class="feature-title">Ranking de clientes</p>
                    <p class="feature-desc">Receita por cliente com % de participação</p>
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-icon" style="background: rgba(186,117,23,0.15);">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#BA7517" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                </div>
                <div>
                    <p class="feature-title">Centro de custos</p>
                    <p class="feature-desc">Resultado por área do escritório</p>
                </div>
            </div>
            <div class="feature-card-bi">
                <div class="feature-icon" style="background: rgba(243,120,32,0.15);">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#F37820" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                </div>
                <div>
                    <p class="feature-title-bi">Dashboard Power BI</p>
                    <p class="feature-desc-bi">Visualizações interativas em tempo real</p>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="bi-card">
        <div class="bi-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F37820" stroke-width="2">
                <path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>
            </svg>
        </div>
        <div style="flex: 1;">
            <p class="bi-card-title">Integração com Power BI</p>
            <p class="bi-card-desc">O relatório gerado é compatível com Power BI. Conecte o arquivo ao seu dashboard e visualize DRE, ranking de clientes e evolução mensal de forma interativa — sem reconfigurar nada.</p>
        </div>
        <div class="bi-badge"><span>Power BI ready</span></div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="upload-section"><p class="upload-title">Gerar relatório</p>', unsafe_allow_html=True)

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

col1, col2 = st.columns([1, 2])
with col1:
    provisao_vinicius = st.number_input(
        "Provisão de repasse (R$) — deixe 0 se não houver",
        min_value=0.0, value=0.0, step=100.0, format="%.2f"
    )
with col2:
    uploaded_file = st.file_uploader(
        "Selecione o arquivo Excel exportado (.xlsx)",
        type="xlsx"
    )

st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    with st.spinner("⏳ Processando relatório..."):
        try:
            df = pd.read_excel(uploaded_file)

            mapa_categorias = {
                "Honorários", "Exito", "Contratado", "Partido", "Sucumbencial",
                "Compensação/liminar", "Impostos", "Despesa bancária", "Despesa Fixa",
                "Despesa Variável", "Repasse", "Participação em contrato",
                "Folha de pagamento", "Diversos", "Distribuição de lucros",
                "Participação Vinicius Fraga", "Transferência", "Saldo inicial"
            }
            cats_desconhecidas = set(df["Categoria"].dropna().unique()) - mapa_categorias
            if cats_desconhecidas:
                st.warning(f"⚠️ Categorias não reconhecidas (serão ignoradas): **{', '.join(sorted(cats_desconhecidas))}**")

            try:
                primeira_data = pd.to_datetime(df["Data"].dropna().iloc[0], dayfirst=True)
                mes_nome      = MESES[primeira_data.month]
                ano           = primeira_data.year
                mes_ano       = f"{mes_nome} {ano}"
                nome_arquivo  = f"Relatorio_{mes_nome}_{ano}.xlsx"
            except Exception:
                mes_ano      = ""
                nome_arquivo = "Relatorio_Completo.xlsx"

            dre_operacional, nao_contabil, resumo, conciliacao, despesas_detalhadas, bancos_pivot = gerar_relatorios(df, provisao_vinicius=provisao_vinicius)
            ranking = gerar_ranking_clientes(df)
            centros = gerar_centro_custos(df)

            with pd.ExcelWriter(nome_arquivo, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Movimentos", index=False)
                dre_operacional.to_excel(writer, sheet_name="DRE_Operacional", index=False, startrow=2)
                nao_contabil.to_excel(writer, sheet_name="DRE_Operacional", startrow=len(dre_operacional)+7, index=False)
                conciliacao.to_excel(writer, sheet_name="Conciliacao", index=False, startrow=2)
                despesas_detalhadas.to_excel(writer, sheet_name="Despesas", index=False, startrow=2)
                bancos_pivot.to_excel(writer, sheet_name="Bancos", index=False, startrow=2)
                ranking.reset_index().to_excel(writer, sheet_name="Ranking_Clientes", index=False, startrow=2)
                centros.to_excel(writer, sheet_name="Centro_Custos", index=False, startrow=2)
                workbook  = writer.book
                fmts = aplicar_estilos(workbook, writer, dre_operacional, nao_contabil, resumo, despesas_detalhadas, conciliacao, bancos_pivot, mes_ano=mes_ano)

                ws_rank = writer.sheets["Ranking_Clientes"]
                rf = fmts["rank_fmts"]
                for i, row in ranking.reset_index().iterrows():
                    r = i + 3
                    zebra = (r % 2 == 0)
                    ws_rank.write(r, 0, row["POS."], rf["pos_zebra"] if zebra else rf["pos_num"])
                    ws_rank.write(r, 1, row["CLIENTE"], rf["zebra_txt"] if zebra else rf["plain"])
                    ws_rank.write(r, 2, row["RECEITA (R$)"], rf["zebra_val"] if zebra else rf["moeda"])
                    ws_rank.write(r, 3, row["PARTICIPAÇÃO (%)"] / 100, rf["pct_zebra"] if zebra else rf["pct"])
                total_r = len(ranking) + 3
                ws_rank.write(total_r, 0, "", rf["total_txt"])
                ws_rank.write(total_r, 1, "TOTAL", rf["total_txt"])
                ws_rank.write(total_r, 2, ranking["RECEITA (R$)"].sum(), rf["total_val"])
                ws_rank.write(total_r, 3, 1.0, rf["pct"])

                ws_cc = writer.sheets["Centro_Custos"]
                cf = fmts["cc_fmts"]
                for i, row in centros.iterrows():
                    r = i + 3
                    zebra = (r % 2 == 0)
                    is_total = str(row["CENTRO DE CUSTO"]) == "TOTAL"
                    txt_f = cf["total_txt"] if is_total else (cf["zebra_txt"] if zebra else cf["plain"])
                    rec_f = cf["total_val"] if is_total else (cf["zebra_val"] if zebra else cf["moeda"])
                    dep_f = cf["total_val"] if is_total else (cf["zebra_neg"] if zebra else cf["neg"])
                    res   = row["RESULTADO (R$)"]
                    res_f = cf["total_val"] if is_total else (cf["res_pz"] if (zebra and res >= 0) else cf["res_pos"] if res >= 0 else cf["res_nz"] if zebra else cf["res_neg"])
                    ws_cc.write(r, 0, row["CENTRO DE CUSTO"], txt_f)
                    ws_cc.write(r, 1, row["RECEITA (R$)"], rec_f)
                    ws_cc.write(r, 2, row["DESPESA (R$)"], dep_f)
                    ws_cc.write(r, 3, res, res_f)

            st.success(f"Relatório de **{mes_ano}** gerado com sucesso!")

            receita_bruta         = dre_operacional.loc[dre_operacional["Conta"] == "Receita Bruta", "Valor (R$)"].values[0]
            resultado_operacional = dre_operacional.loc[dre_operacional["Conta"] == "Resultado Operacional", "Valor (R$)"].values[0]
            linhas_despesa        = ["(-) Impostos", "(-) Folha de Pagamento", "(-) Despesa Bancária", "(-) Despesas Fixas", "(-) Despesas Variáveis", "(-) Participação em Contratos", "(-) Repasse"]
            total_despesas        = dre_operacional[dre_operacional["Conta"].isin(linhas_despesa)]["Valor (R$)"].sum()
            if provisao_vinicius:
                total_despesas += -abs(provisao_vinicius)

            cor_resultado = "value-green" if resultado_operacional >= 0 else "value-red"

            st.markdown(f"""
                <div style="margin-top: 20px;">
                    <p style="font-size: 11px; font-weight: 500; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.6px; margin: 0 0 12px;">Resumo — {mes_ano}</p>
                    <div class="resumo-grid">
                        <div class="resumo-metric">
                            <p class="resumo-label">Receita Bruta</p>
                            <p class="resumo-value value-blue">{formatar_brl(receita_bruta)}</p>
                        </div>
                        <div class="resumo-metric">
                            <p class="resumo-label">Total Despesas</p>
                            <p class="resumo-value value-red">{formatar_brl(abs(total_despesas))}</p>
                        </div>
                        <div class="resumo-metric">
                            <p class="resumo-label">Resultado Operacional</p>
                            <p class="resumo-value {cor_resultado}">{formatar_brl(resultado_operacional)}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if provisao_vinicius:
                st.info(f"Provisão de repasse de **{formatar_brl(provisao_vinicius)}** incluída no resultado.")

            st.download_button(
                label="Baixar Relatório Completo",
                data=open(nome_arquivo, "rb"),
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {e}")

st.markdown("""
    <div class="footer">
        <p class="footer-text">© 2026 Raquel Bomjardim</p>
        <div style="display: flex; gap: 6px; align-items: center;">
            <div style="width: 6px; height: 6px; border-radius: 50%; background: #378ADD;"></div>
            <div style="width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,0.15);"></div>
            <div style="width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,0.15);"></div>
        </div>
    </div>
""", unsafe_allow_html=True)
