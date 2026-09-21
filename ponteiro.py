from flask import Flask, request, jsonify
import os
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_KEY"))

@app.route("/")
def home():
    return """
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:Arial;background:#111;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh}
#chat{flex:1;overflow:auto;padding:15px}
.u{background:#0066ff;margin:10px 0 10px auto;padding:10px 14px;border-radius:15px;max-width:80%;text-align:right}
.b{background:#222;margin:10px auto 10px 0;padding:10px 14px;border-radius:15px;max-width:80%}
#bar{display:flex;padding:10px;background:#000}
input{flex:1;padding:12px;border-radius:20px;border:none;font-size:16px}
button{margin-left:8px;padding:12px 18px;border-radius:20px;border:none;background:#00e676;color:#000;font-weight:bold}
</style></head>
<body>
<div id="chat"><div class="b">🏢 Olá! Sou o Porteiro IA. Como posso ajudar?</div></div>
<div id="bar"><input id="inp" placeholder="Digite aqui..."><button onclick="send()">ENVIAR</button></div>
<script>
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="u">${t}</div>`; i.value='';
 try{
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
  let d=await r.json(); c.innerHTML+=`<div class="b">${d.reply}</div>`;
 }catch(e){c.innerHTML+=`<div class="b">Erro de conexão</div>`}
 c.scrollTop=c.scrollHeight;
}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script>
</body></html>
"""

@app.route("/chat", methods=["POST"])
def chat():
    try:
        msg = request.get_json().get("message","")
        comp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":"Você é o Porteiro IA, simpático, prestativo, fale em pt-br curto"},{"role":"user","content":msg}],
            max_tokens=400
        )
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Erro: {str(e)[:300]}"})

if __name__ == "__main__":
    app.run()
