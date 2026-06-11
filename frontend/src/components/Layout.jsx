import { NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";
import { LedraIcon } from "./LedraIcon";

const initials = (name) =>
  name ? name.split(" ").map((n) => n[0]).slice(0, 2).join("").toUpperCase() : "?";

export default function Layout({ children }) {
  const { user, logout } = useAuth();

  return (
    <div style={styles.shell}>
      <div style={styles.sidebar}>
        <div style={styles.logo}>
          <LedraIcon size={32} variant="dark" />
          <span style={styles.logoText}>Ledra</span>
        </div>

        <nav style={styles.nav}>
          <NavItem to="/dashboard" label="Relatório" icon="ti-chart-bar" />
          <NavItem to="/categorias" label="Categorias" icon="ti-tags" />
          <NavItem to="/alterar-senha" label="Senha" icon="ti-lock" />
        </nav>

        <div style={styles.user}>
          <div style={styles.avatar}>{initials(user?.full_name || "")}</div>
          <div>
            <div style={styles.userName}>{user?.full_name || user?.username}</div>
            <button style={styles.logoutBtn} onClick={logout}>Sair</button>
          </div>
        </div>
      </div>

      <div style={styles.main}>{children}</div>
    </div>
  );
}

function NavItem({ to, label, icon }) {
  return (
    <NavLink
      to={to}
      style={({ isActive }) => ({
        ...styles.navItem,
        ...(isActive ? styles.navItemActive : {}),
      })}
    >
      <i className={`ti ${icon}`} aria-hidden="true" style={{ fontSize: 16 }}></i>
      {label}
    </NavLink>
  );
}

const styles = {
  shell: {
    display: "flex",
    minHeight: "100vh",
    fontFamily: "'Inter', system-ui, sans-serif",
    background: "#F7F5F0",
  },
  sidebar: {
    width: 210,
    background: "#fff",
    borderRight: "0.5px solid #E0DEDD",
    display: "flex",
    flexDirection: "column",
    flexShrink: 0,
  },
  logo: {
    padding: "20px 20px 16px",
    borderBottom: "0.5px solid #E0DEDD",
    display: "flex",
    alignItems: "center",
    gap: 10,
  },
  logoText: {
    fontSize: 15,
    fontWeight: 600,
    color: "#0C2340",
    letterSpacing: "-0.3px",
  },
  nav: { padding: "10px 0", flex: 1 },
  navItem: {
    display: "flex",
    alignItems: "center",
    gap: 9,
    padding: "10px 20px",
    fontSize: 13,
    color: "#5F5E5A",
    textDecoration: "none",
    borderLeft: "2.5px solid transparent",
  },
  navItemActive: {
    background: "#E6F1FB",
    color: "#0C2340",
    fontWeight: 600,
    borderLeft: "2.5px solid #185FA5",
  },
  user: {
    padding: "14px 20px",
    borderTop: "0.5px solid #E0DEDD",
    display: "flex",
    alignItems: "center",
    gap: 10,
  },
  avatar: {
    width: 30,
    height: 30,
    borderRadius: "50%",
    background: "#B5D4F4",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 11,
    fontWeight: 700,
    color: "#0C447C",
    flexShrink: 0,
  },
  userName: { fontSize: 12.5, fontWeight: 600, color: "#0C2340" },
  logoutBtn: {
    background: "none",
    border: "none",
    fontSize: 11,
    color: "#888780",
    cursor: "pointer",
    padding: 0,
    fontFamily: "inherit",
  },
  main: { flex: 1, display: "flex", flexDirection: "column" },
};