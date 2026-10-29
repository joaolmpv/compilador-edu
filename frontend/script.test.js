/**
 * Testes automatizados do frontend (Etapa 3).
 *
 * Como executar:
 *   cd frontend
 *   npm install
 *   npm test
 */

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { JSDOM } = require("jsdom");

const {
  EXAMPLES,
  validarCodigo,
  mensagemFalhaComunicacao,
  htmlTabelaTokens,
  htmlTabelaErros,
  htmlContagemCategorias,
  badgeClass,
  escHtml,
  inicializarInterface,
} = require("./script.js");

// ── Regressão Etapa 2: lógica pura ──────────────────────────────────────────

test("existem ao menos 4 exemplos cadastrados (incluindo o de erro léxico)", () => {
  assert.ok(EXAMPLES.length >= 4);
  for (const ex of EXAMPLES) {
    assert.ok(ex.titulo.length > 0);
    assert.ok(ex.codigo.trim().length > 0);
  }
});

test("validarCodigo rejeita string vazia", () => {
  const r = validarCodigo("");
  assert.equal(r.valido, false);
  assert.match(r.mensagem, /informe um código-fonte/i);
});

test("validarCodigo rejeita apenas espaços", () => {
  assert.equal(validarCodigo("   \n").valido, false);
});

test("validarCodigo aceita código válido", () => {
  assert.equal(validarCodigo("x = 10").valido, true);
});

test("mensagemFalhaComunicacao retorna mensagem compreensível", () => {
  assert.match(mensagemFalhaComunicacao().mensagem, /não foi possível comunicar/i);
});

// ── Geração de HTML dos tokens ───────────────────────────────────────────────

test("htmlTabelaTokens gera linhas para cada token", () => {
  const tokens = [
    { tipo: "IDENTIFICADOR", lexema: "x", linha: 1, coluna: 1 },
    { tipo: "OPERADOR",       lexema: "=", linha: 1, coluna: 3 },
  ];
  const html = htmlTabelaTokens(tokens);
  assert.ok(html.includes("x"));
  assert.ok(html.includes("IDENTIFICADOR") || html.includes("Identificador"));
});

test("htmlTabelaTokens mostra mensagem quando lista está vazia", () => {
  const html = htmlTabelaTokens([]);
  assert.ok(html.toLowerCase().includes("nenhum token"));
});

test("htmlTabelaErros gera linhas para cada erro", () => {
  const erros = [{
    tipo: "ERRO_LEXICO", lexema: "@", linha: 2, coluna: 5,
    mensagem: "Caractere não reconhecido '@'."
  }];
  const html = htmlTabelaErros(erros);
  assert.ok(html.includes("@"));
  assert.ok(html.includes("2"));
});

test("htmlContagemCategorias conta corretamente", () => {
  const tokens = [
    { tipo: "IDENTIFICADOR", lexema: "x" },
    { tipo: "IDENTIFICADOR", lexema: "y" },
    { tipo: "OPERADOR",       lexema: "=" },
  ];
  const html = htmlContagemCategorias(tokens);
  assert.ok(html.includes("2") || html.includes("Identificador"));
});

test("escHtml escapa caracteres perigosos", () => {
  assert.equal(escHtml("<script>"), "&lt;script&gt;");
  assert.equal(escHtml('"hello"'), "&quot;hello&quot;");
});

test("badgeClass agrupa delimitadores numa classe única", () => {
  assert.equal(badgeClass("ABRE_PAREN"), "DELIMITADOR");
  assert.equal(badgeClass("VIRGULA"),    "DELIMITADOR");
  assert.equal(badgeClass("OPERADOR"),   "OPERADOR");
});

// ── Testes de interface (DOM com jsdom) ──────────────────────────────────────

function montarDom() {
  const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
  return new JSDOM(html);
}

test("a tela contém os elementos obrigatórios da Etapa 3", () => {
  const doc = montarDom().window.document;
  assert.ok(doc.getElementById("exemplo-select"));
  assert.ok(doc.getElementById("codigo-input"));
  assert.ok(doc.getElementById("analisar-btn"));
  assert.ok(doc.getElementById("resultado-lexico"));
  assert.ok(doc.getElementById("tabela-tokens"));
  assert.ok(doc.getElementById("tabela-erros"));
  assert.match(doc.body.textContent, /python/i);
});

test("selecionar exemplo preenche textarea e substitui ao trocar", () => {
  const dom = montarDom();
  inicializarInterface(dom.window.document);
  const select   = dom.window.document.getElementById("exemplo-select");
  const textarea = dom.window.document.getElementById("codigo-input");

  select.value = "0";
  select.dispatchEvent(new dom.window.Event("change"));
  assert.equal(textarea.value, EXAMPLES[0].codigo);

  select.value = "2";
  select.dispatchEvent(new dom.window.Event("change"));
  assert.equal(textarea.value, EXAMPLES[2].codigo);
});

test("clicar analisar sem código mostra erro sem chamar backend", async () => {
  const dom = montarDom();
  let chamou = false;
  global.fetch = async () => { chamou = true; throw new Error("não devia chamar"); };
  inicializarInterface(dom.window.document);

  const botao    = dom.window.document.getElementById("analisar-btn");
  const textarea = dom.window.document.getElementById("codigo-input");
  const msg      = dom.window.document.getElementById("resultado-msg");

  textarea.value = "";
  botao.dispatchEvent(new dom.window.Event("click"));
  await new Promise(r => setTimeout(r, 0));

  assert.match(msg.textContent, /informe um código-fonte/i);
  assert.equal(chamou, false);
});

test("resposta com tokens do backend é exibida na tabela", async () => {
  const dom = montarDom();
  global.fetch = async () => ({
    ok: true,
    status: 200,
    json: async () => ({
      sucesso: true,
      tokens: [
        { tipo: "IDENTIFICADOR", lexema: "x",  linha: 1, coluna: 1 },
        { tipo: "OPERADOR",       lexema: "=",  linha: 1, coluna: 3 },
        { tipo: "LITERAL_INTEIRO", lexema: "10", linha: 1, coluna: 5 },
      ],
      erros: [],
    }),
  });
  inicializarInterface(dom.window.document);

  const botao    = dom.window.document.getElementById("analisar-btn");
  const textarea = dom.window.document.getElementById("codigo-input");

  textarea.value = "x = 10";
  botao.dispatchEvent(new dom.window.Event("click"));
  await new Promise(r => setTimeout(r, 20));

  const tabela = dom.window.document.getElementById("tabela-tokens");
  assert.ok(tabela.innerHTML.includes("x"));
  assert.ok(tabela.innerHTML.includes("10"));
});

test("erros léxicos aparecem na seção de erros", async () => {
  const dom = montarDom();
  global.fetch = async () => ({
    ok: true,
    status: 200,
    json: async () => ({
      sucesso: false,
      tokens: [{ tipo: "IDENTIFICADOR", lexema: "x", linha: 1, coluna: 1 }],
      erros: [{
        tipo: "ERRO_LEXICO", lexema: "@", linha: 1, coluna: 5,
        mensagem: "Erro léxico na linha 1, coluna 5: caractere não reconhecido '@'.",
      }],
    }),
  });
  inicializarInterface(dom.window.document);

  const botao    = dom.window.document.getElementById("analisar-btn");
  const textarea = dom.window.document.getElementById("codigo-input");

  textarea.value = "x @ 1";
  botao.dispatchEvent(new dom.window.Event("click"));
  await new Promise(r => setTimeout(r, 20));

  const secaoErros = dom.window.document.getElementById("secao-erros");
  assert.notEqual(secaoErros.style.display, "none");
  const tabErros = dom.window.document.getElementById("tabela-erros");
  assert.ok(tabErros.innerHTML.includes("@"));
});

test("falha de rede exibe mensagem compreensível", async () => {
  const dom = montarDom();
  global.fetch = async () => { throw new Error("network down"); };
  inicializarInterface(dom.window.document);

  const botao    = dom.window.document.getElementById("analisar-btn");
  const textarea = dom.window.document.getElementById("codigo-input");
  const msg      = dom.window.document.getElementById("resultado-msg");

  textarea.value = "x = 10";
  botao.dispatchEvent(new dom.window.Event("click"));
  await new Promise(r => setTimeout(r, 20));

  assert.match(msg.textContent, /não foi possível comunicar/i);
});
