// File: nlp.js - Lógica para la sección de Procesamiento de Lenguaje Natural (Revisado)

document.addEventListener('DOMContentLoaded', () => {

    // --- Referencias a Elementos DOM de NLP (Actualizadas) ---
    const nlpTextoEntrada = document.getElementById('nlp-texto-entrada');
    const nlpToggleModeBtn = document.getElementById('nlp-toggle-mode'); // Botón Switch
    const nlpResultadoDiv = document.getElementById('nlp-resultado'); // Salida ÚNICA
    const mensajeNlpDiv = document.getElementById('mensaje-nlp');
    const nlpLeyendaColoresDiv = document.getElementById('nlp-leyenda-colores');
    // const nlpTokenizarSalida = document.getElementById('nlp-tokenizar-salida'); // ELIMINADO
    // const btnEtiquetar = document.getElementById('btn-etiquetar'); // ELIMINADO

    // --- Estado y Constantes de NLP ---
    let debounceTimeoutId = null;
    const DEBOUNCE_DELAY = 750;
    let ultimoResultadoNLP = []; // Guardará la lista [palabra, tag]
    let modoVistaActual = 'color'; // 'color' o 'etiqueta'

    // Paletas de colores (Sin cambios)
    const coloresPosTag = {
        'NN': '#FFAB91', 'NNS': '#FFAB91', 'NNP': '#FF8A65', 'NNPS': '#FF8A65',
        'VB': '#80CBC4', 'VBD': '#4DB6AC', 'VBG': '#26A69A', 'VBN': '#009688', 'VBP': '#80CBC4', 'VBZ': '#4DB6AC',
        'JJ': '#9FA8DA', 'JJR': '#7986CB', 'JJS': '#5C6BC0',
        'RB': '#CE93D8', 'RBR': '#BA68C8', 'RBS': '#AB47BC',
        'DT': '#FFF59D', 'IN': '#A1887F', 'PRP': '#90CAF9', 'PRP$': '#64B5F6',
        'WP': '#90CAF9', 'WP$': '#64B5F6', 'WRB': '#CE93D8', 'CC': '#BCAAA4',
        'CD': '#B0BEC5', 'MD': '#B39DDB', 'RP': '#C5E1A5', 'TO': '#F48FB1', 'UH': '#FFCC80',
        '.': '#CFD8DC', ',': '#CFD8DC', ':': '#CFD8DC', '(': '#CFD8DC', ')': '#CFD8DC',
        '``': '#CFD8DC', "''": '#CFD8DC', '$': '#CFD8DC',
        'DEFAULT': '#ECEFF1'
    };

    // --- Funciones Auxiliares (Asumiendo fetchApi y mostrarMensaje existen globalmente) ---
    // Duplicada aquí para asegurar que existe (puedes borrarla si estás seguro que hub.js la provee)
    async function fetchApi(endpoint, options = {}) {
        const apiUrlBase = 'http://api.localhost'; // Asegúrate que sea la URL correcta
        try {
            const response = await fetch(`${apiUrlBase}${endpoint}`, options);
            // Intentar parsear como JSON sólo si la respuesta es OK o si el Content-Type lo sugiere
            let data;
            const contentType = response.headers.get("content-type");
            if (response.ok || (contentType && contentType.indexOf("application/json") !== -1)) {
                 try {
                     data = await response.json();
                 } catch (jsonError) {
                      // Si falla el parseo JSON pero la respuesta fue OK, podría ser un problema
                      console.error("Error parseando JSON de respuesta OK:", jsonError);
                      // Devolver un error o un objeto vacío dependiendo de cómo quieras manejarlo
                      throw new Error("Respuesta inesperada del servidor (no es JSON válido).");
                 }
            } else {
                 // Si la respuesta no es OK, intentar obtener texto para el mensaje de error
                 const errorText = await response.text();
                 // Usar el texto si existe, o el statusText
                 throw new Error(data?.error || errorText || `Error ${response.status}: ${response.statusText}`);
            }

            if (!response.ok) {
                // Incluso si parseó JSON, verificar el status ok
                throw new Error(data.error || `Error ${response.status}: ${response.statusText}`);
            }
            return data;
        } catch (error) {
            console.error(`Error en fetchApi para ${endpoint}:`, error);
            // Re-lanzar el error para que el llamador lo maneje
            throw error;
        }
    }
    // Duplicada aquí (puedes borrarla si estás seguro que hub.js la provee)
    function mostrarMensaje(divElement, texto, tipo = 'error') {
        if (divElement) {
            divElement.textContent = texto;
            divElement.className = `mensaje ${tipo} visible`; // Clases CSS necesarias
        }
    }

    function ocultarMensajeNlp() {
        if (mensajeNlpDiv) {
            mensajeNlpDiv.classList.remove('visible', 'success', 'error', 'info');
        }
    }

    // --- Función Única de Renderizado NLP ---
    function renderizarResultadoNLP() {
        if (!nlpResultadoDiv || !nlpLeyendaColoresDiv) return;

        nlpResultadoDiv.innerHTML = ''; // Limpiar salida anterior
        nlpLeyendaColoresDiv.innerHTML = '<strong>Leyenda:</strong> '; // Limpiar y empezar leyenda
        const etiquetasUsadas = new Set();

        if (ultimoResultadoNLP && ultimoResultadoNLP.length > 0) {
            ultimoResultadoNLP.forEach(([palabra, tag]) => { // Usar el resultado guardado
                const span = document.createElement('span');
                const color = coloresPosTag[tag] || coloresPosTag['DEFAULT'];

                span.style.backgroundColor = color;
                span.style.color = '#111'; // Ajustar contraste si es necesario
                span.style.padding = '3px 5px';
                span.style.marginRight = '4px';
                span.style.marginBottom = '4px';
                span.style.borderRadius = '4px';
                span.style.display = 'inline-block';
                span.style.whiteSpace = 'nowrap';

                // Añadir palabra
                const palabraStrong = document.createElement('strong');
                palabraStrong.textContent = palabra;
                span.appendChild(palabraStrong);

                // Añadir etiqueta SOLO si el modo es 'etiqueta'
                if (modoVistaActual === 'etiqueta') {
                    const tagSub = document.createElement('sub');
                    tagSub.textContent = ` (${tag})`;
                    tagSub.style.fontSize = '0.75em';
                    tagSub.style.marginLeft = '2px';
                    // tagSub.style.color = '#eee'; // Podría necesitar ajuste de contraste
                    span.appendChild(tagSub);
                }

                nlpResultadoDiv.appendChild(span);

                // Añadir a leyenda si no está ya
                if (!etiquetasUsadas.has(tag)) {
                    const leyendaSpan = document.createElement('span');
                    leyendaSpan.style.backgroundColor = color;
                    leyendaSpan.style.padding = '1px 4px';
                    leyendaSpan.style.margin = '0 5px 2px 0';
                    leyendaSpan.style.borderRadius = '3px';
                    leyendaSpan.style.display = 'inline-block';
                    leyendaSpan.textContent = tag;
                    nlpLeyendaColoresDiv.appendChild(leyendaSpan);
                    etiquetasUsadas.add(tag);
                }
            });
            // Mostrar mensaje de éxito guardado (si lo hubiera) o uno genérico
            // (El mensaje original viene de la llamada API, aquí solo redibujamos)
            // mostrarMensaje(mensajeNlpDiv, 'Resultado actualizado.', 'info');

        } else {
            // Si no hay resultado guardado
            nlpResultadoDiv.textContent = 'Introduce texto arriba para procesar.';
            nlpLeyendaColoresDiv.textContent = ''; // Limpiar leyenda
        }
    }

    // --- Event Listeners para NLP ---

    // Debounce para Procesamiento automático
    if (nlpTextoEntrada) {
        nlpTextoEntrada.addEventListener('input', () => {
            clearTimeout(debounceTimeoutId);
            ocultarMensajeNlp();
            // No mostrar "Procesando..." aquí para no parpadear, se mostrará al enviar
            // nlpResultadoDiv.textContent = '...';

            debounceTimeoutId = setTimeout(async () => {
                const texto = nlpTextoEntrada.value.trim();
                if (texto) {
                    // Mostrar feedback ANTES de la llamada API
                    nlpResultadoDiv.textContent = 'Procesando texto...';
                    if(typeof mostrarMensaje === 'function') mostrarMensaje(mensajeNlpDiv, 'Enviando a la API...', 'info');

                    try {
                        // Llamar al NUEVO endpoint unificado
                        const datosProcesados = await fetchApi('/procesar_nlp', {
                             method: 'POST',
                             headers: { 'Content-Type': 'application/json' },
                             body: JSON.stringify({ texto: texto })
                        });

                        // Guardar el resultado
                        ultimoResultadoNLP = datosProcesados.resultado || [];
                        // Renderizar por primera vez (en modo color por defecto)
                        renderizarResultadoNLP();
                        // Mostrar mensaje de éxito de la API
                        if(typeof mostrarMensaje === 'function') mostrarMensaje(mensajeNlpDiv, datosProcesados.mensaje || 'Procesado correctamente.', 'success');

                    } catch (error) {
                        console.error("Error en procesamiento automático:", error);
                        ultimoResultadoNLP = []; // Limpiar resultado en caso de error
                        renderizarResultadoNLP(); // Renderizar estado vacío/error
                        if(typeof mostrarMensaje === 'function') mostrarMensaje(mensajeNlpDiv, error.message || "Error al contactar la API.", 'error');
                         nlpResultadoDiv.textContent = 'Error al procesar. Intenta de nuevo.'; // Mensaje en área de resultado
                    }
                } else {
                    // Limpiar si el texto está vacío
                    ultimoResultadoNLP = [];
                    renderizarResultadoNLP(); // Mostrar mensaje "Introduce texto..."
                    ocultarMensajeNlp();
                     nlpLeyendaColoresDiv.textContent = ''; // Limpiar leyenda
                }
            }, DEBOUNCE_DELAY);
        });
    }

    // Event Listener para el botón de cambio de modo
    if (nlpToggleModeBtn) {
        nlpToggleModeBtn.addEventListener('click', () => {
            // Cambiar modo
            if (modoVistaActual === 'color') {
                modoVistaActual = 'etiqueta';
                nlpToggleModeBtn.textContent = 'Ocultar Etiquetas';
                nlpToggleModeBtn.classList.remove('btn-secondary');
                nlpToggleModeBtn.classList.add('btn-info'); // Cambiar estilo del botón
            } else {
                modoVistaActual = 'color';
                nlpToggleModeBtn.textContent = 'Ver Etiquetas';
                 nlpToggleModeBtn.classList.remove('btn-info');
                nlpToggleModeBtn.classList.add('btn-secondary');
            }
            // Volver a renderizar con el nuevo modo, usando los datos guardados
            renderizarResultadoNLP();
        });
    }

}); // Fin DOMContentLoaded