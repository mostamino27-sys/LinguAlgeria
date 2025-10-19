from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import requests
import re

app = Flask(__name__)
CORS(app)

# إعدادات OpenRouter
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
API_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'meta-llama/llama-3.2-3b-instruct:free'  # ✅ Model مجاني مضمون!

def call_ai(messages, max_tokens=2000):
    """استدعاء Llama 3.2 عبر OpenRouter"""
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
        raise Exception('Délai dépassé')
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
1. Identifie TOUS les mots d'origine française
2. Donne le mot français original entre parenthèses
3. Propose des alternatives en arabe/darija
4. Calcule le pourcentage approximatif de français
5. Identifie les domaines (cuisine, transport, etc.)

Format de réponse:

📝 TEXTE ANALYSÉ:
[Réécris le texte avec les mots français en MAJUSCULES]

📊 STATISTIQUES:
• Pourcentage français: X%
• Nombre de mots français: X
• Domaines: [liste]

🔍 MOTS FRANÇAIS IDENTIFIÉS:
1. [mot algérien] (français: xxx) → Alternative arabe: [xxx]
2. ...

💡 ANALYSE SOCIOLINGUISTIQUE:
[Brève analyse de 2-3 phrases]

Réponds en français de manière claire."""

        result = call_ai([
            {
                'role': 'system',
                'content': 'Tu es un sociolinguiste expert du dialecte algérien. Tu analyses avec précision l\'influence française.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ])
        
        return jsonify({'result': result, 'success': True})
        
    except Exception as e:
        print(f'Erreur: {str(e)}')
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/compare', methods=['POST'])
def compare_texts():
    try:
        data = request.get_json()
        text1 = data.get('text1', '').strip()
        text2 = data.get('text2', '').strip()
        
        if not text1 or not text2:
            return jsonify({'error': 'Deux textes requis', 'success': False}), 400
        
        prompt = f"""Compare ces deux textes algériens en termes d'influence française:

Texte 1: {text1}
Texte 2: {text2}

Analyse comparative:
1. Pourcentage de français dans chaque texte
2. Quel texte est le plus influencé et pourquoi?
3. Différences dans les domaines lexicaux
4. Conclusions sociolinguistiques

Réponds en français de manière structurée."""

        result = call_ai([
            {
                'role': 'system',
                'content': 'Tu es un sociolinguiste comparant des textes algériens.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ])
        
        return jsonify({'result': result, 'success': True})
        
    except Exception as e:
        print(f'Erreur: {str(e)}')
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
    print('=' * 60)
    print('🇩🇿 LinguAlgeria - Démarrage')
    print(f'🤖 Model: {MODEL}')
    print(f'🔑 API: {"✅" if OPENROUTER_API_KEY else "❌"}')
    print('=' * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
