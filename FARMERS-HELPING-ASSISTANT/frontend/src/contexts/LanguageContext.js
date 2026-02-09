import React, { createContext, useState, useContext, useEffect } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en');
  const [translations, setTranslations] = useState({});

  useEffect(() => {
    loadTranslations(language);
  }, [language]);

  const loadTranslations = async (lang) => {
    try {
      const response = await fetch(`http://localhost:8000/translations/${lang}`);
      const data = await response.json();
      setTranslations(data.translations);
    } catch (error) {
      console.error('Failed to load translations:', error);
    }
  };

  const changeLanguage = (newLang) => {
    setLanguage(newLang);
  };

  const translate = (key) => {
    const keys = key.split('.');
    let value = translations;
    
    for (const k of keys) {
      value = value?.[k];
      if (value === undefined) return key;
    }
    
    return value || key;
  };

  const value = {
    language,
    translations,
    changeLanguage,
    translate
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};