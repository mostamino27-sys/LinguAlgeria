from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import requests
import re

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
API_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'meta-llama/llama-3.3-70b-instruct'

def call_ai(messages, max_tokens=2000):
    if not OPENROUTER_API_KEY:
        raise Exception('Clé API non configurée')
    
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
            timeout=60
        )
        
        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f'Erreur API {response.status_code}')
        
        data = response.json()
        return data['choices'][0]['message']['content']
        
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
        
        prompt = f"""Analyse ce texte en dialecte algérien et identifie l'influence française.

Texte: {text}

Instructions:
1. Identifie les mots d'origine française
2. Donne le mot français original
3. Propose des alternatives en arabe
4. Calcule le pourcentage de français
5. Identifie les domaines lexicaux

Format:
📝 TEXTE ANALYSÉ: [texte avec mots français en MAJUSCULES]
📊 STATISTIQUES: Pourcentage, nombre de mots
🔍 MOTS FRANÇAIS: Liste avec alternatives
💡 ANALYSE: Brève analyse sociolinguistique

Réponds en français."""

        result = call_ai([
            {'role': 'system', 'content': 'Tu es un sociolinguiste expert du dialecte algérien.'},
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
        
        prompt = f"""Compare ces deux textes algériens:

Texte 1: {text1}
Texte 2: {text2}

Analyse:
1. Pourcentage de français dans chaque texte
2. Quel texte est le plus influencé?
3. Différences dans les domaines
4. Conclusions

Réponds en français."""

        result = call_ai([
            {'role': 'system', 'content': 'Tu es un sociolinguiste comparant des textes algériens.'},
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
    print('🇩🇿 LinguAlgeria - Llama 3.3 70B')
    app.run(host='0.0.0.0', port=port, debug=False)
