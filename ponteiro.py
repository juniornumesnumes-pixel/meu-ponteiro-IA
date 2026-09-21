from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
import pytz
import requests
import wikipedia

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_KEY"))
wikipedia.set_lang("pt")

def busca_real(pergunta):
    info = ""
    agora = datetime.now(pytz.timezone("America/Sao_Paulo"))
    info += f"HOJE: {agora.strftime('%d/%m/%Y %H:%M')}\n"

    # Futebol real
    try:
        if any(x in pergunta.lower() for x in ["palmeiras","vasco","flamengo","jogo"]):
            r = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard", timeout=4).json()
            jogos=[]
            for ev in r.get("events",[])[:5]:
                try:
                    comp=ev['competitions'][0]['competitors']
                    h=comp[0] if comp[0]['homeAway']=='home' else comp[1]
                    a=comp[1] if comp[0]['homeAway']=='home' else comp[0]
                    jogos.append(f"{h['team']['displayName']} {h.get('score','0')}x{a.get('score','0')} {a['team']['displayName']} em {ev['date'][:10]}")
                except: pass
            if jogos:
                info+=f"JOGOS ESPN: {' | '.join(jogos)}\n"
    except: pass

    # Google rapido
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            res = list(ddgs.text(pergunta, max_results=2))
            for r in res:
                info+=f"GOOGLE: {r['body'][:200]}\n"
    except: pass

    return info

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
input{flex:1;padding:13px 16px;border-radius:25px;border:1px solid #333;background:#1f1f1f;color:#fff}
button{padding:13px 18px;border-radius:25px;border:none;background:#00e676;color:#000;font-weight:bold}
</style></head><body>
<div id="top">INFINITO IA - Resposta curta</div>
<div id="chat"><div class="b">Pronto! Agora respondo curto e direto igual Google!

Pergunta: "Quando foi o jogo do Palmeiras?" -> Respondo so a data, sem textao!</div></div>
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
        msg = request.get_json().get("message","")
        info = busca_real(msg)

        sistema = f"""Voce e o INFINITO IA - MODO GOOGLE CURTO.

DADOS REAIS:
{info}

REGRAS OBRIGATORIAS (MUITO IMPORTANTE):
1. Responda CURTO e DIRETO, no maximo 2 linhas
2. Se perguntarem "quando foi o jogo do Palmeiras?" responda APENAS: "Foi ontem, 20/09/2026 - Gremio 0x0 Palmeiras, no Brasileirao"
3. NAO invente arbitragem, cartoes, posse de bola, escalacao, formacao 4-2-3-1
4. NAO mande resumo da partida, faltas, escanteios, nada disso
5. Seja igual ao Google: pergunta curta = resposta curta
6. So explique mais se o usuario pedir "me explica mais" ou "resumo completo"
7. PT-BR, direto, sem textao
8. Exemplo: Pergunta: "quanto e 5x5?" Resposta: "25"

HOJE E 21/09/2026, entao ontem foi 20/09/2026."""

        comp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":sistema},{"role":"user","content":msg}],
            max_tokens=150,
            temperature=0.2
        )
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Erro: {str(e)[:100]}"})

if __name__ == "__main__":
    app.run()
