/**
 * UHAI DAMU - AI Chatbot Assistant
 * Complete Chatbot System with Blood Donation Knowledge Base
 */

class BloodDonationChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        // Create chatbot HTML structure
        this.createChatbotHTML();
        
        // Add event listeners
        this.addEventListeners();
        
        // Add initial greeting
        setTimeout(() => {
            this.addMessage('bot', '🩸 Hello! I\'m Uhai Damu Assistant. How can I help you with blood donation today?');
            this.addQuickReplies();
        }, 500);
    }

    createChatbotHTML() {
        const chatbotHTML = `
            <div class="chatbot-container" id="chatbot">
                <div class="chatbot-window" id="chatbotWindow">
                    <div class="chatbot-header">
                        <h4>
                            <span class="blood-icon">🩸</span>
                            Uhai Damu Assistant
                        </h4>
                        <button class="chatbot-close" id="closeChatbot">
                            <i class="fas fa-times"></i> ✕
                        </button>
                    </div>
                    <div class="chatbot-messages" id="chatbotMessages">
                        <!-- Messages will appear here -->
                    </div>
                    <div class="chatbot-input">
                        <input type="text" id="chatbotInput" placeholder="Type your question..." autocomplete="off">
                        <button id="sendMessage">
                            <i class="fas fa-paper-plane"></i> ➤
                        </button>
                    </div>
                </div>
                <button class="chatbot-toggle" id="chatbotToggle">
                    <span class="blood-icon">🩸</span>
                </button>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    }

    addEventListeners() {
        const toggle = document.getElementById('chatbotToggle');
        const close = document.getElementById('closeChatbot');
        const send = document.getElementById('sendMessage');
        const input = document.getElementById('chatbotInput');
        const window = document.getElementById('chatbotWindow');

        // Toggle chatbot
        toggle.addEventListener('click', () => {
            window.classList.toggle('active');
            this.isOpen = window.classList.contains('active');
            
            if (this.isOpen) {
                input.focus();
            }
        });

        // Close chatbot
        close.addEventListener('click', () => {
            window.classList.remove('active');
            this.isOpen = false;
        });

        // Send message
        send.addEventListener('click', () => this.sendUserMessage());
        
        // Enter key
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendUserMessage();
            }
        });
    }

    sendUserMessage() {
        const input = document.getElementById('chatbotInput');
        const message = input.value.trim();
        
        if (message === '') return;
        
        // Add user message
        this.addMessage('user', message);
        
        // Clear input
        input.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Generate response after delay
        setTimeout(() => {
            this.hideTypingIndicator();
            const response = this.generateResponse(message);
            this.addMessage('bot', response);
            
            // Suggest follow-up questions
            setTimeout(() => {
                this.addQuickReplies();
            }, 1000);
        }, 1000 + Math.random() * 1000);
    }

    addMessage(sender, text) {
        const messagesContainer = document.getElementById('chatbotMessages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = this.formatMessage(text);
        
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    formatMessage(text) {
        // Convert URLs to links
        text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        
        // Convert bold text
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert italic text
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert line breaks
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbotMessages');
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message message-bot';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-content">
                <span class="typing-dots">
                    <span>.</span><span>.</span><span>.</span>
                </span>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    addQuickReplies() {
        const quickReplies = [
            'Blood donation requirements',
            'Where can I donate?',
            'Blood types compatibility',
            'Donation process',
            'Emergency contact'
        ];
        
        const messagesContainer = document.getElementById('chatbotMessages');
        
        const quickRepliesDiv = document.createElement('div');
        quickRepliesDiv.className = 'message message-bot quick-replies';
        quickRepliesDiv.style.display = 'flex';
        quickRepliesDiv.style.flexWrap = 'wrap';
        quickRepliesDiv.style.gap = '10px';
        quickRepliesDiv.style.marginBottom = '15px';
        
        quickReplies.forEach(reply => {
            const button = document.createElement('button');
            button.className = 'quick-reply-btn';
            button.style.cssText = `
                background: #f0f0f0;
                border: 1px solid #ddd;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.3s;
                color: var(--dark-gray);
            `;
            button.innerHTML = reply;
            
            button.addEventListener('mouseover', () => {
                button.style.background = 'var(--primary-red)';
                button.style.color = 'white';
                button.style.borderColor = 'var(--primary-red)';
            });
            
            button.addEventListener('mouseout', () => {
                button.style.background = '#f0f0f0';
                button.style.color = 'var(--dark-gray)';
                button.style.borderColor = '#ddd';
            });
            
            button.addEventListener('click', () => {
                this.addMessage('user', reply);
                const response = this.generateResponse(reply);
                setTimeout(() => this.addMessage('bot', response), 500);
                quickRepliesDiv.remove();
            });
            
            quickRepliesDiv.appendChild(button);
        });
        
        messagesContainer.appendChild(quickRepliesDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    generateResponse(input) {
        input = input.toLowerCase();
        
        // Blood donation requirements
        if (input.includes('require') || input.includes('eligibility') || input.includes('can i donate')) {
            return `🩸 **Blood Donation Requirements:**\n\n✅ Age: 17-65 years\n✅ Weight: Minimum 50kg\n✅ General good health\n✅ No recent illnesses\n✅ Not pregnant or breastfeeding\n✅ No recent tattoos/piercings (6 months)\n✅ Healthy hemoglobin levels\n\nVisit any KNBTS center or partner hospital to check your eligibility!`;
        }
        
        // Where to donate
        if (input.includes('where') || input.includes('location') || input.includes('donate')) {
            return `📍 **Donation Centers in Nairobi & Kiambu:**\n\n🏥 Kenyatta National Hospital\n🏥 MP Shah Hospital\n🏥 Aga Khan University Hospital\n🏥 Thika Level 5 Hospital\n🏥 Kiambu County Referral Hospital\n\nCheck our Live Status page for real-time blood availability!`;
        }
        
        // Blood types
        if (input.includes('blood type') || input.includes('compatibility')) {
            return `🩸 **Blood Type Compatibility:**\n\n🔴 O-: Universal Donor - Can donate to all types\n🔵 AB+: Universal Recipient - Can receive from all types\n\n📊 Most common: O+ (36%)\n📈 Rarest: AB- (1%)\n🌟 Golden Blood (Rh-null): Only 50 people worldwide\n\nCheck our Blood Group Chart for complete compatibility!`;
        }
        
        // Donation process
        if (input.includes('process') || input.includes('how to') || input.includes('steps')) {
            return `📋 **Blood Donation Process:**\n\n1️⃣ Registration (5 min)\n2️⃣ Health screening (10 min)\n3️⃣ Donation (10-15 min)\n4️⃣ Rest & refreshments (15 min)\n5️⃣ Recovery & snacks\n\nTotal time: 45-60 minutes\n💝 Your one donation can save up to 3 lives!`;
        }
        
        // Emergency contact
        if (input.includes('emergency') || input.includes('contact') || input.includes('call')) {
            return `🚨 **Emergency Contact Information:**\n\n📞 Emergency Hotline: +254 700 000 000\n📧 Email: emergency@uhai-damu.co.ke\n\n🕐 24/7/365 Available\n\n📍 Nairobi: +254 704 000 004\n📍 Kiambu: +254 705 000 005`;
        }
        
        // Appointment
        if (input.includes('appointment') || input.includes('schedule') || input.includes('book')) {
            return `📅 **To Schedule a Donation:**\n\n1. Login to your account\n2. Go to "Live Blood Bank Status"\n3. Select your preferred hospital\n4. Click "Schedule Appointment"\n5. Choose date & time\n\nOr call our donor services: +254 701 000 001`;
        }
        
        // Benefits
        if (input.includes('benefit') || input.includes('why') || input.includes('good')) {
            return `💝 **Benefits of Blood Donation:**\n\n❤️ Saves up to 3 lives per donation\n💪 Free health check-up\n🩸 Reduces iron overload\n🔥 Burns calories (650 kcal)\n📊 Know your blood type\n🎁 Get donor recognition\n\nPlus the satisfaction of saving lives! ✨`;
        }
        
        // Side effects
        if (input.includes('side effect') || input.includes('pain') || input.includes('feel')) {
            return `😊 **Common Side Effects:**\n\n• Mild bruising (very common)\n• Lightheadedness (temporary)\n• Fatigue (resolves in 24hrs)\n\n✅ Tips:\n- Drink plenty of fluids\n- Eat iron-rich foods\n- Avoid strenuous exercise\n- Rest for 15-20 minutes\n\nMost donors feel great and return to donate again! 💪`;
        }
        
        // Frequency
        if (input.includes('often') || input.includes('frequent') || input.includes('times')) {
            return `📊 **Donation Frequency:**\n\n🩸 Whole Blood: Every 3 months (men), 4 months (women)\n🧬 Platelets: Every 2 weeks (up to 24x/year)\n💧 Plasma: Every 4 weeks\n🔴 Double Red Cells: Every 6 months\n\nTrack your donations in your donor dashboard!`;
        }
        
        // Greetings
        if (input.includes('hi') || input.includes('hello') || input.includes('hey')) {
            return `👋 Hello! Welcome to Uhai Damu. I'm your blood donation assistant. How can I help you today?`;
        }
        
        // Thanks
        if (input.includes('thank')) {
            return `❤️ You're welcome! Thank YOU for your interest in saving lives. Is there anything else I can help with?`;
        }
        
        // Default response
        return `I'm here to help with blood donation questions! You can ask me about:\n\n✅ Donation requirements\n📍 Where to donate\n🩸 Blood types & compatibility\n📋 Donation process\n🚨 Emergency contacts\n💝 Benefits of donation\n\nWhat would you like to know?`;
    }
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new BloodDonationChatbot();
});