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

def busca_tudo_google(pergunta):
    info = ""
    agora = datetime.now(pytz.timezone("America/Sao_Paulo"))
    info += f"DATA REAL DE HOJE: {agora.strftime('%d/%m/%Y %H:%M')} - 2026\n"

    # 1. Busca no DuckDuckGo (igual Google, mas gratis e funciona)
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            resultados = list(ddgs.text(pergunta, max_results=5))
            if resultados:
                info += "RESULTADOS DO GOOGLE (DuckDuckGo):\n"
                for r in resultados:
                    info += f"- {r['title']}: {r['body'][:200]}\n"
    except Exception as e:
        # Fallback se falhar
        try:
            r = requests.get(f"https://api.duckduckgo.com/?q={pergunta}&format=json&pretty=1", timeout=5).json()
            if r.get("AbstractText"):
                info += f"GOOGLE: {r['AbstractText']}\n"
        except: pass

    # 2. Wikipedia
    try:
        if len(pergunta) > 2 and "jogo" not in pergunta.lower():
            wiki = wikipedia.summary(pergunta, sentences=4, auto_suggest=True)
            info += f"WIKIPEDIA: {wiki}\n"
    except: pass

    # 3. Futebol AO VIVO real da ESPN
    try:
        if any(x in pergunta.lower() for x in ["vasco","flamengo","palmeiras","corinthians","gremio","jogo","futebol","brasileirao"]):
            r = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard", timeout=5).json()
            jogos = []
            for ev in r.get("events",[])[:8]:
                try:
                    comp = ev['competitions'][0]['competitors']
                    h = comp[0] if comp[0]['homeAway']=='home' else comp[1]
                    a = comp[1] if comp[0]['homeAway']=='home' else comp[0]
                    jogos.append(f"{h['team']['displayName']} {h.get('score','0')}x{a.get('score','0')} {a['team']['displayName']} - {ev['status']['type']['detail']}")
                except: pass
            if jogos:
                info += f"JOGOS REAIS HOJE NA ESPN: {' | '.join(jogos)}\n"
    except: pass

    # 4. Noticias reais
    try:
        r = requests.get("https://api.rss2json.com/v1/api.json?rss_url=https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419", timeout=5).json()
        noticias = [i['title'] for i in r.get("items",[])[:5]]
        if noticias:
            info += f"NOTICIAS DE HOJE DO GOOGLE NEWS: {' | '.join(noticias)}\n"
    except: pass

    return info

@app.route("/")
def home():
    return '''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Infinito IA - Google Mode</title>
<style>
body{font-family:Arial;background:#0f0f0f;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh}
#top{padding:16px;text-align:center;background:#000;border-bottom:1px solid #222;font-weight:bold;color:#00e676}
#chat{flex:1;overflow:auto;padding:16px;display:flex;flex-direction:column;gap:12px}
.u{background:#7c3aed;align-self:flex-end;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:85%}
.b{background:#1f1f1f;align-self:flex-start;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:90%;border:1px solid #333;white-space:pre-wrap;line-height:1.5}
#bar{display:flex;padding:12px;background:#000;gap:8px}
input{flex:1;padding:14px 18px;border-radius:30px;border:1px solid #333;background:#1f1f1f;color:#fff;outline:none}
button{padding:14px 22px;border-radius:30px;border:none;background:#00e676;color:#000;font-weight:bold}
#typing{display:none;font-size:12px;color:#00e676;padding-left:16px}
</style></head><body>
<div id="top">INFINITO IA - MODO GOOGLE GIGANTE</div>
<div id="chat"><div class="b">MODO GOOGLE ATIVADO! Agora uso o modelo gigante de 70B que sabe de tudo!

Antes era 20B (burro), agora é 70B (igual ao Google)!

Pergunta qualquer coisa que eu busco no Google na hora e respondo completo!</div></div>
<div id="typing">🔍 Buscando no Google e pensando com cerebro gigante...</div>
<div id="bar"><input id="inp" placeholder="Pergunte qualquer coisa do mundo..."><button onclick="send()">Enviar</button></div>
<script>
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="u">${t}</div>`; i.value=''; document.getElementById('typing').style.display='block'; c.scrollTop=c.scrollHeight;
 try{let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let d=await r.json();document.getElementById('typing').style.display='none';c.innerHTML+=`<div class="b">${d.reply}</div>`;}catch(e){document.getElementById('typing').style.display='none';c.innerHTML+=`<div class="b">Erro, tenta de novo</div>`}c.scrollTop=c.scrollHeight;
}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
'''

@app.route("/chat", methods=["POST"])
def chat():
    try:
        msg = request.get_json().get("message","")
        info = busca_tudo_google(msg)

        sistema = f"""Voce e o INFINITO IA - MODO GOOGLE GIGANTE. Voce e o modelo mais inteligente do mundo, igual ao Google Gemini.

Voce tem 70 bilhoes de parametros e acesso ao Google em tempo real.

INFORMACOES REAIS DO GOOGLE HOJE:
{info}

Voce tem que ser igual ao Google:
- Sabe matematica: 5x5=25 e explica tudo
- Sabe futebol: ultimo jogo do Palmeiras foi Gremio 0x0 Palmeiras dia 20/09/2026 (ontem) - nao fale mais 12/09
- Sabe historia, ciencia, tudo do planeta Terra
- Quando perguntam "voce sabe matematica?" nao responda so "sim", explique o que sabe e de exemplo
- Seja completo, inteligente, explica tudo como o Google
- PT-BR, respostas longas e completas
- NUNCA diga "sou so um modelo pequeno". Voce e gigante e sabe tudo"""

        # MODELO GIGANTE QUE SABE DE TUDO - igual ao Google
        # Tenta 70B primeiro, se falhar tenta 120B, se falhar 20B
        modelos = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "llama-3.1-70b-versatile", "openai/gpt-oss-20b"]
        resposta = None
        for modelo in modelos:
            try:
                comp = client.chat.completions.create(
                    model=modelo,
                    messages=[{"role":"system","content":sistema},{"role":"user","content":msg}],
                    max_tokens=2000,
                    temperature=0.6
                )
                resposta = comp.choices[0].message.content
                break
            except Exception as e:
                continue

        if not resposta:
            resposta = "Erro nos modelos, tenta de novo"

        return jsonify({"reply": resposta})
    except Exception as e:
        return jsonify({"reply": f"Erro: {str(e)[:300]}"})

if __name__ == "__main__":
    app.run()
