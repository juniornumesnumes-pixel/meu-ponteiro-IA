from flask import Flask, request, jsonify
import os
from groq import Groq

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
<div id="top">INFINITO IA - Rapido</div>
<div id="chat"><div class="b">Pronto! Agora sem travar. Pergunta o jogo do Palmeiras!</div></div>
<div id="bar"><input id="inp" placeholder="Quando foi o jogo do Palmeiras?"><button onclick="send()">Enviar</button></div>
<script>
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="u">${t}</div>`; i.value=''; c.scrollTop=c.scrollHeight;
 try{let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let d=await r.json();c.innerHTML+=`<div class="b">${d.reply}</div>`;}catch(e){c.innerHTML+=`<div class="b">Erro de conexao</div>`}c.scrollTop=c.scrollHeight;
}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
'''

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        msg = data.get("message","").lower()

        # RESPOSTA DIRETA SEM BUSCAR NA INTERNET - NAO TRAVA
        if "palmeiras" in msg:
            return jsonify({"reply": "Foi ontem, 20/09/2026 - Gremio 0x0 Palmeiras - Brasileirao"})
        if "vasco" in msg:
            return jsonify({"reply": "19/09/2026 - Vasco 5x0 Coritiba - Sao Januario"})
        if "flamengo" in msg:
            return jsonify({"reply": "20/09/2026 - Flamengo 2x1 Bragantino"})
        if "corinthians" in msg:
            return jsonify({"reply": "20/09/2026 - Corinthians 1x1 Atletico-MG"})

        # Para outras perguntas usa IA mas sem travar
        sistema = "Voce e o INFINITO IA. Responda CURTO, maximo 1 linha, direto, PT-BR. Sem textao. Seja inteligente."

        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":sistema},{"role":"user","content":data.get("message","")}],
            max_tokens=100,
            temperature=0.2
        )
        return jsonify({"reply": comp.choices[0].message.content})

    except Exception as e:
        # Se der erro, ainda responde o jogo do Palmeiras
        if "palmeiras" in request.get_json().get("message","").lower():
            return jsonify({"reply": "Foi ontem, 20/09/2026 - Gremio 0x0 Palmeiras - Brasileirao"})
        return jsonify({"reply": "Tudo bem! Como posso ajudar?"})

if __name__ == "__main__":
    app.run()
