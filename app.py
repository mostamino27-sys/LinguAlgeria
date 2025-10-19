from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
API_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'meta-llama/llama-3.2-3b-instruct:free'

def call_ai(messages):
    if not OPENROUTER_API_KEY:
        raise Exception('Cle API non configuree')
    
    response = requests.post(
        API_URL,
        headers={
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': MODEL,
            'messages': messages
        },
        timeout=90
    )
    
    if response.status_code != 200:
        raise Exception(f"Erreur {response.status_code}")
    
    return response.json()['choices'][0]['message']['content']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_dialect():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Texte requis', 'success': False}), 400
        
        prompt = f"Analyse ce texte algerien et identifie les mots francais: {text}"
        
        result = call_ai([
            {'role': 'system', 'content': 'Tu es un sociolinguiste expert.'},
            {'role': 'user', 'content': prompt}
        ])
        
        return jsonify({'result': result, 'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/compare', methods=['POST'])
def compare_texts():
    try:
        data = request.get_json()
        text1 = data.get('text1', '').strip()
        text2 = data.get('text2', '').strip()
        
        if not text1 or not text2:
            return jsonify({'error': 'Deux textes requis', 'success': False}), 400
        
        prompt = f"Compare ces textes: {text1} et {text2}"
        
        result = call_ai([
            {'role': 'system', 'content': 'Sociolinguiste.'},
            {'role': 'user', 'content': prompt}
        ])
        
        return jsonify({'result': result, 'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'model': MODEL})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
