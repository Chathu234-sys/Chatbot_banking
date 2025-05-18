document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const typingIndicator = document.getElementById('typing-indicator');
    const unknownQueryForm = document.getElementById('unknown-query-form');
    const userAnswer = document.getElementById('user-answer');
    const submitAnswer = document.getElementById('submit-answer');
    const cancelAnswer = document.getElementById('cancel-answer');
    
    // State variables
    let currentQueryId = null;
    let lastUserQuery = '';
    
    // Add welcome message
    addBotMessage("Hello! I'm your banking assistant. How can I help you today?");
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    submitAnswer.addEventListener('click', submitUserAnswer);
    cancelAnswer.addEventListener('click', cancelUserAnswer);
    
    // Send message function
    function sendMessage() {
        const message = userInput.value.trim();
        
        if (message === '') {
            return;
        }
        
        // Add user message to chat
        addUserMessage(message);
        
        // Clear input
        userInput.value = '';
        
        // Save last query
        lastUserQuery = message;
        
        // Show typing indicator
        typingIndicator.classList.remove('d-none');
        
        // Send request to server
        fetch('/api/v1/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: message })
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            typingIndicator.classList.add('d-none');
            
            if (data.query_id) {
                // Unknown query
                currentQueryId = data.query_id;
                unknownQueryForm.classList.remove('d-none');
            } else {
                // Regular response
                addBotMessage(data.response);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Hide typing indicator
            typingIndicator.classList.add('d-none');
            
            // Show error message
            addBotMessage("I'm sorry, but I encountered an error processing your request. Please try again later.");
        });
    }
    
    // Submit user answer for unknown query
    function submitUserAnswer() {
        const answer = userAnswer.value.trim();
        
        if (answer === '') {
            alert('Please provide an answer');
            return;
        }
        
        // Disable form
        submitAnswer.disabled = true;
        cancelAnswer.disabled = true;
        
        // Send answer to server
        fetch(`/api/v1/chat/learn/${currentQueryId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ answer: answer })
        })
        .then(response => response.json())
        .then(data => {
            // Hide form
            unknownQueryForm.classList.add('d-none');
            
            // Add bot message
            addBotMessage("Thank you for teaching me! I'll remember that for next time.");
            
            // Add the answer as a bot message
            addBotMessage(answer);
            
            // Reset form
            userAnswer.value = '';
            submitAnswer.disabled = false;
            cancelAnswer.disabled = false;
            currentQueryId = null;
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Show error message
            addBotMessage("I'm sorry, but I encountered an error saving your answer. Please try again later.");
            
            // Reset form
            submitAnswer.disabled = false;
            cancelAnswer.disabled = false;
        });
    }
    
    // Cancel user answer for unknown query
    function cancelUserAnswer() {
        unknownQueryForm.classList.add('d-none');
        userAnswer.value = '';
        currentQueryId = null;
        
        // Add bot message
        addBotMessage("No problem. Is there something else I can help you with?");
    }
    
    // Add user message to chat
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message user-message';
        messageElement.innerHTML = `
            ${message}
            <div class="message-time">${getCurrentTime()}</div>
        `;
        
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }
    
    // Add bot message to chat
    function addBotMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message bot-message';
        
        // Format the message (handle line breaks)
        const formattedMessage = message.replace(/\n/g, '<br>');
        
        messageElement.innerHTML = `
            ${formattedMessage}
            <div class="message-time">${getCurrentTime()}</div>
        `;
        
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }
    
    // Scroll to bottom of chat
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Get current time in HH:MM format
    function getCurrentTime() {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        
        return `${hours}:${minutes}`;
    }
});