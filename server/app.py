from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY is None:
    raise ValueError("GOOGLE_API_KEY not found in .env or environment variables.")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-pro-exp')

conversation_history = []  # Store conversation history

def get_gemini_response(prompt):
    """Gets a response from the Gemini API."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chat requests."""
    try:
        data = request.get_json()
        user_message = data['message']

        conversation_history.append({"role": "user", "parts": user_message})

        # Construct the prompt with context and history
        prompt = "You are a helpful assistant that only answers questions about tourism in Indonesia. "
        prompt += "If the user asks for recommendations for the best tourist attractions, provide a list of the 10 best locations. "
        prompt += "Answer in Indonesian as the main language unless the user asks for a different language. "
        prompt += "If the user asks for a different language, provide the answer in that language. "
        prompt += "\n\nConversation History:\n"
        prompt += "\n".join([f"{msg['role']}: {msg['parts']}" for msg in conversation_history]) + "\nassistant:"

        gemini_response = get_gemini_response(prompt)
        conversation_history.append({"role": "model", "parts": gemini_response})

        return jsonify({'response': gemini_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=int(os.environ.get("PORT", 5000)))