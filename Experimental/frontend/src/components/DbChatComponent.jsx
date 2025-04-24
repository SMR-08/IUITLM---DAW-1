import React, { useState, useEffect, useRef } from 'react';
import mermaid from 'mermaid';
import './db-chat.css';

const DbChatComponent = () => {
    // ... (estados useState sin cambios) ...
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [mermaidCode, setMermaidCode] = useState(null);
    const [suggestedReplies, setSuggestedReplies] = useState([]);
    const [currentInput, setCurrentInput] = useState('');

    const chatContainerRef = useRef(null);
    const mermaidContainerRef = useRef(null);

    // Initialize Mermaid (sin cambios)
    useEffect(() => {
        mermaid.initialize({ startOnLoad: false });
    }, []);

    // Render Mermaid diagram whenever mermaidCode or isLoading changes
    useEffect(() => {
        const container = mermaidContainerRef.current;
        // Solo continuar si el contenedor existe en el DOM
        if (!container) {
            return;
        }

        // Decidir qué mostrar DENTRO del contenedor
        if (mermaidCode) {
            // Tenemos código Mermaid, intentar renderizarlo
            container.innerHTML = 'Rendering diagram...'; // Mostrar estado mientras se renderiza
            try {
                mermaid.render('mermaid-diagram', mermaidCode)
                    .then(({ svg }) => {
                        // Solo actualizar si el componente no se desmontó mientras tanto
                        // Y si todavía tenemos código (por si el usuario envió otro msg rápido)
                        if (mermaidContainerRef.current === container && mermaidCode) {
                             container.innerHTML = svg;
                        }
                    })
                    .catch(error => {
                        console.error("Mermaid rendering error:", error);
                        if (mermaidContainerRef.current === container) {
                            container.innerHTML = `<p style="color: red;">Error rendering diagram: ${error.message}</p><pre style="font-size: 0.8em; color: grey;">${mermaidCode}</pre>`;
                        }
                    });
            } catch (error) {
                 console.error("Mermaid rendering setup error:", error);
                 if (mermaidContainerRef.current === container) {
                    container.innerHTML = `<p style="color: red;">Setup error rendering diagram: ${error.message}</p>`;
                 }
            }
        } else if (isLoading) {
            // No code, but we are waiting for backend response
            // You can put a message or leave it empty if the "Thinking..." in the chat is enough
            container.innerHTML = '<p>Waiting for diagram data...</p>'; // Or simply ''
        } else {
            // No code and not loading -> Initial state or after response without diagram
            container.innerHTML = '<p>Diagram will appear here as you design your database.</p>';
        }

    // We depend on both to update the content correctly
    }, [mermaidCode, isLoading]);

    // Auto-scroll chat to bottom (sin cambios)
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);

    // handleSend (sin cambios)
    const handleSend = async (messageText) => {
        if (!messageText.trim() || isLoading) return;

        const newUserMessage = { role: 'user', content: messageText };
        const updatedMessages = [...messages, newUserMessage];
        setMessages(updatedMessages);
        setCurrentInput('');
        setSuggestedReplies([]);
        setIsLoading(true);
        // Important: Reset mermaidCode here so the useEffect shows "Waiting..."
        setMermaidCode(null);

        try {
            const backendUrl = 'http://localhost:8000';
            const response = await fetch(`${backendUrl}/api/v1/db-chat/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: updatedMessages }),
            });

            if (!response.ok) {
                // Try to get the error detail, even if it's not JSON
                let errorDetail = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || JSON.stringify(errorData);
                } catch (jsonError) {
                    // If the error response is not JSON, use the text
                    errorDetail = await response.text() || errorDetail;
                }
                throw new Error(errorDetail);
            }

            const data = await response.json();
            console.log("Received from backend:", data);

            const newAIMessage = { role: 'model', content: data.reply };
            setMessages(prevMessages => [...prevMessages, newAIMessage]);
            // Update mermaidCode AFTER messages
            setMermaidCode(data.mermaid_code);
            setSuggestedReplies(data.suggested_replies || []);

        } catch (error) {
            console.error("Error sending message:", error);
            const errorMessage = { role: 'model', content: `Error: ${error.message}` };
            setMessages(prevMessages => [...prevMessages, errorMessage]);
            setSuggestedReplies([]);
            // Make sure to reset mermaidCode on error as well
            setMermaidCode(null);
        } finally {
            setIsLoading(false);
        }
    };

    // ... (handleInputChange, handleKeyPress, handleSuggestedReplyClick sin cambios) ...
    const handleInputChange = (event) => { setCurrentInput(event.target.value); };
    const handleKeyPress = (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); handleSend(currentInput); } };
    const handleSuggestedReplyClick = (replyText) => { handleSend(replyText); };

    return (
        <div className="db-chat-container">
            <h1>Database Design Chat</h1>

            <div className="chat-and-diagram">
                <div className="chat-window" ref={chatContainerRef}>
                    {/* ... (renderizado de mensajes sin cambios) ... */}
                     {messages.map((msg, index) => (
                        <div key={index} className={`chat-message ${msg.role}`}>
                            <div className="message-bubble">
                                {msg.content}
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                         <div className="chat-message model">
                             <div className="message-bubble loading">
                                 Thinking...
                             </div>
                         </div>
                    )}
                </div>

                <div className="mermaid-diagram-container">
                    <h2>ER Diagram</h2>
                    {/* Contenedor para Mermaid. Mantenemos la key para forzar re-montaje */}
                    {/* PERO el contenido interno ahora lo gestiona SÓLO el useEffect */}
                    <div
                        key={mermaidCode || 'no-mermaid'} // Mantenemos la key para ayudar a React
                        ref={mermaidContainerRef}
                        className="mermaid-output"
                        /* No renderizar contenido aquí directamente */
                    ></div>
                </div>
            </div>

             {/* ... (renderizado de sugerencias y input sin cambios) ... */}
             {suggestedReplies.length > 0 && (
                <div className="suggested-replies">
                    {suggestedReplies.map((reply, index) => (
                        <button key={index} onClick={() => handleSuggestedReplyClick(reply)} disabled={isLoading}>
                            {reply}
                        </button>
                    ))}
                </div>
            )}
            <div className="chat-input-area">
                <textarea value={currentInput} onChange={handleInputChange} onKeyPress={handleKeyPress} placeholder="Describe your database idea..." rows="3" disabled={isLoading} />
                <button onClick={() => handleSend(currentInput)} disabled={isLoading}> Send </button>
            </div>
        </div>
    );
};

export default DbChatComponent;