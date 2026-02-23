import streamlit as st
import pandas as pd
from relatorios import gerar_relatorios
from estilos import aplicar_estilos
from graficos import criar_graficos

st.set_page_config(page_title="Relatório Financeiro", page_icon="💼", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        font-family: 'Arial', sans-serif;
    }
    .upload-box {
        border: 2px dashed #4F81BD;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Gerador de Relatórios Financeiros")
st.write("Bem-vinda! Faça upload do arquivo gerado pelo Astrea e receba o relatório completo em Excel.")

st.markdown('<div class="upload-box">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Selecione o arquivo (.xlsx)", type="xlsx")
st.markdown('</div>', unsafe_allow_html=True)

st.info("ℹ️ Envie apenas o relatório exportado do Astrea em formato Excel (.xlsx). Outros arquivos não serão aceitos.")

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
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
            label="📥 Baixar Relatório",
            data=open("Relatorio_Completo.xlsx", "rb"),
            file_name="Relatorio_Completo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error("❌ O arquivo enviado não está no formato esperado. Verifique se é o relatório do Astrea em .xlsx.")



