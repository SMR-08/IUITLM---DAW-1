"use client";

import { useState, useEffect, useRef } from "react";
import { Sun, Moon, ExternalLink } from 'lucide-react';
import "./nltk-processor.css";

const NLTKProcessor = () => {
  // --- Estado ---
  const [modoActual, setModoActual] = useState("simple");
  const [modoVistaEtiquetas, setModoVistaEtiquetas] = useState("color");
  const [textoSimple, setTextoSimple] = useState("");
  const [textoEs, setTextoEs] = useState("");
  const [textoEn, setTextoEn] = useState("");
  const [idiomaSimple, setIdiomaSimple] = useState("es");
  const [mensaje, setMensaje] = useState({ texto: "", tipo: "", visible: false });
  const [procesando, setProcesando] = useState(false);
  const [ultimoResultadoSimple, setUltimoResultadoSimple] = useState({
    resultado: [],
    idioma_procesado: "es",
  });
  const [ultimoResultadoParalelo, setUltimoResultadoParalelo] = useState({
    alineacion: [],
    datos_es: [],
    datos_en: [],
  });

  // --- Referencias ---
  const debounceTimeoutRef = useRef(null);

  // --- Constantes ---
  const DEBOUNCE_DELAY = 800;

  // Paletas de colores
  const coloresPosTagNLTK = {
    NN: "#FFAB91", NNS: "#FFAB91", NNP: "#FF8A65", NNPS: "#FF8A65",
    VB: "#80CBC4", VBD: "#4DB6AC", VBG: "#26A69A", VBN: "#009688", VBP: "#80CBC4", VBZ: "#4DB6AC",
    JJ: "#9FA8DA", JJR: "#7986CB", JJS: "#5C6BC0",
    RB: "#CE93D8", RBR: "#BA68C8", RBS: "#AB47BC",
    DT: "#FFF59D", IN: "#A1887F",
    PRP: "#90CAF9", "PRP$": "#64B5F6", WP: "#90CAF9", "WP$": "#64B5F6", WRB: "#CE93D8",
    CC: "#BCAAA4", CD: "#B0BEC5", MD: "#B39DDB", RP: "#C5E1A5", TO: "#F48FB1", UH: "#FFCC80",
    ".": "#CFD8DC", ",": "#CFD8DC", ":": "#CFD8DC", "(": "#CFD8DC", ")": "#CFD8DC",
    "``": "#CFD8DC", "''": "#CFD8DC", "$": "#CFD8DC", FW: "#E0E0E0",
    DEFAULT: "#ECEFF1",
  };

  const coloresPosTagUD = {
    NOUN: "#FFAB91", PROPN: "#FF8A65", VERB: "#80CBC4", ADJ: "#9FA8DA", ADV: "#CE93D8",
    DET: "#FFF59D", ADP: "#A1887F", PRON: "#90CAF9", AUX: "#B39DDB",
    CCONJ: "#BCAAA4", SCONJ: "#A1887F", NUM: "#B0BEC5", PART: "#C5E1A5", INTJ: "#FFCC80",
    PUNCT: "#CFD8DC", SYM: "#CFD8DC", SPACE: "#FFFFFF", X: "#ECEFF1",
    DEFAULT: "#ECEFF1",
  };

  // --- Funciones Auxiliares ---
  const fetchApi = async (endpoint, options = {}) => {
    const apiUrlBase = "http://api.localhost";
    const defaultOptions = {
      method: options.body ? "POST" : "GET",
      headers: {
        ...(options.body && typeof options.body === "string" && options.body.startsWith("{")
          ? { "Content-Type": "application/json" }
          : {}),
        ...options.headers,
      },
    };
    const finalOptions = { ...defaultOptions, ...options };

    try {
      const response = await fetch(`${apiUrlBase}${endpoint}`, finalOptions);
      let data = null;
      const contentType = response.headers.get("content-type");
      if (response.ok || (contentType && contentType.indexOf("application/json") !== -1)) {
        try {
          if (response.status === 204 || response.headers.get("Content-Length") === "0") {
            data = {};
          } else {
            data = await response.json();
          }
        } catch (jsonError) {
          console.error("Error parseando JSON:", response.url, jsonError);
          if (response.ok) return {};
          throw new Error("Respuesta inesperada del servidor (no JSON).");
        }
      }
      if (!response.ok) {
        const errorText = data?.error || (await response.text()) || `Error ${response.status}`;
        throw new Error(errorText);
      }
      return data;
    } catch (error) {
      console.error(`Error en fetchApi para ${finalOptions.method} ${endpoint}:`, error);
      throw new Error(error.message || "Error de red o al contactar la API.");
    }
  };

  const mostrarMensaje = (texto, tipo = "error") => {
    setMensaje({ texto, tipo, visible: true });
  };

  const ocultarMensaje = () => {
    setMensaje((prev) => ({ ...prev, visible: false }));
  };

  // --- Funciones de Procesamiento ---
  const procesarTextoSimple = async () => {
    const texto = textoSimple.trim();
    
    if (texto) {
      setProcesando(true);
      ocultarMensaje();
      mostrarMensaje("Enviando a la API...", "info");

      try {
        const datosProcesados = await fetchApi("/procesar_nlp", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ texto: texto, idioma: idiomaSimple }),
        });

        setUltimoResultadoSimple({
          resultado: datosProcesados.resultado || [],
          idioma_procesado: datosProcesados.idioma_procesado || idiomaSimple,
        });

        mostrarMensaje(datosProcesados.mensaje || "Procesado correctamente.", "success");
      } catch (error) {
        setUltimoResultadoSimple({ resultado: [], idioma_procesado: idiomaSimple });
        mostrarMensaje(error.message || "Error al contactar la API.", "error");
      } finally {
        setProcesando(false);
      }
    } else {
      setUltimoResultadoSimple({ resultado: [], idioma_procesado: idiomaSimple });
      ocultarMensaje();
    }
  };

  const procesarTextosParalelos = async () => {
    const textoEsValue = textoEs.trim();
    const textoEnValue = textoEn.trim();

    if (!textoEsValue || !textoEnValue) {
      mostrarMensaje("Introduce texto en AMBOS campos (ES y EN).", "error");
      return;
    }

    setProcesando(true);
    ocultarMensaje();
    mostrarMensaje("Enviando ambos textos a la API...", "info");

    try {
      const datosParalelos = await fetchApi("/procesar_paralelo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto_es: textoEsValue, texto_en: textoEnValue }),
      });

      setUltimoResultadoParalelo(datosParalelos || { alineacion: [], datos_es: [], datos_en: [] });

      let mensajeTipo = "success";
      let mensajeTexto = datosParalelos.mensaje || "Procesado correctamente.";
      
      if (datosParalelos.errores) {
        mensajeTipo = "warning";
        mensajeTexto += " (Se produjeron algunos errores en el etiquetado. Revisa los resultados.)";
        console.error("Errores parciales recibidos:", datosParalelos.errores);
      }
      
      mostrarMensaje(mensajeTexto, mensajeTipo);
    } catch (error) {
      setUltimoResultadoParalelo({ alineacion: [], datos_es: [], datos_en: [] });
      mostrarMensaje(error.message || "Error al contactar la API.", "error");
    } finally {
      setProcesando(false);
    }
  };

  // --- Componentes de Renderizado ---
  const SecuenciaTags = ({ datosTags, idioma, etiquetasGlobales }) => {
    if (!datosTags || datosTags.length === 0) {
      return <div>{idioma === "es" ? "(Sin datos para ES)" : "(Sin datos para EN)"}</div>;
    }

    const paletaActual = idioma === "es" ? coloresPosTagUD : coloresPosTagNLTK;
    const esEspañol = idioma === "es";

    return (
      <div className="tags-container">
        {datosTags.map(([palabra, tag], index) => {
          if (etiquetasGlobales && tag) {
            etiquetasGlobales.add(tag);
          }
          
          const tagKey = esEspañol ? tag?.toUpperCase() : tag;
          const color = paletaActual[tagKey] || paletaActual["DEFAULT"];
          
          return (
            <span
              key={index}
              className="tag-span"
              style={{ backgroundColor: color }}
            >
              <strong>{palabra}</strong>
              {modoVistaEtiquetas === "etiqueta" && (
                <sub className="tag-sub"> ({tag})</sub>
              )}
            </span>
          );
        })}
      </div>
    );
  };

  const LeyendaColores = ({ etiquetasSetEs, etiquetasSetEn }) => {
    const etiquetasMostradas = new Set();
    
    const renderLeyendaItem = (tag, idioma) => {
      const key = `${tag}_${idioma}`;
      if (etiquetasMostradas.has(key) || !tag) return null;
      
      const paleta = idioma === "es" ? coloresPosTagUD : coloresPosTagNLTK;
      const tagKey = idioma === "es" ? tag.toUpperCase() : tag;
      const color = paleta[tagKey] || paleta["DEFAULT"];
      
      etiquetasMostradas.add(key);
      
      return (
        <span
          key={key}
          className="leyenda-item"
          style={{ backgroundColor: color }}
        >
          {tag} ({idioma.toUpperCase()})
        </span>
      );
    };

    return (
      <div className="leyenda-colores">
        <strong>Leyenda:</strong>{" "}
        {etiquetasSetEs && Array.from(etiquetasSetEs).map(tag => renderLeyendaItem(tag, "es"))}
        {etiquetasSetEn && Array.from(etiquetasSetEn).map(tag => renderLeyendaItem(tag, "en"))}
        {(!etiquetasSetEs || etiquetasSetEs.size === 0) && 
         (!etiquetasSetEn || etiquetasSetEn.size === 0) && 
         " Esperando procesamiento..."}
      </div>
    );
  };

  const ResultadoSimple = () => {
    const etiquetasGlobales = new Set();
    
    return (
      <div className="resultado-simple">
        <h4 id="nlp-titulo-resultado">
          Resultado Procesado (<span id="nlp-idioma-mostrado">
            {ultimoResultadoSimple.idioma_procesado.toUpperCase()}
          </span>):
        </h4>
        
        <div className="output-area">
          {procesando ? (
            `Procesando (${idiomaSimple.toUpperCase()})...`
          ) : ultimoResultadoSimple.resultado.length > 0 ? (
            <SecuenciaTags
              datosTags={ultimoResultadoSimple.resultado}
              idioma={ultimoResultadoSimple.idioma_procesado}
              etiquetasGlobales={etiquetasGlobales}
            />
          ) : (
            "Introduce texto para procesar."
          )}
        </div>
        
        <LeyendaColores
          etiquetasSetEs={ultimoResultadoSimple.idioma_procesado === "es" ? etiquetasGlobales : null}
          etiquetasSetEn={ultimoResultadoSimple.idioma_procesado === "en" ? etiquetasGlobales : null}
        />
      </div>
    );
  };

  const ResultadoParalelo = () => {
    const etiquetasGlobalesEs = new Set();
    const etiquetasGlobalesEn = new Set();
    const { alineacion, datos_es, datos_en } = ultimoResultadoParalelo;

    if (procesando) {
      return <div className="output-area">Procesando y alineando textos...</div>;
    }

    if (!alineacion || !datos_es || !datos_en) {
      return <div className="output-area">Faltan datos para renderizar la alineación.</div>;
    }

    if (alineacion.length === 0 && (datos_es.length > 0 || datos_en.length > 0)) {
      return (
        <div className="output-area">
          <p><i>No se pudo generar alineación (Gale-Church). Mostrando frases secuencialmente (si existen).</i></p>
        </div>
      );
    }

    if (datos_es.length === 0 && datos_en.length === 0) {
      return <div className="output-area">No se encontraron frases en ninguna entrada.</div>;
    }

    return (
      <div className="resultado-paralelo">
        <h4 id="nlp-titulo-resultado">
          Resultado Procesado (ES/EN):
        </h4>
        
        <div className="output-area">
          {alineacion.map(([idxEs, idxEn], index) => {
            if (idxEs === null || idxEn === null || idxEs >= datos_es.length || idxEn >= datos_en.length) {
              return null;
            }

            return (
              <div key={index} className="bloque-alineado">
                <div className="columna-es">
                  {datos_es[idxEs] ? (
                    <>
                      <SecuenciaTags
                        datosTags={datos_es[idxEs].tags || []}
                        idioma="es"
                        etiquetasGlobales={etiquetasGlobalesEs}
                      />
                      {datos_es[idxEs].error && (
                        <div className="error-tag">Error Tagging: {datos_es[idxEs].error}</div>
                      )}
                    </>
                  ) : (
                    "(Frase ES no encontrada)"
                  )}
                </div>
                
                <div className="columna-en">
                  {datos_en[idxEn] ? (
                    <>
                      <SecuenciaTags
                        datosTags={datos_en[idxEn].tags || []}
                        idioma="en"
                        etiquetasGlobales={etiquetasGlobalesEn}
                      />
                      {datos_en[idxEn].error && (
                        <div className="error-tag">Error Tagging: {datos_en[idxEn].error}</div>
                      )}
                    </>
                  ) : (
                    "(Frase EN no encontrada)"
                  )}
                </div>
              </div>
            );
          })}
        </div>
        
        <LeyendaColores
          etiquetasSetEs={etiquetasGlobalesEs}
          etiquetasSetEn={etiquetasGlobalesEn}
        />
      </div>
    );
  };

  // --- Efectos ---
  useEffect(() => {
    if (modoActual === "simple" && textoSimple.trim()) {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
      
      debounceTimeoutRef.current = setTimeout(() => {
        procesarTextoSimple();
      }, DEBOUNCE_DELAY);
    }
    
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [textoSimple, idiomaSimple]);

  return (
    <div className="ejercicio-container nltk-container">
      <h2>Ejercicio NLP: Procesamiento Simple y Paralelo</h2>
      <p>
        Selecciona un modo: procesa un solo texto automáticamente o introduce textos paralelos (ES/EN) y
        procésalos manualmente.
      </p>

      {/* Selector de Modo */}
      <div className="form-group modo-selector">
        <label>Modo de Procesamiento:</label>
        <div>
          <button
            className={`btn ${modoActual === "simple" ? "btn-info active" : "btn-outline-info"} btn-sm nlp-mode-btn`}
            onClick={() => setModoActual("simple")}
          >
            Simple (Auto)
          </button>
          <button
            className={`btn ${modoActual === "paralelo" ? "btn-info active" : "btn-outline-info"} btn-sm nlp-mode-btn`}
            onClick={() => setModoActual("paralelo")}
            style={{ marginLeft: "5px" }}
          >
            Paralelo (ES/EN)
          </button>
        </div>
      </div>

      {/* Área de Entrada */}
      {modoActual === "simple" ? (
        <div className="nlp-input-area">
          <div className="form-group">
            <label htmlFor="nlp-texto-entrada-simple">Texto de Entrada:</label>
            <select
              id="nlp-idioma-simple"
              className="form-control form-control-sm idioma-selector"
              value={idiomaSimple}
              onChange={(e) => setIdiomaSimple(e.target.value)}
            >
              <option value="es">Español (spaCy)</option>
              <option value="en">Inglés (NLTK)</option>
            </select>
            <textarea
              id="nlp-texto-entrada-simple"
              rows="6"
              className="form-control"
              placeholder="Escribe o pega tu texto aquí... El procesamiento se activa al dejar de escribir."
              value={textoSimple}
              onChange={(e) => setTextoSimple(e.target.value)}
            />
          </div>
        </div>
      ) : (
        <div className="nlp-input-area entrada-paralelo">
          <div className="contenedor-paralelo">
            <div className="form-group">
              <label htmlFor="nlp-texto-es">Texto Español:</label>
              <textarea
                id="nlp-texto-es"
                rows="6"
                className="form-control"
                placeholder="Introduce el texto en español..."
                value={textoEs}
                onChange={(e) => setTextoEs(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="nlp-texto-en">Texto Inglés:</label>
              <textarea
                id="nlp-texto-en"
                rows="6"
                className="form-control"
                placeholder="Introduce el texto en inglés..."
                value={textoEn}
                onChange={(e) => setTextoEn(e.target.value)}
              />
            </div>
          </div>
          <div className="boton-procesar-contenedor">
            <button
              id="btn-procesar-paralelo"
              className="btn btn-success"
              onClick={procesarTextosParalelos}
              disabled={procesando}
            >
              Procesar Textos Paralelos
            </button>
          </div>
        </div>
      )}

      {/* Controles Comunes y Mensajes */}
      <div className="controles-comunes">
        <button
          id="nlp-toggle-mode-vista"
          className={`btn ${modoVistaEtiquetas === "etiqueta" ? "btn-info" : "btn-secondary"} btn-sm`}
          onClick={() => setModoVistaEtiquetas(modoVistaEtiquetas === "color" ? "etiqueta" : "color")}
        >
          {modoVistaEtiquetas === "color" ? "Ver Etiquetas" : "Ocultar Etiquetas"}
        </button>
        
        {mensaje.visible && (
          <div className={`mensaje ${mensaje.tipo} visible`}>
            {mensaje.texto}
          </div>
        )}
      </div>

      {/* Área de Salida */}
      {modoActual === "simple" ? <ResultadoSimple /> : <ResultadoParalelo />}
    </div>
  );
};

export default NLTKProcessor;
