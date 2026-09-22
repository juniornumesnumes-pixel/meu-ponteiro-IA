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
#top{padding:10px;text-align:center;background:#000;border-bottom:1px solid #222;font-weight:bold;color:#00e676;display:flex;justify-content:space-between;align-items:center}
#top button{padding:6px 12px;border-radius:6px;border:1px solid #333;background:#222;color:#fff;font-size:12px}
#chat{flex:1;overflow:auto;padding:14px;display:flex;flex-direction:column;gap:10px}
.u{background:#7c3aed;align-self:flex-end;padding:10px 14px;border-radius:18px 18px 4px 18px;max-width:80%}
.b{background:#1f1f1f;align-self:flex-start;padding:10px 14px;border-radius:18px 18px 4px 18px;max-width:90%;border:1px solid #333;white-space:pre-wrap}
#bar{display:flex;padding:10px;background:#000;gap:8px}
input{flex:1;padding:13px 16px;border-radius:25px;border:1px solid #333;background:#1f1f1f;color:#fff;outline:none}
button.send{padding:13px 18px;border-radius:25px;border:none;background:#00e676;color:#000;font-weight:bold}
</style></head><body>
<div id="top"><span>INFINITO IA - Com Memoria</span><div><button onclick="nova()">NOVA</button> <button onclick="limpar()">LIMPAR</button></div></div>
<div id="chat"></div>
<div id="bar"><input id="inp" placeholder="Digite sua mensagem..."><button class="send" onclick="send()">ENVIAR</button></div>
<script>
let historico = JSON.parse(localStorage.getItem('hist_infinito') || '[]');
let chatDiv = document.getElementById('chat');

function render(){
 chatDiv.innerHTML='';
 historico.forEach(m=>{
   if(m.role==='user') chatDiv.innerHTML+=`<div class="u">${m.content}</div>`;
   else chatDiv.innerHTML+=`<div class="b">${m.content}</div>`;
 });
 chatDiv.scrollTop = chatDiv.scrollHeight;
 if(historico.length===0) chatDiv.innerHTML='<div class="b">Olá! Qual é o seu nome?</div>';
}
render();

function salvar(){ localStorage.setItem('hist_infinito', JSON.stringify(historico)); }

async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 historico.push({role:'user', content:t}); salvar(); render(); i.value='';
 try{
   let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:historico})});
   let d=await r.json();
   historico.push({role:'assistant', content:d.reply}); salvar(); render();
 }catch(e){ historico.push({role:'assistant', content:'Erro de conexao'}); salvar(); render(); }
}

function limpar(){ historico=[]; salvar(); render(); }
function nova(){ limpar(); }

document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
'''

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        if not messages:
            msg = data.get("message","")
            messages = [{"role":"user","content":msg}]

        agora = datetime.now(pytz.timezone("America/Sao_Paulo"))

        # Pega nome se ja falou
        nome = ""
        for m in messages:
            if "meu nome é" in m.get("content","").lower():
                try:
                    nome = m["content"].lower().split("meu nome é")[-1].strip().split()[0].capitalize()
                except: pass

        sistema = f"""Voce e o INFINITO IA, inteligente, com MEMORIA, igual ao Google.

        DATA: {agora.strftime('%d/%m/%Y %H:%M')} Bacabal

        REGRAS DE MEMORIA IMPORTANTES:
        - Voce TEM memoria do historico, lembre o nome da pessoa!
        - Se o usuario ja disse o nome, NUNCA pergunte de novo "qual seu nome"
        - Se nome = Junior, chame de Junior
        - Se perguntarem "qual meu nome?" responda o nome que esta no historico
        - Nao escreva "sabho", escreva certo "sei"
        - Seja inteligente: resposta curta se pergunta curta, longa se pergunta longa
        - Sabe de tudo: futebol (Palmeiras 20/09 Gremio 0x0), clima, matematica, historias de 300 linhas
        - Nome detectado: {nome}

        HISTORICO JA TEM NOME? Se sim, use.
        """

        # Monta mensagens para a Groq com memoria
        groq_messages = [{"role":"system","content":sistema}]
        for m in messages[-10:]: # ultimas 10 mensagens pra ter memoria
            role = m.get("role","user")
            if role not in ["user","assistant"]: continue
            groq_messages.append({"role":role,"content":m.get("content","")})

        # Detecta tamanho
        ultima = messages[-1]["content"].lower()
        if any(x in ultima for x in ["historia","300 linha","conto"]):
            max_t = 3000
        elif len(ultima.split()) <= 6 and any(x in ultima for x in ["que dia","quando foi","que horas","clima"]):
            max_t = 120
        else:
            max_t = 800

        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=groq_messages,
            max_tokens=max_t,
            temperature=0.6
        )
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Erro: {e}"})

if __name__ == "__main__":
    app.run()
