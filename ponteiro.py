import os, requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import defaultdict
import time

app = Flask(__name__)
CORS(app)

GROQ_KEY = os.environ.get("GROQ_KEY")
uso = defaultdict(list)

@app.route("/chat")
def chat():
    ip = request.remote_addr
    agora = time.time()
    uso[ip] = [t for t in uso[ip] if agora - t < 60]
    if len(uso[ip]) >= 15:
        return jsonify({"r": "Calma! Muitas perguntas. Espera 1 minuto."})
    uso[ip].append(agora)
    pergunta = request.args.get("q","Olá")
    if not GROQ_KEY:
        return jsonify({"r": "Erro: chave GROQ_KEY não configurada no servidor."})
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type":"application/json"},
            json={"model":"llama-3.1-8b-instant","messages":[{"role":"user","content":pergunta}],"max_tokens":500},
            timeout=25)
        resp = r.json()['choices'][0]['message']['content']
        return jsonify({"r": resp})
    except Exception as e:
        return jsonify({"r": f"Erro no porteiro: {e}"})

@app.route("/")
def home():
    return "Porteiro online! Use /chat?q=sua pergunta"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
