"""
database.py — Facior
Gerencia conexão com PostgreSQL e operações de categorias.
"""
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path

# Categorias hardcoded (fallback se banco não disponível)
from relatorios import (
    CATS_RECEITA, CATS_CUSTO_DIRETO, CATS_DESPESA_OP,
    CATS_RESULTADO_FIN, CATS_IMPOSTO, CATS_RECEITA_FIN,
    CATS_SOCIETARIO, CATS_EMPRESTIMO, CATS_TRANSITORIO,
)

GRUPOS_HARDCODED = {
    "CATS_RECEITA":       CATS_RECEITA,
    "CATS_CUSTO_DIRETO":  CATS_CUSTO_DIRETO,
    "CATS_DESPESA_OP":    CATS_DESPESA_OP,
    "CATS_RESULTADO_FIN": CATS_RESULTADO_FIN,
    "CATS_IMPOSTO":       CATS_IMPOSTO,
    "CATS_RECEITA_FIN":   CATS_RECEITA_FIN,
    "CATS_SOCIETARIO":    CATS_SOCIETARIO,
    "CATS_EMPRESTIMO":    CATS_EMPRESTIMO,
    "CATS_TRANSITORIO":   CATS_TRANSITORIO,
}


def get_conn():
    """Retorna conexão com o banco."""
    return psycopg2.connect(os.environ["DATABASE_URL"])


def init_db():
    """Cria tabela de categorias se não existir."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS categorias (
                    id     SERIAL PRIMARY KEY,
                    grupo  TEXT NOT NULL,
                    nome   TEXT NOT NULL,
                    UNIQUE (grupo, nome)
                )
            """)
        conn.commit()


def load_categorias() -> dict:
    """
    Retorna dicionário com todas as categorias (hardcoded + dinâmicas do banco).
    Formato: { "CATS_RECEITA": [...], "CATS_DESPESA_OP": [...], ... }
    """
    result = {grupo: list(cats) for grupo, cats in GRUPOS_HARDCODED.items()}
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT grupo, nome FROM categorias ORDER BY id")
                rows = cur.fetchall()
        for row in rows:
            grupo, nome = row["grupo"], row["nome"]
            if grupo in result and nome not in result[grupo]:
                result[grupo].append(nome)
    except Exception:
        pass  # se banco falhar, retorna só as hardcoded
    return result


def add_categoria(nome: str, grupo: str) -> dict:
    """Adiciona categoria no banco. Retorna todas as categorias."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO categorias (grupo, nome) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (grupo, nome)
            )
        conn.commit()
    return load_categorias()


def delete_categoria(grupo: str, nome: str) -> dict:
    """Remove categoria do banco. Retorna todas as categorias."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM categorias WHERE grupo = %s AND nome = %s",
                (grupo, nome)
            )
        conn.commit()
    return load_categorias()


def categoria_existe(grupo: str, nome: str) -> bool:
    """Verifica se categoria já existe (hardcoded ou no banco)."""
    cats = load_categorias()
    return nome in cats.get(grupo, [])