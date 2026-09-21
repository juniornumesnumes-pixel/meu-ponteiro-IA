from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
import pytz
import requests

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_KEY"))

def get_clima_tempo():
    try:
        # Tempo real de Bacabal
        r = requests.get("https://wttr.in/Bacabal?format=%C+%t+vento+%w", timeout=3)
        return r.text
    except:
        return "Clima de Bacabal nao disponivel agora"

@app.route("/")
def home():
    return '''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:Arial;background:#0f0f0f;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh}
#top{padding:14px;text-align:center;background:#000;border-bottom:1px solid #222;font-weight:bold;color:#00e676}
#chat{flex:1;overflow:auto;padding:14px;display:flex;flex-direction:column;gap:10px}
.u{background:#7c3aed;align-self:flex-end;padding:10px 14px;border-radius:18px 18px 4px 18px;max-width:80%}
.b{background:#1f1f1f;align-self:flex-start;padding:10px 14px;border-radius:18px 18px 4px 18px;max-width:85%;border:1px solid #333;white-space:pre-wrap}
#bar{display:flex;padding:10px;background:#000;gap:8px}
input{flex:1;padding:13px 16px;border-radius:25px;border:1px solid #333;background:#1f1f1f;color:#fff;outline:none}
button{padding:13px 18px;border-radius:25px;border:none;background:#00e676;color:#000;font-weight:bold}
</style></head><body>
<div id="top">INFINITO IA - Inteligente</div>
<div id="chat"><div class="b">Agora sou inteligente de verdade!

Pergunta curta = respondo curto
Pergunta longa = respondo longo

Testa: "que dia foi o jogo?" e "me explica o jogo"</div></div>
<div id="bar"><input id="inp" placeholder="Pergunte..."><button onclick="send()">Enviar</button></div>
<script>
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="u">${t}</div>`; i.value=''; c.scrollTop=c.scrollHeight;
 try{let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let d=await r.json();c.innerHTML+=`<div class="b">${d.reply}</div>`;}catch(e){c.innerHTML+=`<div class="b">Erro</div>`}c.scrollTop=c.scrollHeight;
}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
'''

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        msg_original = data.get("message","")
        msg = msg_original.lower().strip()
        agora = datetime.now(pytz.timezone("America/Sao_Paulo"))

        # --- DETECTOR INTELIGENTE DE TAMANHO ---
        # Pergunta curta: poucas palavras ou pede data/hora/clima
        palavras_curta = ["que dia", "quando foi", "que horas", "que hora", "clima", "tempo hoje", "placar", "quanto foi", "resultado"]
        palavras_longa = ["explica", "me ajuda", "como faz", "como funciona", "por que", "porque", "dever", "me ensina", "detalha", "resumo", "completo"]

        eh_curta = len(msg.split()) <= 6 or any(p in msg for p in palavras_curta)
        eh_longa = len(msg.split()) > 8 or any(p in msg for p in palavras_longa)

        # Dados reais
        clima = ""
        if "clima" in msg or "tempo" in msg:
            clima = get_clima_tempo()

        info_base = f"HOJE: {agora.strftime('%d/%m/%Y %H:%M')} - Bacabal. Ontem 20/09/2026 Gremio 0x0 Palmeiras. Clima: {clima}"

        if eh_curta and not eh_longa:
            # MODO CURTO - igual Google
            sistema = f"""Voce e o Google. Responda CURTO e DIRETO, 1 linha no maximo.

            DADOS: {info_base}

            REGRAS MODO CURTO:
            - Se perguntarem "que dia foi o jogo do Palmeiras?" -> "Foi ontem, 20/09/2026 - Gremio 0x0 Palmeiras"
            - Se perguntarem "que horas sao?" -> "{agora.strftime('%H:%M')} em Bacabal"
            - Se perguntarem "como esta o clima?" -> Responda curto com o clima: {clima}
            - Se perguntarem "quanto e 5x5?" -> "25"
            - NUNCA mande textao. 1 linha.
            - PT-BR"""
            max_tokens = 80
            temp = 0.2
        else:
            # MODO LONGO - explica tudo
            sistema = f"""Voce e o INFINITO IA, igual ao Google, sabe tudo.

            DADOS: {info_base}

            REGRAS MODO LONGO:
            - Usuario fez pergunta longa ou pediu explicacao
            - Responda completo, inteligente, passo a passo
            - Se for dever de casa, explique como professor
            - Se for "me explica o jogo do Palmeiras", explique onde foi, horario, rodada, o que aconteceu
            - Pode usar 3-5 paragrafos
            - PT-BR, completo"""
            max_tokens = 800
            temp = 0.6

        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":sistema},{"role":"user","content":msg_original}],
            max_tokens=max_tokens,
            temperature=temp
        )
        return jsonify({"reply": comp.choices[0].message.content})

    except Exception as e:
        return jsonify({"reply": "Tenta de novo, deu um erro aqui"})

if __name__ == "__main__":
    app.run()
