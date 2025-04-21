"use client"

import { createContext, useContext, useState, useEffect } from "react"

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    // Inicializar desde localStorage o preferencia del sistema
    if (typeof window !== "undefined") {
      return (
        localStorage.getItem("theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
      )
    }
    return "light"
  })

  useEffect(() => {
    // Aplicar el tema al documento
    if (theme === "dark") {
      document.documentElement.classList.add("dark-theme")
      document.body.classList.add("dark-mode-body")
    } else {
      document.documentElement.classList.remove("dark-theme")
      document.body.classList.remove("dark-mode-body")
    }

    // Guardar en localStorage
    localStorage.setItem("theme", theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider")
  }
  return context
}
