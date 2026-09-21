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

FUSOS = {"Bacabal / Brasil": "America/Sao_Paulo","Nova York":"America/New_York","Londres":"Europe/London","Toquio":"Asia/Tokyo"}

def get_relogio():
    txt=""
    for n,f in FUSOS.items():
        txt+=f"{n}: {datetime.now(pytz.timezone(f)).strftime('%H:%M:%S %d/%m')}\n"
    return txt

def get_noticias_mundo():
    try:
        # Pega noticias do Google News via API gratis
        r = requests.get("https://api.rss2json.com/v1/api.json?rss_url=https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419", timeout=6).json()
        noticias = []
        for item in r.get("items",[])[:8]:
            noticias.append(f"- {item['title']} ({item['pubDate'][:16]})")
        return "\n".join(noticias)
    except:
        return "Noticias indisponiveis no momento"

def get_futebol():
    jogos=[]
    try:
        r = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard", timeout=5).json()
        for ev in r.get("events",[])[:6]:
            try:
                c=ev['competitions'][0]['competitors']
                h=c[0] if c[0]['homeAway']=='home' else c[1]
                a=c[1] if c[0]['homeAway']=='home' else c[0]
                jogos.append(f"{h['team']['displayName']} {h.get('score','0')} x {a.get('score','0')} {a['team']['displayName']} - {ev['status']['type']['detail']}")
            except: pass
    except: pass
    return "\n".join(jogos) if jogos else "Nenhum jogo ao vivo agora"

def busca_wikipedia(tema):
    try:
        if len(tema)<3: return ""
        resumo = wikipedia.summary(tema, sentences=3, auto_suggest=False)
        return f"INFO WIKIPEDIA SOBRE '{tema}': {resumo}"
    except:
        try:
            busca = wikipedia.search(tema, results=1)
            if busca:
                return f"INFO WIKIPEDIA SOBRE '{busca[0]}': {wikipedia.summary(busca[0], sentences=3)}"
        except: pass
        return ""

@app.route("/")
def home():
    return '''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;font-family:Arial;background:#0f0f0f;color:#fff;height:100vh;display:flex;flex-direction:column}
#top{background:#000;padding:12px;text-align:center;font-weight:bold;border-bottom:1px solid #222}
#tabs{display:flex;background:#000;border-bottom:1px solid #222}
.tab{flex:1;padding:10px;text-align:center;cursor:pointer;opacity:0.6;font-size:12px}
.tab.active{opacity:1;border-bottom:2px solid #00e676;font-weight:bold}
#chat,#futebol,#mundo,#relogioPage{flex:1;overflow:auto;padding:12px;display:none;flex-direction:column;gap:10px}
#chat.active,#futebol.active,#mundo.active,#relogioPage.active{display:flex}
.u{background:#7c3aed;align-self:flex-end;padding:10px 14px;border-radius:18px 18px 4px 18px;max-width:85%}
.b{background:#1f1f1f;align-self:flex-start;padding:10px 14px;border-radius:18px 18px 4px 18px;max-width:85%;border:1px solid #333;white-space:pre-wrap}
#bar{display:flex;padding:10px;background:#000;gap:8px}
input{flex:1;padding:12px 16px;border-radius:25px;border:1px solid #333;background:#1f1f1f;color:#fff}
button{padding:12px 16px;border-radius:25px;border:none;background:#fff;color:#000;font-weight:bold}
.card{background:#1f1f1f;border:1px solid #333;padding:12px;border-radius:12px}
</style></head><body>
<div id="top">INFINITO IA - SABE TUDO DO MUNDO</div>
<div id="tabs"><div class="tab active" onclick="showTab('chat',this)">Chat</div><div class="tab" onclick="showTab('futebol',this)">Futebol</div><div class="tab" onclick="showTab('mundo',this)">Mundo</div><div class="tab" onclick="showTab('relogioPage',this)">Relogio</div></div>

<div id="chat" class="active"><div class="b">Eu sou o INFINITO IA com CEREBRO DO MUNDO!
🌍 Sei noticias de hoje, futebol ao vivo, hora mundial, Wikipedia, tudo!

Pergunte qualquer coisa: "O que aconteceu hoje no Brasil?" "Quem ganhou o jogo do Flamengo?" "O que e buraco negro?"</div></div>
<div id="futebol"><button onclick="loadFutebol()" style="background:#00e676">Atualizar Futebol</button><div id="listaFut"></div></div>
<div id="mundo"><button onclick="loadMundo()" style="background:#00e676">Atualizar Noticias do Mundo</button><div id="listaMundo"></div></div>
<div id="relogioPage"><div id="clockList"></div><button onclick="loadClocks()">Atualizar</button></div>

<div id="bar"><input id="inp" placeholder="Pergunte qualquer coisa do mundo..."><button onclick="send()">Enviar</button></div>

<script>
function showTab(t,el){document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));document.querySelectorAll('#chat,#futebol,#mundo,#relogioPage').forEach(e=>e.classList.remove('active'));el.classList.add('active');document.getElementById(t).classList.add('active');if(t=='futebol')loadFutebol();if(t=='mundo')loadMundo();if(t=='relogioPage')loadClocks();}
async function send(){
 let i=document.getElementById('inp');let t=i.value.trim();if(!t)return;
 let c=document.getElementById('chat');c.innerHTML+=`<div class="u">${t}</div>`;i.value='';c.scrollTop=c.scrollHeight;
 c.innerHTML+=`<div class="b" id="temp">Pesquisando no mundo todo...</div>`;
 try{let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let d=await r.json();document.getElementById('temp').remove();c.innerHTML+=`<div class="b">${d.reply}</div>`;}catch(e){document.getElementById('temp').remove();c.innerHTML+=`<div class="b">Erro</div>`}c.scrollTop=c.scrollHeight;
}
async function loadFutebol(){document.getElementById('listaFut').innerHTML='Carregando...';let r=await fetch('/api/futebol');let d=await r.json();let h='';d.jogos.forEach(j=>{h+=`<div class="card">${j}</div>`});document.getElementById('listaFut').innerHTML=h||'Nenhum jogo hoje';}
async function loadMundo(){document.getElementById('listaMundo').innerHTML='Buscando noticias do mundo...';let r=await fetch('/api/mundo');let d=await r.json();let h='';d.noticias.forEach(n=>{h+=`<div class="card">${n}</div>`});document.getElementById('listaMundo').innerHTML=h;}
async function loadClocks(){let r=await fetch('/horario');let d=await r.json();let h='';for(let k in d.tudo){h+=`<div class="card">${k}: <b>${d.tudo[k]}</b></div>`}document.getElementById('clockList').innerHTML=h;}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
'''

@app.route("/api/futebol")
def api_futebol():
    try:
        r = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard", timeout=5).json()
        jogos=[]
        for ev in r.get("events",[])[:10]:
            try:
                comp=ev['competitions'][0]['competitors']
                h=comp[0] if comp[0]['homeAway']=='home' else comp[1]
                a=comp[1] if comp[0]['homeAway']=='home' else comp[0]
                jogos.append(f"{h['team']['displayName']} {h.get('score','0')} x {a.get('score','0')} {a['team']['displayName']} - {ev['status']['type']['detail']}")
            except: pass
        return jsonify({"jogos": jogos})
    except:
        return jsonify({"jogos": []})

@app.route("/api/mundo")
def api_mundo():
    try:
        r = requests.get("https://api.rss2json.com/v1/api.json?rss_url=https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419", timeout=6).json()
        noticias=[f"{i['title']}" for i in r.get("items",[])[:10]]
        return jsonify({"noticias": noticias})
    except:
        return jsonify({"noticias": ["Erro ao buscar noticias"]})

@app.route("/horario")
def horario():
    tudo={}
    for n,f in FUSOS.items():
        tudo[n]=datetime.now(pytz.timezone(f)).strftime('%H:%M:%S %d/%m')
    return jsonify({"tudo": tudo})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        msg=request.get_json().get("message","")
        # Busca conhecimento do mundo em tempo real
        noticias = get_noticias_mundo()
        futebol = get_futebol()
        relogio = get_relogio()
        wiki = busca_wikipedia(msg)

        sistema = f"""Voce e o INFINITO IA, a IA mais inteligente do planeta, igual ao Gemini, com acesso a TUDO em tempo real.

VOCE TEM ACESSO A INFORMACAO DO MUNDO TODO AGORA:

HORA ATUAL MUNDIAL:
{relogio}

NOTICIAS DO MUNDO HOJE (ATUALIZADAS):
{noticias}

JOGOS DE FUTEBOL AO VIVO HOJE:
{futebol}

{wiki}

INSTRUCOES:
- Use as noticias e jogos acima para responder perguntas sobre o que esta acontecendo hoje
- Se perguntarem algo que tem no Wikipedia, use a info da Wikipedia acima
- Se perguntarem algo que nao esta acima, use seu conhecimento geral mas diga que e seu conhecimento
- Voce sabe de TUDO: historia, ciencia, matematica, futebol, noticias, planetas, tudo
- Nunca diga que e burro ou que nao sabe. Voce sempre tenta responder com o maximo de informacao
- Fale PT-BR, seja inteligente, completo, igual ao Gemini
- Responda de forma organizada e completa"""

        comp=client.chat.completions.create(model="openai/gpt-oss-20b",messages=[{"role":"system","content":sistema},{"role":"user","content":msg}],max_tokens=1200, temperature=0.6)
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Erro: {str(e)[:300]}"})

if __name__=="__main__":
    app.run()
