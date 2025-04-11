// File: nlp.js - Lógica para NLP Simple y Paralelo (Alineación Gale-Church)

document.addEventListener('DOMContentLoaded', () => {

    // --- Referencias DOM ---
    const nlpTextoEntradaSimple = document.getElementById('nlp-texto-entrada-simple');
    const nlpTextoEntradaEs = document.getElementById('nlp-texto-es');
    const nlpTextoEntradaEn = document.getElementById('nlp-texto-en');
    const nlpIdiomaSimpleSelect = document.getElementById('nlp-idioma-simple');
    const nlpToggleModeVistaBtn = document.getElementById('nlp-toggle-mode-vista');
    const btnProcesarParalelo = document.getElementById('btn-procesar-paralelo');
    const nlpResultadoSimpleDiv = document.getElementById('nlp-resultado-simple');
    const nlpResultadoParaleloContenedor = document.getElementById('nlp-resultado-paralelo'); // Contenedor paralelo
    // Los divs internos nlp-resultado-es y nlp-resultado-en se crean dinámicamente
    const mensajeNlpDiv = document.getElementById('mensaje-nlp');
    const nlpLeyendaColoresDiv = document.getElementById('nlp-leyenda-colores');
    const idiomaMostradoSpan = document.getElementById('nlp-idioma-mostrado');
    const modoActualInput = document.getElementById('nlp-modo-actual');
    const modeButtons = document.querySelectorAll('.nlp-mode-btn');
    const entradaSimpleDiv = document.getElementById('nlp-entrada-simple');
    const entradaParaleloDiv = document.getElementById('nlp-entrada-paralelo');

    // --- Estado y Constantes ---
    let debounceTimeoutId = null;
    const DEBOUNCE_DELAY = 800;
    let ultimoResultadoSimple = { resultado: [], idioma_procesado: 'es' }; // Guardar también idioma
    let ultimoResultadoParalelo = { alineacion: [], datos_es: [], datos_en: [] }; // Estructura completa
    let modoVistaEtiquetas = 'color'; // 'color' o 'etiqueta'

    // Paletas de colores
    const coloresPosTagNLTK = { 'NN': '#FFAB91', 'NNS': '#FFAB91', 'NNP': '#FF8A65', 'NNPS': '#FF8A65', 'VB': '#80CBC4', 'VBD': '#4DB6AC', 'VBG': '#26A69A', 'VBN': '#009688', 'VBP': '#80CBC4', 'VBZ': '#4DB6AC', 'JJ': '#9FA8DA', 'JJR': '#7986CB', 'JJS': '#5C6BC0', 'RB': '#CE93D8', 'RBR': '#BA68C8', 'RBS': '#AB47BC', 'DT': '#FFF59D', 'IN': '#A1887F', 'PRP': '#90CAF9', 'PRP$': '#64B5F6', 'WP': '#90CAF9', 'WP$': '#64B5F6', 'WRB': '#CE93D8', 'CC': '#BCAAA4', 'CD': '#B0BEC5', 'MD': '#B39DDB', 'RP': '#C5E1A5', 'TO': '#F48FB1', 'UH': '#FFCC80', '.': '#CFD8DC', ',': '#CFD8DC', ':': '#CFD8DC', '(': '#CFD8DC', ')': '#CFD8DC', '``': '#CFD8DC', "''": '#CFD8DC', '$': '#CFD8DC', 'FW': '#E0E0E0', 'DEFAULT': '#ECEFF1' };
    const coloresPosTagUD = { 'NOUN': '#FFAB91', 'PROPN': '#FF8A65', 'VERB': '#80CBC4', 'ADJ': '#9FA8DA', 'ADV': '#CE93D8', 'DET': '#FFF59D', 'ADP': '#A1887F', 'PRON': '#90CAF9', 'AUX': '#B39DDB', 'CCONJ': '#BCAAA4', 'SCONJ': '#A1887F', 'NUM': '#B0BEC5', 'PART': '#C5E1A5', 'INTJ': '#FFCC80', 'PUNCT': '#CFD8DC', 'SYM': '#CFD8DC', 'SPACE': '#FFFFFF', 'X': '#ECEFF1', 'DEFAULT': '#ECEFF1' };

    // --- Funciones Auxiliares ---
    async function fetchApi(endpoint, options = {}) {
        const apiUrlBase = 'http://api.localhost';
        const defaultOptions = {
             method: options.body ? 'POST' : 'GET',
             headers: {
                 ...(options.body && typeof options.body === 'string' && options.body.startsWith('{') ? {'Content-Type': 'application/json'} : {}),
                 ...options.headers
             },
        };
        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(`${apiUrlBase}${endpoint}`, finalOptions);
            let data = null;
            const contentType = response.headers.get("content-type");
            if (response.ok || (contentType && contentType.indexOf("application/json") !== -1)) {
                 try {
                     if (response.status === 204 || response.headers.get('Content-Length') === '0') { data = {}; }
                     else { data = await response.json(); }
                 } catch (jsonError) {
                      console.error("Error parseando JSON:", response.url, jsonError);
                      if (response.ok) return {};
                      throw new Error("Respuesta inesperada del servidor (no JSON).");
                 }
            }
            if (!response.ok) {
                 const errorText = data?.error || await response.text() || `Error ${response.status}`;
                 throw new Error(errorText);
            }
            return data;
        } catch (error) {
            console.error(`Error en fetchApi para ${finalOptions.method} ${endpoint}:`, error);
            throw new Error(error.message || "Error de red o al contactar la API.");
        }
    }

    function mostrarMensaje(divElement, texto, tipo = 'error') {
        if (divElement) { divElement.textContent = texto; divElement.className = `mensaje ${tipo} visible`; }
    }

    function ocultarMensajeNlp() {
        if (mensajeNlpDiv) { mensajeNlpDiv.classList.remove('visible', 'success', 'error', 'info'); }
    }

    // --- Funciones de Renderizado ---

    /**
     * Renderiza UNA secuencia de palabras/tags en un div específico.
     * @param {Array} datosTags Lista de [palabra, tag].
     * @param {HTMLElement} divSalida Elemento DIV donde renderizar.
     * @param {string} idioma 'es' o 'en'.
     * @param {Set<string>} etiquetasGlobales Set para acumular tags para la leyenda.
     */
    function renderizarSecuenciaTags(datosTags, divSalida, idioma, etiquetasGlobales) {
        if (!divSalida) return;
        divSalida.innerHTML = ''; // Limpiar solo este div
        const paletaActual = (idioma === 'es') ? coloresPosTagUD : coloresPosTagNLTK;
        const esEspañol = (idioma === 'es');

        if (datosTags && datosTags.length > 0) {
            datosTags.forEach(([palabra, tag]) => {
                etiquetasGlobales.add(tag);
                const span = document.createElement('span');
                const tagKey = esEspañol ? tag.toUpperCase() : tag;
                const color = paletaActual[tagKey] || paletaActual['DEFAULT'];
                span.style.backgroundColor = color;
                span.style.color = '#111';
                span.style.padding = '3px 5px';
                span.style.marginRight = '4px';
                span.style.marginBottom = '4px';
                span.style.borderRadius = '4px';
                span.style.display = 'inline-block';
                span.style.whiteSpace = 'nowrap';
                const palabraStrong = document.createElement('strong');
                palabraStrong.textContent = palabra;
                span.appendChild(palabraStrong);
                if (modoVistaEtiquetas === 'etiqueta') {
                    const tagSub = document.createElement('sub');
                    tagSub.textContent = ` (${tag})`;
                    tagSub.style.fontSize = '0.75em';
                    tagSub.style.marginLeft = '2px';
                    span.appendChild(tagSub);
                }
                divSalida.appendChild(span);
            });
        } else {
            divSalida.textContent = `(Sin datos para ${idioma.toUpperCase()})`;
        }
    }

    /** Actualiza la leyenda global */
    function actualizarLeyendaGlobal(etiquetasSetEs, etiquetasSetEn) {
         if (!nlpLeyendaColoresDiv) return;
         nlpLeyendaColoresDiv.innerHTML = '<strong>Leyenda:</strong> ';
         const etiquetasMostradas = new Set();
         const addLeyendaItem = (tag, idioma) => {
             const key = `${tag}_${idioma}`;
             if(etiquetasMostradas.has(key) || !tag) return; // Evitar duplicados y tags nulos/vacíos
             const paleta = (idioma === 'es') ? coloresPosTagUD : coloresPosTagNLTK;
             const tagKey = (idioma === 'es') ? tag.toUpperCase() : tag;
             const color = paleta[tagKey] || paleta['DEFAULT'];
             const leyendaSpan = document.createElement('span');
             leyendaSpan.style.backgroundColor = color;
             leyendaSpan.style.padding = '1px 4px';
             leyendaSpan.style.margin = '0 5px 2px 0';
             leyendaSpan.style.borderRadius = '3px';
             leyendaSpan.style.display = 'inline-block';
             leyendaSpan.textContent = `${tag} (${idioma.toUpperCase()})`;
             nlpLeyendaColoresDiv.appendChild(leyendaSpan);
             etiquetasMostradas.add(key);
         };
         if(etiquetasSetEs) { etiquetasSetEs.forEach(tag => addLeyendaItem(tag, 'es')); }
         if(etiquetasSetEn) { etiquetasSetEn.forEach(tag => addLeyendaItem(tag, 'en')); }
         if (etiquetasMostradas.size === 0) { nlpLeyendaColoresDiv.innerHTML += ' Esperando procesamiento...'; }
    }

    /** Renderiza los resultados paralelos usando la alineación Gale-Church */
    function renderizarAlineacionGaleChurch() {
        if (!nlpResultadoParaleloContenedor || !ultimoResultadoParalelo) return;

        const { alineacion, datos_es, datos_en } = ultimoResultadoParalelo;
        nlpResultadoParaleloContenedor.innerHTML = '';
        const etiquetasGlobalesEs = new Set();
        const etiquetasGlobalesEn = new Set();

        if (!alineacion || !datos_es || !datos_en) {
            nlpResultadoParaleloContenedor.textContent = 'Faltan datos para renderizar la alineación.';
            actualizarLeyendaGlobal(null, null);
            return;
        }

         if (alineacion.length === 0 && (datos_es.length > 0 || datos_en.length > 0)) {
            nlpResultadoParaleloContenedor.innerHTML = '<p><i>No se pudo generar alineación (Gale-Church). Mostrando frases secuencialmente (si existen).</i></p>';
            // Podríamos añadir aquí la renderización secuencial si se desea
            actualizarLeyendaGlobal(null, null);
            return;
        }
        if (datos_es.length === 0 && datos_en.length === 0) {
             nlpResultadoParaleloContenedor.textContent = 'No se encontraron frases en ninguna entrada.';
             actualizarLeyendaGlobal(null, null);
             return;
        }

        // Crear divs para cada bloque alineado
        alineacion.forEach(([idxEs, idxEn]) => {
             if (idxEs === null || idxEn === null || idxEs >= datos_es.length || idxEn >= datos_en.length) return; // Ignorar inválidos

             const divBloqueContenedor = document.createElement('div');
             divBloqueContenedor.style.display = 'flex';
             divBloqueContenedor.style.gap = '15px';
             divBloqueContenedor.style.marginBottom = '10px';
             divBloqueContenedor.style.paddingBottom = '10px';
             divBloqueContenedor.style.borderBottom = '1px dashed #eee';

             // Columna Izquierda (Español)
             const divColEs = document.createElement('div');
             divColEs.style.flex = '1';
             divColEs.style.minWidth = '0'; // Para flexbox wrapping
             if (datos_es[idxEs]) {
                  // Usar la función auxiliar que renderiza y acumula tags
                  renderizarSecuenciaTags(datos_es[idxEs].tags || [], divColEs, 'es', etiquetasGlobalesEs);
                  if (datos_es[idxEs].error) {
                      divColEs.innerHTML += `<br><small style='color: red;'>Error Tagging: ${datos_es[idxEs].error}</small>`;
                  }
             } else {
                  divColEs.innerHTML = "(Frase ES no encontrada)";
             }


             // Columna Derecha (Inglés)
             const divColEn = document.createElement('div');
             divColEn.style.flex = '1';
             divColEn.style.minWidth = '0'; // Para flexbox wrapping
              if (datos_en[idxEn]) {
                   renderizarSecuenciaTags(datos_en[idxEn].tags || [], divColEn, 'en', etiquetasGlobalesEn);
                   if (datos_en[idxEn].error) {
                       divColEn.innerHTML += `<br><small style='color: red;'>Error Tagging: ${datos_en[idxEn].error}</small>`;
                  }
              } else {
                   divColEn.innerHTML = "(Frase EN no encontrada)";
              }

             divBloqueContenedor.appendChild(divColEs);
             divBloqueContenedor.appendChild(divColEn);
             nlpResultadoParaleloContenedor.appendChild(divBloqueContenedor);
        });

        // Nota: Este renderizado simple no maneja explícitamente alineaciones M-N de Gale-Church
        // (donde un índice puede aparecer varias veces). Muestra los pares tal cual vienen.
        // Tampoco muestra frases que Gale-Church no haya alineado. Una mejora sería detectar y mostrar esas.

        actualizarLeyendaGlobal(etiquetasGlobalesEs, etiquetasGlobalesEn);
    }

    // --- Funciones de Procesamiento API ---
    async function procesarTextoSimple() {
        if (!nlpTextoEntradaSimple || !nlpResultadoSimpleDiv || !nlpIdiomaSimpleSelect || !idiomaMostradoSpan) return;
        const texto = nlpTextoEntradaSimple.value.trim();
        const idiomaSeleccionado = nlpIdiomaSimpleSelect.value;

        if (texto) {
            nlpResultadoSimpleDiv.textContent = `Procesando (${idiomaSeleccionado.toUpperCase()})...`;
            ocultarMensajeNlp();
            mostrarMensaje(mensajeNlpDiv, 'Enviando a la API...', 'info');
            idiomaMostradoSpan.textContent = idiomaSeleccionado.toUpperCase();

            try {
                 const datosProcesados = await fetchApi('/procesar_nlp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ texto: texto, idioma: idiomaSeleccionado })
                 });
                 // Guardar resultado como objeto para consistencia
                 ultimoResultadoSimple = {
                     resultado: datosProcesados.resultado || [],
                     idioma_procesado: datosProcesados.idioma_procesado || idiomaSeleccionado
                 };
                 idiomaUltimoSimple = ultimoResultadoSimple.idioma_procesado; // Actualizar idioma real

                 const etiquetasSetSimple = new Set();
                 renderizarSecuenciaTags(ultimoResultadoSimple.resultado, nlpResultadoSimpleDiv, idiomaUltimoSimple, etiquetasSetSimple);
                 actualizarLeyendaGlobal(idiomaUltimoSimple === 'es' ? etiquetasSetSimple : null, idiomaUltimoSimple === 'en' ? etiquetasSetSimple : null);
                 mostrarMensaje(mensajeNlpDiv, datosProcesados.mensaje || 'Procesado correctamente.', 'success');
                 idiomaMostradoSpan.textContent = idiomaUltimoSimple.toUpperCase();

            } catch (error) {
                ultimoResultadoSimple = { resultado: [], idioma_procesado: idiomaSeleccionado }; // Resetear con idioma intentado
                renderizarSecuenciaTags([], nlpResultadoSimpleDiv, idiomaSeleccionado, new Set());
                actualizarLeyendaGlobal(null, null);
                mostrarMensaje(mensajeNlpDiv, error.message || "Error al contactar la API.", 'error');
                nlpResultadoSimpleDiv.textContent = 'Error al procesar.';
                idiomaMostradoSpan.textContent = 'Error';
            }
        } else {
            ultimoResultadoSimple = { resultado: [], idioma_procesado: idiomaSeleccionado };
            renderizarSecuenciaTags([], nlpResultadoSimpleDiv, idiomaSeleccionado, new Set());
            actualizarLeyendaGlobal(null, null);
            ocultarMensajeNlp();
            nlpResultadoSimpleDiv.textContent = 'Introduce texto para procesar.';
            idiomaMostradoSpan.textContent = 'N/A';
        }
    }

    async function procesarTextosParalelos() {
        if (!nlpTextoEntradaEs || !nlpTextoEntradaEn || !nlpResultadoParaleloContenedor || !btnProcesarParalelo) return;
        const textoEs = nlpTextoEntradaEs.value.trim();
        const textoEn = nlpTextoEntradaEn.value.trim();
        if (!textoEs || !textoEn) {
            mostrarMensaje(mensajeNlpDiv, 'Introduce texto en AMBOS campos (ES y EN).', 'error');
            return;
        }

        ocultarMensajeNlp();
        nlpResultadoParaleloContenedor.innerHTML = '<p>Procesando y alineando textos...</p>';
        mostrarMensaje(mensajeNlpDiv, 'Enviando ambos textos a la API...', 'info');
        btnProcesarParalelo.disabled = true;

        try {
            const datosParalelos = await fetchApi('/procesar_paralelo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ texto_es: textoEs, texto_en: textoEn })
            });

            // Guardar la estructura completa devuelta por la API
            ultimoResultadoParalelo = datosParalelos || { alineacion: [], datos_es: [], datos_en: [] };
            renderizarAlineacionGaleChurch(ultimoResultadoParalelo); // Usar la función de renderizado específica

            let mensajeTipo = 'success';
            let mensajeTexto = datosParalelos.mensaje || 'Procesado correctamente.';
             if (datosParalelos.errores) {
                 mensajeTipo = 'warning'; // Usar warning para errores parciales
                 mensajeTexto += ` (Se produjeron algunos errores en el etiquetado. Revisa los resultados.)`;
                 console.error("Errores parciales recibidos:", datosParalelos.errores);
                 // El renderizador ya muestra errores a nivel de frase si existen en los datos
             }
              mostrarMensaje(mensajeNlpDiv, mensajeTexto, mensajeTipo);

        } catch (error) {
            ultimoResultadoParalelo = { alineacion: [], datos_es: [], datos_en: [] };
            renderizarAlineacionGaleChurch(ultimoResultadoParalelo); // Limpiar salida
            mostrarMensaje(mensajeNlpDiv, error.message || "Error al contactar la API.", 'error');
            nlpResultadoParaleloContenedor.innerHTML = '<p style="color: red;">Error al procesar textos paralelos.</p>';
        } finally {
            btnProcesarParalelo.disabled = false;
        }
    }

    // --- Función para Cambiar Modo de Procesamiento ---
    function cambiarModoProcesamiento(nuevoModo) {
        if (!entradaSimpleDiv || !entradaParaleloDiv || !nlpResultadoSimpleDiv || !nlpResultadoParaleloContenedor || !btnProcesarParalelo || !modeButtons || !modoActualInput || !nlpTextoEntradaSimple) return;
        const modoActual = nuevoModo || 'simple';
        modoActualInput.value = modoActual;

        // Actualizar botones de modo
        modeButtons.forEach(button => {
             if (button.dataset.mode === modoActual) {
                 button.classList.add('active', 'btn-info');
                 button.classList.remove('btn-outline-info');
             } else {
                 button.classList.remove('active', 'btn-info');
                 button.classList.add('btn-outline-info');
             }
        });

        // Mostrar/ocultar divs y controles
        if (modoActual === 'simple') {
            entradaSimpleDiv.style.display = 'block';
            entradaParaleloDiv.style.display = 'none';
            nlpResultadoSimpleDiv.style.display = 'block';
            nlpResultadoParaleloContenedor.style.display = 'none';
            btnProcesarParalelo.style.display = 'none';
            nlpTextoEntradaSimple.disabled = false;
        } else { // modo 'paralelo'
            entradaSimpleDiv.style.display = 'none';
            entradaParaleloDiv.style.display = 'flex';
            nlpResultadoSimpleDiv.style.display = 'none';
            nlpResultadoParaleloContenedor.style.display = 'block';
            btnProcesarParalelo.style.display = 'inline-block';
            nlpTextoEntradaSimple.disabled = true;
            clearTimeout(debounceTimeoutId);
        }

        ocultarMensajeNlp();
        // Renderizar el estado apropiado al cambiar
        if (modoActual === 'simple') {
            const etiquetasSetSimple = new Set();
            renderizarSecuenciaTags(ultimoResultadoSimple.resultado, nlpResultadoSimpleDiv, ultimoResultadoSimple.idioma_procesado, etiquetasSetSimple);
            actualizarLeyendaGlobal(ultimoResultadoSimple.idioma_procesado === 'es' ? etiquetasSetSimple : null, ultimoResultadoSimple.idioma_procesado === 'en' ? etiquetasSetSimple : null);
        } else {
            renderizarAlineacionGaleChurch(ultimoResultadoParalelo);
        }
    }

    // --- Event Listeners ---
    if (nlpTextoEntradaSimple) {
        nlpTextoEntradaSimple.addEventListener('input', () => {
            if (modoActualInput.value === 'simple') {
                clearTimeout(debounceTimeoutId);
                debounceTimeoutId = setTimeout(procesarTextoSimple, DEBOUNCE_DELAY);
            }
        });
         if (nlpIdiomaSimpleSelect) {
              nlpIdiomaSimpleSelect.addEventListener('change', () => {
                   if (modoActualInput.value === 'simple') {
                        clearTimeout(debounceTimeoutId);
                        procesarTextoSimple();
                   }
              });
         }
    }

    if (btnProcesarParalelo) {
        btnProcesarParalelo.addEventListener('click', procesarTextosParalelos);
    }

    if (nlpToggleModeVistaBtn) {
        nlpToggleModeVistaBtn.addEventListener('click', () => {
            if (modoVistaEtiquetas === 'color') {
                modoVistaEtiquetas = 'etiqueta';
                nlpToggleModeVistaBtn.textContent = 'Ocultar Etiquetas';
                nlpToggleModeVistaBtn.classList.replace('btn-secondary', 'btn-info');
            } else {
                modoVistaEtiquetas = 'color';
                nlpToggleModeVistaBtn.textContent = 'Ver Etiquetas';
                nlpToggleModeVistaBtn.classList.replace('btn-info', 'btn-secondary');
            }
            // Redibujar la salida activa
            if (modoActualInput.value === 'simple') {
                 const etiquetasSetSimple = new Set();
                 renderizarSecuenciaTags(ultimoResultadoSimple.resultado, nlpResultadoSimpleDiv, ultimoResultadoSimple.idioma_procesado, etiquetasSetSimple);
                 actualizarLeyendaGlobal(ultimoResultadoSimple.idioma_procesado === 'es' ? etiquetasSetSimple : null, ultimoResultadoSimple.idioma_procesado === 'en' ? etiquetasSetSimple : null);
            } else {
                 renderizarAlineacionGaleChurch(ultimoResultadoParalelo);
            }
        });
    }

    if (modeButtons) {
        modeButtons.forEach(button => {
            button.addEventListener('click', () => {
                if (!button.classList.contains('active')) {
                    cambiarModoProcesamiento(button.dataset.mode);
                }
            });
        });
    }

    // --- Inicialización ---
    cambiarModoProcesamiento(modoActualInput.value || 'simple');

}); // Fin DOMContentLoaded