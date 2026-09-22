from flask import Flask, request, jsonify, session
import os
from groq import Groq
from datetime import datetime
import pytz
import uuid

app = Flask(__name__)
app.secret_key = "infinito-ia-pro-2026-seguro"
client = Groq(api_key=os.environ.get("GROQ_KEY"))

# MEMORIA PROFISSIONAL - cada usuario tem sua memoria
usuarios_memoria = {}

def get_user_id():
    # Pega ID do usuario do header ou cria novo
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        user_id = str(uuid.uuid4())
    return user_id

@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>INFINITO IA - Pro</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto; background:#0a0a0a; color:#ececec; height:100vh; display:flex; flex-direction:column}
#header{background:#000; border-bottom:1px solid #1a1a1a; padding:14px 20px; display:flex; justify-content:space-between; align-items:center}
#header h1{font-size:16px; color:#00e676; letter-spacing:1px}
#header div{display:flex; gap:8px}
.btn{padding:8px 14px; border-radius:8px; border:1px solid #2a2a2a; background:#151515; color:#fff; font-size:12px; cursor:pointer}
.btn:hover{background:#222}
#chat{flex:1; overflow:auto; padding:20px; display:flex; flex-direction:column; gap:16px; max-width:900px; margin:0 auto; width:100%}
.msg{padding:14px 18px; border-radius:18px; max-width:85%; line-height:1.5; font-size:15px; white-space:pre-wrap; word-wrap:break-word}
.user{align-self:flex-end; background:#7c3aed; color:#fff; border-radius:18px 18px 4px 18px}
.bot{align-self:flex-start; background:#1a1a1a; border:1px solid #2a2a2a; color:#ececec; border-radius:18px 18px 18px 4px}
#input-area{background:#000; border-top:1px solid #1a1a1a; padding:16px; display:flex; justify-content:center}
#input-wrap{display:flex; gap:10px; max-width:900px; width:100%; background:#1a1a1a; border:1px solid #2a2a2a; border-radius:28px; padding:8px 8px 8px 20px; align-items:center}
#inp{flex:1; background:transparent; border:none; color:#fff; font-size:15px; outline:none}
#send{padding:10px 20px; border-radius:24px; border:none; background:#00e676; color:#000; font-weight:bold; cursor:pointer; font-size:14px}
#send:hover{background:#00c853}
.typing{font-style:italic; opacity:0.7}
</style></head><body>
<div id="header"><h1>INFINITO IA • PRO</h1><div><button class="btn" onclick="novaChat()">+ NOVA</button><button class="btn" onclick="limpar()">LIMPAR</button></div></div>
<div id="chat"><div class="msg bot">Olá! Sou o INFINITO IA Pro. Qual é o seu nome?</div></div>
<div id="input-area"><div id="input-wrap"><input id="inp" placeholder="Digite sua mensagem..." autocomplete="off"><button id="send" onclick="send()">ENVIAR</button></div></div>

<script>
let USER_ID = localStorage.getItem('infinito_user_id');
if(!USER_ID){ USER_ID = 'user_'+Math.random().toString(36).substr(2,9); localStorage.setItem('infinito_user_id', USER_ID); }

let historicoLocal = JSON.parse(localStorage.getItem('hist_'+USER_ID) || '[]');
let chatDiv = document.getElementById('chat');

function render(){
 if(historicoLocal.length===0){ chatDiv.innerHTML='<div class="msg bot">Olá! Sou o INFINITO IA Pro. Qual é o seu nome?</div>'; return; }
 chatDiv.innerHTML='';
 historicoLocal.forEach(m=>{
   let cls = m.role==='user'? 'msg user' : 'msg bot';
   chatDiv.innerHTML+=`<div class="${cls}">${escapeHtml(m.content)}</div>`;
 });
 chatDiv.scrollTop = chatDiv.scrollHeight;
}
function escapeHtml(t){ let d=document.createElement('div'); d.textContent=t; return d.innerHTML; }
render();

async function send(){
 let input = document.getElementById('inp');
 let text = input.value.trim(); if(!text) return;
 historicoLocal.push({role:'user', content:text});
 localStorage.setItem('hist_'+USER_ID, JSON.stringify(historicoLocal));
 render(); input.value='';
 chatDiv.innerHTML+=`<div class="msg bot typing">Digitando...</div>`;
 chatDiv.scrollTop = chatDiv.scrollHeight;

 try{
   let r = await fetch('/chat',{
     method:'POST',
     headers:{'Content-Type':'application/json','X-User-ID':USER_ID},
     body:JSON.stringify({messages:historicoLocal})
   });
   let d = await r.json();
   historicoLocal.pop(); // remove typing
   document.querySelector('.typing')?.remove();
   historicoLocal.push({role:'user', content:text});
   historicoLocal.push({role:'assistant', content:d.reply});
   localStorage.setItem('hist_'+USER_ID, JSON.stringify(historicoLocal));
   render();
 }catch(e){
   document.querySelector('.typing')?.remove();
   historicoLocal.push({role:'assistant', content:'Erro de conexão, tente novamente'});
   localStorage.setItem('hist_'+USER_ID, JSON.stringify(historicoLocal));
   render();
 }
}
function limpar(){ historicoLocal=[]; localStorage.removeItem('hist_'+USER_ID); fetch('/limpar',{method:'POST', headers:{'X-User-ID':USER_ID}}); render(); }
function novaChat(){ limpar(); }
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script>
</body></html>
'''

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_id = get_user_id()
        data = request.get_json()
        messages = data.get("messages", [])

        # Salva memoria profissional por usuario
        if user_id not in usuarios_memoria:
            usuarios_memoria[user_id] = []
        usuarios_memoria[user_id] = messages[-20:] # guarda ultimas 20

        agora = datetime.now(pytz.timezone("America/Sao_Paulo"))
        nome = ""
        for m in messages:
            c = m.get("content","").lower()
            if "meu nome e" in c or "meu nome é" in c:
                try:
                    nome = c.split("meu nome e")[-1].split("meu nome é")[-1].strip().split()[0].capitalize()
                except: pass

        # SISTEMA PROFISSIONAL
        sistema = f"""Você é o INFINITO IA PRO - app profissional para milhares de pessoas.

        DATA: {agora.strftime('%d/%m/%Y %H:%M')} - Bacabal, Brasil
        USUARIO ATUAL ID: {user_id[:8]} - Nome detectado: {nome if nome else 'ainda não sei'}

        REGRAS PRO:
        1. MEMORIA INDIVIDUAL: Lembre o nome SÓ deste usuario, nao misture com outros
        2. INTELIGENTE ADAPTATIVO:
           - Pergunta curta (que dia foi o jogo? que horas sao? clima?) -> resposta curta 1 linha
           - Pergunta media (quanto e 123x234?) -> resposta media direta
           - Pergunta longa (explica, dever, historia 300 linhas) -> resposta longa completa
        3. SABE DE TUDO: futebol real (Gremio 0x0 Palmeiras 20/09/2026), matematica, clima, historias
        4. PROFISSIONAL: português perfeito, sem "sabho", educado, chama pelo nome
        5. Se perguntarem "qual meu nome?" responda o nome deste usuario
        6. Nunca diga que é de outra empresa, você é INFINITO IA PRO
        """

        groq_msgs = [{"role":"system","content":sistema}]
        for m in messages[-12:]:
            if m.get("role") in ["user","assistant"]:
                groq_msgs.append({"role":m["role"],"content":m["content"]})

        ultima = messages[-1]["content"].lower() if messages else ""
        if any(x in ultima for x in ["historia","história","300","conto","livro"]):
            max_t = 3000
        elif len(ultima.split()) <= 7:
            max_t = 120
        else:
            max_t = 800

        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=groq_msgs,
            max_tokens=max_t,
            temperature=0.6
        )
        reply = comp.choices[0].message.content

        return jsonify({"reply": reply, "user_id": user_id, "nome": nome})

    except Exception as e:
        return jsonify({"reply": "Tive um erro pro, tenta de novo"})

@app.route("/limpar", methods=["POST"])
def limpar():
    user_id = get_user_id()
    if user_id in usuarios_memoria:
        del usuarios_memoria[user_id]
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run()
