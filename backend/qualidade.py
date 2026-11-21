import re
import unicodedata
from difflib import get_close_matches

import pandas as pd

# Prefixo usado no Astrea → grupo cadastrado. "REC" é ambíguo (receita x receita
# financeira); a tela deixa o usuário trocar o grupo antes de cadastrar.
PREFIXO_GRUPO = {
    "REC": "CATS_RECEITA",
    "CUS": "CATS_CUSTO_DIRETO",
    "DES": "CATS_DESPESA_OP",
    "IMP": "CATS_IMPOSTO",
    "SOC": "CATS_SOCIETARIO",
    "FIN": "CATS_EMPRESTIMO",
    "REP": "CATS_TRANSITORIO",
}

CORTE_SEMELHANCA = 0.8
MAX_EXEMPLOS = 5
MAX_AJUSTES = 10


def chave_categoria(nome) -> str:
    """Forma de comparação: sem diferença de caixa, espaços ou espaço no '|'."""
    s = re.sub(r"\s*\|\s*", " | ", str(nome).strip())
    return " ".join(s.split()).casefold()


def _chave_semelhanca(nome) -> str:
    """Como chave_categoria, mas também ignora acentos (para sugerir 'parecida com')."""
    s = unicodedata.normalize("NFKD", chave_categoria(nome))
    return s.encode("ascii", "ignore").decode()


def _em_branco(serie: pd.Series) -> pd.Series:
    return serie.isna() | (serie.astype(str).str.strip() == "")


def canonizar_categorias(df: pd.DataFrame, cadastradas) -> tuple[pd.DataFrame, list[dict]]:
    """Troca a grafia do arquivo pela grafia cadastrada quando só mudam caixa/espaços.

    Se duas categorias cadastradas forem iguais nessa comparação, vale a primeira.
    Devolve (df novo, lista de {"arquivo", "cadastrada"} com o que foi ajustado).
    """
    canonica: dict[str, str] = {}
    for nome in cadastradas:
        canonica.setdefault(chave_categoria(nome), nome)

    original = df["Categoria"]
    novo = original.map(
        lambda c: c if pd.isna(c) else canonica.get(chave_categoria(c), str(c).strip())
    )

    ajustes = sorted({
        (str(o), str(n))
        for o, n in zip(original, novo)
        if pd.notna(o) and str(o) != str(n)
    })
    df = df.copy()
    df["Categoria"] = novo
    return df, [{"arquivo": o, "cadastrada": n} for o, n in ajustes[:MAX_AJUSTES]]


def categorias_nao_reconhecidas(df: pd.DataFrame, cadastradas) -> list[str]:
    """Categorias do arquivo que não estão cadastradas (já com a grafia ajustada)."""
    conhecidas = set(cadastradas)
    usadas = df.loc[~_em_branco(df["Categoria"]), "Categoria"].astype(str).unique()
    return sorted(c for c in usadas if c not in conhecidas)


def sugerir_cadastro(categoria: str, cats_por_grupo: dict) -> dict:
    """Sugere em qual grupo cadastrar e, se existir, uma categoria parecida.

    parecidaCom: categoria já cadastrada quase igual (ex.: sem acento ou com
    letra trocada). grupoSugerido: grupo dessa parecida; se não houver, o grupo
    pelo prefixo ("DES | ..." → Despesas Operacionais); senão None.
    """
    por_chave = {
        _chave_semelhanca(nome): (grupo, nome)
        for grupo, nomes in cats_por_grupo.items()
        for nome in nomes
    }
    parecida = get_close_matches(_chave_semelhanca(categoria), list(por_chave), n=1, cutoff=CORTE_SEMELHANCA)
    if parecida:
        grupo, nome = por_chave[parecida[0]]
        return {"parecidaCom": nome, "grupoSugerido": grupo}
    prefixo = str(categoria).split("|")[0].strip().upper()
    return {"parecidaCom": None, "grupoSugerido": PREFIXO_GRUPO.get(prefixo)}


def analisar_qualidade(df: pd.DataFrame, cats_operacionais) -> dict:
    """Conta os problemas do arquivo. 'cats_operacionais' = categorias que entram
    no DRE por área (receitas, custos, despesas e impostos): só nelas o centro de
    custo faz diferença."""
    sem_categoria = _em_branco(df["Categoria"])
    sem_centro = _em_branco(df["Centro de custo"]) & df["Categoria"].isin(set(cats_operacionais))
    valores = pd.to_numeric(df["Valor"], errors="coerce")
    valor_abs = valores.abs()

    cols = ["Data", "Descricao", "Valor", "Tipo", "Pago para / Recebido de", "Categoria"]
    chave = pd.Series(
        ["|".join("" if pd.isna(v) else str(v) for v in linha)
         for linha in df[cols].itertuples(index=False, name=None)],
        index=df.index,
    )
    contagem = chave.value_counts()
    repetidas = contagem[contagem > 1]
    exemplos = []
    for k, vezes in repetidas.head(MAX_EXEMPLOS).items():
        linha = df.loc[chave == k].iloc[0]
        exemplos.append({
            "data": "" if pd.isna(linha["Data"]) else str(linha["Data"]),
            "descricao": ("" if pd.isna(linha["Descricao"]) else str(linha["Descricao"]))[:60],
            "valor": float(round(valores[linha.name], 2)) if pd.notna(valores[linha.name]) else 0.0,
            "vezes": int(vezes),
        })

    return {
        "semCategoria": {
            "qtd": int(sem_categoria.sum()),
            "valor": float(round(valor_abs[sem_categoria].sum(), 2)),
        },
        "semCentroCusto": {
            "qtd": int(sem_centro.sum()),
            "valor": float(round(valor_abs[sem_centro].sum(), 2)),
        },
        "valorInvalido": {"qtd": int(valores.isna().sum())},
        "possiveisDuplicadas": {
            "grupos": int(len(repetidas)),
            "qtd": int(repetidas.sum()),
            "exemplos": exemplos,
        },
    }