Quero evoluir o Porteiro IA para que ele consiga pesquisar informações atuais na internet antes de responder perguntas que dependem de informações em tempo real.

IMPORTANTE:
- Primeiro leia TODO o arquivo atual `ponteiro.py`.
- Preserve a estrutura existente.
- Não apague o sistema atual do Groq.
- Não remova o chat atual.
- Não altere o visual atual sem necessidade.
- Não crie respostas falsas para simular pesquisa.
- Não invente informações.
- O sistema deve realmente consultar a internet.

OBJETIVO:

Transformar o Porteiro IA em um sistema híbrido:

USUÁRIO
↓
PERGUNTA
↓
ANÁLISE DA PERGUNTA
↓
É necessário conhecimento atual?
↓
SIM → pesquisar na internet
↓
resultados da pesquisa
↓
Groq analisa os resultados
↓
resposta final
↓
mostrar fontes

Quando a pergunta não precisar de informações atuais, o Groq pode responder normalmente sem pesquisa.

EXEMPLOS QUE DEVEM ACIONAR PESQUISA:

- "Qual é a notícia de hoje?"
- "Quem ganhou o jogo de hoje?"
- "Qual é o preço atual do Bitcoin?"
- "Qual é a cotação do dólar agora?"
- "O que aconteceu hoje no Brasil?"
- "Qual é o clima agora?"
- "Quem é o atual presidente..."
- "Quais são os filmes lançados recentemente?"
- "Qual é a versão mais recente do Android?"
- "Pesquise sobre..."
- "O que aconteceu com..."
- "Qual é o preço atual de..."
- "Onde posso encontrar..."
- qualquer pergunta que claramente dependa de informação atual da internet.

PERGUNTAS QUE NÃO PRECISAM DE PESQUISA:

- matemática;
- explicações gerais;
- programação baseada em conhecimento geral;
- escrita de histórias;
- criação de textos;
- conversas normais;
- perguntas que possam ser respondidas com segurança pelo modelo sem informação atual.

==================================================
1. PESQUISA REAL NA INTERNET
==================================================

Adicionar ao backend um mecanismo REAL de pesquisa na internet.

Não usar dados simulados.

A chave da API de pesquisa deve ficar em variável de ambiente.

Exemplo:

SEARCH_API_KEY

NUNCA colocar a chave diretamente no código.

A implementação deve funcionar no servidor hospedado no Render.

==================================================
2. NOVA FUNÇÃO DE PESQUISA
==================================================

Criar uma função semelhante a:

search_web(query)

Ela deve:

1. receber a pergunta;
2. enviar a pesquisa para o serviço de busca;
3. receber os resultados;
4. extrair:
   - título;
   - URL;
   - trecho/resumo;
5. retornar os resultados para o sistema.

Limitar inicialmente a aproximadamente 5 a 8 resultados relevantes para não gastar recursos desnecessariamente.

==================================================
3. DECIDIR QUANDO PESQUISAR
==================================================

Criar uma função semelhante a:

needs_web_search(message)

Ela deve determinar se a pergunta depende de informações atuais.

Não usar somente palavras-chave de forma rígida.

Sempre que possível, usar o próprio modelo para classificar se a pesquisa é necessária.

Por exemplo:

PERGUNTA:
"Quem é Albert Einstein?"

Pode responder sem pesquisa.

PERGUNTA:
"Quem é o atual presidente do Brasil?"

Pesquisar.

PERGUNTA:
"Qual é a notícia mais recente sobre inteligência artificial?"

Pesquisar.

PERGUNTA:
"Quanto é 25 x 30?"

Não pesquisar.

==================================================
4. GROQ + PESQUISA
==================================================

Quando houver pesquisa:

1. receber a pergunta do usuário;
2. pesquisar na internet;
3. pegar os resultados;
4. enviar os resultados junto com a pergunta para o Groq;
5. pedir ao Groq para produzir uma resposta clara usando as informações encontradas.

O prompt enviado ao Groq deve deixar claro:

"Você é o Porteiro IA.
Use os resultados da pesquisa como fonte para responder.
Não invente informações que não estejam nos resultados.
Se as fontes forem contraditórias, informe a divergência.
Se não houver informação suficiente, diga claramente que não foi possível confirmar.
Responda em português do Brasil.
Se a pergunta pedir informação atual, priorize os resultados mais recentes."

==================================================
5. FONTES
==================================================

Quando a resposta usar pesquisa da internet, mostrar as fontes abaixo da resposta.

Exemplo:

Resposta do Porteiro IA:

"O dólar está sendo cotado aproximadamente em ..."

Fontes:
• Banco Central
• Reuters
• Valor Econômico

Cada fonte deve ter o link real correspondente.

NÃO inventar URLs.

==================================================
6. INFORMAÇÕES ATUAIS
==================================================

O sistema deve conseguir pesquisar informações como:

- notícias;
- esportes;
- tecnologia;
- preços;
- produtos;
- empresas;
- pessoas públicas;
- acontecimentos recentes;
- lançamentos;
- atualizações de software;
- clima;
- informações públicas;
- documentação;
- programação;
- pesquisas;
- assuntos gerais.

==================================================
7. SEGURANÇA
==================================================

Nunca colocar:

GROQ_KEY
SEARCH_API_KEY

diretamente no HTML ou JavaScript do navegador.

As chaves devem permanecer somente no servidor.

Usar:

os.environ.get("GROQ_KEY")
os.environ.get("SEARCH_API_KEY")

ou a variável correspondente utilizada pelo serviço escolhido.

==================================================
8. ERROS
==================================================

Se a pesquisa falhar:

Não mostrar erro técnico para o usuário.

Mostrar algo como:

"Não consegui consultar a internet neste momento. Vou tentar responder usando meu conhecimento."

Se o Groq estiver funcionando, continuar a conversa.

Se a pesquisa não encontrar resultados:

"Não encontrei fontes suficientes para confirmar essa informação."

Não inventar uma resposta.

==================================================
9. VELOCIDADE
==================================================

Não pesquisar todas as perguntas.

Pesquisar somente quando necessário.

Evitar chamadas duplicadas.

Manter o chat rápido.

==================================================
10. INTERFACE
==================================================

Não modificar o design atual do chat neste momento.

Apenas adicionar as fontes abaixo das respostas que realmente utilizaram pesquisa.

==================================================
11. CONTEXTO
==================================================

Continuar usando o contexto da conversa quando apropriado.

Exemplo:

Usuário:
"Quem é Neymar?"

IA:
resposta.

Usuário:
"Onde ele joga atualmente?"

O sistema deve entender que "ele" se refere ao Neymar e pesquisar a informação atual.

==================================================
12. NÃO INVENTAR
==================================================

Esta regra é obrigatória:

Se a informação não estiver disponível ou não puder ser confirmada pelas fontes, NÃO inventar.

A IA deve admitir quando não sabe.

==================================================
13. ARQUITETURA
==================================================

Manter o endpoint atual `/chat`.

Não quebrar o frontend existente.

O frontend continuará enviando:

POST /chat

O backend continuará retornando JSON.

Se necessário, adicionar ao JSON algo como:

{
  "answer": "...",
  "sources": [
    {
      "title": "...",
      "url": "..."
    }
  ],
  "web_search": true
}

Quando não houver pesquisa:

{
  "answer": "...",
  "sources": [],
  "web_search": false
}

==================================================
14. ANTES DE ALTERAR
==================================================

Primeiro leia o `ponteiro.py` inteiro e entenda:

- Flask;
- endpoint `/`;
- endpoint `/chat`;
- cliente Groq;
- HTML;
- JavaScript;
- formato atual das mensagens.

Depois faça a implementação preservando o que já existe.

Não reescreva o projeto inteiro sem necessidade.

==================================================
15. RESULTADO ESPERADO
==================================================

Depois da implementação quero poder perguntar:

"Qual é a notícia mais recente sobre IA?"

E o Porteiro IA deve:

1. pesquisar na internet;
2. encontrar resultados reais;
3. analisar os resultados com Groq;
4. responder em português;
5. mostrar as fontes;
6. fornecer links reais.

Também quero poder perguntar:

"Quanto está o dólar hoje?"

e receber uma resposta baseada em uma consulta atual, em vez de uma resposta baseada somente no conhecimento antigo do modelo.

NO FINAL:

Informe exatamente:

1. quais arquivos foram alterados;
2. qual serviço de pesquisa foi utilizado;
3. qual variável de ambiente precisa ser adicionada no Render;
4. como testar a pesquisa;
5. um exemplo de pergunta que deve pesquisar;
6. um exemplo de pergunta que não deve pesquisar.

NÃO remova o Groq.
NÃO remova o chat.
NÃO crie dados falsos.
NÃO simule uma pesquisa.
A pesquisa precisa ser REAL.
