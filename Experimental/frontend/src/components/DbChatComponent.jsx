import React, { useState, useEffect, useRef } from 'react';
import mermaid from 'mermaid';
import './db-chat.css'; // We will create this CSS file next

const DbChatComponent = () => {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [mermaidCode, setMermaidCode] = useState(null);
    const [suggestedReplies, setSuggestedReplies] = useState([]);
    const [currentInput, setCurrentInput] = useState('');

    const chatContainerRef = useRef(null);
    const mermaidContainerRef = useRef(null);

    // Initialize Mermaid
    useEffect(() => {
        mermaid.initialize({ startOnLoad: false });
    }, []);

    // Render Mermaid diagram whenever mermaidCode changes
    useEffect(() => {
        if (mermaidCode && mermaidContainerRef.current) {
            try {
                mermaid.render('mermaid-diagram', mermaidCode)
                    .then(({ svg }) => {
                        mermaidContainerRef.current.innerHTML = svg;
                    })
                    .catch(error => {
                        console.error("Mermaid rendering error:", error);
                        mermaidContainerRef.current.innerHTML = `<p style="color: red;">Error rendering diagram: ${error.message}</p>`;
                    });
            } catch (error) {
                 console.error("Mermaid rendering setup error:", error);
                 mermaidContainerRef.current.innerHTML = `<p style="color: red;">Setup error rendering diagram: ${error.message}</p>`;
            }
        } else if (mermaidContainerRef.current) {
            mermaidContainerRef.current.innerHTML = ''; // Clear diagram if no code
        }
    }, [mermaidCode]);

    // Auto-scroll chat to bottom
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async (messageText) => {
        if (!messageText.trim() || isLoading) return;

        const newUserMessage = { role: 'user', content: messageText };
        const updatedMessages = [...messages, newUserMessage];
        setMessages(updatedMessages);
        setCurrentInput('');
        setSuggestedReplies([]); // Clear suggestions when user sends a message
        setIsLoading(true);

        try {
            // Use the environment variable for the backend URL
            // Use localhost:8000 to access the backend from the browser on the host machine
            const backendUrl = 'http://localhost:8000';

            const response = await fetch(`${backendUrl}/api/v1/db-chat/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ messages: updatedMessages }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Received from backend:", data); // Log the received data

            const newAIMessage = { role: 'model', content: data.reply };
            setMessages(prevMessages => [...prevMessages, newAIMessage]);
            setMermaidCode(data.mermaid_code);
            setSuggestedReplies(data.suggested_replies || []); // Ensure it's an array

        } catch (error) {
            console.error("Error sending message:", error);
            const errorMessage = { role: 'model', content: `Error: ${error.message}` };
            setMessages(prevMessages => [...prevMessages, errorMessage]);
            setSuggestedReplies([]); // Clear suggestions on error
        } finally {
            setIsLoading(false);
        }
    };

    const handleInputChange = (event) => {
        setCurrentInput(event.target.value);
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSend(currentInput);
        }
    };

    const handleSuggestedReplyClick = (replyText) => {
        handleSend(replyText);
    };

    return (
        <div className="db-chat-container">
            <h1>Database Design Chat</h1>

            <div className="chat-and-diagram">
                <div className="chat-window" ref={chatContainerRef}>
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
                    <div ref={mermaidContainerRef} className="mermaid-output">
                        {/* Mermaid diagram will be rendered here */}
                        {!mermaidCode && <p>Diagram will appear here as you design your database.</p>}
                    </div>
                </div>
            </div>

            {suggestedReplies.length > 0 && (
                <div className="suggested-replies">
                    {suggestedReplies.map((reply, index) => (
                        <button
                            key={index}
                            onClick={() => handleSuggestedReplyClick(reply)}
                            disabled={isLoading}
                        >
                            {reply}
                        </button>
                    ))}
                </div>
            )}

            <div className="chat-input-area">
                <textarea
                    value={currentInput}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    placeholder="Describe your database idea..."
                    rows="3"
                    disabled={isLoading}
                />
                <button onClick={() => handleSend(currentInput)} disabled={isLoading}>
                    Send
                </button>
            </div>
        </div>
    );
};

export default DbChatComponent;