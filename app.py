import streamlit as st
import pandas as pd
from relatorios import gerar_relatorios
from estilos import aplicar_estilos
from graficos import criar_graficos

# ===== Configuração da página =====
st.set_page_config(page_title="Relatório Financeiro", page_icon="🗂️", layout="centered")

# ===== Estilos customizados =====
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; font-family: 'Segoe UI', sans-serif; }
    h1 { color: #2c3e50; text-align: center; }
    .upload-box {
        border: 2px dashed #4F81BD; padding: 30px; border-radius: 10px;
        text-align: center; background-color: #ffffff; transition: 0.3s;
    }
    .upload-box:hover { background-color: #f0f8ff; border-color: #2c3e50; }
    .stDownloadButton>button {
        background-color: #4F81BD; color: white; font-weight: bold;
        border-radius: 8px; padding: 10px 20px; transition: 0.3s;
    }
    .stDownloadButton>button:hover { background-color: #2c3e50; }
    </style>
""", unsafe_allow_html=True)

# ===== Banner inicial =====
st.markdown("""
    <div style="background-color:#4F81BD;padding:20px;border-radius:10px;margin-bottom:20px">
        <h1 style="color:white;text-align:center;">Relatório Financeiro</h1>
        <p style="color:white;text-align:center;">Faça o upload do relatório do Astrea e receba análises completas em Excel</p>
    </div>
""", unsafe_allow_html=True)

# ===== Upload de arquivo =====
st.markdown('<div class="upload-box">📂 Arraste e solte seu arquivo aqui</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Selecione o arquivo (.xlsx)", type="xlsx")
st.info("ℹ️ Envie apenas o relatório exportado do Astrea em formato Excel (.xlsx). Outros arquivos não serão aceitos.")

# ===== Mapa de meses =====
MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# ===== Processamento =====
if uploaded_file is not None:
    with st.spinner("⏳ Processando relatório..."):
        try:
            df = pd.read_excel(uploaded_file)

            # ===== VALIDAÇÃO DE CATEGORIAS =====
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

            # ===== EXTRAIR MÊS/ANO =====
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

            st.success("✅ Relatório gerado com sucesso!")
            st.download_button(
                label="Baixar Relatório",
                data=open(nome_arquivo, "rb"),
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Erro: {e}")

# ===== Rodapé =====
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888;'>Desenvolvido por Raquel • 2026</p>", unsafe_allow_html=True)
