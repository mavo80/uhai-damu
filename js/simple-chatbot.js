/**
 * UHAI DAMU - Simple Working Chatbot
 */

document.addEventListener('DOMContentLoaded', function() {
    // Create chatbot HTML
    const chatbotHTML = `
        <div id="chatbot" style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; font-family: Arial, sans-serif;">
            <button id="chatBtn" style="background: #c41e3a; color: white; border: none; border-radius: 50px; padding: 12px 20px; cursor: pointer; box-shadow: 0 2px 10px rgba(0,0,0,0.2); display: flex; align-items: center; gap: 8px;">
                💬 Chat with us
            </button>
            <div id="chatWindow" style="display: none; position: absolute; bottom: 70px; right: 0; width: 300px; height: 400px; background: white; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.2); flex-direction: column; overflow: hidden;">
                <div style="background: #c41e3a; color: white; padding: 10px; text-align: center;">
                    <strong>Uhai Damu Assistant</strong>
                    <button id="closeChat" style="float: right; background: none; border: none; color: white; cursor: pointer;">✕</button>
                </div>
                <div id="chatMessages" style="flex: 1; padding: 10px; overflow-y: auto; background: #f5f5f5;"></div>
                <div style="padding: 10px; display: flex; gap: 5px;">
                    <input id="chatInput" type="text" placeholder="Ask a question..." style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    <button id="sendChat" style="background: #c41e3a; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">Send</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    
    const chatBtn = document.getElementById('chatBtn');
    const chatWindow = document.getElementById('chatWindow');
    const closeChat = document.getElementById('closeChat');
    const sendChat = document.getElementById('sendChat');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    
    let isOpen = false;
    
    chatBtn.onclick = () => {
        isOpen = !isOpen;
        chatWindow.style.display = isOpen ? 'flex' : 'none';
        if (isOpen && chatMessages.children.length === 0) {
            addMessage('bot', 'Hello! I\'m your Uhai Damu assistant. Ask me about blood donation requirements, where to donate, or emergency contacts.');
        }
    };
    
    closeChat.onclick = () => {
        isOpen = false;
        chatWindow.style.display = 'none';
    };
    
    function addMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.style.margin = '5px 0';
        msgDiv.style.textAlign = sender === 'user' ? 'right' : 'left';
        msgDiv.innerHTML = `<span style="display: inline-block; padding: 8px 12px; border-radius: 15px; background: ${sender === 'user' ? '#c41e3a' : '#e0e0e0'}; color: ${sender === 'user' ? 'white' : 'black'};">${text}</span>`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function getResponse(message) {
        const msg = message.toLowerCase();
        
        if (msg.includes('require') || msg.includes('eligible')) {
            return "Blood donation requirements: Age 17-65 years, Weight 50kg+, Good health, Valid ID.";
        }
        if (msg.includes('where') || msg.includes('location')) {
            return "Donation centers: Kenyatta National Hospital, MP Shah Hospital, Aga Khan Hospital, Thika Level 5 Hospital.";
        }
        if (msg.includes('emergency') || msg.includes('urgent')) {
            return "Emergency Hotline: +254 700 000 000 (24/7). For life-threatening emergencies, go to the nearest hospital.";
        }
        if (msg.includes('type') || msg.includes('compatible')) {
            return "O- is the universal donor. AB+ is the universal recipient. Check our Blood Group Chart for full compatibility.";
        }
        if (msg.includes('hi') || msg.includes('hello')) {
            return "Hello! How can I help you with blood donation today?";
        }
        
        return "I can help with blood donation requirements, locations, emergency contacts, and blood types. What would you like to know?";
    }
    
    sendChat.onclick = () => {
        const question = chatInput.value.trim();
        if (!question) return;
        
        addMessage('user', question);
        chatInput.value = '';
        
        setTimeout(() => {
            const answer = getResponse(question);
            addMessage('bot', answer);
        }, 500);
    };
    
    chatInput.onkeypress = (e) => {
        if (e.key === 'Enter') sendChat.onclick();
    };
});