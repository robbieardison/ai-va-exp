from flask import Flask, request, jsonify, g
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask_cors import CORS
import firebase_admin
import json
from firebase_admin import credentials, db, auth

app = Flask(__name__)
CORS(app)

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
FIREBASE_CREDENTIAL_PRIVATE_KEY = os.getenv("FIREBASE_CREDENTIAL_PRIVATE_KEY")
DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")

if GOOGLE_API_KEY is None:
    raise ValueError("GOOGLE_API_KEY not found in .env or environment variables.")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-pro-exp')

# Initialize Firebase
try:
    key_json = json.loads(FIREBASE_CREDENTIALS)
    cred_json = {
        **key_json,
        "private_key": "\n".join(FIREBASE_CREDENTIAL_PRIVATE_KEY.split(r"\n"))
    }

    cred = credentials.Certificate(cred_json)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DATABASE_URL
    })
except Exception as e:
    print(f"Firebase Initialization Error: {e}")
    raise

def get_gemini_response(prompt):
    """Gets a response from the Gemini API."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"
    
@app.before_request
def verify_token():
    """Verify Firebase Authentication token."""
    if request.path == '/chat':
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        try:
            decoded_token = auth.verify_id_token(token)
            g.uid = decoded_token['uid']  # Store user ID in Flask's g object
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chat requests."""
    try:
        data = request.get_json()
        user_message = data['message']

        # Store user message in Firebase Realtime Database with user ID
        chat_ref = db.reference(f'users/{g.uid}/chat')  # Use g.uid here
        chat_ref.push({'role': 'user', 'parts': user_message})

        # Retrieve conversation history for the user from Firebase
        history_query = chat_ref.get()
        conversation_history = []
        if history_query:
            for message in history_query.values():
                conversation_history.append({'role': message['role'], 'parts': message['parts']})

        # Construct the prompt with context and history
        prompt = "You are a helpful assistant that only answers questions about tourism in Indonesia. "
        prompt += "If the user asks for recommendations for the best tourist attractions, provide a list of the 10 best locations. "
        prompt += "Answer in Indonesian as the main language unless the user asks for a different language. "
        prompt += "If the user asks for a different language, provide the answer in that language. "
        prompt += "\n\nConversation History:\n"
        prompt += "\n".join([f"{msg['role']}: {msg['parts']}" for msg in conversation_history]) + "\nassistant:"

        gemini_response = get_gemini_response(prompt)
        # Store bot message in Firebase with user ID
        chat_ref.push({'role': 'model', 'parts': gemini_response})

        return jsonify({'response': gemini_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=int(os.environ.get("PORT", 5000)))