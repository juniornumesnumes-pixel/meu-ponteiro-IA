from flask import Flask, request, jsonify
import os
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_KEY"))

SYSTEM = "Voce e o INFINITO IA, igual ao Gemini, super inteligente, criativo, prestativo, fala PT-BR, responde sobre TUDO: dever, codigos, textos, ideias. Voce e o Infinito IA, nunca diga que e da Groq."

@app.route("/")
def home():
    html = '''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Infinito IA</title>
<style>
body{font-family:Arial;background:#0f0f0f;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh}
#top{padding:15px;text-align:center;background:#000;border-bottom:1px solid #222;font-weight:bold}
#chat{flex:1;overflow:auto;padding:15px;display:flex;flex-direction:column;gap:10px}
.u{background:#7c3aed;align-self:flex-end;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:85%}
.b{background:#1f1f1f;align-self:flex-start;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:85%;border:1px solid #333;white-space:pre-wrap}
#bar{display:flex;padding:12px;background:#000;gap:8px}
input{flex:1;padding:14px 18px;border-radius:30px;border:1px solid #333;background:#1f1f1f;color:#fff;outline:none}
button{padding:14px 22px;border-radius:30px;border:none;background:#fff;color:#000;font-weight:bold}
</style></head><body>
<div id="top">INFINITO IA - Seu Gemini Pessoal</div>
<div id="chat"><div class="b">Ola! Eu sou o Infinito IA! Igual ao Gemini, posso ajudar com tudo. O que quer fazer hoje?</div></div>
<div id="bar"><input id="inp" placeholder="Pergunte qualquer coisa..."><button onclick="send()">Enviar</button></div>
<script>
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
</script></body></html>
'''
    return html

@app.route("/chat", methods=["POST"])
def chat():
    try:
        msg = request.get_json().get("message","")
        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content": SYSTEM},{"role":"user","content": msg}],
            max_tokens=1000
        )
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        try:
            comp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role":"system","content": SYSTEM},{"role":"user","content": msg}],
                max_tokens=1000
            )
            return jsonify({"reply": comp.choices[0].message.content})
        except Exception as e2:
            return jsonify({"reply": "Erro: " + str(e2)[:300]})

if __name__ == "__main__":
    app.run()
