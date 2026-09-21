from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
import pytz
import html

app = Flask(__name__)

client = Groq(
    api_key=os.environ.get("GROQ_KEY")
)

@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>INFINITO IA</title>

<style>
body{
    font-family:Arial;
    background:#0f0f0f;
    color:#fff;
    margin:0;
    display:flex;
    flex-direction:column;
    height:100vh
}

#top{
    padding:14px;
    text-align:center;
    background:#000;
    border-bottom:1px solid #222;
    font-weight:bold;
    color:#00e676
}

#chat{
    flex:1;
    overflow:auto;
    padding:14px;
    display:flex;
    flex-direction:column;
    gap:10px
}

.u{
    background:#7c3aed;
    align-self:flex-end;
    padding:10px 14px;
    border-radius:18px 18px 4px 18px;
    max-width:80%;
    white-space:pre-wrap;
    line-height:1.4
}

.b{
    background:#1f1f1f;
    align-self:flex-start;
    padding:10px 14px;
    border-radius:18px 18px 4px 18px;
    max-width:90%;
    border:1px solid #333;
    white-space:pre-wrap;
    line-height:1.5
}

#bar{
    display:flex;
    padding:10px;
    background:#000;
    gap:8px
}

input{
    flex:1;
    padding:13px 16px;
    border-radius:25px;
    border:1px solid #333;
    background:#1f1f1f;
    color:#fff;
    outline:none
}

button{
    padding:13px 18px;
    border-radius:25px;
    border:none;
    background:#00e676;
    color:#000;
    font-weight:bold
}
</style>
</head>

<body>

<div id="top">INFINITO IA - Inteligência em tempo real</div>

<div id="chat">
<div class="b">Olá! Eu sou o INFINITO IA. Posso pesquisar informações atuais na internet quando necessário.</div>
</div>

<div id="bar">
<input id="inp" placeholder="Pergunte qualquer coisa...">
<button onclick="send()">Enviar</button>
</div>

<script>

function addMessage(text, classe){
    let c = document.getElementById('chat');
    let div = document.createElement('div');
    div.className = classe;
    div.textContent = text;
    c.appendChild(div);
    c.scrollTop = c.scrollHeight;
}

async function send(){

    let i = document.getElementById('inp');
    let t = i.value.trim();

    if(!t) return;

    addMessage(t, 'u');
    i.value = '';

    addMessage('Pesquisando e preparando a resposta...', 'b');

    try{

        let r = await fetch('/chat',{
            method:'POST',
            headers:{
                'Content-Type':'application/json'
            },
            body:JSON.stringify({
                message:t
            })
        });

        let d = await r.json();

        let mensagens = document.querySelectorAll('.b');

        if(mensagens.length > 0){
            mensagens[mensagens.length - 1].remove();
        }

        addMessage(d.reply || 'Não consegui responder.', 'b');

    }catch(e){

        let mensagens = document.querySelectorAll('.b');

        if(mensagens.length > 0){
            mensagens[mensagens.length - 1].remove();
        }

        addMessage('Erro ao conectar com a inteligência. Tente novamente.', 'b');
    }

    i.focus();
}

document.getElementById('inp').addEventListener('keypress',function(e){
    if(e.key === 'Enter'){
        send();
    }
});

</script>

</body>
</html>
'''


def precisa_pesquisa(msg):

    texto = msg.lower()

    palavras = [
        "hoje",
        "agora",
        "atualmente",
        "2026",
        "últimas notícias",
        "ultimas noticias",
        "notícia",
        "noticias",
        "notícia de hoje",
        "noticias de hoje",
        "tempo",
        "clima",
        "previsão",
        "previsao",
        "placar",
        "jogo",
        "futebol",
        "resultado",
        "eleição",
        "eleicoes",
        "eleições",
        "presidente",
        "política",
        "politica",
        "preço",
        "preco",
        "cotação",
        "cotacao",
        "dólar",
        "dolar",
        "euro",
        "lançamento",
        "lancamento",
        "filme",
        "série",
        "serie",
        "empresa",
        "quem é",
        "quem e",
        "pesquise",
        "pesquisar",
        "procure",
        "internet",
        "mundo",
        "último",
        "ultima",
        "últimas",
        "ultimas"
    ]

    return any(p in texto for p in palavras)


@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json() or {}

        msg_original = str(data.get("message", "")).strip()

        if not msg_original:
            return jsonify({
                "reply": "Digite uma pergunta."
            })

        agora = datetime.now(
            pytz.timezone("America/Sao_Paulo")
        )

        pesquisa = precisa_pesquisa(msg_original)

        if len(msg_original.split()) > 20 and any(
            x in msg_original.lower()
            for x in [
                "história",
                "historia",
                "conto",
                "livro",
                "roteiro"
            ]
        ):
            modo = "CRIATIVO"

        elif any(
            x in msg_original.lower()
            for x in [
                "300 linhas",
                "300 linha",
                "200 linhas",
                "100 linhas",
                "texto grande"
            ]
        ):
            modo = "TEXTO_LONGO"

        else:
            modo = "NORMAL"


        sistema = f"""
Você é o INFINITO IA, um assistente inteligente em português do Brasil.

Data e hora atual:
{agora.strftime('%d/%m/%Y %H:%M')}

Seu objetivo é responder com precisão, clareza e naturalidade.

REGRAS:

1. Responda sempre em português do Brasil.

2. Nunca invente fatos.

3. Quando houver informação atualizada disponível pela pesquisa na internet,
use as informações encontradas para responder.

4. Quando utilizar pesquisa na internet, diferencie fatos atuais de
informações antigas.

5. Se a pergunta for sobre notícias, futebol, resultados, preços,
clima, acontecimentos recentes, pessoas públicas, empresas,
tecnologia ou qualquer assunto que possa ter mudado recentemente,
pesquise antes de responder.

6. Se a pergunta for criativa, como história, roteiro ou personagem,
não precisa pesquisar.

7. Não diga que possui conhecimento infinito.

8. Se não encontrar informação suficiente, diga claramente que não
encontrou informação suficiente.

9. Não invente fontes ou links.

10. Seja inteligente e explique o necessário sem ficar repetitivo.

MODO ATUAL:
{modo}

PESQUISA NA INTERNET:
{"ATIVADA" if pesquisa else "NÃO NECESSÁRIA"}
"""


        # ============================================
        # PERGUNTAS QUE PRECISAM DE INTERNET
        # ============================================

        if pesquisa:

            resposta = client.chat.completions.create(

                model="openai/gpt-oss-20b",

                messages=[
                    {
                        "role": "system",
                        "content": sistema
                    },
                    {
                        "role": "user",
                        "content": msg_original
                    }
                ],

                tools=[
                    {
                        "type": "browser_search"
                    }
                ],

                tool_choice="required",

                max_completion_tokens=4000,

                temperature=0.6,

                include_reasoning=False
            )

        else:

            # ============================================
            # PERGUNTAS NORMAIS / CRIATIVAS
            # ============================================

            if modo == "TEXTO_LONGO":

                max_tokens = 6000

            elif modo == "CRIATIVO":

                max_tokens = 4000

            else:

                max_tokens = 2000


            resposta = client.chat.completions.create(

                model="openai/gpt-oss-20b",

                messages=[
                    {
                        "role": "system",
                        "content": sistema
                    },
                    {
                        "role": "user",
                        "content": msg_original
                    }
                ],

                max_completion_tokens=max_tokens,

                temperature=0.7,

                include_reasoning=False
            )


        conteudo = resposta.choices[0].message.content

        if not conteudo:
            conteudo = "Não consegui gerar uma resposta."

        return jsonify({
            "reply": conteudo
        })


    except Exception as e:

        print("ERRO:", repr(e))

        return jsonify({
            "reply": "Ocorreu um erro ao consultar a inteligência. Tente novamente."
        }), 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
