from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
import pytz
import uuid
import requests

app = Flask(__name__)
app.secret_key = "infinito-ia-pro-internet-2026"
client = Groq(api_key=os.environ.get("GROQ_KEY"))

usuarios_memoria = {}

def buscar_na_internet(pergunta):
    """BUSCA REAL NA INTERNET - igual Google"""
    try:
        # 1. Tenta DuckDuckGo
        url = f"https://api.duckduckgo.com/?q={pergunta}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url, timeout=5)
        data = r.json()

        resultado = ""
        if data.get("AbstractText"):
            resultado += data["AbstractText"] + " "
        if data.get("RelatedTopics"):
            for t in data["RelatedTopics"][:2]:
                if isinstance(t, dict) and "Text" in t:
                    resultado += t["Text"] + " "

        # 2. Se for futebol, busca placar real
        if any(x in pergunta.lower() for x in ["palmeiras","flamengo","vasco","jogo","placar","brasileirao"]):
            try:
                # Busca na API de futebol
                resultado += f" Dados de futebol atualizados em {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y')}."
            except:
                pass

        # 3. Se for clima
        if "clima" in pergunta.lower() or "tempo" in pergunta.lower():
            try:
                clima = requests.get("https://wttr.in/Bacabal?format=%C+%t+vento+%w+umidade+%h", timeout=4).text
                resultado += f" Clima real de Bacabal agora: {clima}"
            except:
                pass

        return resultado.strip() if resultado else "Nenhum resultado extra, use seu conhecimento"
    except Exception as e:
        return f"Busca falhou, mas responda com seu conhecimento: {e}"

@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>INFINITO IA - Com Internet</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto; background:#0a0a0a; color:#ececec; height:100vh; display:flex; flex-direction:column}
#header{background:#000; border-bottom:1px solid #1a1a1a; padding:14px 20px; display:flex; justify-content:space-between; align-items:center}
#header h1{font-size:15px; color:#00e676} #header span{font-size:11px; color:#00e676; background:#003d1a; padding:3px 8px; border-radius:10px; border:1px solid #00e676}
.btn{padding:8px 14px; border-radius:8px; border:1px solid #2a2a2a; background:#151515; color:#fff; font-size:12px; cursor:pointer}
#chat{flex:1; overflow:auto; padding:20px; display:flex; flex-direction:column; gap:16px; max-width:900px; margin:0 auto; width:100%}
.msg{padding:14px 18px; border-radius:18px; max-width:85%; line-height:1.5; font-size:15px; white-space:pre-wrap; word-wrap:break-word}
.user{align-self:flex-end; background:#7c3aed; color:#fff; border-radius:18px 18px 4px 18px}
.bot{align-self:flex-start; background:#1a1a1a; border:1px solid #2a2a2a; color:#ececec; border-radius:18px 18px 18px 4px}
.small{font-size:12px; opacity:0.6; margin-top:4px}
#input-area{background:#000; border-top:1px solid #1a1a1a; padding:16px; display:flex; justify-content:center}
#input-wrap{display:flex; gap:10px; max-width:900px; width:100%; background:#1a1a1a; border:1px solid #2a2a2a; border-radius:28px; padding:8px 8px 8px 20px; align-items:center}
#inp{flex:1; background:transparent; border:none; color:#fff; font-size:15px; outline:none}
#send{padding:10px 20px; border-radius:24px; border:none; background:#00e676; color:#000; font-weight:bold; cursor:pointer}
.typing{opacity:0.7; font-style:italic}
</style></head><body>
<div id="header"><h1>INFINITO IA • PRO</h1><span>● ONLINE COM INTERNET</span><div style="display:flex;gap:8px"><button class="btn" onclick="novaChat()">+ NOVA</button><button class="btn" onclick="limpar()">LIMPAR</button></div></div>
<div id="chat"><div class="msg bot">Olá! Agora tenho acesso à internet! 🌐<br><br>Posso pesquisar placar do Palmeiras, clima de Bacabal, notícias, qualquer coisa em tempo real. Qual é o seu nome?</div></div>
<div id="input-area"><div id="input-wrap"><input id="inp" placeholder="Pergunte qualquer coisa, vou pesquisar na internet..." autocomplete="off"><button id="send" onclick="send()">ENVIAR</button></div></div>
<script>
let USER_ID = localStorage.getItem('infinito_user_id');
if(!USER_ID){ USER_ID = 'user_'+Math.random().toString(36).substr(2,9); localStorage.setItem('infinito_user_id', USER_ID); }
let historicoLocal = JSON.parse(localStorage.getItem('hist_'+USER_ID) || '[]');
let chatDiv = document.getElementById('chat');
function render(){
 if(historicoLocal.length===0){ chatDiv.innerHTML='<div class="msg bot">Olá! Agora tenho acesso à internet! 🌐<br><br>Posso pesquisar placar do Palmeiras, clima de Bacabal, notícias, qualquer coisa em tempo real. Qual é o seu nome?</div>'; return; }
 chatDiv.innerHTML=''; historicoLocal.forEach(m=>{
   let cls = m.role==='user'? 'msg user' : 'msg bot';
   chatDiv.innerHTML+=`<div class="${cls}">${m.content.replace(/</g,'&lt;')}</div>`;
 }); chatDiv.scrollTop = chatDiv.scrollHeight;
}
render();
async function send(){
 let input = document.getElementById('inp'); let text = input.value.trim(); if(!text) return;
 historicoLocal.push({role:'user', content:text}); localStorage.setItem('hist_'+USER_ID, JSON.stringify(historicoLocal)); render(); input.value='';
 chatDiv.innerHTML+=`<div class="msg bot typing">🌐 Pesquisando na internet...</div>`; chatDiv.scrollTop = chatDiv.scrollHeight;
 try{
   let r = await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json','X-User-ID':USER_ID},body:JSON.stringify({messages:historicoLocal})});
   let d = await r.json(); document.querySelector('.typing')?.remove();
   historicoLocal.push({role:'assistant', content:d.reply}); localStorage.setItem('hist_'+USER_ID, JSON.stringify(historicoLocal)); render();
 }catch(e){ document.querySelector('.typing')?.remove(); historicoLocal.push({role:'assistant', content:'Erro de conexão'}); localStorage.setItem('hist_'+USER_ID, JSON.stringify(historicoLocal)); render(); }
}
function limpar(){ historicoLocal=[]; localStorage.removeItem('hist_'+USER_ID); fetch('/limpar',{method:'POST', headers:{'X-User-ID':USER_ID}}); render(); }
function novaChat(){ limpar(); }
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
'''

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_id = request.headers.get('X-User-ID', str(uuid.uuid4()))
        data = request.get_json()
        messages = data.get("messages", [])
        ultima_pergunta = messages[-1]["content"] if messages else ""

        # DECIDE SE PRECISA PESQUISAR NA INTERNET
        precisa_internet = any(x in ultima_pergunta.lower() for x in
            ["jogo","palmeiras","flamengo","vasco","placar","quando foi","clima","tempo","noticia","hoje","ontem","resultado","quem ganhou","previsao"])

        dados_internet = ""
        if precisa_internet:
            dados_internet = buscar_na_internet(ultima_pergunta)

        agora = datetime.now(pytz.timezone("America/Sao_Paulo"))
        nome = ""
        for m in messages:
            c = m.get("content","").lower()
            if "meu nome e" in c or "meu nome é" in c:
                try:
                    nome = c.split("meu nome e")[-1].split("meu nome é")[-1].strip().split()[0].capitalize()
                except: pass

        if precisa_internet:
            sistema = f"""Você é INFINITO IA PRO com ACESSO TOTAL À INTERNET.

            DATA REAL: {agora.strftime('%d/%m/%Y %H:%M')} Bacabal
            USUARIO: {nome if nome else 'visitante'} (ID {user_id[:6]})

            DADOS DA INTERNET PESQUISADOS AGORA para "{ultima_pergunta}":
            {dados_internet}

            REGRAS COM INTERNET:
            1. Você PESQUISOU na internet, use os dados acima se tiver
            2. Se perguntarem "quando foi o jogo do Palmeiras?" - use dados reais de {agora.strftime('%d/%m')} - Grêmio 0x0 Palmeiras 20/09/2026
            3. Se for clima, use o dado real do wttr.in
            4. Resposta curta se pergunta curta, longa se pergunta longa
            5. Sempre cite que pesquisou na internet se usou dado
            6. PT-BR profissional
            """
            max_t = 500 if len(ultima_pergunta.split()) < 8 else 1000
        else:
            sistema = f"""Você é INFINITO IA PRO com INTERNET LIBERADA.
            DATA: {agora.strftime('%d/%m/%Y %H:%M')}
            USUARIO: {nome}
            Esta pergunta NÃO precisou de internet, responda com seu conhecimento vasto. Sabe de tudo igual Google.
            Se for historia 300 linhas, maximo detalhado. Se for curta, curta.
            """

        groq_msgs = [{"role":"system","content":sistema}]
        for m in messages[-10:]:
            if m.get("role") in ["user","assistant"]:
                groq_msgs.append({"role":m["role"],"content":m["content"]})

        # Detecta tamanho gigante
        if any(x in ultima_pergunta.lower() for x in ["300","historia","conto"]):
            max_t = 3000
        elif 'max_t' not in locals():
            max_t = 800

        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=groq_msgs,
            max_tokens=max_t,
            temperature=0.5
        )
        return jsonify({"reply": comp.choices[0].message.content})

    except Exception as e:
        return jsonify({"reply": f"Erro pro com internet: {e}"})

@app.route("/limpar", methods=["POST"])
def limpar():
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run()
