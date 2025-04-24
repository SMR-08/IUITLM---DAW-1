"use client"

import { useEffect } from "react" // Keep useEffect if needed for other purposes, otherwise remove
import { Brain, Home } from "lucide-react"
import { Link } from "react-router-dom"
import NLTKProcessor from "../components/nltk-processor"
import "../styles/nltk-page.css"
import { useTheme } from "../context/theme-context" // Import useTheme hook

export default function NLTKPage() {
  // Use the global theme context
  const { theme, toggleTheme } = useTheme();

  // Remove the local useState, useEffect, and toggleTheme function

  return (
    <div className="nltk-page">
      <header className="nltk-header">
        <div className="header-content">
          <div className="logo-section">
            <Brain className="brain-icon" size={28} />
            <h1>Procesamiento de Lenguaje Natural</h1>
          </div>
          <div className="main-nav">
            <Link to="/" className="nav-link">
              <Home size={18} />
              <span>Inicio</span>
            </Link>
            {/* Use the global toggleTheme function */}
            <button className="theme-toggle" onClick={toggleTheme} aria-label="Cambiar tema">
              <div className="toggle-ball"></div>
              <div className="sun-icon"></div>
              <div className="moon-icon"></div>
            </button>
          </div>
        </div>
      </header>

      <main className="nltk-main">
        <section className="hero-section">
          <div className="hero-content">
            <h2 className="hero-title">
              Análisis de texto con <span className="highlight">NLTK</span> y <span className="highlight">spaCy</span>
            </h2>
            <p className="hero-description">
              Herramientas avanzadas para el procesamiento de lenguaje natural en español e inglés. Analiza textos,
              identifica partes del discurso y compara traducciones en paralelo.
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
        </section>

        <section className="processor-container">
          <NLTKProcessor />
        </section>

        <section className="features-section">
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
              <p>Compara textos en español e inglés, alineando frases y mostrando sus estructuras gramaticales.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Procesamiento en Tiempo Real</h3>
              <p>Analiza textos automáticamente mientras escribes, con resultados inmediatos y visuales.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎨</div>
              <h3>Visualización por Colores</h3>
              <p>Sistema de colores intuitivo para identificar rápidamente las diferentes categorías gramaticales.</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="nltk-footer">
        <div className="footer-content">
          <div className="footer-logo">
            <Brain size={20} />
            NLP Tools
          </div>
          <div className="footer-links">
            <a href="#">Documentación</a>
            <a href="#">API</a>
            <a href="#">Recursos</a>
            <a href="#">Contacto</a>
          </div>
          <div className="footer-copyright">
            © {new Date().getFullYear()} Aplicaciones Web - Todos los derechos reservados
          </div>
        </div>
      </footer>
    </div>
  )
}
