import React, { useState, useEffect, useRef, useCallback } from 'react';
import mermaid from 'mermaid';
import './db-chat.css';

// Definir estados de carga más específicos
const LOADING_STATES = {
    IDLE: 'idle',
    GENERATING: 'generando',
    RETRYING_JSON: 'reintentando_json', // Podríamos usarlo si el backend nos indicara reintento
    FIXING_MERMAID: 'puliendo_diagrama',
    ERROR: 'error'
};

const DbChatComponent = () => {
    const [messages, setMessages] = useState([]);
    // const [isLoading, setIsLoading] = useState(false); // Reemplazado por loadingState
    const [loadingState, setLoadingState] = useState(LOADING_STATES.IDLE);
    const [mermaidCode, setMermaidCode] = useState(null);
    const [suggestedReplies, setSuggestedReplies] = useState([]);
    const [currentInput, setCurrentInput] = useState('');
    const [diagramViewMode, setDiagramViewMode] = useState('image');
    const [mermaidRenderError, setMermaidRenderError] = useState(null); // { message: string, code: string } | null
    const [lastAttemptedMermaidCode, setLastAttemptedMermaidCode] = useState(null); // Para evitar bucles de corrección

    const chatContainerRef = useRef(null);
    const mermaidContainerRef = useRef(null);
    const fixAttemptedRef = useRef(false); // Ref para rastrear si ya intentamos corregir este código

    // Initialize Mermaid
    useEffect(() => {
        mermaid.initialize({ startOnLoad: false });
    }, []);

    // >>> Función para intentar corregir Mermaid automáticamente
    const triggerAutoFixMermaid = useCallback(async (errorMessage, codeToFix) => {
        if (loadingState !== LOADING_STATES.IDLE && loadingState !== LOADING_STATES.ERROR) return; // Evitar si ya está cargando/arreglando
        if(fixAttemptedRef.current) {
            console.log("Ya se intentó corregir este bloque de código. Evitando bucle.");
            // Mostrar el error persistente al usuario
            setMermaidRenderError({ message: `Error persistente tras intento de corrección: ${errorMessage}`, code: codeToFix });
            setLoadingState(LOADING_STATES.ERROR); // Poner en estado de error final
            return;
        }

        console.log("Detectado error de Mermaid, iniciando corrección automática...");
        setLoadingState(LOADING_STATES.FIXING_MERMAID); // Mostrar "Puliendo diagrama..."
        fixAttemptedRef.current = true; // Marcar que hemos intentado corregir este código
        setMermaidRenderError(null); // Limpiar el error visualmente mientras intentamos

        try {
             const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
             const response = await fetch(`${backendUrl}/api/v1/db-chat/fix-mermaid`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ incorrect_code: codeToFix }),
            });

            const data = await response.json(); // Intentar parsear siempre, incluso si !response.ok

            if (!response.ok || data.error_message) {
                 throw new Error(data.error_message || `Error ${response.status} del servidor al corregir.`);
            }

            if (data.fixed_code) {
                 console.log("Corrección automática exitosa. Aplicando nuevo código.");
                 setMermaidCode(data.fixed_code); // Aplicar código corregido
                 // El useEffect de renderizado se encargará
                 const fixSuccessMessage = { role: 'model', content: "Se intentó corregir el diagrama. Aplicando nueva versión..." };
                 setMessages(prevMessages => [...prevMessages, fixSuccessMessage]);
                 setLoadingState(LOADING_STATES.IDLE); // Volver a idle tras éxito
            } else {
                 // Caso raro: ok=true, pero no hay fixed_code ni error_message
                 throw new Error("La respuesta de corrección del servidor fue inválida.");
            }

        } catch (error) {
            console.error("Error en la corrección automática de Mermaid:", error);
            const fixErrorMessage = { role: 'model', content: `No se pudo corregir el diagrama automáticamente: ${error.message}` };
            setMessages(prevMessages => [...prevMessages, fixErrorMessage]);
            // Volver a mostrar el error original (el código no se pudo arreglar)
            setMermaidRenderError({ message: `Fallo en la corrección automática: ${error.message}`, code: codeToFix });
            setLoadingState(LOADING_STATES.ERROR); // Poner en estado de error final
        }
    }, [loadingState, setLoadingState, setMermaidRenderError, setMessages, setMermaidCode]); // <<< Añade las dependencias de useCallback


    // useEffect para renderizar Mermaid o manejar errores
    useEffect(() => {
        const container = mermaidContainerRef.current;
        if (!container) return;
        container.innerHTML = ''; // Limpiar siempre

        // Si hay un error de renderizado ALMACENADO, mostrarlo
        if (mermaidRenderError) {
            container.innerHTML = `
                <div class="mermaid-error-message">
                    <h4>Error al renderizar el diagrama:</h4>
                    <p>${mermaidRenderError.message}</p>
                </div>
                <pre class="mermaid-code-view"><code>${mermaidRenderError.code || 'No code available'}</code></pre>
            `;
            // No añadir botón de corrección aquí, ya que la corrección ahora es automática
            return; // Salir para no intentar renderizar/mostrar otras cosas
        }

        // Si estamos en modo código...
        if (diagramViewMode === 'code') {
            if (mermaidCode) {
                const codeElement = document.createElement('code');
                codeElement.textContent = mermaidCode;
                const preElement = document.createElement('pre');
                preElement.className = 'mermaid-code-view';
                preElement.appendChild(codeElement);
                container.appendChild(preElement);
                // <<< AÑADIR ESTO SI QUIERES QUE SE QUITE EL LOADING AL VER CÓDIGO >>>
                if (loadingState !== LOADING_STATES.IDLE && loadingState !== LOADING_STATES.ERROR) {
                   console.log("USE_EFFECT (Mermaid): Modo código con código. Estado ANTES de reset:", loadingState);
                   setLoadingState(LOADING_STATES.IDLE);
                   console.log("USE_EFFECT (Mermaid): Estado cambiado a IDLE tras mostrar código.");
                }
            } else {
                container.innerHTML = '<p>No hay código Mermaid disponible.</p>';
                // <<< AÑADIR ESTO: Resetear si no hay código >>>
                if (loadingState === LOADING_STATES.GENERATING || loadingState === LOADING_STATES.FIXING_MERMAID) {
                   console.log("USE_EFFECT (Mermaid): Modo código sin código. Estado ANTES de reset:", loadingState);
                   setLoadingState(LOADING_STATES.IDLE);
                   console.log("USE_EFFECT (Mermaid): Estado cambiado a IDLE porque no hay código.");
                }
            }
        }
        // Si estamos en modo imagen y hay código...
        else if (diagramViewMode === 'image' && mermaidCode) {
            // Verificar si es el mismo código que ya intentamos renderizar y falló (evitar bucle si el trigger falla)
            if (lastAttemptedMermaidCode === mermaidCode && loadingState === LOADING_STATES.ERROR) {
                 console.log("Evitando re-renderizar código que ya sabemos que falla tras intento de corrección.");
                 // Podríamos mostrar el error almacenado aquí de nuevo si quisiéramos
                 return;
            }

            container.innerHTML = '<p>Renderizando diagrama...</p>';
            setLastAttemptedMermaidCode(mermaidCode); // Mark this code as the one we are attempting to render
            try {
                const uniqueId = `mermaid-diagram-${Date.now()}`;
                mermaid.render(uniqueId, mermaidCode)
                    .then(({ svg }) => {
                        if (mermaidContainerRef.current === container && diagramViewMode === 'image' && mermaidCode === lastAttemptedMermaidCode) {
                             container.innerHTML = svg;
                             const svgElement = container.querySelector('svg');
                             if (svgElement) {
                                 svgElement.style.maxWidth = '100%';
                                 svgElement.style.height = 'auto';
                             }

                             // <<< !!! AÑADIR ESTO ES CRUCIAL !!! >>>
                             // Resetear el estado a IDLE DESPUÉS de renderizar exitosamente
                             if (loadingState === LOADING_STATES.GENERATING || loadingState === LOADING_STATES.FIXING_MERMAID) {
                                 console.log("USE_EFFECT (Mermaid): Render exitoso. Estado ANTES de reset:", loadingState);
                                 setLoadingState(LOADING_STATES.IDLE);
                                 console.log("USE_EFFECT (Mermaid): Estado cambiado a IDLE tras render exitoso.");
                             }
                             // <<< FIN DE LA ADICIÓN CRUCIAL >>>

                             // Éxito, resetear el tracker de intento de corrección para este código
                             if (mermaidCode === lastAttemptedMermaidCode) { // Only if this is the code we attempted to render
                                fixAttemptedRef.current = false;
                             }

                        }
                    })
                    .catch(error => {
                        console.error("Mermaid rendering error:", error);
                        if (mermaidContainerRef.current === container && diagramViewMode === 'image' && mermaidCode === lastAttemptedMermaidCode) {
                            // >>> Iniciar corrección automática (esto ya maneja el estado al finalizar)
                            triggerAutoFixMermaid(error.message, mermaidCode);
                        }
                    });
            } catch (error) {
                 console.error("Mermaid rendering setup error:", error);
                 if (mermaidContainerRef.current === container && diagramViewMode === 'image' && mermaidCode === lastAttemptedMermaidCode) {
                    // También podríamos intentar corregir aquí si es relevante, o solo mostrar error
                    setMermaidRenderError({ message: `Setup Error: ${error.message}`, code: mermaidCode });
                    // <<< AÑADIR ESTO: Asegurarse de que el estado no se quede en generando si hay error de setup >>>
                    console.log("USE_EFFECT (Mermaid): Error de setup. Estado ANTES de set ERROR:", loadingState);
                    setLoadingState(LOADING_STATES.ERROR);
                    console.log("USE_EFFECT (Mermaid): Estado cambiado a ERROR tras error de setup.");
                 }
            }
        }
        // Si no hay código y no hay error, mostrar mensajes de estado
        else if (loadingState === LOADING_STATES.GENERATING || loadingState === LOADING_STATES.RETRYING_JSON) {
             container.innerHTML = '<p>Esperando datos del diagrama...</p>';
        } else if (loadingState === LOADING_STATES.FIXING_MERMAID) {
            container.innerHTML = '<p>Puliendo diagrama...</p>';
        }
         else {
            container.innerHTML = '<p>El diagrama aparecerá aquí.</p>';
             // <<< AÑADIR ESTO: Resetear si llegamos aquí sin nada que hacer >>>
             if (loadingState === LOADING_STATES.GENERATING || loadingState === LOADING_STATES.FIXING_MERMAID) {
                console.log("USE_EFFECT (Mermaid): No hay código o error. Estado ANTES de reset:", loadingState);
                setLoadingState(LOADING_STATES.IDLE);
                console.log("USE_EFFECT (Mermaid): Estado cambiado a IDLE porque no hay render.");
             }
        }

    // Asegúrate de incluir loadingState en las dependencias si lo usas para condiciones de seteo
    }, [mermaidCode, diagramViewMode, mermaidRenderError, loadingState, triggerAutoFixMermaid, lastAttemptedMermaidCode, setLoadingState]); // Added setLoadingState to dependencies


    // Auto-scroll chat
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);


    // handleSend modificado para usar loadingState
    const handleSend = async (messageText) => {
        if (!messageText.trim() || loadingState !== LOADING_STATES.IDLE) return;

        const newUserMessage = { role: 'user', content: messageText };
        const updatedMessages = [...messages, newUserMessage];

        setMessages(updatedMessages);
        setCurrentInput('');
        setSuggestedReplies([]);
        setLoadingState(LOADING_STATES.GENERATING); // Estado inicial: generando
        setMermaidCode(null);
        setMermaidRenderError(null);
        fixAttemptedRef.current = false; // Resetear intento de corrección para nueva solicitud
        setLastAttemptedMermaidCode(null); // Reset the last attempted code on new send

        try {
            const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
            console.log("Intentando conectar a:", backendUrl); // <--- AÑADE ESTO
            const response = await fetch(`${backendUrl}/api/v1/db-chat/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: updatedMessages }),
            });

            if (!response.ok) {
                 let errorDetail = `HTTP error! status: ${response.status}`;
                 let errorBody = null;
                 try { errorBody = await response.json(); errorDetail = errorBody.detail || JSON.stringify(errorBody); }
                 catch (jsonError) { errorDetail = await response.text() || errorDetail; }
                 throw new Error(errorDetail);
            }
            const data = await response.json();
            console.log("Received from backend:", data);
            const newAIMessage = { role: 'model', content: data.reply };
            setMessages(prevMessages => [...prevMessages, newAIMessage]);
            setMermaidCode(data.mermaid_code); // Esto activará el useEffect de renderizado/corrección
            setSuggestedReplies(data.suggested_replies || []);

        } catch (error) {
            console.error("Error sending message:", error);
            const errorMessage = { role: 'model', content: `Error: ${error.message}` };
            setMessages(prevMessages => [...prevMessages, errorMessage]);
            setSuggestedReplies([]);
            setMermaidCode(null);
            setMermaidRenderError(null);
            setLoadingState(LOADING_STATES.ERROR); // Poner en estado de error
        } finally {
            // The loading state is reset to IDLE or ERROR within the useEffect or triggerAutoFixMermaid
            // if (loadingState === LOADING_STATES.GENERATING) { // Only if not entering correction cycle
            //    setLoadingState(LOADING_STATES.IDLE); // This is now handled by useEffect or triggerAutoFixMermaid
            // }
        }
    };

    // ... (toggleDiagramView, handleInputChange, handleKeyPress, handleSuggestedReplyClick sin cambios) ...
    const toggleDiagramView = () => { setDiagramViewMode(prevMode => (prevMode === 'image' ? 'code' : 'image')); };
    const handleInputChange = (event) => { setCurrentInput(event.target.value); };
    const handleKeyPress = (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); handleSend(currentInput); } };
    const handleSuggestedReplyClick = (replyText) => { handleSend(replyText); };

    // Determinar si la entrada/botones deben estar deshabilitados
    const isInputDisabled = loadingState !== LOADING_STATES.IDLE && loadingState !== LOADING_STATES.ERROR;

    // Texto del mensaje de carga
    const loadingMessage = () => {
        switch (loadingState) {
            case LOADING_STATES.GENERATING:
                return "Pensando...";
            case LOADING_STATES.RETRYING_JSON: // Aunque no lo usemos activamente, lo dejamos por si acaso
                return "Pensando con intensidad...";
            case LOADING_STATES.FIXING_MERMAID:
                return "Puliendo diagrama...";
            default:
                return null; // No mostrar mensaje si está IDLE o ERROR
        }
    };


    return (
        <div className="db-chat-container">
            <h1>Chat de Diseño de Base de Datos</h1>

            <div className="chat-and-diagram">
                {/* Ventana de Chat */}
                 <div className="chat-window" ref={chatContainerRef}>
                     {messages.map((msg, index) => (
                        <div key={index} className={`chat-message ${msg.role}`}> <div className="message-bubble"> {msg.content} </div> </div>
                    ))}
                    {/* Mostrar mensaje de carga específico */}
                    {loadingMessage() && (
                        <div className="chat-message model">
                            <div className="message-bubble loading"> {loadingMessage()} </div>
                        </div>
                    )}
                </div>

                {/* Contenedor del Diagrama */}
                <div className="mermaid-diagram-container">
                    <div className="diagram-header">
                        <h2>Diagrama ER</h2>
                        {/* Botón Ver Código/Diagrama */}
                        {(mermaidCode || mermaidRenderError) && !isInputDisabled && (
                            <button onClick={toggleDiagramView} className="view-toggle-btn" disabled={isInputDisabled}>
                                {diagramViewMode === 'image' ? 'Ver Código' : 'Ver Diagrama'}
                            </button>
                        )}
                    </div>
                    {/* Salida Mermaid (gestionada por useEffect) */}
                    <div ref={mermaidContainerRef} className="mermaid-output">
                        {/* Contenido inyectado por useEffect */}
                    </div>
                     {/* Ya no necesitamos el botón manual de "Intentar corregir" */}
                </div>
            </div>

            {/* Sugerencias */}
             {suggestedReplies.length > 0 && !isInputDisabled && (
                <div className="suggested-replies">
                    {suggestedReplies.map((reply, index) => (
                        <button key={index} onClick={() => handleSuggestedReplyClick(reply)} disabled={isInputDisabled}>
                            {reply}
                        </button>
                    ))}
                </div>
             )}

             {/* Área de Entrada */}
             <div className="chat-input-area">
                <textarea
                    value={currentInput}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    placeholder="Describe tu idea de base de datos..."
                    rows="3"
                    disabled={isInputDisabled}
                />
                <button onClick={() => handleSend(currentInput)} disabled={isInputDisabled}>
                    {isInputDisabled ? 'Procesando...' : 'Enviar'}
                </button>
             </div>

        </div>
    );
};

export default DbChatComponent;