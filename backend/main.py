import io
import json
import os
import bcrypt
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from auth import (
    authenticate_user, create_access_token, create_refresh_token,
    decode_token, get_current_user, load_users, USERS_FILE
)
from relatorios import gerar_relatorios, gerar_ranking_clientes, gerar_centro_custos
from estilos import aplicar_estilos

app = FastAPI(title="Relatório Financeiro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://ledra-app.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CATS_FILE = Path(__file__).parent / "categorias.json"
MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}


class RefreshRequest(BaseModel):
    refresh_token: str

class CategoriaRequest(BaseModel):
    nome: str
    grupo: str

class AlterarSenhaRequest(BaseModel):
    senha_atual: str
    nova_senha: str


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Usuário ou senha incorretos")
    return {
        "access_token":  create_access_token({"sub": user["username"]}),
        "refresh_token": create_refresh_token({"sub": user["username"]}),
        "token_type":    "bearer",
        "full_name":     user["full_name"],
    }


@app.post("/auth/refresh")
def refresh(body: RefreshRequest):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token inválido")
    return {"access_token": create_access_token({"sub": payload["sub"]}), "token_type": "bearer"}


@app.post("/auth/alterar-senha")
def alterar_senha(body: AlterarSenhaRequest, current_user: dict = Depends(get_current_user)):
    if not bcrypt.checkpw(body.senha_atual.encode(), current_user["hashed_password"].encode()):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    if os.getenv("USERS_JSON"):
        raise HTTPException(status_code=400, detail="Alteração de senha não disponível neste ambiente")
    users = load_users()
    users[current_user["username"]]["hashed_password"] = bcrypt.hashpw(
        body.nova_senha.encode(), bcrypt.gensalt()
    ).decode()
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)
    return {"message": "Senha alterada com sucesso"}


@app.get("/auth/me")
def me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "full_name": current_user["full_name"]}


@app.post("/relatorio")
async def gerar_relatorio(
    file: UploadFile = File(...),
    provisao: float = Form(0.0),
    current_user: dict = Depends(get_current_user),
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .xlsx")

    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))

    try:
        primeira_data = pd.to_datetime(df["Data"].dropna().iloc[0], dayfirst=True)
        mes_nome      = MESES[primeira_data.month]
        ano           = primeira_data.year
        mes_ano       = f"{mes_nome} {ano}"
        nome_arquivo  = f"Relatorio_{mes_nome}_{ano}.xlsx"
    except Exception:
        mes_ano      = ""
        nome_arquivo = "Relatorio_Completo.xlsx"

    if provisao:
        linha_provisao = pd.DataFrame([{
            "Data": primeira_data.strftime("%d/%m/%Y") if mes_ano else "",
            "Conta Financeira": "", "Descricao": "Provisão Repasse Ex-Sócio",
            "Categoria": "Provisão", "Centro de custo": "",
            "Pago para / Recebido de": "", "Valor": -abs(provisao), "Tipo": "Saída"
        }])
        df = pd.concat([df, linha_provisao], ignore_index=True)

    (
        dre_operacional, receita_financeira, societario,
        emprestimos, transitorio, conciliacao, despesas_detalhadas,
    ) = gerar_relatorios(df, provisao_vinicius=provisao)

    ranking = gerar_ranking_clientes(df)
    centros = gerar_centro_custos(df)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Movimentos", index=False)
        dre_operacional.to_excel(writer, sheet_name="DRE_Operacional", index=False, startrow=2)
        conciliacao.to_excel(writer, sheet_name="Receitas", index=False, startrow=2)
        despesas_detalhadas.to_excel(writer, sheet_name="Despesas", index=False, startrow=2)
        ranking.reset_index().to_excel(writer, sheet_name="Ranking_Clientes", index=False, startrow=2)
        centros.to_excel(writer, sheet_name="Centro_Custos", index=False, startrow=2)

        workbook = writer.book

        fmts = aplicar_estilos(
            workbook, writer,
            dre_operacional, receita_financeira, societario,
            emprestimos, transitorio, despesas_detalhadas,
            conciliacao, ranking, centros, mes_ano=mes_ano,
        )

        ws_rank = writer.sheets["Ranking_Clientes"]
        rf = fmts["rank_fmts"]
        for i, row in ranking.reset_index().iterrows():
            r = i + 3
            zebra = (r % 2 == 0)
            ws_rank.write(r, 0, row["POS."],             rf["pos_zebra"] if zebra else rf["pos_num"])
            ws_rank.write(r, 1, row["CLIENTE"],          rf["zebra_txt"] if zebra else rf["plain"])
            ws_rank.write(r, 2, row["RECEITA (R$)"],     rf["zebra_val"] if zebra else rf["moeda"])
            ws_rank.write(r, 3, row["PARTICIPAÇÃO (%)"] / 100, rf["pct_zebra"] if zebra else rf["pct"])
        total_r = len(ranking) + 3
        ws_rank.write(total_r, 0, "", rf["total_txt"])
        ws_rank.write(total_r, 1, "TOTAL", rf["total_txt"])
        ws_rank.write(total_r, 2, ranking["RECEITA (R$)"].sum(), rf["total_val"])
        ws_rank.write(total_r, 3, 1.0, rf["pct"])

        ws_cc = writer.sheets["Centro_Custos"]
        cf = fmts["cc_fmts"]
        for i, row in centros.iterrows():
            r        = i + 3
            zebra    = (r % 2 == 0)
            is_total = str(row["CENTRO DE CUSTO"]) == "TOTAL"
            txt_f = cf["total_txt"] if is_total else (cf["zebra_txt"] if zebra else cf["plain"])
            rec_f = cf["total_val"] if is_total else (cf["zebra_val"] if zebra else cf["moeda"])
            dep_f = cf["total_val"] if is_total else (cf["zebra_neg"] if zebra else cf["neg"])
            res   = row["RESULTADO (R$)"]
            if is_total:   res_f = cf["total_val"]
            elif res >= 0: res_f = cf["res_pz"] if zebra else cf["res_pos"]
            else:          res_f = cf["res_nz"] if zebra else cf["res_neg"]
            ws_cc.write(r, 0, row["CENTRO DE CUSTO"], txt_f)
            ws_cc.write(r, 1, row["RECEITA (R$)"],    rec_f)
            ws_cc.write(r, 2, row["DESPESA (R$)"],    dep_f)
            ws_cc.write(r, 3, res,                    res_f)

    output.seek(0)

    receita_bruta  = dre_operacional.loc[dre_operacional["Conta"] == "RECEITAS OPERACIONAIS", "Valor (R$)"].values[0]
    lucro_liquido  = dre_operacional.loc[dre_operacional["Conta"] == "LUCRO LÍQUIDO", "Valor (R$)"].values[0]
    total_despesas = dre_operacional.loc[dre_operacional["Conta"] == "DESPESAS OPERACIONAIS", "Valor (R$)"].values[0]
    resultado_op   = dre_operacional.loc[dre_operacional["Conta"] == "RESULTADO OPERACIONAL", "Valor (R$)"].values[0]
    lucro_bruto    = dre_operacional.loc[dre_operacional["Conta"] == "LUCRO BRUTO", "Valor (R$)"].values[0]

    dre_grafico = [
        {"nome": "Receita Bruta",  "valor": round(receita_bruta, 2)},
        {"nome": "Lucro Bruto",    "valor": round(lucro_bruto, 2)},
        {"nome": "Resultado Op.",  "valor": round(resultado_op, 2)},
        {"nome": "Lucro Líquido",  "valor": round(lucro_liquido, 2)},
    ]

    ranking_grafico = [
        {"cliente": row["CLIENTE"][:25], "receita": round(row["RECEITA (R$)"], 2)}
        for _, row in ranking.head(8).reset_index().iterrows()
    ]

    desp_cats = dre_operacional[
        dre_operacional["Conta"].str.startswith("  ") &
        ~dre_operacional["Conta"].isin(["  Provisão Repasse Ex-Sócio"])
    ].copy()
    desp_cats = desp_cats[desp_cats["Valor (R$)"] < 0].nsmallest(8, "Valor (R$)")
    despesas_grafico = [
        {"nome": row["Conta"].strip()[:20], "valor": round(abs(row["Valor (R$)"]), 2)}
        for _, row in desp_cats.iterrows()
    ]

    dados_json = json.dumps({
        "mesAno":        mes_ano,
        "nomeArquivo":   nome_arquivo,
        "receitaBruta":  round(receita_bruta, 2),
        "lucroLiquido":  round(lucro_liquido, 2),
        "totalDespesas": round(total_despesas, 2),
        "dre":           dre_grafico,
        "ranking":       ranking_grafico,
        "despesas":      despesas_grafico,
    }, ensure_ascii=False)

    headers = {
        "X-Dados": dados_json,
        "Access-Control-Expose-Headers": "X-Dados",
    }

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


def load_categorias() -> dict:
    if not CATS_FILE.exists():
        from relatorios import (
            CATS_RECEITA, CATS_CUSTO_DIRETO, CATS_DESPESA_OP,
            CATS_RESULTADO_FIN, CATS_IMPOSTO, CATS_RECEITA_FIN,
            CATS_SOCIETARIO, CATS_EMPRESTIMO, CATS_TRANSITORIO,
        )
        cats = {
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
        with open(CATS_FILE, "w") as f:
            json.dump(cats, f, indent=2, ensure_ascii=False)
        return cats
    with open(CATS_FILE) as f:
        return json.load(f)


@app.get("/categorias")
def get_categorias(current_user: dict = Depends(get_current_user)):
    return load_categorias()


@app.post("/categorias")
def add_categoria(body: CategoriaRequest, current_user: dict = Depends(get_current_user)):
    cats = load_categorias()
    if body.grupo not in cats:
        raise HTTPException(status_code=400, detail=f"Grupo '{body.grupo}' não existe")
    if body.nome in cats[body.grupo]:
        raise HTTPException(status_code=400, detail="Categoria já existe neste grupo")
    cats[body.grupo].append(body.nome)
    with open(CATS_FILE, "w") as f:
        json.dump(cats, f, indent=2, ensure_ascii=False)
    return {"message": "Categoria adicionada", "categorias": cats}


@app.delete("/categorias/{grupo}/{nome}")
def delete_categoria(grupo: str, nome: str, current_user: dict = Depends(get_current_user)):
    cats = load_categorias()
    if grupo not in cats:
        raise HTTPException(status_code=400, detail=f"Grupo '{grupo}' não existe")
    nome_decoded = nome.replace("__PIPE__", " | ")
    if nome_decoded not in cats[grupo]:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    cats[grupo].remove(nome_decoded)
    with open(CATS_FILE, "w") as f:
        json.dump(cats, f, indent=2, ensure_ascii=False)
    return {"message": "Categoria removida", "categorias": cats}
