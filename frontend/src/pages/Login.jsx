import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../services/api";
import { useAuth } from "../hooks/useAuth.jsx";
import { LedraIcon } from "../components/LedraIcon";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);
  const navigate                = useNavigate();
  const { setUserAfterLogin }   = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await login(username, password);
      setUserAfterLogin({ username, full_name: data.full_name });
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.brand}>
          <LedraIcon size={48} variant="dark" />
          <h1 style={styles.brandTitle}>Ledra</h1>
          <p style={styles.brandSub}>Acesse sua conta para continuar</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={styles.field}>
            <label style={styles.label}>Usuário</label>
            <input
              style={styles.input}
              type="text"
              placeholder="seu_usuario"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Senha</label>
            <input
              style={styles.input}
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <p style={styles.error}>{error}</p>}

          <button style={loading ? styles.btnDisabled : styles.btn} type="submit" disabled={loading}>
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <p style={styles.footer}>Desenvolvido por Raquel Bomjardim • 2026</p>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "#E6F1FB",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "'Inter', system-ui, sans-serif",
  },
  card: {
    background: "#fff",
    border: "0.5px solid #D3D1C7",
    borderRadius: 14,
    padding: "40px 36px",
    width: 360,
    boxShadow: "0 4px 24px rgba(12,35,64,0.08)",
  },
  brand: {
    textAlign: "center",
    marginBottom: 28,
  },
  brandTitle: {
    fontSize: 20,
    fontWeight: 600,
    color: "#0C2340",
    margin: "10px 0 4px",
    letterSpacing: "-0.3px",
  },
  brandSub: {
    fontSize: 13,
    color: "#5F5E5A",
    margin: 0,
  },
  field: { marginBottom: 16 },
  label: {
    display: "block",
    fontSize: 11,
    fontWeight: 600,
    color: "#5F5E5A",
    textTransform: "uppercase",
    letterSpacing: "0.6px",
    marginBottom: 7,
  },
  input: {
    width: "100%",
    border: "0.5px solid #D3D1C7",
    borderRadius: 8,
    padding: "10px 14px",
    fontSize: 14,
    color: "#0C2340",
    background: "#F7F5F0",
    outline: "none",
    boxSizing: "border-box",
    fontFamily: "inherit",
  },
  btn: {
    width: "100%",
    background: "#0C2340",
    color: "#F7F5F0",
    border: "none",
    borderRadius: 24,
    padding: "13px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    marginTop: 8,
    boxShadow: "0 4px 14px rgba(12,35,64,0.18)",
    fontFamily: "inherit",
  },
  btnDisabled: {
    width: "100%",
    background: "#B5D4F4",
    color: "#0C2340",
    border: "none",
    borderRadius: 24,
    padding: "13px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "not-allowed",
    marginTop: 8,
    fontFamily: "inherit",
  },
  error: {
    color: "#A32D2D",
    fontSize: 12,
    marginTop: -8,
    marginBottom: 8,
    background: "#FDE8E8",
    borderRadius: 6,
    padding: "8px 12px",
  },
  footer: {
    textAlign: "center",
    marginTop: 24,
    fontSize: 11,
    color: "#B4B2A9",
  },
};