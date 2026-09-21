from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
import pytz

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_KEY"))

FUSOS = {
    "Bacabal / Brasil": "America/Sao_Paulo",
    "Nova York / EUA": "America/New_York",
    "Londres / UK": "Europe/London",
    "Tóquio / Japão": "Asia/Tokyo",
    "Dubai": "Asia/Dubai",
    "Lisboa": "Europe/Lisbon"
}

def get_relogio():
    txt = ""
    for nome, fuso in FUSOS.items():
        agora = datetime.now(pytz.timezone(fuso))
        txt += f"{nome}: {agora.strftime('%H:%M:%S %d/%m')}\n"
    return txt

@app.route("/")
def home():
    return '''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;font-family:Arial;background:#0f0f0f;color:#fff;height:100vh;display:flex;flex-direction:column}
#top{background:#000;padding:12px;text-align:center;font-weight:bold;border-bottom:1px solid #222}
#tabs{display:flex;background:#000;border-bottom:1px solid #222}
.tab{flex:1;padding:12px;text-align:center;cursor:pointer;opacity:0.6}
.tab.active{opacity:1;border-bottom:2px solid #7c3aed;font-weight:bold}
#chat,#jogos,#relogioPage{flex:1;overflow:auto;padding:15px;display:none;flex-direction:column;gap:10px}
#chat.active,#jogos.active,#relogioPage.active{display:flex}
.u{background:#7c3aed;align-self:flex-end;padding:10px 14px;border-radius:18px 18px 4px 18px;max-width:80%}
.b{background:#1f1f1f;align-self:flex-start;padding:10px 14px;border-radius:18px 18px 4px 18px;max-width:80%;border:1px solid #333;white-space:pre-wrap}
#bar{display:flex;padding:10px;background:#000;gap:8px}
input{flex:1;padding:12px 16px;border-radius:25px;border:1px solid #333;background:#1f1f1f;color:#fff}
button{padding:12px 16px;border-radius:25px;border:none;background:#fff;color:#000;font-weight:bold}
.game-card{background:#1f1f1f;border:1px solid #333;padding:15px;border-radius:15px;text-align:center}
.game-card button{width:100%;margin-top:10px;background:#7c3aed;color:#fff}
canvas{background:#000;border-radius:10px;margin:auto;display:block}
.grid{display:grid;grid-template-columns:repeat(3,80px);gap:5px;justify-content:center}
.cell{width:80px;height:80px;background:#222;display:flex;align-items:center;justify-content:center;font-size:32px;cursor:pointer;border-radius:8px}
</style></head><body>
<div id="top">INFINITO IA - Chat + Jogos + Relogio</div>
<div id="tabs"><div class="tab active" onclick="showTab('chat')">Chat IA</div><div class="tab" onclick="showTab('jogos')">Jogos</div><div class="tab" onclick="showTab('relogioPage')">Relogio</div></div>

<div id="chat" class="active"><div class="b">Ola! Sou o Infinito IA! Aqui voce tem chat igual Gemini + Jogos + Relogio Mundial!</div></div>

<div id="jogos">
  <div class="game-card"><h3>⭕ Jogo da Velha</h3><div id="velha" class="grid"></div><button onclick="initVelha()">Reiniciar</button><p id="velhaMsg"></p></div>
  <div class="game-card"><h3>🐍 Snake</h3><canvas id="snake" width="300" height="300"></canvas><button onclick="initSnake()">Jogar Snake</button><p>Use as setas do teclado ou deslize</p></div>
  <div class="game-card"><h3>🧠 Jogo da Memoria</h3><div id="memoria" style="display:grid;grid-template-columns:repeat(4,70px);gap:8px;justify-content:center"></div><button onclick="initMemoria()">Novo Jogo</button></div>
  <div class="game-card"><h3>🎯 Adivinhe o Numero</h3><p>Estou pensando em um numero de 1 a 100</p><input id="guessInput" type="number" placeholder="Seu palpite"><button onclick="checkGuess()">Chutar</button><p id="guessMsg"></p></div>
</div>

<div id="relogioPage"><div id="clockList" style="display:flex;flex-direction:column;gap:10px"></div><button onclick="loadClocks()" style="margin-top:15px">Atualizar Horarios</button></div>

<div id="bar"><input id="inp" placeholder="Pergunte qualquer coisa..."><button onclick="send()">Enviar</button></div>

<script>
function showTab(t){
 document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
 document.querySelectorAll('#chat,#jogos,#relogioPage').forEach(e=>e.classList.remove('active'));
 event.target.classList.add('active');
 document.getElementById(t).classList.add('active');
 if(t=='relogioPage')loadClocks();
}
async function send(){
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="u">${t}</div>`; i.value=''; c.scrollTop=c.scrollHeight;
 try{let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let d=await r.json();c.innerHTML+=`<div class="b">${d.reply}</div>`;}catch(e){c.innerHTML+=`<div class="b">Erro</div>`}c.scrollTop=c.scrollHeight;
}
async function loadClocks(){
 let r=await fetch('/horario'); let d=await r.json();
 let html=''; for(let k in d.tudo){html+=`<div class="game-card">${k}: <b>${d.tudo[k]}</b></div>`}
 document.getElementById('clockList').innerHTML=html;
}
// JOGO DA VELHA
let velhaBoard, velhaTurn;
function initVelha(){velhaBoard=Array(9).fill('');velhaTurn='X';document.getElementById('velhaMsg').innerText='Vez do X';renderVelha()}
function renderVelha(){let g=document.getElementById('velha');g.innerHTML='';velhaBoard.forEach((v,i)=>{let d=document.createElement('div');d.className='cell';d.innerText=v;d.onclick=()=>{if(velhaBoard[i]==''&&!checkWin()){velhaBoard[i]=velhaTurn;velhaTurn=velhaTurn=='X'?'O':'X';renderVelha();let w=checkWin();if(w)document.getElementById('velhaMsg').innerText=w=='E'?'Empate!':`Vencedor: ${w}`;else document.getElementById('velhaMsg').innerText=`Vez do ${velhaTurn}`}};g.appendChild(d)})}
function checkWin(){let c=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];for(let [a,b,c2] of c){if(velhaBoard[a]&&velhaBoard[a]==velhaBoard[b]&&velhaBoard[a]==velhaBoard[c2])return velhaBoard[a]}return velhaBoard.includes('')?null:'E'}
// ADIVINHA
let secret=Math.floor(Math.random()*100)+1;
function checkGuess(){let g=parseInt(document.getElementById('guessInput').value);let m=document.getElementById('guessMsg');if(g==secret){m.innerText='ACERTOU! Era '+secret;secret=Math.floor(Math.random()*100)+1}else if(g<secret)m.innerText='Maior!';else m.innerText='Menor!';}
// MEMORIA
let memEmojis=['🍎','🍎','🚀','🚀','⚽','🎮','🎮','🐶','🐶','🍕','🍕','🌟','🌟','🎧','🎧'];
function initMemoria(){memEmojis.sort(()=>Math.random()-0.5);let g=document.getElementById('memoria');g.innerHTML='';let opened=[];memEmojis.forEach((e,i)=>{let d=document.createElement('div');d.style.cssText='width:70px;height:70px;background:#222;display:flex;align-items:center;justify-content:center;font-size:30px;border-radius:8px;cursor:pointer';d.innerText='?';d.onclick=()=>{if(opened.length<2&&d.innerText=='?'){d.innerText=e;opened.push({d,e});if(opened.length==2){setTimeout(()=>{if(opened[0].e!=opened[1].e){opened[0].d.innerText='?';opened[1].d.innerText='?';}opened=[]},800)}}};g.appendChild(d)})}
// SNAKE SIMPLES
let snakeCanvas=document.getElementById('snake'), sCtx=snakeCanvas.getContext('2d'), snake, dir, food, loop;
function initSnake(){snake=[{x:10,y:10}];dir={x:1,y:0};food={x:15,y:10};if(loop)clearInterval(loop);loop=setInterval(drawSnake,120)}
function drawSnake(){let head={x:snake[0].x+dir.x,y:snake[0].y+dir.y};if(head.x<0)head.x=19;if(head.x>19)head.x=0;if(head.y<0)head.y=19;if(head.y>19)head.y=0;if(snake.some(s=>s.x==head.x&&s.y==head.y)){clearInterval(loop);return}snake.unshift(head);if(head.x==food.x&&head.y==food.y)food={x:Math.floor(Math.random()*20),y:Math.floor(Math.random()*20)};else snake.pop();sCtx.fillStyle='#000';sCtx.fillRect(0,0,300,300);sCtx.fillStyle='#7c3aed';snake.forEach(s=>sCtx.fillRect(s.x*15,s.y*15,14,14));sCtx.fillStyle='#00e676';sCtx.fillRect(food.x*15,food.y*15,14,14)}
document.addEventListener('keydown',e=>{if(e.key=='ArrowUp'&&dir.y==0)dir={x:0,y:-1};if(e.key=='ArrowDown'&&dir.y==0)dir={x:0,y:1};if(e.key=='ArrowLeft'&&dir.x==0)dir={x:-1,y:0};if(e.key=='ArrowRight'&&dir.x==0)dir={x:1,y:0}});
document.getElementById('inp').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
initVelha(); initMemoria();
</script></body></html>
    '''

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
        sys=f"Voce e o INFINITO IA com jogos e relogio mundial.\nHORARIOS ATUAIS:\n{relogios}\nResponda sobre tudo, PT-BR."
        comp=client.chat.completions.create(model="openai/gpt-oss-20b",messages=[{"role":"system","content":sys},{"role":"user","content":msg}],max_tokens=1000)
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        try:
            comp=client.chat.completions.create(model="llama-3.1-8b-instant",messages=[{"role":"system","content":sys},{"role":"user","content":msg}],max_tokens=1000)
            return jsonify({"reply": comp.choices[0].message.content})
        except Exception as e2:
            return jsonify({"reply":"Erro: "+str(e2)[:200]})

if __name__=="__main__":
    app.run()
