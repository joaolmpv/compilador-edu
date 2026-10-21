# Software Educacional de Compiladores

Aplicação web educacional para visualização interativa das fases de
análise léxica e sintática de compiladores, voltada a estudantes de
graduação em Ciência da Computação.

## Linguagem e escopo

- **Linguagem analisada:** Python.
- **Por quê:** sintaxe simples e baixa barreira de entrada, permitindo
  que o aluno concentre esforço nos conceitos de compilação em vez da
  complexidade sintática da linguagem.
- **Subconjunto previsto:**
  - declaração e inicialização de variáveis (`numero = 10`)
  - operadores aritméticos (`+`, `-`, `*`, `/`)
  - estruturas condicionais (`if` / `else`)

  Esse recorte evita tentar cobrir a linguagem Python inteira de uma só
  vez, mantendo o projeto viável dentro do prazo da disciplina.

## Status do projeto

- **Etapa 1 (concluída):** estrutura do projeto, repositório GitHub e
  ambiente Docker, com um "Hello, World!" de ponta a ponta.
- **Etapa 2 (esta etapa):** interface web funcional, entrada e edição
  de código-fonte, exemplos prontos, comunicação real entre frontend e
  backend, validações de entrada, mensagens de erro e testes
  automatizados cobrindo os comportamentos acima.
  **Ainda não há** análise léxica, sintática ou semântica — isso será
  implementado nas próximas etapas.

## Arquitetura

```
compilador-edu/
├── backend/              # API em Python (Flask)
│   ├── app.py
│   ├── test_app.py        # testes automatizados (pytest)
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile
├── frontend/              # Interface web estática (HTML/CSS/JS servido via Nginx)
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   ├── script.test.js     # testes automatizados (node --test + jsdom)
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
├── docs/
│   └── testes.md           # registro das execuções de teste
├── docker-compose.yml
└── .gitignore
```

## Interface web (Etapa 2)

A tela principal (`frontend/index.html`) contém:

- **Identificação do sistema:** nome do software e a linguagem
  analisada (Python), com o subconjunto suportado.
- **Seletor de exemplos:** lista suspensa com 3 programas prontos (ver
  seção "Exemplos disponíveis").
- **Área de entrada de código:** campo de texto monoespaçado onde o
  usuário escreve, cola ou edita um programa.
- **Botão "Analisar código":** envia o conteúdo da área de código ao
  backend.
- **Área de resultados:** exibe mensagens de validação, sucesso ou erro
  retornadas pela aplicação.

Selecionar um exemplo substitui o conteúdo da área de código, que
continua totalmente editável depois disso.

## Exemplos disponíveis

| Exemplo | Construção demonstrada | Código |
|---|---|---|
| 1 | Declaração e inicialização de variável | `numero = 10` |
| 2 | Operação aritmética | `resultado = 10 + 5` |
| 3 | Estrutura condicional | `if numero > 0:` / `    numero = numero + 1` |

## Comunicação entre frontend e backend

O frontend chama sempre o caminho relativo `/api/analisar`. Dentro do
Docker Compose, o Nginx do frontend faz *proxy* dessas chamadas para o
contêiner do backend (`http://backend:5000/api/analisar`), evitando
depender de um endereço (`localhost`) que só existe no navegador do
usuário, e não dentro da rede do Docker.

**Requisição** (`POST /api/analisar`):

```json
{ "codigo": "numero = 10" }
```

**Resposta de sucesso** (`200`):

```json
{ "mensagem": "Código recebido com sucesso.", "recebido": true }
```

**Resposta de erro** (`400`), por exemplo com entrada vazia:

```json
{ "mensagem": "Informe um código-fonte antes de solicitar a análise.", "recebido": false }
```

Nesta etapa, o backend **recebe e valida** o código, mas ainda não
executa nenhuma análise léxica, sintática ou semântica.

## Validações e mensagens de erro

| Situação | Onde é tratada | Mensagem |
|---|---|---|
| Entrada vazia | Frontend (antes de enviar) e backend | "Informe um código-fonte antes de solicitar a análise." |
| Entrada apenas com espaços/quebras de linha | Frontend e backend | mesma mensagem acima |
| Campo `codigo` ausente ou de tipo inválido | Backend | "Campo 'codigo' é obrigatório." / "Campo 'codigo' deve ser uma string." |
| Requisição que não é um JSON válido | Backend | "Requisição inválida. Envie um JSON com o campo 'codigo'." |
| Falha de comunicação com o servidor | Frontend | "Não foi possível comunicar com o servidor. Verifique a conexão e tente novamente." |
| Erro inesperado no servidor | Backend | "Ocorreu um erro inesperado no servidor. Tente novamente." (sem detalhes internos) |

O frontend valida a entrada antes de enviar (evitando uma chamada de
rede desnecessária), mas o backend **sempre** revalida, já que a
interface não é a única forma de acessar a API.

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) versão 24 ou superior
- Docker Compose v2 (já incluso no Docker Desktop e no Docker Engine
  recentes — verifique com `docker compose version`)

## Como executar

Na raiz do repositório:

```bash
docker compose up --build
```

- Frontend: <http://localhost:8080>
- Backend (healthcheck): <http://localhost:5000/api/health>

Os dois serviços possuem *healthcheck* configurado; `docker compose ps`
deve mostrar ambos como `healthy` depois de alguns segundos.

## Como encerrar

```bash
docker compose down
```

## Testes automatizados

### Backend (pytest)

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
```

Cobre as rotas `/api/hello` e `/api/health` (regressão da Etapa 1), a
nova rota `/api/analisar` (casos válidos e todos os casos de erro),
rota inexistente, método não permitido e tratamento de erro inesperado
sem exposição de detalhes internos.

### Frontend (Node.js + jsdom)

```bash
cd frontend
npm install
npm test
```

Cobre a lógica de validação e interpretação de respostas, a presença
dos elementos exigidos na tela, a seleção de exemplos e o fluxo
completo do botão "Analisar" (sucesso, erro retornado pelo backend e
falha de comunicação), com o `fetch` simulado.

Os resultados detalhados de cada execução estão registrados em
[`docs/testes.md`](docs/testes.md).

## Validação de instalação limpa

Para reproduzir o ambiente do zero (como um avaliador faria):

```bash
git clone <url-do-repositorio>
cd compilador-edu
docker compose up --build
```

Depois de alguns segundos, acessar <http://localhost:8080> deve exibir
a tela do software educacional, já identificando a linguagem (Python).
Selecionar um exemplo, clicar em "Analisar código" e ver a mensagem
"Código recebido com sucesso." confirma que a comunicação entre
frontend e backend funciona de ponta a ponta.

## Limitações conhecidas (Etapa 2)

- Não há, ainda, análise léxica, sintática ou semântica: o backend
  apenas valida a entrada e confirma o recebimento.
- Não há realce de sintaxe, numeração de linhas ou autocompletar no
  editor de código (fora do escopo desta etapa).
- O teste de falha de comunicação no frontend usa um `fetch` simulado;
  não há ainda um teste automatizado de ponta a ponta contra o backend
  real em contêiner.
