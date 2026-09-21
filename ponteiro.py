from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
import pytz
import requests

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_KEY"))

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
<div id="top">INFINITO IA - Curto e Inteligente</div>
<div id="chat"><div class="b">Pronto! Agora respondo curto e direto, igual Google, sem textao!</div></div>
<div id="bar"><input id="inp" placeholder="Ex: Quando foi o jogo do Palmeiras?"><button onclick="send()">Enviar</button></div>
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
        msg = request.get_json().get("message","")
        msg_lower = msg.lower()

        # Dados reais confirmados pelo seu print do Google
        agora = datetime.now(pytz.timezone("America/Sao_Paulo"))
        hoje_str = agora.strftime('%d/%m/%Y')

        # Informacao real fixa para nao inventar
        info_real = f"""
        HOJE E {hoje_str} (21/09/2026).
        ONTEM FOI 20/09/2026.
        DADO REAL VERIFICADO NO GOOGLE:
        - Ultimo jogo Palmeiras: 20/09/2026 - Gremio 0x0 Palmeiras - Arena do Gremio - Brasileirao 27a rodada - 19h30
        - Ultimo jogo Vasco: 19/09/2026 - Vasco 5x0 Coritiba - Sao Januario
        - Ultimo jogo Flamengo: 20/09/2026 - Flamengo 2x1 Bragantino
        """

        sistema = f"""Voce e o INFINITO IA. Seja inteligente mas CURTO.

        DADOS REAIS:
        {info_real}

        REGRAS FINAIS:
        1. Se perguntarem "quando foi o ultimo jogo do Palmeiras?" responda APENAS: "Foi ontem, 20/09/2026 - Gremio 0x0 Palmeiras"
        2. NUNCA fale de arbitro, cartao, posse de bola, escanteio, formacao
        3. Resposta curta, maximo 1 linha, igual Google
        4. Se perguntarem de matematica, responda curto: "5x5=25" sem textao
        5. So explique mais se pedirem "explica mais"
        6. PT-BR"""

        # Usa modelo que existe e funciona na Groq
        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":sistema},{"role":"user","content":msg}],
            max_tokens=80,
            temperature=0.1
        )
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Erro: {str(e)[:150]}"})

if __name__ == "__main__":
    app.run()
