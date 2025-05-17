document.addEventListener('DOMContentLoaded', function() {
    // Chat form processing
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message');
    const chatContainer = document.querySelector('.chat-container');
    const voiceInputBtn = document.getElementById('voice-input-btn');
    const voiceOutputToggle = document.getElementById('voice-output-toggle');
    const voiceStatus = document.getElementById('voice-status');
    
    // Voice recognition setup
    let recognition = null;
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
    }
    
    // Speech synthesis setup
    // Speech synthesis is now handled by voiceSynth class
    let voiceOutputEnabled = localStorage.getItem('voiceOutputEnabled') === 'true';
    
    // Update voice toggle button state based on stored preference
    if (voiceOutputToggle) {
        if (voiceOutputEnabled) {
            voiceOutputToggle.classList.add('active');
            voiceOutputToggle.classList.remove('btn-outline-secondary');
            voiceOutputToggle.classList.add('btn-secondary');
        } else {
            voiceOutputToggle.classList.remove('active');
            voiceOutputToggle.classList.add('btn-outline-secondary');
            voiceOutputToggle.classList.remove('btn-secondary');
        }
    }
    
    // Add existing messages to the chat if they exist
    function addExistingMessages() {
        // This will be populated from the server-side template
        if (typeof existingMessages !== 'undefined' && existingMessages.length > 0) {
            existingMessages.forEach(msg => {
                addMessageToChat(msg.role, msg.content);
            });
            
            // Scroll to the latest message
            scrollToLatestMessage();
        }
    }
    
    // Handle chat form submission
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = messageInput.value.trim();
            
            if (message) {
                // Add user message to chat immediately
                addMessageToChat('user', message);
                
                // Clear input field
                messageInput.value = '';
                
                // Send message to server
                sendMessage(message);
            }
        });
    }
    
    // Voice input button click handler
    if (voiceInputBtn && recognition) {
        voiceInputBtn.addEventListener('click', function() {
            if (voiceStatus.style.display === 'none' || voiceStatus.style.display === '') {
                // Start listening
                voiceStatus.style.display = 'block';
                recognition.start();
                
                // Update button style
                voiceInputBtn.classList.remove('btn-outline-secondary');
                voiceInputBtn.classList.add('btn-secondary');
            } else {
                // Stop listening
                voiceStatus.style.display = 'none';
                recognition.stop();
                
                // Reset button style
                voiceInputBtn.classList.add('btn-outline-secondary');
                voiceInputBtn.classList.remove('btn-secondary');
            }
        });
    } else if (voiceInputBtn) {
        // Voice recognition not supported
        voiceInputBtn.classList.add('disabled');
        voiceInputBtn.setAttribute('title', 'Voice input not supported in this browser');
    }
    
    // Voice output toggle click handler
    if (voiceOutputToggle) {
        voiceOutputToggle.addEventListener('click', function() {
            voiceOutputEnabled = !voiceOutputEnabled;
            localStorage.setItem('voiceOutputEnabled', voiceOutputEnabled);
            
            if (voiceOutputEnabled) {
                voiceOutputToggle.classList.remove('btn-outline-secondary');
                voiceOutputToggle.classList.add('btn-secondary');
            } else {
                voiceOutputToggle.classList.add('btn-outline-secondary');
                voiceOutputToggle.classList.remove('btn-secondary');
                
                // Stop any ongoing speech
                if (synth.speaking) {
                    synth.cancel();
                }
            }
        });
    }
    
    // Speech recognition result handler
    if (recognition) {
        recognition.onresult = function(event) {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');
            
            messageInput.value = transcript;
        };
        
        recognition.onend = function() {
            // Reset UI when recognition ends
            voiceStatus.style.display = 'none';
            voiceInputBtn.classList.add('btn-outline-secondary');
            voiceInputBtn.classList.remove('btn-secondary');
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            voiceStatus.style.display = 'none';
            voiceInputBtn.classList.add('btn-outline-secondary');
            voiceInputBtn.classList.remove('btn-secondary');
        };
    }
    
    // Send message to server
    function sendMessage(message) {
        // Show typing indicator
        showTypingIndicator();
        
        const formData = new FormData();
        formData.append('message', message);
        
        fetch('/chat/message', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add AI response to chat
            addMessageToChat('assistant', data.message, data.reasoning);
            
            // Speak the response if voice output is enabled
            if (voiceOutputEnabled && typeof voiceSynth !== 'undefined') {
                // Check if there's voice data in the response
                if (data.voice) {
                    // Use the voice settings from the response
                    const voiceSettings = {
                        pitch: data.voice.settings.pitch || 1,
                        rate: data.voice.settings.rate || 1,
                        gender: data.voice.voice.gender || 'neutral'
                    };
                    voiceSynth.speak(data.message, voiceSettings);
                } else {
                    // Use default settings
                    voiceSynth.speak(data.message);
                }
            }
            
            // Scroll to latest message
            scrollToLatestMessage();
        })
        .catch(error => {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            addMessageToChat('system', 'Error: Unable to get a response. Please try again.');
        });
    }
    
    // Add message to chat
    function addMessageToChat(role, content, reasoning = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        let messageContent = `
            <div class="message-avatar">
                <img src="/static/images/${role === 'user' ? 'user.svg' : 'assistant.svg'}" alt="${role} avatar">
            </div>
            <div class="message-content">
                <div class="message-text">${formatMessageContent(content)}</div>
                <div class="message-time">${getCurrentTime()}</div>
            </div>
        `;
        
        // Add reasoning section for assistant messages if available
        if (role === 'assistant' && reasoning) {
            messageContent += `
                <div class="message-reasoning">
                    <button class="btn btn-sm btn-outline-secondary reasoning-toggle" type="button" data-bs-toggle="collapse" data-bs-target="#reasoning-${Date.now()}" aria-expanded="false">
                        <i class="fas fa-brain"></i> View reasoning
                    </button>
                    <div class="collapse reasoning-content" id="reasoning-${Date.now()}">
                        <div class="card card-body mt-2">
                            ${reasoning}
                        </div>
                    </div>
                </div>
            `;
        }
        
        messageDiv.innerHTML = messageContent;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the latest message
        scrollToLatestMessage();
    }
    
    // Show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <img src="/static/images/assistant.svg" alt="assistant avatar">
            </div>
            <div class="message-content">
                <div class="message-text">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </div>
            </div>
        `;
        typingDiv.id = 'typing-indicator';
        chatMessages.appendChild(typingDiv);
        
        scrollToLatestMessage();
    }
    
    // Remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Format message content with Markdown or code blocks
    function formatMessageContent(content) {
        // Simple code block detection (not perfect but works for demo)
        content = content.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Bold text
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic text
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Links
        content = content.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
        
        // Convert new lines to <br>
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }
    
    // Get current time for message timestamp
    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Scroll to the latest message
    function scrollToLatestMessage() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Initial setup
    addExistingMessages();
    scrollToLatestMessage();
});