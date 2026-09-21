from flask import Flask, request, jsonify
import os
from groq import Groq
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

API_KEY = os.environ.get("GROQ_KEY")

client = Groq(
    api_key=API_KEY
)


# =========================================================
# PÁGINA DO CHAT
# =========================================================

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
    color:white;
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
    color:white;
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

button:active{
    transform:scale(.97);
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


        let dados = null;


        try{

            dados =
                JSON.parse(texto);

        }
        catch(erro){

            addMessage(
                "ERRO DO SERVIDOR\n\n" +
                "HTTP: " +
                resposta.status +
                "\n\n" +
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
            "ERRO DE CONEXÃO\n\n" +
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


# =========================================================
# DETECTA SE A PERGUNTA PODE PRECISAR DA INTERNET
# =========================================================

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
        "tempo",
        "previsão",
        "previsao",

        "lançamento",
        "lancamento",

        "filme",
        "série",
        "serie",

        "empresa",

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


# =========================================================
# DETECTA PERGUNTAS CRIATIVAS
# =========================================================

def pergunta_criativa(texto):

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
        "ficção",
        "poema",
        "poesia"
    ]

    return any(
        palavra in texto
        for palavra in palavras
    )


# =========================================================
# CHAMADA NORMAL DA GROQ
# =========================================================

def chamar_normal(mensagem, max_tokens):

    return client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role":"system",
                "content":SISTEMA
            },
            {
                "role":"user",
                "content":mensagem
            }
        ],

        max_completion_tokens=max_tokens,

        temperature=0.7,

        stream=False
    )


# =========================================================
# CHAMADA COM PESQUISA
# =========================================================

def chamar_pesquisa(mensagem):

    return client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role":"system",
                "content":SISTEMA
            },
            {
                "role":"user",
                "content":mensagem
            }
        ],

        tools=[
            {
                "type":"browser_search"
            }
        ],

        tool_choice="required",

        max_completion_tokens=4000,

        temperature=0.6,

        stream=False
    )


# =========================================================
# CHAT
# =========================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data =
            request.get_json(silent=True) or {}


        mensagem =
            str(
                data.get(
                    "message",
                    ""
                )
            ).strip()


        if not mensagem:

            return jsonify({
                "reply":
                "Digite uma pergunta."
            })


        agora = datetime.now(
            ZoneInfo("America/Sao_Paulo")
        )


        global SISTEMA


        SISTEMA = f"""

Você é o INFINITO IA,
um assistente de inteligência artificial
em português do Brasil.

Data atual:
{agora.strftime("%d/%m/%Y")}

Hora atual:
{agora.strftime("%H:%M")}

OBJETIVO:

Responder perguntas com inteligência,
clareza, precisão e bom raciocínio.

REGRAS:

1. Responda em português do Brasil.

2. Não invente fatos.

3. Quando a pergunta depender de informações
recentes, utilize a pesquisa na internet
quando ela estiver disponível.

4. Diferencie fatos de hipóteses.

5. Em perguntas difíceis, analise o problema
com cuidado antes de responder.

6. Explique de forma clara e organizada.

7. Não diga que possui conhecimento infinito.

8. Se não souber alguma coisa, seja honesto.

9. Para histórias e roteiros, seja criativo.

10. Não invente fontes ou links.

"""


        # =================================================
        # MODO DA PERGUNTA
        # =================================================

        pesquisa = precisa_pesquisa(
            mensagem
        )

        criativa = pergunta_criativa(
            mensagem
        )


        # =================================================
        # TEXTO LONGO
        # =================================================

        if any(x in mensagem.lower() for x in [

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


        # =================================================
        # TENTA PESQUISA
        # =================================================

        if pesquisa and not criativa:

            try:

                resposta =
                    chamar_pesquisa(
                        mensagem
                    )

            except Exception as erro_pesquisa:

                print(
                    "PESQUISA FALHOU:",
                    repr(erro_pesquisa)
                )


                # =========================================
                # FALLBACK
                # =========================================

                try:

                    resposta =
                        chamar_normal(
                            mensagem,
                            max_tokens
                        )

                except Exception as erro_normal:

                    raise Exception(
                        "Pesquisa falhou: "
                        + repr(erro_pesquisa)
                        + "\n\n"
                        "Resposta normal também falhou: "
                        + repr(erro_normal)
                    )


        else:

            resposta =
                chamar_normal(
                    mensagem,
                    max_tokens
                )


        # =================================================
        # PEGA RESPOSTA
        # =================================================

        conteudo =
            resposta.choices[0].message.content


        if not conteudo:

            conteudo =
                "Não consegui gerar uma resposta."


        return jsonify({
            "reply": conteudo
        })


    except Exception as erro:

        print(
            "================================"
        )

        print(
            "ERRO REAL:"
        )

        print(
            repr(erro)
        )

        print(
            "================================"
        )


        return jsonify({

            "reply":
            "ERRO REAL DO SERVIDOR:\n\n"
            + repr(erro)

        }), 500


# =========================================================
# INICIAR
# =========================================================

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
