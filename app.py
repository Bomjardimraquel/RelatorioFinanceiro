import streamlit as st
import pandas as pd
from relatorios import gerar_relatorios
from estilos import aplicar_estilos
from graficos import criar_graficos

st.set_page_config(page_title="Relatório Financeiro", page_icon="🗂️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main { background-color: #f4f6f9; }

    .banner {
        background: linear-gradient(135deg, #1F3864 0%, #2E75B6 100%);
        padding: 36px 24px;
        border-radius: 14px;
        margin-bottom: 28px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(31,56,100,0.18);
    }
    .banner h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 8px 0;
        letter-spacing: -0.5px;
    }
    .banner p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin: 0;
    }

    .instrucoes {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
        border-left: 4px solid #2E75B6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .instrucoes h4 {
        color: #1F3864;
        margin: 0 0 12px 0;
        font-size: 0.95rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .instrucoes ol {
        margin: 0;
        padding-left: 20px;
        color: #444;
        font-size: 0.92rem;
        line-height: 1.8;
    }

    .resumo-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .resumo-card h4 {
        color: #1F3864;
        margin: 0 0 16px 0;
        font-size: 0.95rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
    }
    .metric {
        flex: 1;
        min-width: 140px;
        background: #f4f6f9;
        border-radius: 10px;
        padding: 14px 16px;
        text-align: center;
    }
    .metric .label {
        font-size: 0.78rem;
        color: #666;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin-bottom: 6px;
    }
    .metric .value {
        font-size: 1.15rem;
        font-weight: 700;
    }
    .metric .value.green { color: #1a7a4a; }
    .metric .value.red   { color: #c00000; }
    .metric .value.blue  { color: #1F3864; }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #1F3864 0%, #2E75B6 100%);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 12px 28px;
        font-size: 1rem;
        border: none;
        width: 100%;
        transition: opacity 0.2s;
    }
    .stDownloadButton > button:hover { opacity: 0.88; }

    footer { visibility: hidden; }
    .rodape {
        text-align: center;
        color: #aaa;
        font-size: 0.82rem;
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px solid #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="banner">
        <h1>Relatório Financeiro</h1>
        <p>Faça o upload do relatório do Astrea e receba análises completas em Excel</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="instrucoes">
        <h4>Como usar</h4>
        <ol>
            <li>Acesse o <strong>Astrea</strong> e exporte o relatório financeiro do mês em formato <strong>.xlsx</strong></li>
            <li>Certifique-se de que o arquivo contém apenas lançamentos do mês desejado</li>
            <li>Faça o upload abaixo e aguarde o processamento</li>
            <li>Baixe o relatório completo com DRE, Despesas, Conciliação e Bancos</li>
        </ol>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Selecione o arquivo exportado do Astrea (.xlsx)", type="xlsx", label_visibility="visible")
st.info("Envie apenas o relatório exportado do Astrea em formato Excel (.xlsx). Outros arquivos não serão aceitos.")

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
            categorias_no_arquivo = set(df["Categoria"].dropna().unique())
            categorias_desconhecidas = categorias_no_arquivo - mapa_categorias
            if categorias_desconhecidas:
                st.warning(
                    f"⚠️ Categorias não reconhecidas (serão ignoradas): "
                    f"**{', '.join(sorted(categorias_desconhecidas))}**"
                )

            try:
                primeira_data = pd.to_datetime(df["Data"].dropna().iloc[0], dayfirst=True)
                mes_nome = MESES[primeira_data.month]
                ano = primeira_data.year
                mes_ano = f"{mes_nome} {ano}"
                nome_arquivo = f"Relatorio_{mes_nome}_{ano}.xlsx"
            except Exception:
                mes_ano = ""
                nome_arquivo = "Relatorio_Completo.xlsx"

            dre_operacional, destinacao, resumo, conciliacao, despesas_detalhadas, bancos_pivot = gerar_relatorios(df)

            with pd.ExcelWriter(nome_arquivo, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Movimentos", index=False)
                dre_operacional.to_excel(writer, sheet_name="DRE_Operacional", index=False, startrow=2)
                destinacao.to_excel(writer, sheet_name="DRE_Operacional", startrow=len(dre_operacional)+7, index=False)
                resumo.to_excel(writer, sheet_name="DRE_Operacional", startrow=len(dre_operacional)+len(destinacao)+10, index=False)
                conciliacao.to_excel(writer, sheet_name="Conciliacao", index=False, startrow=2)
                despesas_detalhadas.to_excel(writer, sheet_name="Despesas", index=False, startrow=2)
                bancos_pivot.to_excel(writer, sheet_name="Bancos", index=False, startrow=2)
                workbook = writer.book
                worksheet = workbook.add_worksheet("Graficos")
                aplicar_estilos(workbook, writer, dre_operacional, destinacao, resumo, despesas_detalhadas, conciliacao, bancos_pivot, mes_ano=mes_ano)
                criar_graficos(workbook, worksheet, df, despesas_detalhadas, dre_operacional, destinacao, resumo, writer)

            st.success(f"Relatório de **{mes_ano}** gerado com sucesso!")

            receita_bruta         = dre_operacional.loc[dre_operacional["Conta"] == "Receita Bruta", "Valor (R$)"].values[0]
            resultado_operacional = dre_operacional.loc[dre_operacional["Conta"] == "Resultado Operacional", "Valor (R$)"].values[0]
            lucro_liquido         = resumo.loc[resumo["Indicador"] == "Lucro Líquido após Destinação", "Valor (R$)"].values[0]
            linhas_despesa = ["(-) Impostos e Deduções", "(-) Custos/Folha de Pagamento", "(-) Despesas Fixas", "(-) Despesas Variáveis", "Repasse"]
            total_despesas = dre_operacional[dre_operacional["Conta"].isin(linhas_despesa)]["Valor (R$)"].sum()

            cor_resultado = "green" if resultado_operacional >= 0 else "red"
            cor_liquido   = "green" if lucro_liquido >= 0 else "red"

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
                        <div class="metric">
                            <div class="label">Lucro Líquido</div>
                            <div class="value {cor_liquido}">{formatar_brl(lucro_liquido)}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="Baixar Relatório Completo",
                data=open(nome_arquivo, "rb"),
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {e}")

st.markdown("<div class='rodape'>Desenvolvido por Raquel • 2026</div>", unsafe_allow_html=True)
