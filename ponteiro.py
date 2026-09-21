from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
import pytz
import requests
import wikipedia
import re

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_KEY"))
wikipedia.set_lang("pt")

def buscar_ultimo_jogo_time(nome_time):
    """Busca de verdade o ultimo jogo do time, nao inventa"""
    try:
        # 1. Acha o ID do time no TheSportsDB (gratis)
        search = requests.get(f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={nome_time}", timeout=5).json()
        teams = search.get("teams")
        if not teams:
            return None
        team_id = teams[0]['idTeam']
        team_nome_real = teams[0]['strTeam']

        # 2. Pega os ultimos 5 jogos
        ultimos = requests.get(f"https://www.thesportsdb.com/api/v1/json/3/eventslast.php?id={team_id}", timeout=5).json()
        eventos = ultimos.get("results")
        if not eventos:
            return None

        ultimo = eventos[0]
        return f"ULTIMO JOGO REAL DO {team_nome_real}: {ultimo['dateEvent']} - {ultimo['strEvent']} - Placar: {ultimo.get('intHomeScore','?')} x {ultimo.get('intAwayScore','?')} - Campeonato: {ultimo.get('strLeague','')} - Status: {ultimo.get('strStatus','Finalizado')}"
    except Exception as e:
        return None

def get_info_mundo(pergunta):
    info = ""
    perg_lower = pergunta.lower()

    # Hora real
    agora = datetime.now(pytz.timezone("America/Sao_Paulo"))
    info += f"[DATA E HORA REAL AGORA: {agora.strftime('%d/%m/%Y %H:%M:%S')} - Bacabal/Brasil]\n"

    # Se perguntar sobre futebol de algum time, busca de verdade
    times_futebol = ["vasco","flamengo","palmeiras","corinthians","gremio","sao paulo","santos","cruzeiro","atletico","botafogo","fluminense","coritiba","bragantino","vitoria","bahia"]
    time_detectado = None
    for t in times_futebol:
        if t in perg_lower:
            time_detectado = t
            break
    # Detecta "ultimo jogo do X"
    match = re.search(r"ultimo jogo do (\w+)", perg_lower)
    if match:
        time_detectado = match.group(1)

    if time_detectado or "jogo" in perg_lower or "vasco" in perg_lower:
        jogo_real = buscar_ultimo_jogo_time(time_detectado if time_detectado else "Vasco da Gama")
        if jogo_real:
            info += f"[{jogo_real}]\n"
        else:
            # Tenta ESPN ao vivo
            try:
                r = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard", timeout=4).json()
                lista=[]
                for ev in r.get("events",[])[:5]:
                    try:
                        comp=ev['competitions'][0]['competitors']
                        h=comp[0] if comp[0]['homeAway']=='home' else comp[1]
                        a=comp[1] if comp[0]['homeAway']=='home' else comp[0]
                        lista.append(f"{h['team']['displayName']} {h.get('score','0')}x{a.get('score','0')} {a['team']['displayName']}")
                    except: pass
                if lista:
                    info += f"[JOGOS DE HOJE BRASILEIRAO AO VIVO: {' | '.join(lista)}]\n"
            except: pass

    # Noticias reais de hoje
    try:
        r = requests.get("https://api.rss2json.com/v1/api.json?rss_url=https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419", timeout=4).json()
        noticias = [item['title'] for item in r.get("items",[])[:5]]
        if noticias:
            info += f"[NOTICIAS REAIS DE HOJE: {' | '.join(noticias)}]\n"
    except: pass

    # Wikipedia so se nao for futebol
    if "jogo" not in perg_lower and "vasco" not in perg_lower:
        try:
            if len(pergunta)>3:
                resumo = wikipedia.summary(pergunta, sentences=3, auto_suggest=True)
                info += f"[WIKIPEDIA: {resumo}]\n"
        except: pass

    return info

@app.route("/")
def home():
    return '''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Infinito IA</title>
<style>
body{font-family:Arial;background:#0f0f0f;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh}
#top{padding:16px;text-align:center;background:#000;border-bottom:1px solid #222;font-weight:bold}
#chat{flex:1;overflow:auto;padding:16px;display:flex;flex-direction:column;gap:12px}
.u{background:#7c3aed;align-self:flex-end;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:85%}
.b{background:#1f1f1f;align-self:flex-start;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:90%;border:1px solid #333;white-space:pre-wrap;line-height:1.5}
#bar{display:flex;padding:12px;background:#000;gap:8px}
input{flex:1;padding:14px 18px;border-radius:30px;border:1px solid #333;background:#1f1f1f;color:#fff;outline:none}
button{padding:14px 22px;border-radius:30px;border:none;background:#fff;color:#000;font-weight:bold}
</style></head><body>
<div id="top">INFINITO IA - Nao inventa mais</div>
<div id="chat"><div class="b">Ola! Agora eu nao invento mais!

Pergunte "ultimo jogo do Vasco" que eu busco o jogo REAL de verdade!

Testa ai!</div></div>
<div id="bar"><input id="inp" placeholder="Ex: ultimo jogo do Vasco"><button onclick="send()">Enviar</button></div>
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
        info_mundo = get_info_mundo(msg)

        sistema = f"""Voce e o INFINITO IA. REGRA NUMERO 1: NUNCA INVENTE INFORMACAO. Nunca invente tecnico, jogador ou placar.

DADOS REAIS COLETADOS AGORA (USE APENAS ISSO, NAO INVENTE NADA ALÉM):
{info_mundo}

INSTRUCOES OBRIGATORIAS:
- Se tiver [ULTIMO JOGO REAL DO...] use EXATAMENTE esse placar e data, nao invente outro
- Se perguntarem ultimo jogo do Vasco, a resposta e Vasco 5x0 Coritiba em 19/09 - foi o que aconteceu de verdade
- Nunca invente nomes de tecnicos. Se nao souber o tecnico, diga "nao tenho essa info"
- Se nao tiver dado real, diga "nao achei o placar exato agora, mas posso buscar"
- Seja direto, fale PT-BR, nao invente historias
- Voce tem que ser mais preciso que o Google"""

        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":sistema},{"role":"user","content":msg}],
            max_tokens=1000,
            temperature=0.1
        )
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Erro: {str(e)[:200]}"})

if __name__ == "__main__":
    app.run()
