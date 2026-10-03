import React, { createContext, useContext, useEffect, useState } from "react";
import api from "../api/api";

const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [userId, setUserId] = useState(() => {
    const stored = localStorage.getItem("aiFitnessUserId");
    return stored ? Number(stored) : null;
  });
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const refreshUser = async (id = userId) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getUser(id);
      setUser(data);
    } catch (e) {
      setError(e.message);
      // stored id was invalid (e.g. fresh backend db) -> clear it
      localStorage.removeItem("aiFitnessUserId");
      setUserId(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) refreshUser(userId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = (id) => {
    localStorage.setItem("aiFitnessUserId", String(id));
    setUserId(id);
    refreshUser(id);
  };

  const logout = () => {
    localStorage.removeItem("aiFitnessUserId");
    setUserId(null);
    setUser(null);
  };

  return (
    <UserContext.Provider value={{ userId, user, loading, error, login, logout, refreshUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
