"""
Testes de API — main.py
Cobre: autenticação, geração de relatório, categorias.
"""
import io
import json
import pytest
import bcrypt
import pandas as pd
from unittest.mock import patch
from fastapi.testclient import TestClient

# ── Setup ─────────────────────────────────────────────────────────────────────

USUARIO_TESTE = {
    "username": "teste",
    "full_name": "Usuário Teste",
    "hashed_password": bcrypt.hashpw(b"senha123", bcrypt.gensalt()).decode(),
}

USERS_MOCK = {"teste": USUARIO_TESTE}


@pytest.fixture
def client():
    """Client com usuário mockado e banco mockado."""
    with patch("auth.load_users", return_value=USERS_MOCK), \
         patch("database.init_db"):
        from main import app
        with TestClient(app) as c:
            yield c


@pytest.fixture
def token(client):
    """Gera access token via login."""
    resp = client.post("/auth/login", data={"username": "teste", "password": "senha123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def headers(token):
    """Header de autenticação pronto para usar."""
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def xlsx_demo():
    """Gera um arquivo .xlsx mínimo válido para upload."""
    df = pd.DataFrame([
        {"Data": "01/06/2026", "Conta Financeira": "Conta Demo", "Descricao": "Honorário",
         "Categoria": "REC | Honorário Avulso", "Centro de custo": "Civil",
         "Pago para / Recebido de": "Cliente A", "Cliente": "Cliente A",
         "Documento": "", "Caso": "", "Responsavel": "", "Valor": 5000.0,
         "Tipo": "Entrada", "Status": "Recebido"},
        {"Data": "02/06/2026", "Conta Financeira": "Conta Demo", "Descricao": "Aluguel",
         "Categoria": "DES | Aluguel", "Centro de custo": "Administrativo",
         "Pago para / Recebido de": "Imobiliária", "Cliente": "",
         "Documento": "", "Caso": "", "Responsavel": "", "Valor": -2000.0,
         "Tipo": "Saída", "Status": "Pago"},
    ])
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return buf


# ── Auth: login ───────────────────────────────────────────────────────────────

def test_login_sucesso(client):
    resp = client.post("/auth/login", data={"username": "teste", "password": "senha123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert "refresh_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"

def test_login_senha_errada(client):
    resp = client.post("/auth/login", data={"username": "teste", "password": "errada"})
    assert resp.status_code == 401

def test_login_usuario_inexistente(client):
    resp = client.post("/auth/login", data={"username": "naoexiste", "password": "senha123"})
    assert resp.status_code == 401


# ── Auth: refresh ─────────────────────────────────────────────────────────────

def test_refresh_token_valido(client):
    resp_login = client.post("/auth/login", data={"username": "teste", "password": "senha123"})
    refresh = resp_login.json()["refresh_token"]
    resp = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_refresh_token_invalido(client):
    resp = client.post("/auth/refresh", json={"refresh_token": "token_invalido"})
    assert resp.status_code == 422 or resp.status_code == 401


# ── Auth: me ──────────────────────────────────────────────────────────────────

def test_me_autenticado(client, headers):
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "teste"
    assert resp.json()["full_name"] == "Usuário Teste"

def test_me_sem_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


# ── Relatório ─────────────────────────────────────────────────────────────────

def test_relatorio_sucesso(client, headers, xlsx_demo):
    resp = client.post(
        "/relatorio",
        headers=headers,
        files={"file": ("relatorio.xlsx", xlsx_demo, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"provisao": "0"},
    )
    assert resp.status_code == 200
    assert "X-Dados" in resp.headers
    dados = json.loads(resp.headers["X-Dados"])
    assert "receitaBruta" in dados
    assert "lucroLiquido" in dados
    assert "dre" in dados

def test_relatorio_sem_autenticacao(client, xlsx_demo):
    resp = client.post(
        "/relatorio",
        files={"file": ("relatorio.xlsx", xlsx_demo, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"provisao": "0"},
    )
    assert resp.status_code == 401

def test_relatorio_arquivo_invalido(client, headers):
    resp = client.post(
        "/relatorio",
        headers=headers,
        files={"file": ("relatorio.csv", io.BytesIO(b"a,b,c"), "text/csv")},
        data={"provisao": "0"},
    )
    assert resp.status_code == 400

def test_relatorio_com_provisao(client, headers, xlsx_demo):
    resp = client.post(
        "/relatorio",
        headers=headers,
        files={"file": ("relatorio.xlsx", xlsx_demo, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"provisao": "1000"},
    )
    assert resp.status_code == 200

def test_relatorio_categorias_ignoradas(client, headers):
    """Categoria desconhecida aparece em categoriasIgnoradas."""
    df = pd.DataFrame([{
        "Data": "01/06/2026", "Conta Financeira": "Conta", "Descricao": "Teste",
        "Categoria": "CAT | Desconhecida", "Centro de custo": "Civil",
        "Pago para / Recebido de": "X", "Cliente": "", "Documento": "",
        "Caso": "", "Responsavel": "", "Valor": 100.0, "Tipo": "Entrada", "Status": "Recebido"
    }])
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    resp = client.post(
        "/relatorio",
        headers=headers,
        files={"file": ("relatorio.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"provisao": "0"},
    )
    assert resp.status_code == 200


# ── Categorias ────────────────────────────────────────────────────────────────

def test_get_categorias(client, headers):
    with patch("main.db_load_categorias", return_value={"CATS_RECEITA": [], "CATS_DESPESA_OP": []}):
        resp = client.get("/categorias", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "CATS_RECEITA" in data
    assert "CATS_DESPESA_OP" in data

def test_add_categoria(client, headers):
    cats_resultado = {"CATS_RECEITA": ["REC | Nova Categoria"], "CATS_DESPESA_OP": []}
    with patch("main.categoria_existe", return_value=False), \
         patch("main.db_add_categoria", return_value=cats_resultado):
        resp = client.post(
            "/categorias",
            headers=headers,
            json={"nome": "REC | Nova Categoria", "grupo": "CATS_RECEITA"},
        )
    assert resp.status_code == 200
    assert "REC | Nova Categoria" in resp.json()["categorias"]["CATS_RECEITA"]

def test_add_categoria_duplicada(client, headers):
    with patch("main.categoria_existe", return_value=True):
        resp = client.post(
            "/categorias",
            headers=headers,
            json={"nome": "REC | Já Existe", "grupo": "CATS_RECEITA"},
        )
    assert resp.status_code == 400

def test_add_categoria_grupo_invalido(client, headers):
    resp = client.post(
        "/categorias",
        headers=headers,
        json={"nome": "REC | Teste", "grupo": "GRUPO_INEXISTENTE"},
    )
    assert resp.status_code == 400

def test_delete_categoria(client, headers):
    cats_resultado = {"CATS_RECEITA": [], "CATS_DESPESA_OP": []}
    with patch("main.categoria_existe", return_value=True), \
         patch("main.db_delete_categoria", return_value=cats_resultado):
        resp = client.delete(
            "/categorias/CATS_RECEITA/REC__PIPE__Para Deletar",
            headers=headers,
        )
    assert resp.status_code == 200

def test_delete_categoria_sem_autenticacao(client):
    resp = client.delete("/categorias/CATS_RECEITA/REC__PIPE__Teste")
    assert resp.status_code == 401


# ── Relatório: layouts do export do Astrea ────────────────────────────────────

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

CATS_TESTE = {
    "CATS_RECEITA": ["REC | Honorário Partido"],
    "CATS_DESPESA_OP": ["DES | Folha Pagamento", "DES | Pró-Labore"],
    "CATS_SOCIETARIO": ["SOC | Distribuição Lucros"],
}

# mesmos lançamentos nos dois layouts: (data, descrição, cliente, categoria, centro, valor, tipo)
LANCAMENTOS = [
    ("03/09/2026", "ASSESSORIA MENSAL", "SALUTE LTDA", "REC | Honorário Partido", "Tributário", 1350.85, "Entrada"),
    ("04/09/2026", "SALÁRIO", "PHILLIPE", "DES | Folha Pagamento", "Tributário", -4000.0, "Saída"),
    ("04/09/2026", "PRO LABORE", "DANIELA", "DES | Pró-Labore", "Escritório Vitória", -2500.0, "Saída"),
    ("04/09/2026", "DISTRIBUIÇÃO", "HENRIQUE", "SOC | Distribuição Lucros", "Escritório Vitória", -3723.59, "Saída"),
]


def _xlsx(df):
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return buf


def _layout_antigo():
    return pd.DataFrame([{
        "Data": d, "Conta Financeira": "SICOOB", "Descricao": desc, "Categoria": cat,
        "Centro de custo": cc, "Pago para / Recebido de": cli, "Cliente": cli,
        "Documento": "", "Caso": "", "Responsavel": "Daniela Fraga",
        "Valor": v, "Tipo": t, "Status": "Pago",
    } for d, desc, cli, cat, cc, v, t in LANCAMENTOS])


def _layout_novo():
    """Layout do export do Astrea a partir de set/2026."""
    return pd.DataFrame([{
        "DATA": d, "TIPO": t, "DESCRIÇÃO": desc, "CONTATO / CLIENTE": cli, "STATUS": "Pago",
        "DATA DE VENCIMENTO": d, "DATA DE PAGAMENTO": None, "DATA DE COMPENSAÇÃO": None,
        "DATA DO REPASSE": None, "VALOR BRUTO": None, "TAXA": None, "VALOR LÍQUIDO": v,
        "CONTA": "SICOOB - CONTA CORRENTE", "EMISSOR DO BOLETO": None,
        "PAGO PARA / RECEBIDO DE": cli, "CATEGORIA": cat, "CENTRO DE CUSTO": cc,
        "CASO": None, "RESPONSAVEL": "Daniela Fraga", "DOCUMENTO": None,
    } for d, desc, cli, cat, cc, v, t in LANCAMENTOS])


def _post_relatorio(client, headers, df):
    with patch("relatorios._carregar_cats", return_value=CATS_TESTE), \
         patch("main.get_todas_categorias_conhecidas",
               return_value=[c for cs in CATS_TESTE.values() for c in cs]):
        return client.post(
            "/relatorio", headers=headers,
            files={"file": ("relatorio.xlsx", _xlsx(df), XLSX_MIME)},
            data={"provisao": "0"},
        )


def test_relatorio_layout_novo_astrea(client, headers):
    resp = _post_relatorio(client, headers, _layout_novo())
    assert resp.status_code == 200
    dados = json.loads(resp.headers["X-Dados"])
    assert dados["receitaBruta"] == 1350.85
    assert dados["categoriasIgnoradas"] == []
    assert dados["mesAno"] == "Setembro 2026"


def test_relatorio_layout_novo_igual_ao_antigo(client, headers):
    """O mesmo movimento exportado nos dois layouts tem que dar o mesmo resultado."""
    antigo = json.loads(_post_relatorio(client, headers, _layout_antigo()).headers["X-Dados"])
    novo = json.loads(_post_relatorio(client, headers, _layout_novo()).headers["X-Dados"])
    assert novo == antigo


def test_relatorio_valor_como_texto_com_virgula(client, headers):
    df = _layout_novo()
    df["VALOR LÍQUIDO"] = ["1.350,85", "-4.000,00", "-2.500,00", "-3.723,59"]
    resp = _post_relatorio(client, headers, df)
    assert resp.status_code == 200
    assert json.loads(resp.headers["X-Dados"])["receitaBruta"] == 1350.85


def test_relatorio_tipo_sem_acento(client, headers):
    df = _layout_novo()
    df["TIPO"] = df["TIPO"].replace({"Saída": "saida"})
    resp = _post_relatorio(client, headers, df)
    assert resp.status_code == 200
    assert json.loads(resp.headers["X-Dados"])["receitaBruta"] == 1350.85


def test_relatorio_sem_coluna_categoria_retorna_400_claro(client, headers):
    df = _layout_novo().drop(columns=["CATEGORIA"])
    resp = _post_relatorio(client, headers, df)
    assert resp.status_code == 400
    assert "Categoria" in resp.json()["detail"]
    assert "Colunas recebidas" in resp.json()["detail"]


def test_relatorio_erro_interno_retorna_500_com_mensagem(client, headers):
    """Erro inesperado vira 500 com detail (e não 'Failed to fetch' no navegador)."""
    with patch("main.gerar_relatorios", side_effect=RuntimeError("boom")):
        resp = _post_relatorio(client, headers, _layout_novo())
    assert resp.status_code == 500
    assert "Erro ao processar" in resp.json()["detail"]