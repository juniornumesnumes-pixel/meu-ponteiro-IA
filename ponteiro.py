from flask import Flask, request, jsonify
import os
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_KEY"))

SYSTEM = """
Você é o INFINITO IA, uma inteligência artificial igual ao Gemini e ChatGPT, criada pelo usuário.
Você é super inteligente, criativo, prestativo, engraçado e fala PT-BR.
Você responde sobre TUDO: dever de casa, códigos, ideias, conselhos, textos, receitas, tudo.
Você nunca diz que é da Groq ou Meta. Você é o Infinito IA.
Respostas curtas quando precisa, longas quando precisa. Use emojis moderado.
"""

@app.route("/")
def home():
    return """
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Infinito IA - Igual Gemini</title>
<style>
body{font-family:Inter,Arial;background:#0f0f0f;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh}
#top{padding:15px;text-align:center;background:#000;border-bottom:1px solid #222;font-weight:bold;font-size:18px}
#chat{flex:1;overflow:auto;padding:15px;display:flex;flex-direction:column;gap:10px}
.u{background:linear-gradient(135deg,#7c3aed,#4f46e5);align-self:flex-end;padding:12px 16px;border-radius:20px 20px 4px 20px;max-width:85%}
.b{background:#1f1f1f;align-self:flex-start;padding:12px 16px;border-radius:20px 20px 4px;max-width:85%;border:1px solid #333;white-space:pre-wrap}
#bar{display:flex;padding:12px;background:#000;gap:8px}
input{flex:1;padding:14px 18px;border-radius:30px;border:1px solid #333;background:#1f1f1f;color:#fff;outline:none}
button{padding:14px 22px;border-radius:30px;border:none;background:#fff;color:#000;font-weight:bold;cursor:pointer}
</style></head><body>
<div id="top">✨ INFINITO IA - Seu Gemini Pessoal</div>
<div id="chat"><div class="b">Olá! Eu sou o Infinito IA 🚀\n\nSou igual ao Gemini, posso te ajudar com tudo:\n• Fazer dever de casa\n• Criar códigos\n• Escrever textos\n• Dar ideias\n• Tirar dúvidas\n\nO que você quer fazer hoje?</div></div>
<div id="bar"><input id="inp" placeholder="Pergunte qualquer coisa..."><button onclick="send()">➤</button></div>
<script>
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="u">${t}</div>`; i.value='';
 c.scrollTop=c.scrollHeight;
 try{
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
  let d=await r.json();
  c.innerHTML+=`<div class="b">${d.reply}</div>`;
 }catch(e){c.innerHTML+=`<div class="b">Erro de conexão, tente de novo</div>`}
 c.scrollTop=c.scrollHeight;
}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""

@app.route("/chat", methods=["POST"])
def chat():
    try:
        msg = request.get_json().get("message","")
        # Modelo mais inteligente da Groq
        comp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role":"system","content": SYSTEM},
                {"role":"user","content": msg}
            ],
            max_tokens=1000,
            temperature=0.7
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
            return jsonify({"reply": f"Erro: {str(e2)[:300]}"})

if __name__ == "__main__":
    app.run()
"""

**3. Clica em Commit changes**
**4. Vai no Render e espera 2 min**

Aí seu link `https://meu-ponteiro-ia.onrender.com` vai virar um **GEMINI CLONE** de verdade!

No Skit não precisa mexer, porque o WebViewer já abre o link e vai mostrar a cara nova automaticamente!

Testa e me fala! Agora ele vai responder qualquer coisa, igual Gemini mesmo!

Quer que eu coloque seu nome? Tipo "IA do [seu nome]"?
