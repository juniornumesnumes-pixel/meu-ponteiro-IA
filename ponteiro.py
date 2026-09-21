from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
import pytz
import requests

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_KEY"))

FUSOS = {
    "Bacabal / Brasil": "America/Sao_Paulo",
    "Nova York / EUA": "America/New_York",
    "Londres / UK": "Europe/London",
    "Toquio / Japao": "Asia/Tokyo"
}

def get_relogio():
    txt=""
    for nome,fuso in FUSOS.items():
        agora=datetime.now(pytz.timezone(fuso))
        txt+=f"{nome}: {agora.strftime('%H:%M:%S %d/%m')}\n"
    return txt

def get_jogos_futebol():
    jogos=[]
    try:
        # Brasileirão
        r = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard", timeout=5).json()
        for ev in r.get("events",[])[:10]:
            try:
                home = ev['competitions'][0]['competitors'][0]
                away = ev['competitions'][0]['competitors'][1]
                # Garante home correto
                if home['homeAway']=='away':
                    home,away = away,home
                jogos.append({
                    "liga": "Brasileirão",
                    "time1": home['team']['displayName'],
                    "placar1": home.get('score','0'),
                    "time2": away['team']['displayName'],
                    "placar2": away.get('score','0'),
                    "status": ev['status']['type']['detail']
                })
            except: pass
    except: pass

    try:
        # Premier League + La Liga + Champions
        for liga_id, nome_liga in [("eng.1","Premier League"),("esp.1","La Liga"),("uefa.champions","Champions")]:
            r = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{liga_id}/scoreboard", timeout=5).json()
            for ev in r.get("events",[])[:5]:
                try:
                    comp = ev['competitions'][0]['competitors']
                    h = comp[0] if comp[0]['homeAway']=='home' else comp[1]
                    a = comp[1] if comp[0]['homeAway']=='home' else comp[0]
                    jogos.append({
                        "liga": nome_liga,
                        "time1": h['team']['displayName'],
                        "placar1": h.get('score','0'),
                        "time2": a['team']['displayName'],
                        "placar2": a.get('score','0'),
                        "status": ev['status']['type']['detail']
                    })
                except: pass
    except: pass
    return jogos

@app.route("/")
def home():
    return '''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;font-family:Arial;background:#0f0f0f;color:#fff;height:100vh;display:flex;flex-direction:column}
#top{background:#000;padding:12px;text-align:center;font-weight:bold;border-bottom:1px solid #222}
#tabs{display:flex;background:#000;border-bottom:1px solid #222}
.tab{flex:1;padding:12px;text-align:center;cursor:pointer;opacity:0.6;font-size:14px}
.tab.active{opacity:1;border-bottom:2px solid #00e676;font-weight:bold}
#chat,#futebol,#relogioPage{flex:1;overflow:auto;padding:12px;display:none;flex-direction:column;gap:10px}
#chat.active,#futebol.active,#relogioPage.active{display:flex}
.u{background:#7c3aed;align-self:flex-end;padding:10px 14px;border-radius:18px 18px 4px 18px;max-width:80%}
.b{background:#1f1f1f;align-self:flex-start;padding:10px 14px;border-radius:18px 18px 4px 18px;max-width:80%;border:1px solid #333;white-space:pre-wrap}
#bar{display:flex;padding:10px;background:#000;gap:8px}
input{flex:1;padding:12px 16px;border-radius:25px;border:1px solid #333;background:#1f1f1f;color:#fff}
button{padding:12px 16px;border-radius:25px;border:none;background:#fff;color:#000;font-weight:bold}
.jogo{background:#1f1f1f;border:1px solid #333;padding:12px;border-radius:12px}
.jogo.liga{font-size:11px;color:#00e676;font-weight:bold;margin-bottom:5px}
.jogo.times{display:flex;justify-content:space-between;align-items:center;font-weight:bold}
.jogo.placar{background:#000;padding:6px 12px;border-radius:20px}
.status{font-size:11px;opacity:0.7;margin-top:5px}
</style></head><body>
<div id="top">INFINITO IA + FUTEBOL AO VIVO</div>
<div id="tabs"><div class="tab active" onclick="showTab('chat',this)">Chat IA</div><div class="tab" onclick="showTab('futebol',this)">Futebol</div><div class="tab" onclick="showTab('relogioPage',this)">Relogio</div></div>

<div id="chat" class="active"><div class="b">Ola! Sou o Infinito IA com Futebol ao Vivo! Pergunte placar ou veja na aba Futebol!</div></div>

<div id="futebol"><button onclick="loadFutebol()" style="background:#00e676">Atualizar Jogos de Hoje</button><div id="listaJogos" style="display:flex;flex-direction:column;gap:10px"></div></div>

<div id="relogioPage"><div id="clockList" style="display:flex;flex-direction:column;gap:10px"></div><button onclick="loadClocks()" style="background:#00e676">Atualizar Horarios</button></div>

<div id="bar"><input id="inp" placeholder="Pergunte placar do seu time..."><button onclick="send()">Enviar</button></div>

<script>
function showTab(t,el){
 document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
 document.querySelectorAll('#chat,#futebol,#relogioPage').forEach(e=>e.classList.remove('active'));
 el.classList.add('active'); document.getElementById(t).classList.add('active');
 if(t=='futebol')loadFutebol(); if(t=='relogioPage')loadClocks();
}
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="u">${t}</div>`; i.value=''; c.scrollTop=c.scrollHeight;
 try{let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let d=await r.json();c.innerHTML+=`<div class="b">${d.reply}</div>`;}catch(e){c.innerHTML+=`<div class="b">Erro</div>`}c.scrollTop=c.scrollHeight;
}
async function loadFutebol(){
 document.getElementById('listaJogos').innerHTML='Carregando jogos...';
 let r=await fetch('/api/futebol'); let d=await r.json();
 if(d.jogos.length==0){document.getElementById('listaJogos').innerHTML='<div class="jogo">Nenhum jogo hoje. Pergunte no chat: qual jogo do Flamengo hoje?</div>'; return}
 let html=''; d.jogos.forEach(j=>{html+=`<div class="jogo"><div class="liga">${j.liga}</div><div class="times"><span>${j.time1}</span><span class="placar">${j.placar1} x ${j.placar2}</span><span>${j.time2}</span></div><div class="status">${j.status}</div></div>`});
 document.getElementById('listaJogos').innerHTML=html;
}
async function loadClocks(){
 let r=await fetch('/horario'); let d=await r.json();
 let html=''; for(let k in d.tudo){html+=`<div class="jogo">${k}: <b>${d.tudo[k]}</b></div>`}
 document.getElementById('clockList').innerHTML=html;
}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
'''

@app.route("/api/futebol")
def api_futebol():
    jogos = get_jogos_futebol()
    return jsonify({"jogos": jogos})

@app.route("/horario")
def horario():
    tudo={}
    for nome,fuso in FUSOS.items():
        agora=datetime.now(pytz.timezone(fuso))
        tudo[nome]=agora.strftime('%H:%M:%S %d/%m')
    return jsonify({"tudo": tudo})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        msg=request.get_json().get("message","")
        relogios=get_relogio()
        jogos = get_jogos_futebol()
        jogos_txt = "\n".join([f"{j['liga']}: {j['time1']} {j['placar1']} x {j['placar2']} {j['time2']} - {j['status']}" for j in jogos[:10]])
        if not jogos_txt:
            jogos_txt = "Nenhum jogo ao vivo agora nos principais campeonatos"

        sys=f"""Voce e o INFINITO IA, igual ao Gemini, com acesso a placar ao vivo e relogio mundial.

HORARIOS ATUAIS:
{relogios}

JOGOS DE FUTEBOL DE HOJE (AO VIVO):
{jogos_txt}

Se perguntarem sobre futebol, use os placares acima, sao reais. Se nao tiver o time pedido, fale que nao tem jogo hoje mas pode comentar sobre o time.
Fale PT-BR, seja torcedor e animado."""

        comp=client.chat.completions.create(model="openai/gpt-oss-20b",messages=[{"role":"system","content":sys},{"role":"user","content":msg}],max_tokens=1000)
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": "Erro: "+str(e)[:200]})

if __name__=="__main__":
    app.run()
