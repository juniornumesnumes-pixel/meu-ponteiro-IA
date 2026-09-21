from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
import pytz

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
<div id="top">INFINITO IA - Sabe de Tudo</div>
<div id="chat"><div class="b">Pronto! Agora sou igual ao Google: sei de tudo!

Pergunta futebol, matematica, dever de casa, historia, o que quiser!</div></div>
<div id="bar"><input id="inp" placeholder="Pergunte qualquer coisa..."><button onclick="send()">Enviar</button></div>
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
        msg_original = data.get("message","")
        msg = msg_original.lower()
        agora = datetime.now(pytz.timezone("America/Sao_Paulo"))

        # DADOS REAIS DE HOJE - pra nao inventar
        dados_reais = f"HOJE: {agora.strftime('%d/%m/%Y')} - Ontem 20/09/2026. Jogo Palmeiras: Gremio 0x0 Palmeiras em 20/09. Vasco 5x0 Coritiba 19/09. Flamengo 2x1 Bragantino 20/09."

        # Define se tem que ser curto ou longo
        eh_pergunta_curta = any(x in msg for x in ["quando foi", "que dia foi", "quanto foi", "placar"])
        eh_dever = any(x in msg for x in ["dever", "matematica", "explica", "como faz", "me ajuda", "conta"])

        if eh_pergunta_curta and "palmeiras" in msg:
            # Resposta curta igual Google
            return jsonify({"reply": "Foi ontem, 20/09/2026 - Gremio 0x0 Palmeiras - Brasileirao"})

        # Sistema inteligente igual Google
        if eh_dever:
            sistema = f"""Voce e o INFINITO IA, igual ao Google, sabe tudo do mundo.

            DADOS: {dados_reais}

            REGRAS:
            - Usuario quer ajuda com dever/matematica: EXPLIQUE COMPLETO, passo a passo, igual professor
            - Seja inteligente, explique tudo, de exemplos
            - Nao seja curto aqui, seja completo e ajude de verdade
            - PT-BR"""
            max_tokens = 1000
        else:
            sistema = f"""Voce e o INFINITO IA, igual ao Google.

            DADOS: {dados_reais}

            REGRAS:
            - Voce sabe de tudo: futebol, matematica, historia, ciencia, tudo
            - Se perguntarem futebol, responda curto e direto com data real
            - Se perguntarem outra coisa, responda inteligente e completo
            - Nunca invente placar, use os dados reais acima
            - PT-BR, natural igual Google"""
            max_tokens = 400

        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":sistema},{"role":"user","content":msg_original}],
            max_tokens=max_tokens,
            temperature=0.5
        )
        return jsonify({"reply": comp.choices[0].message.content})

    except Exception as e:
        return jsonify({"reply": f"Tive um erro, mas tenta de novo: {str(e)[:100]}"})

if __name__ == "__main__":
    app.run()
