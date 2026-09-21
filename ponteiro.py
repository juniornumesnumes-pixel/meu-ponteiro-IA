from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
import pytz

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_KEY"))

# Lista de fusos que ele vai conhecer
FUSOS = {
    "Bacabal / Brasil": "America/Sao_Paulo",
    "Nova York / EUA": "America/New_York",
    "Londres / UK": "Europe/London",
    "Tóquio / Japão": "Asia/Tokyo",
    "Dubai / Emirados": "Asia/Dubai",
    "Lisboa / Portugal": "Europe/Lisbon"
}

def get_relogio_mundial():
    txt = ""
    for nome, fuso in FUSOS.items():
        try:
            agora = datetime.now(pytz.timezone(fuso))
            txt += f"{nome}: {agora.strftime('%d/%m/%Y %H:%M:%S')}\n"
        except:
            pass
    return txt

@app.route("/")
def home():
    html = '''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Infinito IA com Relogio Mundial</title>
<style>
body{font-family:Arial;background:#0f0f0f;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh}
#top{padding:12px;text-align:center;background:#000;border-bottom:1px solid #222;font-weight:bold;display:flex;justify-content:space-between}
#chat{flex:1;overflow:auto;padding:15px;display:flex;flex-direction:column;gap:10px}
.u{background:#7c3aed;align-self:flex-end;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:85%}
.b{background:#1f1f1f;align-self:flex-start;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:85%;border:1px solid #333;white-space:pre-wrap}
#bar{display:flex;padding:12px;background:#000;gap:8px}
input{flex:1;padding:14px 18px;border-radius:30px;border:1px solid #333;background:#1f1f1f;color:#fff;outline:none}
button{padding:14px 18px;border-radius:30px;border:none;background:#fff;color:#000;font-weight:bold}
#clock{font-size:11px;opacity:0.7}
</style></head><body>
<div id="top"><span>INFINITO IA</span><span id="clock"></span><button onclick="loadClock()" style="padding:5px 10px;font-size:11px">Atualizar Horario</button></div>
<div id="chat"><div class="b">Ola! Sou o Infinito IA com Relogio Mundial!
Posso te dizer a hora exata em qualquer pais.
Pergunte: "Que horas sao em Toquio?" ou "Horario em Nova York"</div></div>
<div id="bar"><input id="inp" placeholder="Pergunte a hora em qualquer lugar..."><button onclick="send()">Enviar</button></div>
<script>
async function loadClock(){
  try{
    let r=await fetch('/horario'); let d=await r.json();
    document.getElementById('clock').innerText = d.brasil;
  }catch(e){}
}
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="u">${t}</div>`; i.value='';
 c.scrollTop=c.scrollHeight;
 try{
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
  let d=await r.json();
  c.innerHTML+=`<div class="b">${d.reply}</div>`;
 }catch(e){c.innerHTML+=`<div class="b">Erro de conexao</div>`}
 c.scrollTop=c.scrollHeight;
}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
loadClock();
setInterval(loadClock, 30000);
</script></body></html>
'''
    return html

@app.route("/horario")
def horario():
    agora_br = datetime.now(pytz.timezone("America/Sao_Paulo"))
    todos = get_relogio_mundial()
    return jsonify({"brasil": agora_br.strftime('%H:%M:%S'), "todos": todos})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        msg = request.get_json().get("message","")
        relogios = get_relogio_mundial()
        system_com_hora = f"""Voce e o INFINITO IA, igual ao Gemini. Voce tem ACESSO AO RELOGIO MUNDIAL em tempo real.

HORARIO ATUAL AGORA:
{relogios}

Use essas informacoes para responder sobre horas. Se perguntarem horario, use os dados acima, sao reais e atualizados.
Fale PT-BR, seja inteligente e prestativo. Voce e o Infinito IA."""

        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content": system_com_hora},{"role":"user","content": msg}],
            max_tokens=1000
        )
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        try:
            comp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role":"system","content": system_com_hora},{"role":"user","content": msg}],
                max_tokens=1000
            )
            return jsonify({"reply": comp.choices[0].message.content})
        except Exception as e2:
            return jsonify({"reply": "Erro: " + str(e2)[:300]})

if __name__ == "__main__":
    app.run()
