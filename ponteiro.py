CORRIGIR TODOS OS ERROS DE SINTAXE DO ponteiro.py

O Render ainda está falhando ao iniciar o aplicativo.

Erro atual:

File "/opt/render/project/src/ponteiro.py", line 36
    ↓
    ^
SyntaxError: invalid character '↓' (U+2193)

IMPORTANTE:
O problema não está somente na linha 36.

O arquivo provavelmente contém vários caracteres ou trechos de fluxograma que foram inseridos como se fossem código Python.

ANTES DE ALTERAR:
Leia o arquivo `ponteiro.py` COMPLETO.

Faça uma revisão de todo o arquivo procurando qualquer conteúdo que não seja código Python válido.

REMOVER:
- setas "↓", "↑", "→", "←";
- fluxogramas;
- textos explicativos que estejam fora de comentários ou strings;
- instruções de arquitetura que foram inseridas diretamente no código;
- caracteres soltos que causariam SyntaxError.

NÃO remover caracteres que estejam corretamente dentro de strings Python e façam parte do funcionamento do aplicativo.

MUITO IMPORTANTE:
Não faça uma simples substituição cega de todos os caracteres.

Identifique quais linhas são código inválido e remova somente essas linhas.

PRESERVAR COMPLETAMENTE:
- Flask;
- `app = Flask(__name__)`;
- cliente Groq;
- variável `GROQ_KEY`;
- endpoint `/`;
- endpoint `/chat`;
- HTML atual;
- JavaScript atual;
- sistema atual de envio de mensagens;
- sistema atual de resposta da IA;
- tratamento de erros existente;
- todas as funcionalidades que estavam funcionando antes.

NÃO implementar neste momento:
- pesquisa na internet;
- novas APIs;
- busca web;
- voz;
- imagens;
- histórico;
- novas funcionalidades.

OBJETIVO ÚNICO:
Fazer o `ponteiro.py` voltar a ser um arquivo Python válido e fazer:

gunicorn ponteiro:app

conseguir importar:

app

CORREÇÃO:

Depois de limpar o arquivo, verifique se não existe mais nenhum caractere ou trecho fora da sintaxe Python.

Faça uma validação completa de sintaxe do arquivo antes de finalizar.

Se tiver acesso ao terminal do projeto, execute uma validação equivalente a:

python -m py_compile ponteiro.py

Se houver erro, corrija-o antes de finalizar.

IMPORTANTE:
Não reescreva o projeto inteiro.
Não substitua o código por um exemplo novo.
Não crie um aplicativo diferente.

Apenas corrija o arquivo existente.

NO FINAL informe:
1. quais linhas inválidas foram removidas/corrigidas;
2. se existem outros erros de sintaxe;
3. se `python -m py_compile ponteiro.py` passou;
4. se `gunicorn ponteiro:app` deverá conseguir iniciar.

NÃO faça nenhuma outra melhoria nesta etapa.
