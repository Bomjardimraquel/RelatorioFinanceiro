const BASE_URL = "http://localhost:8000";

// ── Token management ─────────────────────────────────────────────────────────
const getToken = () => localStorage.getItem("access_token");
const getRefreshToken = () => localStorage.getItem("refresh_token");

const saveTokens = (access, refresh) => {
  localStorage.setItem("access_token", access);
  if (refresh) localStorage.setItem("refresh_token", refresh);
};

const clearTokens = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
};

// ── Fetch com refresh automático ─────────────────────────────────────────────
const fetchWithAuth = async (url, options = {}) => {
  const token = getToken();
  const headers = {
    ...options.headers,
    Authorization: `Bearer ${token}`,
  };

  let res = await fetch(`${BASE_URL}${url}`, { ...options, headers });

  // Token expirado — tenta refresh
  if (res.status === 401) {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearTokens();
      window.location.href = "/login";
      return;
    }

    const refreshRes = await fetch(`${BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!refreshRes.ok) {
      clearTokens();
      window.location.href = "/login";
      return;
    }

    const { access_token } = await refreshRes.json();
    saveTokens(access_token, null);

    // Retry com novo token
    res = await fetch(`${BASE_URL}${url}`, {
      ...options,
      headers: { ...options.headers, Authorization: `Bearer ${access_token}` },
    });
  }

  return res;
};

// ── Auth ──────────────────────────────────────────────────────────────────────
export const login = async (username, password) => {
  const body = new URLSearchParams({ username, password });
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao fazer login");
  }

  const data = await res.json();
  saveTokens(data.access_token, data.refresh_token);
  localStorage.setItem("user", JSON.stringify({ full_name: data.full_name }));
  return data;
};

export const logout = () => {
  clearTokens();
  window.location.href = "/login";
};

export const getMe = async () => {
  const res = await fetchWithAuth("/auth/me");
  if (!res.ok) throw new Error("Não autenticado");
  return res.json();
};

export const alterarSenha = async (senha_atual, nova_senha) => {
  const res = await fetchWithAuth("/auth/alterar-senha", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ senha_atual, nova_senha }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao alterar senha");
  }
  return res.json();
};

// ── Relatório ─────────────────────────────────────────────────────────────────
export const gerarRelatorio = async (file, provisao = 0) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("provisao", provisao);

  const res = await fetchWithAuth("/relatorio", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao gerar relatório");
  }

  const dadosHeader = res.headers.get("X-Dados");
  console.log("HEADER X-Dados:", dadosHeader);
  const dados = dadosHeader ? JSON.parse(dadosHeader) : {};
  const blob = await res.blob();

  return {
    blob,
    nomeArquivo: dados.nomeArquivo || "Relatorio.xlsx",
    resumo: dados,
  };
};

// ── Categorias ────────────────────────────────────────────────────────────────
export const getCategorias = async () => {
  const res = await fetchWithAuth("/categorias");
  if (!res.ok) throw new Error("Erro ao buscar categorias");
  return res.json();
};

export const addCategoria = async (nome, grupo) => {
  const res = await fetchWithAuth("/categorias", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome, grupo }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao adicionar categoria");
  }
  return res.json();
};

export const deleteCategoria = async (grupo, nome) => {
  const nomeEncoded = nome.replace(" | ", "__PIPE__");
  const res = await fetchWithAuth(`/categorias/${grupo}/${encodeURIComponent(nomeEncoded)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao remover categoria");
  }
  return res.json();
};