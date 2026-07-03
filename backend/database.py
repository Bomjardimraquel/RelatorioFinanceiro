"""
database.py — Facior
Gerencia conexão com PostgreSQL e operações de categorias.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

GRUPOS_VALIDOS = [
    "CATS_RECEITA", "CATS_CUSTO_DIRETO", "CATS_DESPESA_OP",
    "CATS_RESULTADO_FIN", "CATS_IMPOSTO", "CATS_RECEITA_FIN",
    "CATS_SOCIETARIO", "CATS_EMPRESTIMO", "CATS_TRANSITORIO",
]


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
    """Retorna todas as categorias do banco agrupadas."""
    result = {grupo: [] for grupo in GRUPOS_VALIDOS}
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT grupo, nome FROM categorias ORDER BY id")
            rows = cur.fetchall()
    for row in rows:
        grupo, nome = row["grupo"], row["nome"]
        if grupo in result:
            result[grupo].append(nome)
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
    """Verifica se categoria já existe no banco."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM categorias WHERE grupo = %s AND nome = %s",
                (grupo, nome)
            )
            return cur.fetchone() is not None
