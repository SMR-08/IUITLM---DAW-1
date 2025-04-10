// File: nlp.js - Lógica para NLP Multilingüe

document.addEventListener('DOMContentLoaded', () => {

    // --- Referencias DOM ---
    const nlpTextoEntrada = document.getElementById('nlp-texto-entrada');
    const nlpToggleModeBtn = document.getElementById('nlp-toggle-mode');
    const nlpResultadoDiv = document.getElementById('nlp-resultado');
    const mensajeNlpDiv = document.getElementById('mensaje-nlp');
    const nlpLeyendaColoresDiv = document.getElementById('nlp-leyenda-colores');
    const langButtons = document.querySelectorAll('.nlp-lang-btn'); // Botones de idioma
    const idiomaSeleccionadoInput = document.getElementById('nlp-idioma-seleccionado'); // Input oculto
    const idiomaMostradoSpan = document.getElementById('nlp-idioma-mostrado'); // Span en título de resultado

    // --- Estado y Constantes ---
    let debounceTimeoutId = null;
    const DEBOUNCE_DELAY = 750;
    let ultimoResultadoNLP = [];
    let idiomaUltimoResultado = 'es'; // Guardar idioma del último resultado bueno
    let modoVistaActual = 'color';

    // Paleta Colores NLTK (Penn Treebank) - Inglés
    const coloresPosTagNLTK = {
        'NN': '#FFAB91', 'NNS': '#FFAB91', 'NNP': '#FF8A65', 'NNPS': '#FF8A65',
        'VB': '#80CBC4', 'VBD': '#4DB6AC', 'VBG': '#26A69A', 'VBN': '#009688', 'VBP': '#80CBC4', 'VBZ': '#4DB6AC',
        'JJ': '#9FA8DA', 'JJR': '#7986CB', 'JJS': '#5C6BC0',
        'RB': '#CE93D8', 'RBR': '#BA68C8', 'RBS': '#AB47BC',
        'DT': '#FFF59D', 'IN': '#A1887F', 'PRP': '#90CAF9', 'PRP$': '#64B5F6',
        'WP': '#90CAF9', 'WP$': '#64B5F6', 'WRB': '#CE93D8', 'CC': '#BCAAA4',
        'CD': '#B0BEC5', 'MD': '#B39DDB', 'RP': '#C5E1A5', 'TO': '#F48FB1', 'UH': '#FFCC80',
        '.': '#CFD8DC', ',': '#CFD8DC', ':': '#CFD8DC', '(': '#CFD8DC', ')': '#CFD8DC',
        '``': '#CFD8DC', "''": '#CFD8DC', '$': '#CFD8DC', 'FW': '#E0E0E0', // Foreign Word
        'DEFAULT': '#ECEFF1'
    };

    // Paleta Colores spaCy (Universal Dependencies) - Español
    const coloresPosTagUD = {
        'NOUN': '#FFAB91', 'PROPN': '#FF8A65', 'VERB': '#80CBC4', 'ADJ': '#9FA8DA',
        'ADV': '#CE93D8', 'DET': '#FFF59D', 'ADP': '#A1887F', 'PRON': '#90CAF9',
        'AUX': '#B39DDB', 'CCONJ': '#BCAAA4', 'SCONJ': '#A1887F', 'NUM': '#B0BEC5',
        'PART': '#C5E1A5', 'INTJ': '#FFCC80', 'PUNCT': '#CFD8DC', 'SYM': '#CFD8DC',
        'SPACE': '#FFFFFF', 'X': '#ECEFF1',
        'DEFAULT': '#ECEFF1'
    };


    // --- Funciones Auxiliares (Duplicadas o globales) ---
    async function fetchApi(endpoint, options = {}) { // Asegúrate que esta función esté definida
        const apiUrlBase = 'http://api.localhost';
        try {
            const response = await fetch(`${apiUrlBase}${endpoint}`, options);
            let data;
            const contentType = response.headers.get("content-type");
            if (response.ok || (contentType && contentType.indexOf("application/json") !== -1)) {
                 try { data = await response.json(); } catch (e) { throw new Error("Respuesta no JSON"); }
            } else {
                 const errorText = await response.text();
                 throw new Error(data?.error || errorText || `Error ${response.status}`);
            }
            if (!response.ok) { throw new Error(data.error || `Error ${response.status}`); }
            return data;
        } catch (error) { console.error(`Error fetchApi ${endpoint}:`, error); throw error; }
    }
    function mostrarMensaje(divElement, texto, tipo = 'error') { // Asegúrate que esté definida
        if (divElement) { divElement.textContent = texto; divElement.className = `mensaje ${tipo} visible`; }
    }
    function ocultarMensajeNlp() {
        if (mensajeNlpDiv) { mensajeNlpDiv.classList.remove('visible', 'success', 'error', 'info'); }
    }

    // --- Renderizado NLP ---
    function renderizarResultadoNLP() {
        if (!nlpResultadoDiv || !nlpLeyendaColoresDiv || !idiomaMostradoSpan) return;

        nlpResultadoDiv.innerHTML = '';
        nlpLeyendaColoresDiv.innerHTML = '<strong>Leyenda:</strong> ';
        const etiquetasUsadas = new Set();
        // Determinar qué paleta usar basado en el idioma del ÚLTIMO resultado exitoso
        const paletaActual = (idiomaUltimoResultado === 'es') ? coloresPosTagUD : coloresPosTagNLTK;
        idiomaMostradoSpan.textContent = (idiomaUltimoResultado === 'es') ? 'Español (spaCy)' : 'Inglés (NLTK)';

        if (ultimoResultadoNLP && ultimoResultadoNLP.length > 0) {
            ultimoResultadoNLP.forEach(([palabra, tag]) => {
                const span = document.createElement('span');
                // Usar toUpperCase para tags UD (spaCy), NLTK ya suele darlos en mayúsculas
                const tagKey = (idiomaUltimoResultado === 'es') ? tag.toUpperCase() : tag;
                const color = paletaActual[tagKey] || paletaActual['DEFAULT'];

                span.style.backgroundColor = color;
                span.style.color = '#111'; // Calcular contraste si es necesario
                span.style.padding = '3px 5px';
                span.style.marginRight = '4px';
                span.style.marginBottom = '4px';
                span.style.borderRadius = '4px';
                span.style.display = 'inline-block';
                span.style.whiteSpace = 'nowrap';

                const palabraStrong = document.createElement('strong');
                palabraStrong.textContent = palabra;
                span.appendChild(palabraStrong);

                if (modoVistaActual === 'etiqueta') {
                    const tagSub = document.createElement('sub');
                    tagSub.textContent = ` (${tag})`; // Mostrar tag original (UD o Penn)
                    tagSub.style.fontSize = '0.75em';
                    tagSub.style.marginLeft = '2px';
                    span.appendChild(tagSub);
                }
                nlpResultadoDiv.appendChild(span);

                // Añadir a leyenda (usar tag original)
                if (!etiquetasUsadas.has(tag)) {
                    const leyendaSpan = document.createElement('span');
                    leyendaSpan.style.backgroundColor = color;
                    leyendaSpan.style.padding = '1px 4px';
                    leyendaSpan.style.margin = '0 5px 2px 0';
                    leyendaSpan.style.borderRadius = '3px';
                    leyendaSpan.style.display = 'inline-block';
                    leyendaSpan.textContent = tag; // Mostrar tag original en leyenda
                    nlpLeyendaColoresDiv.appendChild(leyendaSpan);
                    etiquetasUsadas.add(tag);
                }
            });
        } else {
            nlpResultadoDiv.textContent = 'Introduce texto válido para procesar.';
            nlpLeyendaColoresDiv.textContent = '';
            idiomaMostradoSpan.textContent = 'N/A';
        }
    }

    // --- Función para Procesar Texto ---
    async function procesarTextoNLP() {
        const texto = nlpTextoEntrada.value.trim();
        const idiomaSeleccionado = idiomaSeleccionadoInput.value || 'es'; // Leer del input oculto

        if (texto) {
            nlpResultadoDiv.textContent = `Procesando (${idiomaSeleccionado.toUpperCase()})...`;
            ocultarMensajeNlp();
             if(typeof mostrarMensaje === 'function') mostrarMensaje(mensajeNlpDiv, 'Enviando a la API...', 'info');

            try {
                const datosProcesados = await fetchApi('/procesar_nlp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ texto: texto, idioma: idiomaSeleccionado })
                });

                ultimoResultadoNLP = datosProcesados.resultado || [];
                idiomaUltimoResultado = datosProcesados.idioma_procesado || idiomaSeleccionado; // Usar idioma devuelto por API
                renderizarResultadoNLP();
                 if(typeof mostrarMensaje === 'function') mostrarMensaje(mensajeNlpDiv, datosProcesados.mensaje || 'Procesado correctamente.', 'success');

            } catch (error) {
                console.error(`Error en procesamiento (${idiomaSeleccionado}):`, error);
                ultimoResultadoNLP = [];
                renderizarResultadoNLP(); // Limpiar o mostrar error
                 if(typeof mostrarMensaje === 'function') mostrarMensaje(mensajeNlpDiv, error.message || "Error al contactar la API.", 'error');
                nlpResultadoDiv.textContent = 'Error al procesar. Revisa la consola o los logs.';
            }
        } else {
            ultimoResultadoNLP = [];
            renderizarResultadoNLP();
            ocultarMensajeNlp();
             nlpLeyendaColoresDiv.textContent = '';
        }
    }


    // --- Event Listeners ---

    // Debounce para Procesamiento automático
    if (nlpTextoEntrada) {
        nlpTextoEntrada.addEventListener('input', () => {
            clearTimeout(debounceTimeoutId);
            // nlpResultadoDiv.textContent = '...'; // Evitar parpadeo
            debounceTimeoutId = setTimeout(procesarTextoNLP, DEBOUNCE_DELAY);
        });
    }

    // Botón de cambio de modo
    if (nlpToggleModeBtn) {
        nlpToggleModeBtn.addEventListener('click', () => {
            if (modoVistaActual === 'color') {
                modoVistaActual = 'etiqueta';
                nlpToggleModeBtn.textContent = 'Ocultar Etiquetas';
                nlpToggleModeBtn.classList.replace('btn-secondary', 'btn-info');
            } else {
                modoVistaActual = 'color';
                nlpToggleModeBtn.textContent = 'Ver Etiquetas';
                nlpToggleModeBtn.classList.replace('btn-info', 'btn-secondary');
            }
            renderizarResultadoNLP(); // Redibujar con el nuevo modo
        });
    }

    // Botones de selección de idioma
    if (langButtons && idiomaSeleccionadoInput) {
        langButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Actualizar estado visual de botones
                langButtons.forEach(btn => btn.classList.remove('active', 'btn-primary', 'btn-secondary')); // Quitar clases activas/primarias
                langButtons.forEach(btn => btn.classList.add('btn-outline-secondary')); // Poner todos en outline-secondary por defecto

                button.classList.add('active'); // Activar el clicado
                button.classList.replace('btn-outline-secondary', (button.dataset.lang === 'es' ? 'btn-primary' : 'btn-secondary')); // Poner color primario/secundario


                // Guardar idioma en input oculto
                idiomaSeleccionadoInput.value = button.dataset.lang || 'es';

                // Volver a procesar el texto INMEDIATAMENTE con el nuevo idioma
                procesarTextoNLP();
            });
        });

         // Establecer estado inicial del botón activo (basado en el valor por defecto del input oculto)
         const langInicial = idiomaSeleccionadoInput.value;
         document.querySelector(`.nlp-lang-btn[data-lang="${langInicial}"]`)?.click(); // Simular click inicial
         // O aplicar clases manualmente:
         // document.querySelector(`.nlp-lang-btn[data-lang="${langInicial}"]`)?.classList.add('active');
         // document.querySelector(`.nlp-lang-btn[data-lang="${langInicial}"]`)?.classList.replace('btn-outline-secondary', (langInicial === 'es' ? 'btn-primary' : 'btn-secondary'));

    }

}); // Fin DOMContentLoaded