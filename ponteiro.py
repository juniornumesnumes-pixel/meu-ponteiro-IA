from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

client = Groq(
    api_key=os.environ.get("GROQ_KEY")
)


def obter_hora():
    return datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )


def precisa_pesquisa(texto):
    texto = texto.lower()

    palavras = [
        "hoje",
        "agora",
        "atualmente",
        "último",
        "última",
        "últimas",
        "ultimo",
        "ultima",
        "ultimas",
        "notícia",
        "notícias",
        "noticia",
        "noticias",
        "resultado",
        "placar",
        "jogo",
        "futebol",
        "preço",
        "preco",
        "cotação",
        "cotacao",
        "dólar",
        "dolar",
        "euro",
        "presidente",
        "eleição",
        "eleições",
        "eleicao",
        "eleicoes",
        "clima",
        "previsão",
        "previsao",
        "lançamento",
        "lancamento",
        "filme",
        "série",
        "serie",
        "pesquise",
        "pesquisar",
        "procure",
        "internet",
        "mundo",
        "quem é",
        "quem e"
    ]

    return any(
        palavra in texto
        for palavra in palavras
    )


def e_criativa(texto):
    texto = texto.lower()

    palavras = [
        "história",
        "historia",
        "conto",
        "roteiro",
        "personagem",
        "invente",
        "inventar",
        "crie uma história",
        "criar uma história",
        "poema",
        "poesia"
    ]

    return any(
        palavra in texto
        for palavra in palavras
    )


def criar_sistema():
    agora = obter_hora()

    return f"""
Você é o INFINITO IA, um assistente inteligente
em português do Brasil.

Data atual:
{agora.strftime("%d/%m/%Y")}

Hora atual:
{agora.strftime("%H:%M")}

REGRAS:

1. Responda sempre em português do Brasil.

2. Seja inteligente, claro e preciso.

3. Não invente fatos.

4. Para perguntas que dependem de informações
atuais, utilize a pesquisa na internet quando
ela estiver disponível.

5. Diferencie fatos confirmados de hipóteses.

6. Para perguntas difíceis, faça uma análise
cuidadosa e explique passo a passo.

7. Para matemática, faça os cálculos corretamente.

8. Para histórias e roteiros, seja criativo.

9. Não invente fontes ou links.

10. Se não souber algo, diga claramente.

11. Não diga que possui conhecimento infinito.

12. Responda diretamente à pergunta do usuário.
"""


@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>INFINITO IA</title>

<style>

body{
    font-family:Arial,sans-serif;
    background:#0f0f0f;
    color:#fff;
    margin:0;
    display:flex;
    flex-direction:column;
    height:100vh;
}

#top{
    padding:15px;
    text-align:center;
    background:#000;
    border-bottom:1px solid #222;
    font-weight:bold;
    color:#00e676;
}

#chat{
    flex:1;
    overflow-y:auto;
    padding:14px;
    display:flex;
    flex-direction:column;
    gap:10px;
}

.u{
    background:#7c3aed;
    align-self:flex-end;
    padding:11px 14px;
    border-radius:18px 18px 4px 18px;
    max-width:82%;
    white-space:pre-wrap;
    line-height:1.5;
}

.b{
    background:#1f1f1f;
    align-self:flex-start;
    padding:11px 14px;
    border-radius:18px 18px 4px 18px;
    max-width:92%;
    border:1px solid #333;
    white-space:pre-wrap;
    line-height:1.5;
}

#bar{
    display:flex;
    padding:10px;
    background:#000;
    gap:8px;
}

input{
    flex:1;
    padding:14px 16px;
    border-radius:25px;
    border:1px solid #333;
    background:#1f1f1f;
    color:#fff;
    outline:none;
    font-size:16px;
}

button{
    padding:13px 19px;
    border-radius:25px;
    border:none;
    background:#00e676;
    color:#000;
    font-weight:bold;
    font-size:15px;
}

</style>

</head>

<body>

<div id="top">
INFINITO IA - Inteligência
</div>

<div id="chat">

<div class="b">
Olá! Eu sou o INFINITO IA.
Pergunte qualquer coisa.
</div>

</div>

<div id="bar">

<input
id="inp"
placeholder="Pergunte qualquer coisa..."
autocomplete="off">

<button onclick="send()">
Enviar
</button>

</div>

<script>

function addMessage(text, classe){

    const chat =
        document.getElementById("chat");

    const div =
        document.createElement("div");

    div.className = classe;

    div.textContent = text;

    chat.appendChild(div);

    chat.scrollTop =
        chat.scrollHeight;
}


async function send(){

    const input =
        document.getElementById("inp");

    const pergunta =
        input.value.trim();

    if(!pergunta){
        return;
    }

    addMessage(
        pergunta,
        "u"
    );

    input.value = "";

    addMessage(
        "Pensando...",
        "b"
    );

    try{

        const resposta =
            await fetch(
                "/chat",
                {
                    method:"POST",

                    headers:{
                        "Content-Type":
                        "application/json"
                    },

                    body:JSON.stringify({
                        message:pergunta
                    })
                }
            );


        const texto =
            await resposta.text();


        const mensagens =
            document.querySelectorAll(".b");


        if(mensagens.length > 0){

            mensagens[
                mensagens.length - 1
            ].remove();

        }


        let dados;


        try{

            dados =
                JSON.parse(texto);

        }
        catch(erro){

            addMessage(
                "ERRO DO SERVIDOR\\n\\n" +
                "HTTP: " +
                resposta.status +
                "\\n\\n" +
                texto.substring(0,1500),
                "b"
            );

            return;
        }


        if(!resposta.ok){

            addMessage(
                dados.reply ||
                "Erro HTTP " +
                resposta.status,
                "b"
            );

            return;
        }


        addMessage(
            dados.reply ||
            "Não recebi uma resposta.",
            "b"
        );

    }
    catch(erro){

        const mensagens =
            document.querySelectorAll(".b");


        if(mensagens.length > 0){

            mensagens[
                mensagens.length - 1
            ].remove();

        }


        addMessage(
            "ERRO DE CONEXÃO\\n\\n" +
            erro,
            "b"
        );
    }

    input.focus();
}


document
.getElementById("inp")
.addEventListener(
    "keypress",
    function(event){

        if(event.key === "Enter"){
            send();
        }

    }
);

</script>

</body>

</html>
'''


@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(
            silent=True
        ) or {}


        mensagem = str(
            data.get(
                "message",
                ""
            )
        ).strip()


        if not mensagem:

            return jsonify({
                "reply": "Digite uma pergunta."
            })


        sistema = criar_sistema()


        pesquisa = precisa_pesquisa(
            mensagem
        )


        criativa = e_criativa(
            mensagem
        )


        texto_lower = mensagem.lower()


        if any(x in texto_lower for x in [
            "300 linhas",
            "300 linha",
            "200 linhas",
            "100 linhas",
            "texto grande",
            "livro"
        ]):

            max_tokens = 6000

        elif criativa:

            max_tokens = 4000

        else:

            max_tokens = 3000


        if pesquisa and not criativa:

            resposta = client.chat.completions.create(

                model="openai/gpt-oss-20b",

                messages=[
                    {
                        "role": "system",
                        "content": sistema
                    },
                    {
                        "role": "user",
                        "content": mensagem
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

                stream=False
            )

        else:

            resposta = client.chat.completions.create(

                model="openai/gpt-oss-20b",

                messages=[
                    {
                        "role": "system",
                        "content": sistema
                    },
                    {
                        "role": "user",
                        "content": mensagem
                    }
                ],

                max_completion_tokens=max_tokens,

                temperature=0.7,

                stream=False
            )


        conteudo = (
            resposta.choices[0]
            .message.content
        )


        if not conteudo:

            conteudo = (
                "Não consegui gerar "
                "uma resposta."
            )


        return jsonify({
            "reply": conteudo
        })


    except Exception as erro:

        print(
            "================================"
        )

        print(
            "ERRO REAL DO INFINITO IA:"
        )

        print(
            repr(erro)
        )

        print(
            "================================"
        )


        return jsonify({
            "reply":
            "ERRO REAL DO SERVIDOR:\\n\\n"
            + repr(erro)
        }), 500


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    app.run(
        host="0.0.0.0",
        port=port
        )
