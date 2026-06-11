import { useState, useEffect } from "react";
import { getCategorias, addCategoria, deleteCategoria } from "../services/api";

const GRUPOS_LABELS = {
  CATS_RECEITA:       "Receitas",
  CATS_CUSTO_DIRETO:  "Custos Diretos",
  CATS_DESPESA_OP:    "Despesas Operacionais",
  CATS_IMPOSTO:       "Impostos",
  CATS_RECEITA_FIN:   "Receita Financeira",
  CATS_SOCIETARIO:    "Societário",
  CATS_EMPRESTIMO:    "Empréstimos",
  CATS_TRANSITORIO:   "Transitórios",
};

export default function Categorias() {
  const [cats, setCats]           = useState({});
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState("");
  const [success, setSuccess]     = useState("");
  const [novaCateg, setNovaCateg] = useState("");
  const [novoGrupo, setNovoGrupo] = useState("CATS_DESPESA_OP");
  const [adding, setAdding]       = useState(false);

  useEffect(() => {
    getCategorias()
      .then(setCats)
      .catch(() => setError("Erro ao carregar categorias"))
      .finally(() => setLoading(false));
  }, []);

  const handleAdd = async () => {
    if (!novaCateg.trim()) return;
    setAdding(true);
    setError("");
    setSuccess("");
    try {
      const { categorias } = await addCategoria(novaCateg.trim(), novoGrupo);
      setCats(categorias);
      setNovaCateg("");
      setSuccess(`"${novaCateg.trim()}" adicionada com sucesso!`);
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (grupo, nome) => {
    if (!confirm(`Remover "${nome}"?`)) return;
    setError("");
    try {
      const { categorias } = await deleteCategoria(grupo, nome);
      setCats(categorias);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div style={styles.loading}>Carregando categorias...</div>;

  return (
    <div style={styles.main}>
      <div style={styles.topbar}>
        <div style={styles.topbarTitle}>Categorias</div>
        <div style={styles.topbarSub}>Gerencie as categorias do relatório</div>
      </div>

      <div style={styles.content}>
        <div style={styles.addCard}>
          <div style={styles.sectionLabel}>Adicionar categoria</div>
          <div style={styles.addRow}>
            <input
              style={styles.input}
              type="text"
              placeholder="Ex: DES | Nova Despesa"
              value={novaCateg}
              onChange={(e) => setNovaCateg(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAdd()}
            />
            <select
              style={styles.select}
              value={novoGrupo}
              onChange={(e) => setNovoGrupo(e.target.value)}
            >
              {Object.entries(GRUPOS_LABELS).map(([key, label]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
            <button
              style={adding ? styles.btnDisabled : styles.btnAdd}
              onClick={handleAdd}
              disabled={adding}
            >
              {adding ? "Adicionando..." : "Adicionar"}
            </button>
          </div>
          {error   && <div style={styles.error}>{error}</div>}
          {success && <div style={styles.success}>{success}</div>}
        </div>

        {Object.entries(GRUPOS_LABELS).map(([grupo, label]) => {
          const lista = cats[grupo] || [];
          return (
            <div key={grupo} style={styles.groupCard}>
              <div style={styles.groupHeader}>
                <span style={styles.groupTitle}>{label}</span>
                <span style={styles.groupCount}>{lista.length}</span>
              </div>
              <div style={styles.tagList}>
                {lista.map((cat) => (
                  <div key={cat} style={styles.tag}>
                    <span style={styles.tagText}>{cat}</span>
                    <button
                      style={styles.tagDelete}
                      onClick={() => handleDelete(grupo, cat)}
                      title="Remover"
                    >
                      <i className="ti ti-x" style={{ fontSize: 12 }} aria-hidden="true"></i>
                    </button>
                  </div>
                ))}
                {lista.length === 0 && (
                  <span style={styles.empty}>Nenhuma categoria</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const styles = {
  main: { flex: 1, display: "flex", flexDirection: "column", background: "#F7F5F0" },
  topbar: {
    background: "#fff", borderBottom: "0.5px solid #E0DEDD", padding: "16px 28px",
  },
  topbarTitle: { fontSize: 16, fontWeight: 600, color: "#0C2340", letterSpacing: "-0.3px" },
  topbarSub: { fontSize: 12.5, color: "#5F5E5A", marginTop: 3 },
  content: { padding: "22px 28px", display: "flex", flexDirection: "column", gap: 16 },
  sectionLabel: {
    fontSize: 11, fontWeight: 600, color: "#C9A84C",
    textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 12,
  },
  addCard: {
    background: "#fff", border: "0.5px solid #E0DEDD",
    borderRadius: 10, padding: "18px 20px",
  },
  addRow: { display: "flex", gap: 10, alignItems: "center" },
  input: {
    flex: 1, border: "0.5px solid #D3D1C7", borderRadius: 8,
    padding: "9px 14px", fontSize: 13, color: "#0C2340",
    background: "#F7F5F0", outline: "none", fontFamily: "inherit",
  },
  select: {
    border: "0.5px solid #D3D1C7", borderRadius: 8,
    padding: "9px 12px", fontSize: 13, color: "#0C2340",
    background: "#F7F5F0", fontFamily: "inherit", cursor: "pointer",
  },
  btnAdd: {
    background: "#0C2340", color: "#fff", border: "none",
    borderRadius: 20, padding: "9px 20px", fontSize: 13,
    fontWeight: 600, cursor: "pointer", fontFamily: "inherit",
    whiteSpace: "nowrap",
  },
  btnDisabled: {
    background: "#B5D4F4", color: "#0C2340", border: "none",
    borderRadius: 20, padding: "9px 20px", fontSize: 13,
    cursor: "not-allowed", fontFamily: "inherit", whiteSpace: "nowrap",
  },
  error: {
    marginTop: 10, background: "#FDE8E8", color: "#A32D2D",
    borderRadius: 6, padding: "8px 12px", fontSize: 12,
  },
  success: {
    marginTop: 10, background: "#E2F0D9", color: "#3B6D11",
    borderRadius: 6, padding: "8px 12px", fontSize: 12,
  },
  groupCard: {
    background: "#fff", border: "0.5px solid #E0DEDD",
    borderRadius: 10, padding: "16px 20px",
  },
  groupHeader: {
    display: "flex", alignItems: "center", gap: 8, marginBottom: 12,
  },
  groupTitle: { fontSize: 13, fontWeight: 600, color: "#0C2340" },
  groupCount: {
    background: "#E6F1FB", color: "#185FA5", fontSize: 11,
    fontWeight: 600, borderRadius: 10, padding: "2px 8px",
  },
  tagList: { display: "flex", flexWrap: "wrap", gap: 8 },
  tag: {
    display: "flex", alignItems: "center", gap: 6,
    background: "#F7F5F0", border: "0.5px solid #D3D1C7",
    borderRadius: 6, padding: "5px 10px",
  },
  tagText: { fontSize: 12, color: "#0C2340" },
  tagDelete: {
    background: "none", border: "none", color: "#888780",
    cursor: "pointer", lineHeight: 1, padding: 0,
    display: "flex", alignItems: "center",
  },
  empty: { fontSize: 12, color: "#B4B2A9", fontStyle: "italic" },
  loading: { padding: 40, textAlign: "center", color: "#5F5E5A" },
};