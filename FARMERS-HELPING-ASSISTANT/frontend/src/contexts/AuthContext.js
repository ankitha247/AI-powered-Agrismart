import React, { createContext, useState, useContext } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  const login = async (email, password) => {
    setLoading(true);
    try {
      // Simulate API call - will connect to backend
      setTimeout(() => {
        setUser({
          id: '1',
          name: 'Test Farmer',
          email: email,
          language: 'en'
        });
        setLoading(false);
      }, 1000);
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const signup = async (userData) => {
    setLoading(true);
    try {
      // Simulate API call - will connect to backend
      setTimeout(() => {
        setUser({
          id: '1',
          name: userData.name,
          email: userData.email,
          language: userData.language
        });
        setLoading(false);
      }, 1000);
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
  };

  const value = {
    user,
    login,
    signup,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};