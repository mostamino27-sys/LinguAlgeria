from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import requests
import re

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
API_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'meta-llama/llama-3.2-3b-instruct:free'

def call_ai(messages, max_tokens=2000):
    if not OPENROUTER_API_KEY:
        raise Exception('Cle API non configuree')
    
    try:
        response = requests.post(
            API_URL,
            headers={
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://lingualgeria.up.railway.app',
                'X-Title': 'LinguAlgeria'
            },
            json={
                'model': MODEL,
                'messages': messages,
                'max_tokens': max_tokens,
                'temperature': 0.7
            },
            timeout=90
        )
        
        if response.status_code != 200:
            error_msg = f"Erreur {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_
                    error_msg = error_data['error'].get('message', error_msg)
            except:
                pass
            raise Exception(error_msg)
        
        data = response.json()
        return data['choices'][0]['message']['content']
        
    except requests.exceptions.Timeout:
        raise Exception('Delai depasse')
    except Exception as e:
        raise Exception(str(e))

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
        
        prompt = f"""Analyse ce texte en dialecte algerien:

{text}

Format:
1. Texte analyse avec mots francais en MAJUSCULES
2. Statistiques
3. Mots francais identifies
4. Analyse sociolinguistique

Reponds en francais."""

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
        
        prompt = f"""Compare ces textes algeriens:

Texte 1: {text1}
Texte 2: {text2}

Compare l'influence francaise."""

        result = call_ai([
            {'role': 'system', 'content': 'Sociolinguiste comparatif.'},
            {'role': 'user', 'content': prompt}
        ])
        
        return jsonify({'result': result, 'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'api_configured': bool(OPENROUTER_API_KEY),
        'model': MODEL
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print('LinguAlgeria Starting...')
    print(f'Model: {MODEL}')
    app.run(host='0.0.0.0', port=port, debug=False)
