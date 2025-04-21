"use client"

import { useState, useEffect } from "react"
import NLTKProcessor from "../components/nltk-processor"
import { Code, Brain, Languages, Sparkles, Github } from "lucide-react"
import "../styles/nltk-page.css"

export default function NLTKPage() {
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== "undefined") {
      const savedMode = localStorage.getItem("darkMode")
      return savedMode ? JSON.parse(savedMode) : window.matchMedia("(prefers-color-scheme: dark)").matches
    }
    return false
  })

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark-theme")
    } else {
      document.documentElement.classList.remove("dark-theme")
    }
    localStorage.setItem("darkMode", JSON.stringify(darkMode))
  }, [darkMode])

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
  }

  return (
    <div className="nltk-page">
      <header className="nltk-header">
        <div className="header-content">
          <div className="logo-section">
            <Brain className="brain-icon" />
            <h1>NLP Lab</h1>
          </div>
          <nav className="main-nav">
            <a href="/" className="nav-link">
              <Code size={18} />
              <span>Inicio</span>
            </a>
            <a href="#" className="nav-link active">
              <Languages size={18} />
              <span>NLTK & spaCy</span>
            </a>
            <a href="#" className="nav-link">
              <Sparkles size={18} />
              <span>Ejemplos</span>
            </a>
            <a href="https://github.com" className="nav-link">
              <Github size={18} />
              <span>GitHub</span>
            </a>
          </nav>
          <button className="theme-toggle" onClick={toggleDarkMode}>
            <span className="sun-icon"></span>
            <span className="moon-icon"></span>
            <span className="toggle-ball"></span>
          </button>
        </div>
      </header>

      <main className="nltk-main">
        <div className="hero-section">
          <div className="hero-content">
            <h1 className="hero-title">
              Procesamiento de <span className="highlight">Lenguaje Natural</span>
            </h1>
            <p className="hero-description">
              Analiza textos en español e inglés utilizando las bibliotecas NLTK y spaCy. Identifica partes del
              discurso, compara textos paralelos y visualiza resultados con etiquetas coloreadas.
            </p>
            <div className="tech-badges">
              <span className="badge nltk">NLTK</span>
              <span className="badge spacy">spaCy</span>
              <span className="badge python">Python</span>
              <span className="badge react">React</span>
            </div>
          </div>
          <div className="hero-image">
            <div className="nlp-illustration">
              <div className="code-lines">
                <div className="code-line"></div>
                <div className="code-line"></div>
                <div className="code-line"></div>
                <div className="code-line"></div>
                <div className="code-line"></div>
              </div>
              <div className="nlp-nodes">
                <div className="node n1"></div>
                <div className="node n2"></div>
                <div className="node n3"></div>
                <div className="node n4"></div>
                <div className="node n5"></div>
                <div className="node n6"></div>
                <div className="connector c1"></div>
                <div className="connector c2"></div>
                <div className="connector c3"></div>
                <div className="connector c4"></div>
                <div className="connector c5"></div>
              </div>
            </div>
          </div>
        </div>

        <div className="processor-container">
          <NLTKProcessor />
        </div>

        <div className="features-section">
          <h2 className="section-title">Características</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Análisis Morfológico</h3>
              <p>
                Identifica sustantivos, verbos, adjetivos y otras partes del discurso en textos en español e inglés.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔄</div>
              <h3>Procesamiento Paralelo</h3>
              <p>Compara y alinea textos en diferentes idiomas utilizando el algoritmo Gale-Church.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎨</div>
              <h3>Visualización Intuitiva</h3>
              <p>Visualiza los resultados con un sistema de etiquetas coloreadas para facilitar la interpretación.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Procesamiento en Tiempo Real</h3>
              <p>Obtén resultados instantáneos mientras escribes gracias al procesamiento automático.</p>
            </div>
          </div>
        </div>
      </main>

      <footer className="nltk-footer">
        <div className="footer-content">
          <div className="footer-logo">
            <Brain size={24} />
            <span>NLP Lab</span>
          </div>
          <div className="footer-links">
            <a href="#">Documentación</a>
            <a href="#">API</a>
            <a href="#">Recursos</a>
            <a href="#">Contacto</a>
          </div>
          <div className="footer-copyright">
            <p>© {new Date().getFullYear()} NLP Lab - Todos los derechos reservados</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
