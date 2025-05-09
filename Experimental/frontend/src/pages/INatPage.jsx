// frontend/src/pages/INatPage.jsx
"use client"

import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useTheme } from "../context/theme-context";
import { Home, Leaf, UploadCloud, AlertTriangle, Image as ImageIcon, RotateCcw, Search, BookOpen } from "lucide-react"; // Añadido BookOpen
import "../styles/iNatPage.css";

const INatPage = () => {
    const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setPredictions([]);
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      setPreviewUrl(URL.createObjectURL(file));
    } else {
      setSelectedFile(null);
      setPreviewUrl(null);
    }
  };
  const { theme, toggleTheme } = useTheme();

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [topSpeciesDescription, setTopSpeciesDescription] = useState(null); // Nuevo estado para la descripción
  const [isLoadingDescription, setIsLoadingDescription] = useState(false); // Nuevo estado para carga de descripción

  const API_URL = process.env.REACT_APP_INAT_API_URL || "http://150.214.56.73:7690/predict/";

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const fetchWikipediaDescription = async (speciesName) => {
    if (!speciesName) return;
    setIsLoadingDescription(true);
    setTopSpeciesDescription(null); // Limpiar descripción anterior

    // Usar el proxy de allorigins para evitar problemas de CORS (si Wikipedia los da directamente)
    // O intentar directamente si tu entorno lo permite (menos probable para Wikipedia)
    const searchTerm = encodeURIComponent(speciesName.replace(/\s+/g, '_')); // Reemplazar espacios con guiones bajos para URL de Wikipedia
    
    // Endpoint de la API de MediaWiki para obtener el extracto (primer párrafo)
    // `exintro=true` pide solo el contenido antes de la primera sección.
    // `explaintext=true` pide texto plano en lugar de HTML.
    // `redirects=1` para seguir redirecciones.
    const WIKIPEDIA_API_URL = `https://es.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=true&explaintext=true&redirects=1&origin=*&titles=${searchTerm}`;
    // El parámetro `origin=*` es crucial para intentar permitir CORS desde Wikipedia.

    try {
      const response = await fetch(WIKIPEDIA_API_URL);
      if (!response.ok) {
        throw new Error(`Error al contactar la API de Wikipedia: ${response.status}`);
      }
      const data = await response.json();
      const pages = data.query.pages;
      const pageId = Object.keys(pages)[0]; // Obtener el ID de la primera página encontrada

      if (pageId && pages[pageId].extract) {
        let description = pages[pageId].extract;
        // Limitar la longitud para no mostrar textos demasiado largos
        if (description.length > 500) {
            description = description.substring(0, 500) + "...";
        }
        setTopSpeciesDescription(description);
      } else if (pages[pageId] && pages[pageId].missing !== undefined) {
        setTopSpeciesDescription(`No se encontró una página en Wikipedia para "${speciesName}".`);
      }
       else {
        setTopSpeciesDescription(`No se pudo obtener una descripción para "${speciesName}".`);
      }
    } catch (err) {
      console.error("Error fetching Wikipedia description:", err);
      setTopSpeciesDescription(`Error al obtener descripción: ${err.message}`);
    } finally {
      setIsLoadingDescription(false);
    }
  };


  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Por favor, selecciona una imagen primero.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setPredictions([]);
    setTopSpeciesDescription(null); // Limpiar descripción al hacer nueva predicción

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let errorData;
        try { errorData = await response.json(); }
        catch (e) { errorData = { detail: `Error del servidor: ${response.status} ${response.statusText}` }; }
        throw new Error(errorData.detail || `Error ${response.status}`);
      }

      const data = await response.json();
      if (data.predictions && data.predictions.length > 0) {
        const processedPredictions = data.predictions.map(pred => ({
            ...pred,
            probabilityValue: parseFloat(pred.probability.replace('%', ''))
        }));
        setPredictions(processedPredictions);
        // Obtener descripción de la especie más probable
        if (processedPredictions[0] && processedPredictions[0].label) {
            fetchWikipediaDescription(processedPredictions[0].label);
        }
      } else {
        setError("No se recibieron predicciones válidas del servidor.");
      }
    } catch (err) {
      console.error("Error en la clasificación:", err);
      setError(err.message || "Ocurrió un error al procesar la imagen.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setPredictions([]);
    setError(null);
    setTopSpeciesDescription(null); // Limpiar descripción al resetear
    setIsLoadingDescription(false);
    if (document.getElementById('inat-file-input')) {
        document.getElementById('inat-file-input').value = "";
    }
  };

  const getBarColor = (probabilityValue) => { // Tu función getBarColor aquí (sin cambios)
    const colorSuccess = 'var(--success-color, rgb(76, 175, 80))';
    const colorWarningHigh = 'var(--warning-high-color, rgb(173, 255, 47))';
    const colorWarningLow = 'var(--warning-low-color, rgb(255, 165, 0))';
    const colorDanger = 'var(--danger-color, rgb(183, 28, 28))';

    if (isNaN(probabilityValue)) return 'grey';

    if (probabilityValue >= 90) {
      return colorSuccess;
    } else if (probabilityValue >= 60) {
      const factor = (probabilityValue - 60) / (90 - 60);
      const r = Math.round(255 + factor * (173 - 255));
      const g = Math.round(165 + factor * (255 - 165));
      const b = Math.round(0 + factor * (47 - 0));
      return `rgb(${r}, ${g}, ${b})`;
    } else {
      const factor = probabilityValue / 60;
      const r = Math.round(183 + factor * (255 - 183));
      const g = Math.round(28 + factor * (165 - 28));
      const b = Math.round(28 + factor * (0 - 28));
      return `rgb(${r}, ${g}, ${b})`;
    }
  };

  const handleSearchSpecies = (speciesName) => {
    const query = encodeURIComponent(speciesName);
    window.open(`https://www.google.com/search?q=${query}`, '_blank');
  };


  return (
    <div className={`inat-page ${theme === "dark" ? "dark-theme-page-specific" : ""}`}>
      {/* ... Header sin cambios ... */}
      <header className="inat-header">
        <div className="header-content-inat">
          <div className="logo-section-inat">
            <Leaf className="leaf-icon" size={28} />
            <h1>Clasificador de Especies</h1>
          </div>
          <div className="main-nav-inat">
            <Link to="/" className="nav-link-inat">
              <Home size={18} />
              <span>Inicio</span>
            </Link>
            <button
              className="theme-toggle-inat"
              onClick={toggleTheme}
              aria-label="Cambiar tema"
            >
              <div className="toggle-ball-inat"></div>
              <div className="sun-icon-inat"></div>
              <div className="moon-icon-inat"></div>
            </button>
          </div>
        </div>
      </header>

      <main className="inat-main">
        {/* ... Hero Section sin cambios ... */}
        <section className="inat-hero-section">
          <h2 className="inat-hero-title">
            Identifica Especies con IA
          </h2>
          <p className="inat-hero-description">
            Sube una imagen de un animal y nuestra inteligencia artificial
            predecirá la especie más probable.
          </p>
        </section>

        <section className="inat-classifier-section">
          {/* ... Upload Area sin cambios ... */}
          <div className="inat-upload-area">
            <label htmlFor="inat-file-input" className="inat-file-label">
              <UploadCloud size={24} />
              <span>{selectedFile ? selectedFile.name : "Selecciona o arrastra una imagen"}</span>
              <input
                type="file"
                id="inat-file-input"
                accept="image/png, image/jpeg, image/jpg,image/webp"
                onChange={handleFileChange}
                disabled={isLoading}
              />
            </label>

            <div className="inat-actions">
                <button
                    onClick={handleSubmit}
                    className="inat-submit-button"
                    disabled={!selectedFile || isLoading}
                >
                    {isLoading ? (
                    <>
                        <div className="spinner"></div> Procesando...
                    </>
                    ) : (
                    "Clasificar Imagen"
                    )}
                </button>
                { (selectedFile || predictions.length > 0 || error) && !isLoading && (
                    <button
                        onClick={handleReset}
                        className="inat-reset-button"
                        title="Limpiar selección y resultados"
                    >
                        <RotateCcw size={18} />
                    </button>
                )}
            </div>
          </div>

          {error && (
            <div className="inat-error-message">
              <AlertTriangle size={20} />
              <span>{error}</span>
            </div>
          )}

          {/* Contenedor para imagen y resultados */}
          {(predictions.length > 0 || previewUrl) && !isLoading && (
            <div className="inat-content-with-results">
                {previewUrl && (
                    <div className="inat-image-display-area">
                        <img src={previewUrl} alt="Imagen subida" className="inat-displayed-image" />
                    </div>
                )}

                {predictions.length > 0 && (
                    <div className="inat-results-section">
                    <h3>Predicciones Principales:</h3>
                    <ul className="inat-predictions-list">
                        {predictions.map((pred, index) => {
                            const barColor = getBarColor(pred.probabilityValue);
                            return (
                                <li key={index} className="inat-prediction-item">
                                    <span className="inat-prediction-label">{pred.label}</span>
                                    <div className="inat-prediction-bar-container">
                                        <div
                                            className="inat-prediction-bar"
                                            style={{
                                                width: `${pred.probabilityValue}%`,
                                                backgroundColor: barColor
                                            }}
                                        ></div>
                                    </div>
                                    <span className="inat-prediction-probability">{pred.probability}</span>
                                    <button
                                        onClick={() => handleSearchSpecies(pred.label)}
                                        className="inat-search-button"
                                        title={`Buscar "${pred.label}"`}
                                    >
                                        <Search size={16} />
                                    </button>
                                </li>
                            );
                        })}
                    </ul>
                    </div>
                )}
            </div>
          )}

          {/* NUEVA SECCIÓN PARA LA DESCRIPCIÓN DE WIKIPEDIA */}
          {isLoadingDescription && (
            <div className="inat-description-loading">
                <div className="spinner-description"></div>
                <span>Cargando descripción desde Wikipedia...</span>
            </div>
          )}
          {topSpeciesDescription && !isLoadingDescription && (
            <div className="inat-species-description-section">
                <div className="description-header">
                    <BookOpen size={20} />
                    <h4>Descripción de {predictions[0]?.label || "la especie"} (Wikipedia)</h4>
                </div>
                <p className="description-text">{topSpeciesDescription}</p>
            </div>
          )}

        </section>
      </main>

      {/* ... Footer sin cambios ... */}
      <footer className="inat-footer">
        <div className="footer-content-inat">
          <p>© {new Date().getFullYear()} Clasificador iNat</p>
        </div>
      </footer>
    </div>
  );
};

export default INatPage;