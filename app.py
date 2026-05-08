import os
from flask import Flask, render_template, request, session, jsonify
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Store conversations in memory (baad main database mein daalna)
conversations = {}

@app.route('/')
def index():
    """Home page - login page se pehle"""
    if 'user_id' in session:
        return render_template('chat.html', username=session['username'])
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """User login handle karna"""
    username = request.json.get('username', '').strip()
    password = request.json.get('password', '').strip()
    
    # Basic validation (baad main proper database add karenge)
    if len(username) < 3:
        return jsonify({'success': False, 'error': 'Username kam se kam 3 character ka hona chahiye'}), 400
    
    if len(password) < 4:
        return jsonify({'success': False, 'error': 'Password kam se kam 4 character ka hona chahiye'}), 400
    
    # Session create karna
    session['user_id'] = secrets.token_hex(8)
    session['username'] = username
    conversations[session['user_id']] = []
    
    return jsonify({'success': True, 'message': f'Welcome {username}! 👋'})

@app.route('/chat', methods=['POST'])
def chat():
    """Chat message handle karna"""
    if 'user_id' not in session:
        return jsonify({'error': 'Login karo pehle'}), 401
    
    user_message = request.json.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message khaali nahi ho sakta'}), 400
    
    # User ka message store karna
    user_id = session['user_id']
    if user_id not in conversations:
        conversations[user_id] = []
    
    conversations[user_id].append({
        'type': 'user',
        'message': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    # AI ka response (basic version - baad main upgrade karenge)
    ai_response = generate_ai_response(user_message)
    
    conversations[user_id].append({
        'type': 'ai',
        'message': ai_response,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({
        'success': True,
        'ai_response': ai_response
    })

def generate_ai_response(user_message):
    """Simple AI response generator"""
    responses = {
        'hello': 'Namaste! Kaise ho? 👋',
        'hi': 'Shukriya! Kya chal raha hai? 😊',
        'how are you': 'Main to theek hoon! Tu bataa, tu kaisa hai? 💪',
        'bye': 'Phir milenge! Take care! 👋',
        'thanks': 'Khushi se! Kuch aur chahiye? 🙌'
    }
    
    msg_lower = user_message.lower()
    
    for key, response in responses.items():
        if key in msg_lower:
            return response
    
    return f"Interesting! Aap ne kaha: '{user_message}' 🤔 Mujhe aur improve hona chahiye! 😅"

@app.route('/logout', methods=['POST'])
def logout():
    """User logout"""
    if 'user_id' in session:
        user_id = session['user_id']
        session.clear()
        return jsonify({'success': True, 'message': 'Logout successful! 👋'})
    return jsonify({'success': False}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
