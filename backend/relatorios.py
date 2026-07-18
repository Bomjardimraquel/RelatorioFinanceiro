import json
import pandas as pd
from pathlib import Path
from funcoes import soma, soma_entradas

# ── Categorias base (hardcoded) ───────────────────────────────────────────────

CATS_RECEITA = [
    "REC | Honorário Avulso",
    "REC | Honorário Contratado",
    "REC | Honorário Partido",
    "REC | Honorário Sucumbencial",
    "REC | Honorário Êxito",
    "REC | Honorário Compensação/liminar",
    "REC | Reembolso cliente",
]

CATS_CUSTO_DIRETO = [
    "CUS | Parceiro Jurídico",
    "CUS | Participação contrato",
    "CUS | Diligencia",
    "CUS | Participação Vinicius Fraga",
    "Despesa do cliente",
]

CATS_DESPESA_OP = [
    "DES | Aluguel",
    "DES | Assinaturas Jurídicas",
    "DES | Bancaria",
    "DES | Certificado digital",
    "DES | Condomínio",
    "DES | Consultoria",
    "DES | Contabilidade",
    "DES | Copa/Cozinha",
    "DES | Cursos/Especializações",
    "DES | Estagiários",
    "DES | Energia",
    "DES | Folha Pagamento",
    "DES | Hospedagem/Site",
    "DES | Internet",
    "DES | Limpeza",
    "DES | Manutenção",
    "DES | Marketing",
    "DES | Material Escritório",
    "DES | Não Classificado",
    "DES | OAB/Anuidade",
    "DES | Pró-Labore",
    "DES | Segurança",
    "DES | Software Jurídico",
    "DES | Telefonia",
    "DES | Token/OAB",
    "DES | Tráfego pago",
    "DES | Uber/Combustível",
    "DES | Despesa Bancária",
    "DES | Bancária",
]

CATS_RESULTADO_FIN = []

CATS_IMPOSTO = [
    "IMP | Simples Nacional",
    "IMP | IPTU",
    "IMP | INSS",
]

CATS_RECEITA_FIN = [
    "REC | Receita Financeira",
    "REC | Venda ativo",
]

CATS_SOCIETARIO = [
    "SOC | Distribuição Lucros",
    "SOC | Aporte Sócio",
]

CATS_EMPRESTIMO = [
    "FIN | Empréstimo Bancário",
    "FIN | Empréstimo bancário",
    "FIN | Pagamento Empréstimo",
    "FIN | Consórcio Principal",
    "FIN | Juros Bancários",
    "FIN | Juros bancários",
]

CATS_TRANSITORIO = [
    "REP | Valores transitórios",
    "REP | Repasse Cliente",
]

# ── Categorias via banco de dados ─────────────────────────────────────────────

CATS_FILE = Path(__file__).parent / "categorias.json"

def _carregar_cats():
    """Carrega todas as categorias do banco. Fallback para hardcoded."""
    try:
        import os
        if os.environ.get("DATABASE_URL"):
            import psycopg2
            conn = psycopg2.connect(os.environ["DATABASE_URL"])
            with conn.cursor() as cur:
                cur.execute("SELECT grupo, nome FROM categorias ORDER BY id")
                rows = cur.fetchall()
            conn.close()
            result = {}
            for grupo, nome in rows:
                result.setdefault(grupo, []).append(nome)
            return result
    except Exception:
        pass
    # Fallback: listas vazias (sem banco disponível)
    return {
        "CATS_RECEITA":      [],
        "CATS_CUSTO_DIRETO": [],
        "CATS_DESPESA_OP":   [],
        "CATS_IMPOSTO":      [],
        "CATS_RECEITA_FIN":  [],
        "CATS_SOCIETARIO":   [],
        "CATS_EMPRESTIMO":   [],
        "CATS_TRANSITORIO":  [],
    }

def get_cats_receita():
    return _carregar_cats().get("CATS_RECEITA", CATS_RECEITA)

def get_cats_custo_direto():
    return _carregar_cats().get("CATS_CUSTO_DIRETO", CATS_CUSTO_DIRETO)

def get_cats_despesa_op():
    return _carregar_cats().get("CATS_DESPESA_OP", CATS_DESPESA_OP)

def get_cats_imposto():
    return _carregar_cats().get("CATS_IMPOSTO", CATS_IMPOSTO)

def get_cats_receita_fin():
    return _carregar_cats().get("CATS_RECEITA_FIN", CATS_RECEITA_FIN)

def get_cats_societario():
    return _carregar_cats().get("CATS_SOCIETARIO", CATS_SOCIETARIO)

def get_cats_emprestimo():
    return _carregar_cats().get("CATS_EMPRESTIMO", CATS_EMPRESTIMO)

def get_cats_transitorio():
    return _carregar_cats().get("CATS_TRANSITORIO", CATS_TRANSITORIO)


def get_todas_categorias_conhecidas():
    cats = _carregar_cats()
    todas = []
    for lista in cats.values():
        todas.extend(lista)
    todas += ["Transferência", "Despesa do cliente", "Saldo inicial"]
    return list(set(todas))


def gerar_relatorios(df, provisao_vinicius=0.0):

    # Carrega listas do banco
    cats_receita      = get_cats_receita()
    cats_custo_direto = get_cats_custo_direto()
    cats_despesa_op   = get_cats_despesa_op()
    cats_imposto      = get_cats_imposto()

    # ── Receitas — completamente dinâmico ─────────────────────────────────────
    rec_values = {cat: soma_entradas(df, [cat]) for cat in cats_receita}
    total_receita = sum(rec_values.values())

    # ── Custos diretos ────────────────────────────────────────────────────────
    # Participação em Contrato — soma total das linhas com essa categoria
    cats_part = [c for c in cats_custo_direto if "participação contrato" in c.lower()]
    cats_outros_custo = [c for c in cats_custo_direto if c not in cats_part]

    cus_part_total = df[df["Categoria"].isin(cats_part)]["Valor"].sum()
    cus_outros = {cat: soma(df, [cat]) for cat in cats_outros_custo}

    provisao     = -abs(provisao_vinicius) if provisao_vinicius else 0.0
    total_custos = cus_part_total + sum(cus_outros.values()) + provisao

    lucro_bruto = total_receita + total_custos

    # ── Despesas operacionais ─────────────────────────────────────────────────
    des_values        = {cat: soma(df, [cat]) for cat in cats_despesa_op}
    total_despesas_op = sum(des_values.values())
    resultado_operacional = lucro_bruto + total_despesas_op

    # ── Impostos ──────────────────────────────────────────────────────────────
    imp_values = {cat: soma(df, [cat]) for cat in cats_imposto}
    total_imp  = sum(imp_values.values())

    lucro_liquido = resultado_operacional + total_imp

    # ── Monta DRE ─────────────────────────────────────────────────────────────
    def _label(cat):
        """Remove prefixo padrão para exibição no DRE."""
        for prefix in ["REC | ", "CUS | ", "DES | ", "IMP | ", "FIN | ", "SOC | ", "REP | "]:
            if cat.startswith(prefix):
                return cat[len(prefix):]
        return cat

    contas  = ["RECEITAS OPERACIONAIS"]
    valores = [total_receita]
    for cat, val in rec_values.items():
        contas.append(f"  {_label(cat)}")
        valores.append(val)

    contas  += ["CUSTOS DIRETOS"]
    valores += [total_custos]
    if cats_part:
        contas.append("  Participação em Contrato")
        valores.append(cus_part_total)
    for cat, val in cus_outros.items():
        contas.append(f"  {_label(cat)}")
        valores.append(val)
    if provisao_vinicius:
        contas.append("  Provisão Repasse Ex-Sócio")
        valores.append(provisao)

    contas  += ["LUCRO BRUTO"]
    valores += [lucro_bruto]

    contas  += ["DESPESAS OPERACIONAIS"]
    valores += [total_despesas_op]
    for cat, val in des_values.items():
        contas.append(f"  {_label(cat)}")
        valores.append(val)

    contas  += ["RESULTADO OPERACIONAL"]
    valores += [resultado_operacional]

    contas  += ["IMPOSTOS"]
    valores += [total_imp]
    for cat, val in imp_values.items():
        contas.append(f"  {_label(cat)}")
        valores.append(val)

    contas  += ["LUCRO LÍQUIDO"]
    valores += [lucro_liquido]

    dre_operacional = pd.DataFrame({"Conta": contas, "Valor (R$)": [round(v, 2) for v in valores]})

    # ── Tabelas laterais — completamente dinâmico ─────────────────────────────

    # Receita Financeira
    cats_receita_fin = get_cats_receita_fin()
    rec_fin_rows = {_label(cat): soma_entradas(df, [cat]) for cat in cats_receita_fin}
    receita_financeira = pd.DataFrame({
        "Descrição": list(rec_fin_rows.keys()) + ["TOTAL"],
        "Valor (R$)": list(rec_fin_rows.values()) + [sum(rec_fin_rows.values())],
    })

    # Societário
    cats_societario = get_cats_societario()
    soc_rows = {_label(cat): df[df["Categoria"] == cat]["Valor"].sum() for cat in cats_societario}
    societario = pd.DataFrame({
        "Descrição": list(soc_rows.keys()) + ["SALDO SOCIETÁRIO"],
        "Valor (R$)": list(soc_rows.values()) + [sum(soc_rows.values())],
    })

    # Empréstimos
    cats_emprestimo = get_cats_emprestimo()
    emp_rows = {_label(cat): df[df["Categoria"] == cat]["Valor"].sum() for cat in cats_emprestimo}
    emprestimos = pd.DataFrame({
        "Descrição": list(emp_rows.keys()) + ["TOTAL"],
        "Valor (R$)": list(emp_rows.values()) + [sum(emp_rows.values())],
    })

    # Transitório — entradas e saídas separadas por categoria
    cats_transitorio = get_cats_transitorio()
    trans_rows = {}
    for cat in cats_transitorio:
        label = _label(cat)
        val_e = df[(df["Categoria"] == cat) & (df["Tipo"] == "Entrada")]["Valor"].sum()
        val_s = df[(df["Categoria"] == cat) & (df["Tipo"] == "Saída")]["Valor"].sum()
        if val_e: trans_rows[f"{label} (Entradas)"] = val_e
        if val_s: trans_rows[f"{label} (Saídas)"] = val_s
    transitorio = pd.DataFrame({
        "Descrição": list(trans_rows.keys()) + ["SALDO TRANSITÓRIO"],
        "Valor (R$)": list(trans_rows.values()) + [sum(trans_rows.values())],
    })

    # ── Aba Receitas — completamente dinâmico ────────────────────────────────
    blocos = []
    for cat in cats_receita:
        label = _label(cat)
        bloco = df[
            (df["Tipo"] == "Entrada") & (df["Categoria"] == cat)
        ][["Data", "Pago para / Recebido de", "Descricao", "Categoria", "Valor"]].copy()
        if bloco.empty:
            continue
        total = pd.DataFrame([{
            "Data": "", "Pago para / Recebido de": "",
            "Descricao": f"TOTAL {label.upper()}",
            "Categoria": cat, "Valor": bloco["Valor"].sum()
        }])
        blocos.append(bloco)
        blocos.append(total)
    conciliacao = pd.concat(blocos, ignore_index=True) if blocos else pd.DataFrame(
        columns=["Data", "Pago para / Recebido de", "Descricao", "Categoria", "Valor"]
    )
    conciliacao = conciliacao.rename(columns={
        "Data": "DATA", "Pago para / Recebido de": "CLIENTE",
        "Descricao": "DESCRIÇÃO", "Categoria": "CLASSIFICAÇÃO", "Valor": "VALORES"
    })

    # ── Aba Despesas ──────────────────────────────────────────────────────────
    CATS_DESPESA_DETALHE = cats_custo_direto + cats_despesa_op + cats_imposto
    CATS_LABELS = {}
    for c in cats_custo_direto:
        CATS_LABELS[c] = c.replace("CUS | ", "")
    for c in cats_despesa_op:
        CATS_LABELS[c] = c.replace("DES | ", "")
    for c in cats_imposto:
        CATS_LABELS[c] = c.replace("IMP | ", "")
    CATS_LABELS["Despesa do cliente"] = "Despesa do Cliente"

    blocos_desp = []
    for cat in CATS_DESPESA_DETALHE:
        bloco = df[
            (df["Tipo"] == "Saída") & (df["Categoria"] == cat)
        ][["Data", "Pago para / Recebido de", "Descricao", "Categoria", "Valor"]].copy()
        if bloco.empty:
            continue
        label = CATS_LABELS.get(cat, cat)
        total = pd.DataFrame([{
            "Data": "", "Pago para / Recebido de": "",
            "Descricao": f"TOTAL {label.upper()}",
            "Categoria": cat, "Valor": bloco["Valor"].sum()
        }])
        blocos_desp.append(bloco)
        blocos_desp.append(total)

    despesas_detalhadas = pd.concat(blocos_desp, ignore_index=True) if blocos_desp else pd.DataFrame(
        columns=["Data", "Pago para / Recebido de", "Descricao", "Categoria", "Valor"]
    )
    despesas_detalhadas = despesas_detalhadas.rename(columns={
        "Data": "DATA", "Pago para / Recebido de": "PAGO PARA",
        "Descricao": "DESCRIÇÃO", "Categoria": "CLASSIFICAÇÃO", "Valor": "VALORES"
    })

    return (
        dre_operacional,
        receita_financeira,
        societario,
        emprestimos,
        transitorio,
        conciliacao,
        despesas_detalhadas,
    )


def gerar_ranking_clientes(df):
    cats_receita = get_cats_receita()
    ranking = (
        df[
            (df["Tipo"] == "Entrada") &
            (df["Categoria"].isin(cats_receita))
        ]
        .groupby("Pago para / Recebido de")["Valor"]
        .sum()
        .reset_index()
        .rename(columns={"Pago para / Recebido de": "CLIENTE", "Valor": "RECEITA (R$)"})
        .sort_values("RECEITA (R$)", ascending=False)
        .reset_index(drop=True)
    )
    ranking.index += 1
    ranking.index.name = "POS."
    total = ranking["RECEITA (R$)"].sum()
    ranking["PARTICIPAÇÃO (%)"] = (ranking["RECEITA (R$)"] / total * 100).round(1)
    return ranking


def gerar_centro_custos(df):
    cats_receita    = get_cats_receita()
    cats_despesa_op = get_cats_despesa_op()
    cats_imposto    = get_cats_imposto()
    cats_custo      = get_cats_custo_direto()

    receita = (
        df[(df["Tipo"] == "Entrada") & (df["Categoria"].isin(cats_receita))]
        .groupby("Centro de custo")["Valor"].sum()
        .rename("RECEITA (R$)")
    )
    todas_saidas = cats_custo + cats_despesa_op + cats_imposto
    despesa = (
        df[(df["Tipo"] == "Saída") & (df["Categoria"].isin(todas_saidas))]
        .groupby("Centro de custo")["Valor"].sum()
        .rename("DESPESA (R$)")
    )
    centro = pd.concat([receita, despesa], axis=1).fillna(0).reset_index()
    centro = centro.rename(columns={"Centro de custo": "CENTRO DE CUSTO"})
    centro["RESULTADO (R$)"] = centro["RECEITA (R$)"] + centro["DESPESA (R$)"]
    centro = centro.sort_values("RECEITA (R$)", ascending=False).reset_index(drop=True)
    total = pd.DataFrame([{
        "CENTRO DE CUSTO": "TOTAL",
        "RECEITA (R$)":    centro["RECEITA (R$)"].sum(),
        "DESPESA (R$)":    centro["DESPESA (R$)"].sum(),
        "RESULTADO (R$)":  centro["RESULTADO (R$)"].sum(),
    }])
    return pd.concat([centro, total], ignore_index=True)