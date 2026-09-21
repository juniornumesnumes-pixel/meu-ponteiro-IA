import os,requests,time
from flask import Flask,request,jsonify
from flask_cors import CORS
from collections import defaultdict
app=Flask(__name__)
CORS(app)
GROQ_KEY=os.environ.get("GROQ_KEY")
uso=defaultdict(list)
@app.route("/chat")
def chat():
 ip=request.remote_addr
 agora=time.time()
 uso[ip]=[t for t in uso[ip] if agora-t<60]
 if len(uso[ip])>=15:
  return jsonify({"r":"Calma! Espera 1 min."})
 uso[ip].append(agora)
 q=request.args.get("q","Ola")
 if not GROQ_KEY:
  return jsonify({"r":"Falta chave"})
 try:
  r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},json={"model":"llama-3.1-8b-instant","messages":[{"role":"user","content":q}],"max_tokens":400},timeout=20)
  txt=r.json()["choices"][0]["message"]["content"]
  return jsonify({"r":txt})
 except Exception as e:
  return jsonify({"r":f"Erro: {e}"})
@app.route("/")
def home():
 return "Porteiro ON"
if __name__=="__main__":
 app.run(host="0.0.0.0",port=8000)
