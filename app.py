import streamlit as st
import pandas as pd
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from relatorios import gerar_relatorios, gerar_ranking_clientes, gerar_centro_custos
from estilos import aplicar_estilos

st.set_page_config(page_title="Relatório Financeiro", page_icon="🗂️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #f4f6f9; }
    .banner {
        background: linear-gradient(135deg, #1F3864 0%, #2E75B6 100%);
        padding: 36px 24px; border-radius: 14px; margin-bottom: 28px;
        text-align: center; box-shadow: 0 4px 16px rgba(31,56,100,0.18);
    }
    .banner h1 { color: white; font-size: 2rem; font-weight: 700; margin: 0 0 8px 0; letter-spacing: -0.5px; }
    .banner p  { color: rgba(255,255,255,0.85); font-size: 1rem; margin: 0; }
    .instrucoes {
        background: white; border-radius: 12px; padding: 20px 24px;
        margin-bottom: 24px; border-left: 4px solid #2E75B6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .instrucoes h4 { color: #1F3864; margin: 0 0 12px 0; font-size: 0.95rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .instrucoes ol { margin: 0; padding-left: 20px; color: #444; font-size: 0.92rem; line-height: 1.8; }
    .resumo-card {
        background: white; border-radius: 12px; padding: 20px 24px;
        margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .resumo-card h4 { color: #1F3864; margin: 0 0 16px 0; font-size: 0.95rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-row { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    .metric { flex: 1; min-width: 140px; background: #f4f6f9; border-radius: 10px; padding: 14px 16px; text-align: center; }
    .metric .label { font-size: 0.78rem; color: #666; font-weight: 500; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 6px; }
    .metric .value { font-size: 1.15rem; font-weight: 700; }
    .metric .value.green { color: #1a7a4a; }
    .metric .value.red   { color: #c00000; }
    .metric .value.blue  { color: #1F3864; }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1F3864 0%, #2E75B6 100%);
        color: white; font-weight: 600; border-radius: 10px;
        padding: 12px 28px; font-size: 1rem; border: none; width: 100%;
    }
    footer { visibility: hidden; }
    .rodape { text-align: center; color: #aaa; font-size: 0.82rem; margin-top: 40px; padding-top: 16px; border-top: 1px solid #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

with open("config.yaml") as f:
    config = yaml.load(f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state.get("authentication_status") is False:
    st.error("Usuário ou senha incorretos.")
    st.stop()

if st.session_state.get("authentication_status") is None:
    st.warning("Por favor, insira seu usuário e senha.")
    st.stop()

with st.sidebar:
    st.write(f"Olá, **{st.session_state.get('name')}**!")
    authenticator.logout("Sair")

st.markdown("""
    <div class="banner">
        <h1>Relatório Financeiro</h1>
        <p>Envie o export do seu sistema e receba análises financeiras completas em Excel</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="instrucoes">
        <h4>Como usar</h4>
        <ol>
            <li>Acesse o <strong>seu sistema de gestão</strong> e exporte o relatório financeiro do mês em formato <strong>.xlsx</strong></li>
            <li>Certifique-se de que o arquivo contém apenas lançamentos do mês desejado</li>
            <li>Se houver provisão de repasse ainda não lançada, informe o valor abaixo</li>
            <li>Faça o upload e aguarde o processamento</li>
            <li>Baixe o relatório completo com DRE, Despesas, Conciliação e Bancos</li>
        </ol>
    </div>
""", unsafe_allow_html=True)

provisao_vinicius = st.number_input(
    "Provisão de repasse (R$) (deixe 0 se não houver)",
    min_value=0.0, value=0.0, step=100.0, format="%.2f"
)

uploaded_file = st.file_uploader("Selecione o arquivo exportado do seus sistema de gestão (.xlsx)", type="xlsx")
st.info("Envie apenas o relatório exportado do seu sistema de gestão em formato Excel (.xlsx). Outros arquivos não serão aceitos.")

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
                valor_ignorado = df[df["Categoria"].isin(cats_desconhecidas)]["Valor"].sum()
                st.warning(f"⚠️ Categorias não reconhecidas (serão ignoradas): **{', '.join(sorted(cats_desconhecidas))}**. "
                           f"Total de lançamentos ignorados: **{formatar_brl(abs(valor_ignorado))}**. "
                           f"Verifique se o nome foi alterado no sistema."
                          )
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
                    if is_total:
                        res_f = cf["total_val"]
                    elif res >= 0:
                        res_f = cf["res_pz"] if zebra else cf["res_pos"]
                    else:
                        res_f = cf["res_nz"] if zebra else cf["res_neg"]
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

            cor_resultado = "green" if resultado_operacional >= 0 else "red"

            st.markdown(f"""
                <div class="resumo-card">
                    <h4>Resumo — {mes_ano}</h4>
                    <div class="metric-row">
                        <div class="metric">
                            <div class="label">Receita Bruta</div>
                            <div class="value blue">{formatar_brl(receita_bruta)}</div>
                        </div>
                        <div class="metric">
                            <div class="label">Total Despesas</div>
                            <div class="value red">{formatar_brl(abs(total_despesas))}</div>
                        </div>
                        <div class="metric">
                            <div class="label">Resultado Operacional</div>
                            <div class="value {cor_resultado}">{formatar_brl(resultado_operacional)}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if provisao_vinicius:
                st.info(f"Provisão de repasse **{formatar_brl(provisao_vinicius)}** incluída no resultado.")

            st.download_button(
                label="Baixar Relatório Completo",
                data=open(nome_arquivo, "rb"),
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {e}")

st.markdown("<div class='rodape'>Desenvolvido por Raquel • 2026</div>", unsafe_allow_html=True)
