# Registro de testes — Etapa 2

Este arquivo registra as execuções de teste realizadas durante o
desenvolvimento da Etapa 2 (interface web e entrada de código-fonte),
conforme recomendado no enunciado da atividade.

## Backend (pytest)

- **Módulo testado:** `backend/app.py` (rotas `/api/hello`, `/api/health`
  e `/api/analisar`).
- **Tipo de teste:** unitário + testes de endpoint (requisição/resposta
  HTTP via `Flask.test_client`).
- **Comando:**
  ```bash
  cd backend
  pip install -r requirements-dev.txt
  pytest -v
  ```
- **Resultado da última execução:** `15 passed in 0.21s`.
- **Casos cobertos:**
  - Rotas herdadas da Etapa 1 continuam respondendo (`/api/hello`,
    `/api/health`) — regressão.
  - `/api/analisar` com código válido (3 variações: variável, operação
    aritmética, condicional) → `200`, `recebido: true`.
  - Entrada vazia → `400`, mensagem "Informe um código-fonte antes de
    solicitar a análise.".
  - Entrada apenas com espaços/quebras de linha → `400`, mesma
    mensagem.
  - Campo `codigo` ausente → `400`, "Campo 'codigo' é obrigatório.".
  - Campo `codigo` com tipo errado (número) → `400`.
  - Corpo da requisição que não é um objeto JSON → `400`.
  - Corpo que não é JSON (`Content-Type: text/plain`) → `400`.
  - Rota inexistente → `404`.
  - Método não permitido (`GET /api/analisar`) → `405`.
  - Erro interno inesperado (simulado com mock) → `500`, mensagem
    genérica, sem expor o erro real ao usuário.

## Frontend (Node.js `node --test` + jsdom)

- **Módulo testado:** `frontend/script.js` (lógica pura) e
  `frontend/index.html` (estrutura da tela, via jsdom).
- **Tipo de teste:** unitário (validação de entrada, interpretação de
  respostas) + interface (seleção de exemplos, clique no botão,
  `fetch` simulado com sucesso/erro/falha de rede).
- **Comando:**
  ```bash
  cd frontend
  npm install
  npm test
  ```
- **Resultado da última execução:** `15 passed, 0 failed`.
- **Casos cobertos:**
  - Existem ao menos 3 exemplos cadastrados, todos com título e código.
  - Validação rejeita string vazia e string apenas com espaços; aceita
    código não vazio.
  - Interpretação de resposta do backend reconhece sucesso, erro e
    corpo inesperado.
  - Mensagem de falha de comunicação é compreensível.
  - A tela principal contém: seletor de exemplos, área de código,
    botão de análise e área de resultados, além de identificar a
    linguagem (Python).
  - Selecionar um exemplo preenche a área de código; o conteúdo pode
    ser editado depois; selecionar outro exemplo substitui o conteúdo
    anterior.
  - Clicar em "Analisar" sem código exibe a mensagem de erro e **não**
    chama o backend.
  - Resposta de sucesso do backend (simulada) atualiza a tela com a
    mensagem de sucesso.
  - Resposta de erro do backend (simulada) é exibida corretamente.
  - Falha de comunicação (fetch rejeitado) exibe mensagem compreensível
    ao usuário.

## Testes de implantação (Docker)

- **Tipo de teste:** verificação manual + healthcheck do Docker Compose.
- Foram adicionados healthchecks a `backend` (via `urllib` em Python,
  já presente na imagem) e `frontend` (via `wget`, já presente na
  imagem `nginx:alpine`), e o frontend só sobe depois que o backend
  reporta saudável (`depends_on: condition: service_healthy`).
- **Ainda não executado dentro deste ambiente de desenvolvimento**
  (sem Docker disponível aqui). Antes de entregar a etapa, execute
  localmente:
  ```bash
  docker compose up --build
  ```
  e confirme que:
  - os dois serviços sobem e ficam com status `healthy`
    (`docker compose ps`);
  - a interface em <http://localhost:8080> carrega corretamente;
  - selecionar um exemplo, editar e clicar em "Analisar" retorna
    "Código recebido com sucesso.";
  - enviar o campo vazio (ou apenas espaços) exibe a mensagem de erro
    correspondente, sem chamar o backend.

## Limitações conhecidas

- Nesta etapa o backend apenas valida a entrada e confirma o
  recebimento — não há análise léxica, sintática ou semântica (prevista
  para as próximas etapas).
- O teste de "falha de comunicação" no frontend é simulado (mock de
  `fetch`); não há, ainda, um teste automatizado de ponta a ponta contra
  o backend real rodando em contêiner.
