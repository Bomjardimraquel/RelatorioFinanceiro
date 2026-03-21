import pandas as pd
from relatorios import gerar_relatorios
from estilos import aplicar_estilos
from graficos import criar_graficos

df = pd.read_excel("OUTUBRO.xlsx")
dre_operacional, destinacao, resumo, conciliacao, despesas_detalhadas, bancos_pivot = gerar_relatorios(df)

with pd.ExcelWriter("Relatorio_Completo.xlsx", engine="xlsxwriter") as writer:
    # exporta cada aba
    df.to_excel(writer, sheet_name="Movimentos", index=False)
    dre_operacional.to_excel(writer, sheet_name="DRE_Operacional", index=False)
    destinacao.to_excel(writer, sheet_name="DRE_Operacional", startrow=len(dre_operacional)+3, index=False)
    resumo.to_excel(writer, sheet_name="DRE_Operacional", startrow=len(dre_operacional)+len(destinacao)+6, index=False)
    conciliacao.to_excel(writer, sheet_name="Conciliacao", index=False)
    despesas_detalhadas.to_excel(writer, sheet_name="Despesas", index=False)
    bancos_pivot.to_excel(writer, sheet_name="Bancos", index=False)

    workbook  = writer.book
    worksheet = workbook.add_worksheet("Graficos")

    # aplicar estilos
    aplicar_estilos(workbook, writer, dre_operacional, destinacao, resumo, despesas_detalhadas, conciliacao, bancos_pivot)

    # criar gráficos
    criar_graficos(workbook, worksheet, df, despesas_detalhadas, dre_operacional, destinacao, resumo, writer)

