"""
database.py — Facior
Gerencia conexão com PostgreSQL e operações de categorias.
Todas as categorias (hardcoded e dinâmicas) vivem no banco.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Categorias padrão — usadas apenas na inicialização do banco
GRUPOS_HARDCODED = {
    "CATS_RECEITA": [
        "REC | Honorário Avulso",
        "REC | Honorário Contratado",
        "REC | Honorário Partido",
        "REC | Honorário Sucumbencial",
        "REC | Honorário Êxito",
        "REC | Honorário Compensação/liminar",
        "REC | Reembolso cliente",
    ],
    "CATS_CUSTO_DIRETO": [
        "CUS | Parceiro Jurídico",
        "CUS | Participação contrato",
        "CUS | Diligencia",
        "CUS | Participação Vinicius Fraga",
        "Despesa do cliente",
    ],
    "CATS_DESPESA_OP": [
        "DES | Aluguel", "DES | Assinaturas Jurídicas", "DES | Bancaria",
        "DES | Certificado digital", "DES | Condomínio", "DES | Consultoria",
        "DES | Contabilidade", "DES | Copa/Cozinha", "DES | Cursos/Especializações",
        "DES | Estagiários", "DES | Energia", "DES | Folha Pagamento",
        "DES | Hospedagem/Site", "DES | Internet", "DES | Limpeza",
        "DES | Manutenção", "DES | Marketing", "DES | Material Escritório",
        "DES | Não Classificado", "DES | OAB/Anuidade", "DES | Pró-Labore",
        "DES | Segurança", "DES | Software Jurídico", "DES | Telefonia",
        "DES | Token/OAB", "DES | Tráfego pago", "DES | Uber/Combustível",
        "DES | Despesa Bancária", "DES | Bancária",
    ],
    "CATS_RESULTADO_FIN": [],
    "CATS_IMPOSTO": [
        "IMP | Simples Nacional",
        "IMP | IPTU",
        "IMP | INSS",
    ],
    "CATS_RECEITA_FIN": [
        "REC | Receita Financeira",
        "REC | Venda ativo",
    ],
    "CATS_SOCIETARIO": [
        "SOC | Distribuição Lucros",
        "SOC | Aporte Sócio",
    ],
    "CATS_EMPRESTIMO": [
        "FIN | Empréstimo Bancário", "FIN | Empréstimo bancário",
        "FIN | Pagamento Empréstimo", "FIN | Consórcio Principal",
        "FIN | Juros Bancários", "FIN | Juros bancários",
    ],
    "CATS_TRANSITORIO": [
        "REP | Valores transitórios",
        "REP | Repasse Cliente",
    ],
}


def get_conn():
    """Retorna conexão com o banco."""
    return psycopg2.connect(os.environ["DATABASE_URL"])


def init_db():
    """Cria tabela e popula com categorias padrão se estiver vazia."""
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
            cur.execute("SELECT COUNT(*) FROM categorias")
            total = cur.fetchone()[0]
            if total == 0:
                for grupo, cats in GRUPOS_HARDCODED.items():
                    for nome in cats:
                        cur.execute(
                            "INSERT INTO categorias (grupo, nome) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                            (grupo, nome)
                        )
        conn.commit()


def load_categorias() -> dict:
    """Retorna todas as categorias do banco agrupadas."""
    result = {grupo: [] for grupo in GRUPOS_HARDCODED}
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
