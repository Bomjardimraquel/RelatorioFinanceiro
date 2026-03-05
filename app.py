import streamlit as st
import pandas as pd
from relatorios import gerar_relatorios
from estilos import aplicar_estilos
from graficos import criar_graficos

st.set_page_config(page_title="Relatório Financeiro", page_icon="🗂️", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
        font-family: 'Segoe UI', sans-serif;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
    }
    .upload-box {
        border: 2px dashed #4F81BD;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        background-color: #ffffff;
        transition: 0.3s;
    }
    .upload-box:hover {
        background-color: #f0f8ff;
        border-color: #2c3e50;
    }
    .stDownloadButton>button {
        background-color: #4F81BD;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 20px;
        transition: 0.3s;
    }
    .stDownloadButton>button:hover {
        background-color: #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="background-color:#4F81BD;padding:20px;border-radius:10px;margin-bottom:20px">
        <h1 style="color:white;text-align:center;">Relatório Financeiro</h1>
        <p style="color:white;text-align:center;">Faça o upload do relatório do Astrea e receba análises completas em Excel</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="upload-box">📂 Arraste e solte seu arquivo aqui</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Selecione o arquivo (.xlsx)", type="xlsx")
st.info("ℹ️ Envie apenas o relatório exportado do Astrea em formato Excel (.xlsx). Outros arquivos não serão aceitos.")

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
                    f"⚠️ As seguintes categorias não foram reconhecidas e serão ignoradas no relatório: "
                    f"**{', '.join(sorted(categorias_desconhecidas))}**. "
                    f"Verifique se o arquivo está correto ou avise o suporte."
                )

            dre_operacional, destinacao, resumo, conciliacao, despesas_detalhadas, bancos_pivot = gerar_relatorios(df)

            with pd.ExcelWriter("Relatorio_Completo.xlsx", engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Movimentos", index=False)
                dre_operacional.to_excel(writer, sheet_name="DRE_Operacional", index=False)
                destinacao.to_excel(writer, sheet_name="DRE_Operacional", startrow=len(dre_operacional)+3, index=False)
                resumo.to_excel(writer, sheet_name="DRE_Operacional", startrow=len(dre_operacional)+len(destinacao)+6, index=False)
                conciliacao.to_excel(writer, sheet_name="Conciliacao", index=False)
                despesas_detalhadas.to_excel(writer, sheet_name="Despesas", index=False)
                bancos_pivot.to_excel(writer, sheet_name="Bancos", index=False)
                workbook  = writer.book
                worksheet = workbook.add_worksheet("Graficos")
                aplicar_estilos(workbook, writer, dre_operacional, destinacao, resumo, despesas_detalhadas, conciliacao, bancos_pivot)
                criar_graficos(workbook, worksheet, df, despesas_detalhadas, dre_operacional, destinacao, resumo, writer)

            st.success("✅ Relatório gerado com sucesso!")
            st.download_button(
                label="Baixar Relatório",
                data=open("Relatorio_Completo.xlsx", "rb"),
                file_name="Relatorio_Completo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error("❌ O arquivo enviado não está no formato esperado. Verifique se é o relatório do Astrea em .xlsx.")


st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888;'>Desenvolvido por Raquel • 2026</p>", unsafe_allow_html=True)
