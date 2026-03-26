from flask import Blueprint, request, jsonify
import requests
import os

chatbot_bp = Blueprint('chatbot', __name__)

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

@chatbot_bp.route('/ask', methods=['POST'])
def ask():
    """Simple chatbot endpoint"""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message'}), 400
    
    # Simple responses for testing
    responses = {
        'hello': '👋 Hello! How can I help you today?',
        'hi': '👋 Hi there! Ask me about blood donation.',
        'donate': 'To donate blood, you need to be 17-65 years old and weigh at least 50kg.',
        'where': 'You can donate at Kenyatta National Hospital, MP Shah, or Aga Khan Hospital.',
        'emergency': '🚨 Emergency: Call +254 700 000 000',
    }
    
    # Check for keywords
    message_lower = user_message.lower()
    for key, response in responses.items():
        if key in message_lower:
            return jsonify({'response': response})
    
    # Default response
    return jsonify({
        'response': "I'm not sure about that. Try asking about:\n• Donation requirements\n• Where to donate\n• Emergency contacts"
    })

@chatbot_bp.route('/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'api_key_configured': bool(DEEPSEEK_API_KEY)
    })