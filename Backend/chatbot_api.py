"""
UHAI DAMU - Google Gemini Chatbot API
With your personal Gemini API key
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from datetime import datetime

# ============================================
# CREATE FLASK APP
# ============================================
app = Flask(__name__)
CORS(app)  # This allows your website to talk to the API

# ============================================
# YOUR GEMINI API KEY
# ============================================
YOUR_API_KEY = "AIzaSyCJVG4rnGSV5Kx0ImM9_Q2Ym1aj5ort7uU"
genai.configure(api_key=YOUR_API_KEY)

# Use Gemini 2.5 Flash - fast and free!
MODEL_NAME = "gemini-2.5-flash"

print("=" * 60)
print("🤖 UHAI DAMU - GOOGLE GEMINI CHATBOT")
print("=" * 60)
print(f"✅ Gemini API Key: CONFIGURED")
print(f"   Key: {YOUR_API_KEY[:10]}...{YOUR_API_KEY[-5:]}")
print(f"✅ Model: {MODEL_NAME}")
print(f"✅ Free tier: 250k tokens/min, 250 requests/day")
print("=" * 60)

# ============================================
# KNOWLEDGE BASE (BACKUP - works even without internet)
# ============================================

knowledge_base = {
    "requirements": """
📋 **Blood Donation Requirements in Kenya:**

✅ Age: 17-65 years old
✅ Weight: Minimum 50kg (110 lbs)
✅ Health: Good general health
✅ ID: National ID or Passport
✅ Hemoglobin: Must pass the test

❌ Cannot donate if you have:
• Cold, flu, or fever
• HIV, Hepatitis B/C
• Malaria or typhoid
• Recent surgery/tattoos
• Pregnancy or breastfeeding

Visit any KNBTS center to check your eligibility!
    """,
    
    "locations": """
📍 **Donation Centers in Nairobi & Kiambu:**

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
   📍 Kiambu Town

⏰ Hours: Mon-Sat 8am-6pm, Sun closed
    """,
    
    "compatibility": """
🩸 **Blood Type Compatibility:**

O- (Universal Donor):
   → Can donate to: ALL blood types
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

AB+ (Universal Receiver):
   → Can donate to: AB+ only
   → Can receive from: ALL blood types
    """,
    
    "emergency": """
🚨 **EMERGENCY CONTACTS:**

📞 Emergency Hotline: +254 700 000 000 (24/7)
📧 Email: emergency@uhai-damu.co.ke

📍 Nairobi Regional Office: +254 704 000 004
📍 Kiambu Regional Office: +254 705 000 005

🏥 Kenyatta National Hospital: +254 20 271 3344

⚠️ For life-threatening emergencies, call 911 or go to the nearest hospital immediately!
    """,
    
    "process": """
📋 **Blood Donation Process:**

1️⃣ Registration (5 minutes)
   • Fill out donor form
   • Show ID (National ID/Passport)

2️⃣ Health Screening (10 minutes)
   • Check blood pressure
   • Test hemoglobin
   • Answer health questions

3️⃣ Donation (10-15 minutes)
   • 450ml blood collected
   • Comfortable reclining chair
   • Sterile, single-use equipment

4️⃣ Rest & Refreshments (15 minutes)
   • Drink juice/water
   • Eat snacks
   • Rest before leaving

5️⃣ Recovery (24 hours)
   • Don't lift heavy things
   • Drink plenty of fluids
   • Eat iron-rich foods

Total time: 45-60 minutes
    """,
    
    "benefits": """
💝 **Benefits of Blood Donation:**

❤️ Saves up to 3 lives per donation
💪 Free mini health check-up
🩸 Reduces excess iron (good for heart health)
🔥 Burns approximately 650 calories
📊 Learn your blood type
🎁 Get donor recognition points
🌟 Feel great about helping your community

Plus, you become a hero! 🦸‍♀️🦸‍♂️
    """,
    
    "frequency": """
📊 **How Often Can You Donate?**

🩸 Whole Blood:
   • Men: Every 3 months (4 times/year)
   • Women: Every 4 months (3 times/year)

🧬 Platelets (Apheresis):
   • Every 2 weeks
   • Up to 24 times per year

💧 Plasma:
   • Every 4 weeks

🔴 Double Red Cells:
   • Every 6 months

Track your donations in your donor dashboard!
    """
}

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/chatbot/test', methods=['GET'])
def test():
    """Test if the API is working"""
    return jsonify({
        'status': 'ok',
        'message': 'Uhai Damu Gemini Chatbot is running!',
        'gemini_configured': True,
        'model': MODEL_NAME,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/chatbot/ask', methods=['POST'])
def ask_chatbot():
    """Main endpoint - ask any question"""
    try:
        # Get the user's question
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False, 
                'error': 'Please ask a question'
            }), 400
        
        print(f"\n🤔 User asked: {user_message[:50]}...")
        
        # Try Gemini AI first
        try:
            response = call_gemini(user_message)
            print(f"✅ Gemini responded")
            return jsonify({
                'success': True,
                'response': response,
                'source': 'gemini_ai'
            })
        except Exception as e:
            print(f"⚠️ Gemini error: {e}")
            # Fall back to knowledge base
            response = get_knowledge_base_response(user_message)
            return jsonify({
                'success': True,
                'response': response,
                'source': 'knowledge_base'
            })
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def call_gemini(message):
    """Call Google Gemini API"""
    
    # Create the model
    model = genai.GenerativeModel(MODEL_NAME)
    
    # Create a prompt that guides Gemini to be helpful
    prompt = f"""You are Uhai Damu Assistant, a friendly and helpful chatbot for a Kenyan blood donation platform.

Your job is to answer questions about blood donation in Kenya. Be warm, encouraging, and concise.

Key information to remember:
- Emergency contact: +254 700 000 000
- Donation centers in Nairobi and Kiambu counties
- Blood donation requirements (age 17-65, weight 50kg+, good health)
- Blood type compatibility information

If someone asks a question NOT related to blood donation, politely redirect them to blood donation topics.

Now answer this question: {message}

Keep your response friendly, helpful, and under 200 words."""
    
    # Generate response
    response = model.generate_content(
        prompt,
        generation_config={
            'temperature': 0.7,
            'max_output_tokens': 300,
        }
    )
    
    return response.text

def get_knowledge_base_response(message):
    """Simple keyword matching for common questions"""
    message = message.lower()
    
    # Check for keywords and return appropriate response
    if any(word in message for word in ['require', 'eligible', 'can i donate', 'need to']):
        return knowledge_base['requirements']
    
    elif any(word in message for word in ['where', 'location', 'center', 'hospital', 'near']):
        return knowledge_base['locations']
    
    elif any(word in message for word in ['compatible', 'match', 'type', 'blood type']):
        return knowledge_base['compatibility']
    
    elif any(word in message for word in ['process', 'step', 'how to', 'procedure']):
        return knowledge_base['process']
    
    elif any(word in message for word in ['emergency', 'urgent', 'help', '911']):
        return knowledge_base['emergency']
    
    elif any(word in message for word in ['benefit', 'why donate', 'good', 'important']):
        return knowledge_base['benefits']
    
    elif any(word in message for word in ['often', 'frequent', 'how many times']):
        return knowledge_base['frequency']
    
    elif any(word in message for word in ['hi', 'hello', 'hey', 'greetings']):
        return "👋 Hello! I'm your Uhai Damu Assistant powered by Google Gemini. How can I help you with blood donation today?"
    
    elif any(word in message for word in ['thank', 'thanks', 'appreciate']):
        return "❤️ You're welcome! Thank YOU for caring about saving lives. Is there anything else I can help with?"
    
    else:
        return """I'm here to help with blood donation! You can ask me about:

• ✅ Donation requirements (who can donate)
• 📍 Donation centers (where to go)
• 🩸 Blood type compatibility (who can give/receive)
• 📋 Donation process (what happens)
• 🚨 Emergency contacts (urgent help)
• 💝 Benefits of donation (why donate)

What would you like to know? Just type your question!"""

# ============================================
# START THE SERVER
# ============================================

if __name__ == '__main__':
    port = 5001
    print("\n" + "=" * 60)
    print("🤖 UHAI DAMU - GOOGLE GEMINI CHATBOT")
    print("=" * 60)
    print(f"📅  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑  Your Gemini Key: ✅ ACTIVE")
    print(f"🤖  Model: {MODEL_NAME}")
    print(f"📊  Free tier: 250 requests/day")
    print("-" * 60)
    print(f"🚀  Server: http://localhost:{port}")
    print(f"📝  Test:   http://localhost:{port}/api/chatbot/test")
    print(f"💬  Chat:   http://localhost:{port}/api/chatbot/ask (POST)")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)