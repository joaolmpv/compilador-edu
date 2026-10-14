# Software Educacional de Compiladores

Aplicação web educacional para visualização interativa das fases de
análise léxica e sintática de compiladores, voltada a estudantes de
graduação em Ciência da Computação.

## Linguagem e escopo

- **Linguagem analisada:** Python.
- **Por quê:** sintaxe simples e baixa barreira de entrada, permitindo
  que o aluno concentre esforço nos conceitos de compilação em vez da
  complexidade sintática da linguagem.
- **Subconjunto inicial:** nesta primeira etapa o subconjunto ainda não
  é analisado (o foco é a infraestrutura). Nas próximas etapas, o
  analisador léxico/sintático cobrirá inicialmente:
  - declaração de variáveis (`x = 10`)
  - operadores aritméticos (`+`, `-`, `*`, `/`)
  - estruturas condicionais (`if` / `else`)

  Esse recorte evita tentar cobrir a linguagem Python inteira de uma só
  vez, mantendo o projeto viável dentro do prazo da disciplina.

## Arquitetura

```
compilador-edu/
├── backend/        # API em Python (Flask)
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/        # Interface web estática (HTML/CSS/JS servido via Nginx)
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   ├── nginx.conf
│   └── Dockerfile
└── docker-compose.yml
```

O frontend consome a rota `/api/hello` do backend e exibe a mensagem
"Hello, World!" na tela, confirmando que a comunicação entre os dois
serviços funciona de ponta a ponta.

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

## Como encerrar

```bash
docker compose down
```

## Validação de instalação limpa

Para reproduzir o ambiente do zero (como um avaliador faria):

```bash
git clone <url-do-repositorio>
cd compilador-edu
docker compose up --build
```

Depois de alguns segundos, acessar <http://localhost:8080> deve exibir
a mensagem "Hello, World!" vinda do backend.
