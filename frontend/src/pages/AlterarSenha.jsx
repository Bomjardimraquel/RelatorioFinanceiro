import { useState } from "react";
import { alterarSenha } from "../services/api";

export default function AlterarSenha() {
  const [senhaAtual, setSenhaAtual] = useState("");
  const [novaSenha, setNovaSenha]   = useState("");
  const [confirmar, setConfirmar]   = useState("");
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState("");
  const [success, setSuccess]       = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (novaSenha !== confirmar) {
      setError("As senhas não coincidem");
      return;
    }
    if (novaSenha.length < 6) {
      setError("A nova senha deve ter pelo menos 6 caracteres");
      return;
    }
    setLoading(true);
    try {
      await alterarSenha(senhaAtual, novaSenha);
      setSuccess("Senha alterada com sucesso!");
      setSenhaAtual("");
      setNovaSenha("");
      setConfirmar("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.main}>
      <div style={styles.topbar}>
        <div style={styles.topbarTitle}>Alterar senha</div>
        <div style={styles.topbarSub}>Atualize sua senha de acesso</div>
      </div>

      <div style={styles.content}>
        <div style={styles.card}>
          <form onSubmit={handleSubmit}>
            <Field label="Senha atual" value={senhaAtual} onChange={setSenhaAtual} />
            <Field label="Nova senha" value={novaSenha} onChange={setNovaSenha} />
            <Field label="Confirmar nova senha" value={confirmar} onChange={setConfirmar} />

            {error   && <div style={styles.error}>{error}</div>}
            {success && <div style={styles.success}>{success}</div>}

            <button style={loading ? styles.btnDisabled : styles.btn} type="submit" disabled={loading}>
              {loading ? "Salvando..." : "Salvar nova senha"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, onChange }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <label style={styles.label}>{label}</label>
      <input
        style={styles.input}
        type="password"
        placeholder="••••••••"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
      />
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
  content: { padding: "22px 28px" },
  card: {
    background: "#fff", border: "0.5px solid #E0DEDD",
    borderRadius: 12, padding: "28px", maxWidth: 400,
  },
  label: {
    display: "block", fontSize: 11, fontWeight: 600,
    color: "#5F5E5A", textTransform: "uppercase",
    letterSpacing: "0.6px", marginBottom: 7,
  },
  input: {
    width: "100%", border: "0.5px solid #D3D1C7", borderRadius: 8,
    padding: "10px 14px", fontSize: 14, color: "#0C2340",
    background: "#F7F5F0", outline: "none", boxSizing: "border-box",
    fontFamily: "inherit",
  },
  btn: {
    width: "100%", background: "#0C2340", color: "#fff", border: "none",
    borderRadius: 24, padding: 13, fontSize: 14, fontWeight: 600,
    cursor: "pointer", marginTop: 8, fontFamily: "inherit",
    boxShadow: "0 4px 14px rgba(12,35,64,0.18)",
  },
  btnDisabled: {
    width: "100%", background: "#B5D4F4", color: "#0C2340", border: "none",
    borderRadius: 24, padding: 13, fontSize: 14, cursor: "not-allowed",
    fontFamily: "inherit",
  },
  error: {
    background: "#FDE8E8", color: "#A32D2D",
    borderRadius: 6, padding: "8px 12px", fontSize: 12, marginBottom: 12,
  },
  success: {
    background: "#E2F0D9", color: "#3B6D11",
    borderRadius: 6, padding: "8px 12px", fontSize: 12, marginBottom: 12,
  },
};




























































































































































































