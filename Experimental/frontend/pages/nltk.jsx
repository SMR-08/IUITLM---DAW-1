"use client"

import { useState } from "react"
import NLTKProcessor from "../components/nltk-processor"
import { Sun, Moon } from "lucide-react"

export default function NLTKPage() {
  const [darkMode, setDarkMode] = useState(false)

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    // Aplicar la clase directamente al elemento body
    if (!darkMode) {
      document.body.classList.add("dark-mode-body")
    } else {
      document.body.classList.remove("dark-mode-body")
    }
  }

  return (
    <div className={`App ${darkMode ? "dark-mode" : ""}`}>
      <header className="App-header">
        <div className="logo-container">
          <h1>Procesamiento de Lenguaje Natural</h1>
        </div>
        <button
          className="theme-toggle"
          onClick={toggleDarkMode}
          aria-label={darkMode ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
        >
          {darkMode ? <Sun size={24} /> : <Moon size={24} />}
        </button>
      </header>

      <main className="App-main">
        <div className="hero-section">
          <h2 className="hero-title">NLTK y spaCy</h2>
          <p className="hero-subtitle">Herramientas para el procesamiento de lenguaje natural en español e inglés</p>
        </div>

        <NLTKProcessor />
      </main>

      <footer className="App-footer">
        <p>© {new Date().getFullYear()} Aplicaciones Web - Todos los derechos reservados</p>
      </footer>
    </div>
  )
}
