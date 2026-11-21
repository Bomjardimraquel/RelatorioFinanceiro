import { useState } from "react";
import { addCategoria } from "../services/api";
import { GRUPOS_LABELS } from "../constants/grupos";

const formatBRL = (val) =>
  new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(val);

const plural = (n, um, varios) => `${n} ${n === 1 ? um : varios}`;

// ── Categorias não reconhecidas, com cadastro direto ──────────────────────────
export function AvisoCategorias({ categorias, sugestoes = {}, valorIgnorado = 0, onRegerar, regerando }) {
  const [grupos, setGrupos] = useState(() =>
    Object.fromEntries(categorias.map((c) => [c, sugestoes[c]?.grupoSugerido || ""]))
  );
  const [estado, setEstado] = useState({}); // nome -> { status: "salvando" | "ok" | "erro", ... }

  const cadastrar = async (nome) => {
    const grupo = grupos[nome];
    if (!grupo) return;
    setEstado((e) => ({ ...e, [nome]: { status: "salvando" } }));
    try {
      await addCategoria(nome, grupo);
      setEstado((e) => ({ ...e, [nome]: { status: "ok", grupo } }));
    } catch (err) {
      setEstado((e) => ({ ...e, [nome]: { status: "erro", msg: err.message } }));
    }
  };

  const cadastradas = Object.values(estado).filter((e) => e.status === "ok").length;

  return (
    <div style={s.aviso}>
      <i className="ti ti-alert-triangle" style={{ fontSize: 16, flexShrink: 0, marginTop: 2 }} />
      <div style={{ flex: 1 }}>
        <div style={s.titulo}>Categorias não reconhecidas — não incluídas no relatório</div>
        <div style={s.sub}>
          Escolha o grupo e cadastre. Se for a mesma categoria com outra grafia, corrija no Astrea
          em vez de cadastrar uma nova.
        </div>

        <div style={s.lista}>
          {categorias.map((nome) => {
            const st = estado[nome];
            const parecida = sugestoes[nome]?.parecidaCom;
            return (
              <div key={nome} style={s.linha}>
                <div style={s.nomeCol}>
                  <div style={s.nome}>{nome}</div>
                  {parecida && <div style={s.dica}>Parecida com “{parecida}”</div>}
                </div>
                {st?.status === "ok" ? (
                  <div style={s.ok}>
                    <i className="ti ti-check" style={{ fontSize: 14 }} /> Cadastrada em {GRUPOS_LABELS[st.grupo]}
                  </div>
                ) : (
                  <div style={s.acao}>
                    <select
                      aria-label={`Grupo para ${nome}`}
                      style={s.select}
                      value={grupos[nome]}
                      disabled={st?.status === "salvando"}
                      onChange={(e) => setGrupos((g) => ({ ...g, [nome]: e.target.value }))}
                    >
                      <option value="">Escolha o grupo</option>
                      {Object.entries(GRUPOS_LABELS).map(([valor, rotulo]) => (
                        <option key={valor} value={valor}>{rotulo}</option>
                      ))}
                    </select>
                    <button
                      style={!grupos[nome] || st?.status === "salvando" ? s.btnOff : s.btn}
                      disabled={!grupos[nome] || st?.status === "salvando"}
                      onClick={() => cadastrar(nome)}
                    >
                      {st?.status === "salvando" ? "Salvando…" : "Cadastrar"}
                    </button>
                  </div>
                )}
                {st?.status === "erro" && <div style={s.erro}>{st.msg}</div>}
              </div>
            );
          })}
        </div>

        <div style={s.rodape}>
          <div style={s.valor}>Total ignorado: {formatBRL(valorIgnorado)}</div>
          {cadastradas > 0 && onRegerar && (
            <button style={regerando ? s.btnOff : s.btnRegerar} disabled={regerando} onClick={onRegerar}>
              {regerando
                ? "Gerando…"
                : `Gerar novamente com ${plural(cadastradas, "categoria cadastrada", "categorias cadastradas")}`}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Avisos de qualidade do arquivo ────────────────────────────────────────────
export function AvisosQualidade({ avisos }) {
  if (!avisos) return null;
  const { semCentroCusto, semCategoria, valorInvalido, possiveisDuplicadas, grafiaAjustada = [] } = avisos;

  const itens = [];
  if (semCategoria?.qtd > 0) {
    itens.push({
      id: "sem-categoria",
      texto: `${plural(semCategoria.qtd, "lançamento sem categoria", "lançamentos sem categoria")} (${formatBRL(semCategoria.valor)}) — ficam fora do relatório. Preencha a categoria no Astrea.`,
    });
  }
  if (semCentroCusto?.qtd > 0) {
    itens.push({
      id: "sem-centro",
      texto: `${plural(semCentroCusto.qtd, "lançamento sem centro de custo", "lançamentos sem centro de custo")} (${formatBRL(semCentroCusto.valor)}) — aparecem como “Sem centro de custo” nas abas Receitas, Despesas e Centro_Custos.`,
    });
  }
  if (valorInvalido?.qtd > 0) {
    itens.push({
      id: "valor-invalido",
      texto: `${plural(valorInvalido.qtd, "lançamento com valor ilegível", "lançamentos com valor ilegível")} — não entram nos totais.`,
    });
  }
  if (possiveisDuplicadas?.grupos > 0) {
    itens.push({
      id: "duplicadas",
      texto: `${plural(possiveisDuplicadas.grupos, "possível duplicidade", "possíveis duplicidades")} (${possiveisDuplicadas.qtd} lançamentos idênticos). Confira se não é um lançamento repetido:`,
      detalhes: possiveisDuplicadas.exemplos.map(
        (e) => `${e.data} · ${e.descricao} · ${formatBRL(e.valor)} · ${e.vezes}×`
      ),
    });
  }

  if (itens.length === 0 && grafiaAjustada.length === 0) return null;

  return (
    <>
      {itens.length > 0 && (
        <div style={s.aviso}>
          <i className="ti ti-alert-circle" style={{ fontSize: 16, flexShrink: 0, marginTop: 2 }} />
          <div style={{ flex: 1 }}>
            <div style={s.titulo}>Confira o arquivo</div>
            <ul style={s.ul}>
              {itens.map((i) => (
                <li key={i.id} style={s.li}>
                  {i.texto}
                  {i.detalhes && (
                    <ul style={s.ulInterna}>
                      {i.detalhes.map((d) => <li key={d}>{d}</li>)}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
      {grafiaAjustada.length > 0 && (
        <div style={s.info}>
          <i className="ti ti-info-circle" style={{ fontSize: 16, flexShrink: 0, marginTop: 2 }} />
          <div style={{ flex: 1 }}>
            <div style={s.titulo}>Grafia ajustada para a categoria cadastrada</div>
            <ul style={s.ul}>
              {grafiaAjustada.map((a) => (
                <li key={a.arquivo} style={s.li}>“{a.arquivo}” → “{a.cadastrada}”</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </>
  );
}

const s = {
  aviso: { background: "#FEF9E7", border: "1px solid #C9A84C", borderRadius: 10, padding: "13px 16px", display: "flex", gap: 12, alignItems: "flex-start", color: "#7B5800" },
  info: { background: "#fff", border: "1px solid #85B7EB", borderRadius: 10, padding: "13px 16px", display: "flex", gap: 12, alignItems: "flex-start", color: "#185FA5" },
  titulo: { fontSize: 13, fontWeight: 600, marginBottom: 4 },
  sub: { fontSize: 12.5, marginBottom: 10 },
  lista: { display: "flex", flexDirection: "column", gap: 8 },
  linha: { background: "#fff", border: "0.5px solid #E8D9A0", borderRadius: 8, padding: "9px 12px", display: "flex", flexWrap: "wrap", alignItems: "center", gap: 10 },
  nomeCol: { flex: "1 1 240px", minWidth: 0 },
  nome: { fontSize: 13, fontWeight: 500, color: "#0C2340", wordBreak: "break-word" },
  dica: { fontSize: 11.5, color: "#7B5800", marginTop: 2 },
  acao: { display: "flex", gap: 8, alignItems: "center" },
  select: { border: "0.5px solid #D3D1C7", borderRadius: 8, padding: "6px 10px", fontSize: 12.5, background: "#F7F5F0", color: "#0C2340", fontFamily: "inherit" },
  btn: { background: "#0C2340", color: "#fff", border: "none", borderRadius: 20, padding: "7px 16px", fontSize: 12.5, fontWeight: 600, cursor: "pointer", fontFamily: "inherit" },
  btnOff: { background: "#B5D4F4", color: "#0C2340", border: "none", borderRadius: 20, padding: "7px 16px", fontSize: 12.5, cursor: "not-allowed", fontFamily: "inherit" },
  btnRegerar: { background: "#185FA5", color: "#fff", border: "none", borderRadius: 20, padding: "8px 18px", fontSize: 12.5, fontWeight: 600, cursor: "pointer", fontFamily: "inherit" },
  ok: { fontSize: 12.5, fontWeight: 600, color: "#3B6D11", display: "flex", alignItems: "center", gap: 4 },
  erro: { flexBasis: "100%", fontSize: 12, color: "#A32D2D" },
  rodape: { display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, marginTop: 10, flexWrap: "wrap" },
  valor: { fontSize: 12, fontWeight: 600, color: "#A32D2D" },
  ul: { margin: 0, paddingLeft: 18, fontSize: 12.5 },
  li: { marginBottom: 3 },
  ulInterna: { margin: "3px 0 0", paddingLeft: 18, fontSize: 12 },
};