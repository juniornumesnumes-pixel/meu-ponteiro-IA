from flask import Flask, request, jsonify
import os, requests, re, uuid
from groq import Groq
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_KEY"))

def pesquisa_real_google(pergunta):
    """PESQUISA DE VERDADE NA INTERNET - ACESSA GOOGLE/DDG"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resultados = []

        # 1. PESQUISA REAL NO DUCKDUCKGO LITE (funciona no Render)
        try:
            url = f"https://lite.duckduckgo.com/lite/?q={pergunta}"
            r = requests.get(url, headers=headers, timeout=8)
            soup = BeautifulSoup(r.text, 'html.parser')
            links = soup.find_all('a', limit=5)
            textos = soup.get_text()
            # Pega os primeiros 500 caracteres da pesquisa real
            if len(textos) > 100:
                resultados.append(f"PESQUISA DDG REAL: {textos[:800]}")
        except Exception as e:
            resultados.append(f"DDG erro: {e}")

        # 2. CLIMA REAL DE BACABAL
        if any(x in pergunta.lower() for x in ["clima","tempo","temperatura","bacabal"]):
            try:
                clima = requests.get("https://wttr.in/Bacabal?format=j1", timeout=5).json()
                curr = clima['current_condition'][0]
                resultados.append(f"CLIMA REAL BACABAL AGORA: {curr['weatherDesc'][0]['value']} - Temp {curr['temp_C']}C - Sensacao {curr['FeelsLikeC']}C - Umidade {curr['humidity']}% - Vento {curr['windspeedKmph']}km/h")
            except:
                try:
                    clima2 = requests.get("https://wttr.in/Bacabal?format=%C+%t+%w+%h", timeout=4).text
                    resultados.append(f"CLIMA REAL: {clima2}")
                except: pass

        # 3. FUTEBOL - busca real
        if any(x in pergunta.lower() for x in ["palmeiras","flamengo","vasco","jogo","brasileirao","placar"]):
            try:
                # Busca real no google de futebol
                q = pergunta + " resultado hoje"
                url2 = f"https://lite.duckduckgo.com/lite/?q={q}"
                r2 = requests.get(url2, headers=headers, timeout=6)
                soup2 = BeautifulSoup(r2.text, 'html.parser')
                texto2 = soup2.get_text()[:1000]
                resultados.append(f"FUTEBOL PESQUISA REAL: {texto2}")
            except: pass

        # 4. WIKIPEDIA REAL
        try:
            wiki_url = f"https://pt.wikipedia.org/w/api.php?action=opensearch&search={pergunta}&limit=2&format=json"
            w = requests.get(wiki_url, timeout=5).json()
            if len(w) > 2 and w[2]:
                resultados.append(f"WIKIPEDIA REAL: {w[2][0]}")
        except: pass

        if resultados:
            return "\n\n".join(resultados)
        else:
            return "Pesquisa real não retornou, use conhecimento mas avise que internet falhou"
    except Exception as e:
        return f"Erro pesquisa real: {e}"

@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>INFINITO IA - Internet Real</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial; background:#000; color:#fff; height:100vh; display:flex; flex-direction:column}
#header{background:#111; border-bottom:2px solid #00e676; padding:12px 16px; display:flex; justify-content:space-between; align-items:center}
#header h1{color:#00e676; font-size:14px} #live{font-size:10px; background:#00e676; color:#000; padding:4px 8px; border-radius:12px; font-weight:bold; animation:blink 1s infinite}
@keyframes blink{0%{opacity:1} 50%{opacity:0.5}}
#chat{flex:1; overflow:auto; padding:16px; display:flex; flex-direction:column; gap:12px}
.msg{padding:12px 16px; border-radius:16px; max-width:88%; white-space:pre-wrap; font-size:14px; line-height:1.4}
.user{align-self:flex-end; background:#7c3aed}
.bot{align-self:flex-start; background:#1e1e1e; border:1px solid #333}
.internet{font-size:11px; color:#00e676; border:1px solid #00e676; padding:2px 6px; border-radius:8px; margin-bottom:6px; display:inline-block}
#bar{background:#111; padding:12px; display:flex; justify-content:center; border-top:1px solid #222}
#wrap{display:flex; max-width:900px; width:100%; background:#1e1e1e; border-radius:24px; padding:6px 6px 6px 16px; border:1px solid #333}
#inp{flex:1; background:transparent; border:none; color:#fff; outline:none}
#send{background:#00e676; border:none; padding:10px 18px; border-radius:20px; font-weight:bold}
</style></head><body>
<div id="header"><h1>INFINITO IA • PRO</h1><div id="live">🌐 INTERNET REAL ATIVA</div></div>
<div id="chat"><div class="msg bot"><span class="internet">🌐 INTERNET LIBERADA</span><br>Agora eu pesquiso de VERDADE na internet!<br><br>Teste: "clima de Bacabal agora" ou "jogo do Palmeiras ontem" - vou buscar na hora na internet real!<br><br>Qual seu nome?</div></div>
<div id="bar"><div id="wrap"><input id="inp" placeholder="Pergunte e vou pesquisar na internet de verdade..."><button id="send" onclick="send()">ENVIAR</button></div></div>
<script>
let UID = localStorage.getItem('uid_infinito') || 'u_'+Math.random().toString(36).slice(2);
localStorage.setItem('uid_infinito', UID);
let hist = JSON.parse(localStorage.getItem('hist_'+UID)||'[]');
let chat=document.getElementById('chat');
function render(){
 if(hist.length===0) return;
 chat.innerHTML=''; hist.forEach(m=>{
   chat.innerHTML+=`<div class="msg ${m.role==='user'?'user':'bot'}">${m.content.replace(/</g,'&lt;')}</div>`;
 }); chat.scrollTop=chat.scrollHeight;
}
if(hist.length>0) render();
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t) return;
 hist.push({role:'user',content:t}); localStorage.setItem('hist_'+UID,JSON.stringify(hist)); render(); i.value='';
 chat.innerHTML+=`<div class="msg bot">🌐 <i>Pesquisando na internet de verdade... acessando Google, clima, futebol...</i></div>`;
 chat.scrollTop=chat.scrollHeight;
 try{
   let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json','X-User-ID':UID},body:JSON.stringify({messages:hist})});
   let d=await r.json(); document.querySelector('.msg:last-child').remove();
   hist.push({role:'assistant',content:d.reply}); localStorage.setItem('hist_'+UID,JSON.stringify(hist)); render();
 }catch(e){ chat.innerHTML+=`<div class="msg bot">Erro na internet</div>` }
}
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
'''

@app.route("/chat", methods=["POST"])
def chat():
    user_id = request.headers.get('X-User-ID','anon')
    data = request.get_json()
    msgs = data.get("messages",[])
    pergunta = msgs[-1]["content"] if msgs else ""

    # SEMPRE PESQUISA SE FOR PERGUNTA QUE PRECISA DE INTERNET
    precisa = any(x in pergunta.lower() for x in ["clima","tempo","jogo","palmeiras","flamengo","vasco","hoje","ontem","resultado","placar","quando","noticia","previsao","temperatura","quem ganhou"])

    dados_reais = ""
    if precisa:
        dados_reais = pesquisa_real_google(pergunta)

    agora = datetime.now(pytz.timezone("America/Sao_Paulo"))
    nome = ""
    for m in msgs:
        if "meu nome e" in m["content"].lower():
            try: nome = m["content"].lower().split("meu nome e")[-1].split()[0].capitalize()
            except: pass

    if precisa:
        sistema = f"""Você é INFINITO IA PRO com INTERNET REAL LIBERADA - Você ACABOU de pesquisar na internet de verdade!

        HORA REAL: {agora.strftime('%d/%m/%Y %H:%M')} America/Sao_Paulo
        PERGUNTA DO USUARIO: {pergunta}
        NOME: {nome}

        RESULTADOS REAIS DA PESQUISA NA INTERNET AGORA:
        {dados_reais}

        OBRIGAÇÃO:
        1. Use os DADOS REAIS da internet acima, são de verdade, acessou agora!
        2. Se tem clima real, informe o clima real com temperatura
        3. Se tem futebol, informe placar real
        4. Diga "Pesquisei na internet agora e achei..."
        5. Se pergunta curta, resposta curta com dado real. Se longa, explica.
        6. Você tem internet de verdade, não minta
        """
        max_tokens = 600
    else:
        sistema = f"""Você é INFINITO IA PRO com internet liberada.
        Data: {agora.strftime('%d/%m/%Y %H:%M')} Nome: {nome}
        Responda inteligente. Se for historia 300 linhas, escreva gigante. Se for curta, curta.
        Você tem acesso à internet quando precisar.
        """
        max_tokens = 3000 if "historia" in pergunta.lower() or "300" in pergunta.lower() else 800

    groq_msgs = [{"role":"system","content":sistema}]
    for m in msgs[-8:]:
        if m.get("role") in ["user","assistant"]:
            groq_msgs.append({"role":m["role"],"content":m["content"]})

    comp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=groq_msgs,
        max_tokens=max_tokens,
        temperature=0.4
    )
    return jsonify({"reply": comp.choices[0].message.content, "internet": dados_reais[:200]})

@app.route("/limpar", methods=["POST"])
def limpar():
    return jsonify({"ok":True})

if __name__ == "__main__":
    app.run()
