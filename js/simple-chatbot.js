/**
 * UHAI DAMU - Simple AI Chatbot
 * Intelligent blood donation assistant
 */

// ============================================
// CHATBOT CONFIGURATION
// ============================================
const CHATBOT_CONFIG = {
    apiUrl: '/api/chatbot/ask',  // Backend API endpoint
    botName: 'Uhai Damu Assistant',
    botAvatar: '🩸',
    theme: {
        primary: '#c41e3a',
        secondary: '#8b0000',
        light: '#ffebee'
    }
};

// ============================================
// KNOWLEDGE BASE (Fallback)
// ============================================
const knowledgeBase = {
    requirements: `📋 **Blood Donation Requirements in Kenya:**

✅ Age: 17-65 years old
✅ Weight: Minimum 50kg (110 lbs)
✅ Health: Good general health
✅ ID: National ID or Passport

❌ Cannot donate if you have:
• Cold, flu, or fever
• HIV, Hepatitis B/C
• Malaria or typhoid
• Recent surgery/tattoos (6 months)
• Pregnancy or breastfeeding`,
    
    locations: `📍 **Donation Centers in Nairobi & Kiambu:**

🏥 Kenyatta National Hospital
   📞 +254 20 271 3344
   📍 Hospital Rd, Nairobi

🏥 MP Shah Hospital
   📞 +254 20 429 4000
   📍 Shivachi Rd, Nairobi

🏥 Aga Khan University Hospital
   📞 +254 20 366 0000
   📍 3rd Parklands Ave, Nairobi

🏥 Thika Level 5 Hospital
   📞 +254 67 222 021
   📍 General Kago Rd, Thika

🏥 Kiambu County Referral Hospital
   📞 +254 67 222 000
   📍 Kiambu Town`,
    
    compatibility: `🩸 **Blood Type Compatibility:**

O- (Universal Donor):
   → Can donate to: ALL types
   → Can receive from: O- only

O+:
   → Can donate to: O+, A+, B+, AB+
   → Can receive from: O+, O-

A-:
   → Can donate to: A+, A-, AB+, AB-
   → Can receive from: A-, O-

A+:
   → Can donate to: A+, AB+
   → Can receive from: A+, A-, O+, O-

B-:
   → Can donate to: B+, B-, AB+, AB-
   → Can receive from: B-, O-

B+:
   → Can donate to: B+, AB+
   → Can receive from: B+, B-, O+, O-

AB-:
   → Can donate to: AB+, AB-
   → Can receive from: A-, B-, AB-, O-

AB+ (Universal Recipient):
   → Can donate to: AB+ only
   → Can receive from: ALL types`,
    
    process: `📋 **Blood Donation Process:**

1️⃣ Registration (5 minutes)
   • Fill out donor form
   • Show ID

2️⃣ Health Screening (10 minutes)
   • Check blood pressure
   • Test hemoglobin

3️⃣ Donation (10-15 minutes)
   • 450ml blood collected
   • Sterile equipment

4️⃣ Rest & Refreshments (15 minutes)
   • Drink juice/water
   • Eat snacks

5️⃣ Recovery
   • Don't lift heavy items for 24hrs
   • Drink plenty of fluids

Total time: 45-60 minutes`,
    
    emergency: `🚨 **EMERGENCY CONTACTS:**

📞 Emergency Hotline: +254 700 000 000 (24/7)
📧 Email: emergency@uhai-damu.co.ke

📍 Nairobi Regional Office: +254 704 000 004
📍 Kiambu Regional Office: +254 705 000 005

🏥 Kenyatta National Hospital: +254 20 271 3344

⚠️ For life-threatening emergencies, call 911 or go to the nearest hospital immediately!`,
    
    benefits: `💝 **Benefits of Blood Donation:**

❤️ Saves up to 3 lives per donation
💪 Free health check-up
🩸 Reduces excess iron (good for heart)
🔥 Burns 650 calories
📊 Learn your blood type
🎁 Get donor recognition
🌟 Feel great about helping others`,
    
    frequency: `📊 **How Often Can You Donate?**

🩸 Whole Blood:
   • Men: Every 3 months (4 times/year)
   • Women: Every 4 months (3 times/year)

🧬 Platelets (Apheresis):
   • Every 2 weeks (up to 24 times/year)

💧 Plasma:
   • Every 4 weeks

🔴 Double Red Cells:
   • Every 6 months`
};

// ============================================
// CHATBOT CLASS
// ============================================
class UhaiDamuChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.isTyping = false;
        this.init();
    }
    
    init() {
        this.createChatbotHTML();
        this.loadChatHistory();
        this.addEventListeners();
        this.addWelcomeMessage();
    }
    
    createChatbotHTML() {
        const chatbotHTML = `
            <div id="uhai-chatbot" class="chatbot-container">
                <button class="chatbot-toggle" id="chatbotToggle">
                    <span class="chatbot-icon">💬</span>
                    <span class="chatbot-notification" id="chatbotNotification">1</span>
                </button>
                
                <div class="chatbot-window" id="chatbotWindow">
                    <div class="chatbot-header">
                        <div class="chatbot-header-left">
                            <span class="chatbot-avatar">🩸</span>
                            <div class="chatbot-info">
                                <h4>Uhai Damu Assistant</h4>
                                <span class="chatbot-status">
                                    <span class="status-dot"></span> Online
                                </span>
                            </div>
                        </div>
                        <div class="chatbot-header-right">
                            <button class="chatbot-clear" id="clearChat" title="Clear chat">🗑️</button>
                            <button class="chatbot-close" id="closeChatbot" title="Close">✕</button>
                        </div>
                    </div>
                    
                    <div class="chatbot-messages" id="chatbotMessages"></div>
                    
                    <div class="chatbot-quick" id="quickQuestions">
                        <button class="quick-question" data-question="requirements">📋 Requirements</button>
                        <button class="quick-question" data-question="locations">📍 Locations</button>
                        <button class="quick-question" data-question="emergency">🚨 Emergency</button>
                        <button class="quick-question" data-question="compatibility">🩸 Blood Types</button>
                        <button class="quick-question" data-question="process">📋 Process</button>
                        <button class="quick-question" data-question="benefits">💝 Benefits</button>
                    </div>
                    
                    <div class="chatbot-input">
                        <input type="text" id="chatbotInput" placeholder="Ask about blood donation..." autocomplete="off">
                        <button id="sendMessage" class="chatbot-send">📤</button>
                    </div>
                    
                    <div class="chatbot-footer">
                        <span class="ai-indicator">💡 Knowledge Base</span>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
        this.injectStyles();
    }
    
    injectStyles() {
        const styles = `
            /* Chatbot Container */
            .chatbot-container {
                position: fixed;
                bottom: 30px;
                right: 30px;
                z-index: 9999;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            /* Toggle Button */
            .chatbot-toggle {
                width: 65px;
                height: 65px;
                border-radius: 50%;
                background: linear-gradient(135deg, #c41e3a, #8b0000);
                border: none;
                color: white;
                font-size: 28px;
                cursor: pointer;
                box-shadow: 0 6px 20px rgba(196,30,58,0.4);
                transition: all 0.3s;
                position: relative;
                animation: pulse 2s infinite;
            }
            
            .chatbot-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 8px 25px rgba(196,30,58,0.5);
            }
            
            .chatbot-notification {
                position: absolute;
                top: -5px;
                right: -5px;
                background: #ffc107;
                color: #333;
                width: 22px;
                height: 22px;
                border-radius: 50%;
                font-size: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                border: 2px solid white;
            }
            
            /* Chat Window */
            .chatbot-window {
                position: absolute;
                bottom: 80px;
                right: 0;
                width: 380px;
                height: 550px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                display: none;
                flex-direction: column;
                overflow: hidden;
                border: 1px solid rgba(0,0,0,0.1);
                animation: slideIn 0.3s ease;
            }
            
            .chatbot-window.active {
                display: flex;
            }
            
            /* Header */
            .chatbot-header {
                background: linear-gradient(135deg, #c41e3a, #8b0000);
                color: white;
                padding: 15px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .chatbot-header-left {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .chatbot-avatar {
                width: 40px;
                height: 40px;
                background: rgba(255,255,255,0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
            }
            
            .chatbot-info h4 {
                margin: 0;
                font-size: 14px;
                font-weight: 600;
            }
            
            .chatbot-status {
                font-size: 11px;
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .status-dot {
                width: 8px;
                height: 8px;
                background: #4caf50;
                border-radius: 50%;
                display: inline-block;
                animation: blink 1.5s infinite;
            }
            
            .chatbot-clear, .chatbot-close {
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .chatbot-clear:hover, .chatbot-close:hover {
                background: rgba(255,255,255,0.3);
                transform: scale(1.1);
            }
            
            /* Messages */
            .chatbot-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background: #f8f9fa;
                scroll-behavior: smooth;
            }
            
            .message {
                margin-bottom: 15px;
                display: flex;
                animation: fadeIn 0.3s ease;
            }
            
            .message-bot {
                justify-content: flex-start;
            }
            
            .message-user {
                justify-content: flex-end;
            }
            
            .message-content {
                max-width: 85%;
                padding: 12px 16px;
                border-radius: 18px;
                font-size: 14px;
                line-height: 1.5;
                word-wrap: break-word;
                white-space: pre-line;
            }
            
            .message-bot .message-content {
                background: white;
                border: 1px solid #e9ecef;
                border-bottom-left-radius: 5px;
                color: #333;
            }
            
            .message-user .message-content {
                background: #c41e3a;
                color: white;
                border-bottom-right-radius: 5px;
            }
            
            /* Typing Indicator */
            .typing-indicator {
                display: flex;
                gap: 5px;
                padding: 12px 16px;
                background: white;
                border-radius: 18px;
                border: 1px solid #e9ecef;
                width: fit-content;
            }
            
            .typing-dot {
                width: 8px;
                height: 8px;
                background: #c41e3a;
                border-radius: 50%;
                animation: typing 1.4s infinite;
            }
            
            .typing-dot:nth-child(2) { animation-delay: 0.2s; }
            .typing-dot:nth-child(3) { animation-delay: 0.4s; }
            
            /* Quick Questions */
            .chatbot-quick {
                padding: 10px 15px;
                background: white;
                border-top: 1px solid #e9ecef;
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }
            
            .quick-question {
                background: #f0f0f0;
                border: 1px solid #ddd;
                padding: 6px 12px;
                border-radius: 30px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.3s;
                color: #333;
            }
            
            .quick-question:hover {
                background: #c41e3a;
                color: white;
                border-color: #c41e3a;
            }
            
            /* Input Area */
            .chatbot-input {
                padding: 15px;
                background: white;
                border-top: 1px solid #e9ecef;
                display: flex;
                gap: 10px;
            }
            
            #chatbotInput {
                flex: 1;
                padding: 12px 15px;
                border: 2px solid #e9ecef;
                border-radius: 30px;
                font-size: 14px;
                outline: none;
            }
            
            #chatbotInput:focus {
                border-color: #c41e3a;
                box-shadow: 0 0 0 3px rgba(196,30,58,0.1);
            }
            
            .chatbot-send {
                width: 45px;
                height: 45px;
                border-radius: 50%;
                background: #c41e3a;
                border: none;
                color: white;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 18px;
            }
            
            .chatbot-send:hover {
                background: #8b0000;
                transform: scale(1.1);
            }
            
            /* Footer */
            .chatbot-footer {
                padding: 8px 15px;
                background: #f8f9fa;
                border-top: 1px solid #e9ecef;
                font-size: 11px;
                text-align: center;
                color: #666;
            }
            
            /* Animations */
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.4; }
            }
            
            @keyframes typing {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-5px); }
            }
            
            /* Responsive */
            @media (max-width: 480px) {
                .chatbot-window {
                    width: calc(100vw - 40px);
                    height: 60vh;
                    right: 20px;
                    bottom: 90px;
                }
                .chatbot-toggle {
                    width: 55px;
                    height: 55px;
                    font-size: 24px;
                }
            }
            
            /* Scrollbar */
            .chatbot-messages::-webkit-scrollbar {
                width: 6px;
            }
            .chatbot-messages::-webkit-scrollbar-track {
                background: #f1f1f1;
            }
            .chatbot-messages::-webkit-scrollbar-thumb {
                background: #c41e3a;
                border-radius: 3px;
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    addEventListeners() {
        const toggle = document.getElementById('chatbotToggle');
        const close = document.getElementById('closeChatbot');
        const send = document.getElementById('sendMessage');
        const input = document.getElementById('chatbotInput');
        const clear = document.getElementById('clearChat');
        const quickQuestions = document.querySelectorAll('.quick-question');
        
        toggle.addEventListener('click', () => this.toggleChatbot());
        close.addEventListener('click', () => this.closeChatbot());
        send.addEventListener('click', () => this.sendMessage());
        clear.addEventListener('click', () => this.clearChat());
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        quickQuestions.forEach(btn => {
            btn.addEventListener('click', () => {
                const questionKey = btn.dataset.question;
                const question = this.getQuestionText(questionKey);
                this.addUserMessage(question);
                this.processMessage(question);
            });
        });
    }
    
    getQuestionText(key) {
        const questions = {
            'requirements': 'What are the requirements to donate blood?',
            'locations': 'Where can I donate blood?',
            'emergency': 'What is the emergency contact?',
            'compatibility': 'Tell me about blood type compatibility',
            'process': 'What is the donation process?',
            'benefits': 'What are the benefits of donating blood?'
        };
        return questions[key] || key;
    }
    
    toggleChatbot() {
        const window = document.getElementById('chatbotWindow');
        this.isOpen = !this.isOpen;
        window.classList.toggle('active');
        
        if (this.isOpen) {
            document.getElementById('chatbotInput').focus();
            const notification = document.getElementById('chatbotNotification');
            if (notification) notification.style.display = 'none';
        }
    }
    
    closeChatbot() {
        document.getElementById('chatbotWindow').classList.remove('active');
        this.isOpen = false;
    }
    
    sendMessage() {
        const input = document.getElementById('chatbotInput');
        const message = input.value.trim();
        if (!message) return;
        
        this.addUserMessage(message);
        input.value = '';
        this.processMessage(message);
    }
    
    addUserMessage(text) {
        this.addMessage('user', text);
    }
    
    addBotMessage(text) {
        this.addMessage('bot', text);
    }
    
    addMessage(sender, text) {
        const messagesDiv = document.getElementById('chatbotMessages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = this.formatMessage(text);
        
        messageDiv.appendChild(contentDiv);
        messagesDiv.appendChild(messageDiv);
        
        this.messages.push({ sender, text, timestamp: new Date() });
        this.saveChatHistory();
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    showTypingIndicator() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        const messagesDiv = document.getElementById('chatbotMessages');
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message message-bot';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        `;
        
        messagesDiv.appendChild(typingDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        const indicator = document.getElementById('typingIndicator');
        if (indicator) indicator.remove();
    }
    
    async processMessage(message) {
        this.showTypingIndicator();
        
        try {
            // Try API first
            const response = await fetch(CHATBOT_CONFIG.apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            setTimeout(() => {
                this.hideTypingIndicator();
                if (data.success && data.response) {
                    this.addBotMessage(data.response);
                } else {
                    this.addBotMessage(this.getLocalResponse(message));
                }
            }, 800);
            
        } catch (error) {
            // Fallback to local knowledge base
            setTimeout(() => {
                this.hideTypingIndicator();
                this.addBotMessage(this.getLocalResponse(message));
            }, 800);
        }
    }
    
    getLocalResponse(message) {
        const msg = message.toLowerCase();
        
        if (msg.includes('require') || msg.includes('eligible') || msg.includes('can i donate')) {
            return knowledgeBase.requirements;
        }
        if (msg.includes('where') || msg.includes('location') || msg.includes('center') || msg.includes('hospital')) {
            return knowledgeBase.locations;
        }
        if (msg.includes('compatible') || msg.includes('match') || msg.includes('type')) {
            return knowledgeBase.compatibility;
        }
        if (msg.includes('process') || msg.includes('step') || msg.includes('how to')) {
            return knowledgeBase.process;
        }
        if (msg.includes('emergency') || msg.includes('urgent') || msg.includes('help')) {
            return knowledgeBase.emergency;
        }
        if (msg.includes('benefit') || msg.includes('why donate') || msg.includes('good')) {
            return knowledgeBase.benefits;
        }
        if (msg.includes('often') || msg.includes('frequent') || msg.includes('times')) {
            return knowledgeBase.frequency;
        }
        if (msg.includes('hi') || msg.includes('hello') || msg.includes('hey')) {
            return "👋 Hello! I'm your Uhai Damu Assistant. How can I help you with blood donation today?";
        }
        if (msg.includes('thank')) {
            return "❤️ You're welcome! Thank you for your interest in saving lives. Is there anything else I can help with?";
        }
        
        return `I can help with blood donation! Ask me about:
• ✅ Requirements to donate
• 📍 Donation centers
• 🩸 Blood type compatibility
• 📋 Donation process
• 🚨 Emergency contacts
• 💝 Benefits of donation

What would you like to know?`;
    }
    
    formatMessage(text) {
        // Convert URLs to links
        text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        
        // Convert phone numbers to clickable
        text = text.replace(/(\+?\d{3}[-.]?\d{3}[-.]?\d{4})/g, '<a href="tel:$1">$1</a>');
        
        // Convert line breaks
        text = text.replace(/\n/g, '<br>');
        
        // Convert bold text
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        return text;
    }
    
    addWelcomeMessage() {
        setTimeout(() => {
            if (this.messages.length === 0) {
                this.addBotMessage("🩸 **Welcome to Uhai Damu!**\n\nI'm your blood donation assistant. I can help you with:\n\n• ✅ Donation requirements\n• 📍 Where to donate\n• 🩸 Blood type compatibility\n• 📋 Donation process\n• 🚨 Emergency contacts\n• 💝 Benefits of donation\n\nWhat would you like to know?");
            }
        }, 1000);
    }
    
    clearChat() {
        if (confirm('Clear chat history?')) {
            this.messages = [];
            document.getElementById('chatbotMessages').innerHTML = '';
            localStorage.removeItem('uhai_chat_history');
            this.addWelcomeMessage();
        }
    }
    
    saveChatHistory() {
        try {
            const history = this.messages.slice(-50);
            localStorage.setItem('uhai_chat_history', JSON.stringify(history));
        } catch (e) {
            console.warn('Could not save chat history');
        }
    }
    
    loadChatHistory() {
        try {
            const saved = localStorage.getItem('uhai_chat_history');
            if (saved) {
                this.messages = JSON.parse(saved);
                this.messages.forEach(msg => {
                    this.addMessage(msg.sender, msg.text);
                });
            }
        } catch (e) {
            console.warn('Could not load chat history');
        }
    }
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        window.chatbot = new UhaiDamuChatbot();
    }, 500);
});