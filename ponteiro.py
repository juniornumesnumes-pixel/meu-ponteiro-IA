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

def get_info_mundo(pergunta):
    info = ""

    # 1. Hora mundial
    try:
        agora = datetime.now(pytz.timezone("America/Sao_Paulo"))
        info += f"[HORA ATUAL BRASIL: {agora.strftime('%d/%m/%Y %H:%M:%S')}]\n"
    except: pass

    # 2. Futebol ao vivo
    try:
        r = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard", timeout=4).json()
        jogos=[]
        for ev in r.get("events",[])[:4]:
            try:
                comp=ev['competitions'][0]['competitors']
                h=comp[0] if comp[0]['homeAway']=='home' else comp[1]
                a=comp[1] if comp[0]['homeAway']=='home' else comp[0]
                jogos.append(f"{h['team']['displayName']} {h.get('score','0')}x{a.get('score','0')} {a['team']['displayName']} ({ev['status']['type']['detail']})")
            except: pass
        if jogos:
            info += f"[JOGOS DE FUTEBOL HOJE: {' | '.join(jogos)}]\n"
    except: pass

    # 3. Noticias do mundo hoje
    try:
        r = requests.get("https://api.rss2json.com/v1/api.json?rss_url=https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419", timeout=4).json()
        noticias = [item['title'] for item in r.get("items",[])[:5]]
        if noticias:
            info += f"[NOTICIAS DE HOJE: {' | '.join(noticias)}]\n"
    except: pass

    # 4. Wikipedia sobre o que o usuario perguntou
    try:
        if len(pergunta)>2:
            res = wikipedia.summary(pergunta, sentences=4, auto_suggest=True)
            info += f"[WIKIPEDIA SOBRE '{pergunta}': {res}]\n"
    except:
        try:
            busca = wikipedia.search(pergunta, results=1)
            if busca:
                res = wikipedia.summary(busca[0], sentences=4)
                info += f"[WIKIPEDIA: {res}]\n"
        except: pass

    return info

@app.route("/")
def home():
    return '''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Infinito IA</title>
<style>
body{font-family:Arial;background:#0f0f0f;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh}
#top{padding:16px;text-align:center;background:#000;border-bottom:1px solid #222;font-weight:bold;letter-spacing:1px}
#chat{flex:1;overflow:auto;padding:16px;display:flex;flex-direction:column;gap:12px}
.u{background:#7c3aed;align-self:flex-end;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:85%;line-height:1.4}
.b{background:#1f1f1f;align-self:flex-start;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:90%;border:1px solid #333;white-space:pre-wrap;line-height:1.5}
#bar{display:flex;padding:12px;background:#000;gap:8px}
input{flex:1;padding:14px 18px;border-radius:30px;border:1px solid #333;background:#1f1f1f;color:#fff;outline:none;font-size:15px}
button{padding:14px 22px;border-radius:30px;border:none;background:#fff;color:#000;font-weight:bold}
#typing{font-size:12px;opacity:0.6;padding-left:16px;display:none}
</style></head><body>
<div id="top">INFINITO IA - Sabe tudo do mundo</div>
<div id="chat"><div class="b">Ola! Eu sou o Infinito IA!
Eu sei tudo que acontece no mundo em tempo real!

Pode me perguntar qualquer coisa:
- Noticias de hoje
- Futebol ao vivo
- Hora em qualquer pais
- Historia, ciencia, tudo

O que voce quer saber?</div></div>
<div id="typing">Pesquisando no mundo todo...</div>
<div id="bar"><input id="inp" placeholder="Pergunte qualquer coisa do mundo..."><button onclick="send()">Enviar</button></div>
<script>
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat');
 c.innerHTML+=`<div class="u">${t}</div>`;
 i.value='';
 document.getElementById('typing').style.display='block';
 c.scrollTop=c.scrollHeight;
 try{
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
  let d=await r.json();
  document.getElementById('typing').style.display='none';
  c.innerHTML+=`<div class="b">${d.reply}</div>`;
 }catch(e){
  document.getElementById('typing').style.display='none';
  c.innerHTML+=`<div class="b">Erro de conexao, tenta de novo</div>`
 }
 c.scrollTop=c.scrollHeight;
}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
'''

@app.route("/chat", methods=["POST"])
def chat():
    try:
        msg = request.get_json().get("message","")
        info_mundo = get_info_mundo(msg)

        sistema = f"""Voce e o INFINITO IA, a IA mais inteligente do planeta Terra. Voce tem acesso a informacoes do mundo todo em tempo real.

INFORMACOES DO MUNDO EM TEMPO REAL AGORA (USE PARA RESPONDER):
{info_mundo}

REGRAS:
- Voce sabe de TUDO: noticias de hoje, futebol ao vivo, hora atual, ciencia, historia, matematica, geografia, tudo do planeta Terra
- Use as informacoes acima quando relevante
- Se o usuario perguntar sobre futebol, use os jogos acima
- Se perguntar sobre noticias, use as noticias acima
- Se perguntar sobre qualquer tema, explique completo, como o Gemini
- Nunca diga "nao sei" ou "sou burro". Voce sempre sabe e responde completo
- Fale PT-BR, seja inteligente e direto
- Responda tudo que perguntarem, voce tem conhecimento do mundo inteiro"""

        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":sistema},{"role":"user","content":msg}],
            max_tokens=1500,
            temperature=0.5
        )
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Erro temporario, tenta de novo: {str(e)[:150]}"})

if __name__ == "__main__":
    app.run()
