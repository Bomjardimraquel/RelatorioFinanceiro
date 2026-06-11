import { useState, useEffect, createContext, useContext } from "react";
import { getMe, logout as apiLogout } from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }
    getMe()
      .then((data) => setUser(data))
      .catch(() => {
        localStorage.clear();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const logout = () => {
    setUser(null);
    apiLogout();
  };

  const setUserAfterLogin = (userData) => setUser(userData);

  return (
    <AuthContext.Provider value={{ user, loading, logout, setUserAfterLogin }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);