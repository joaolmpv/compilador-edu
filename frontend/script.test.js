/**
 * Testes automatizados do frontend (Etapa 2).
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
  interpretarResposta,
  mensagemFalhaComunicacao,
  inicializarInterface,
} = require("./script.js");

// --- Lógica pura ------------------------------------------------------

test("existem ao menos 3 exemplos cadastrados e todos têm conteúdo", () => {
  assert.ok(EXAMPLES.length >= 3);
  for (const exemplo of EXAMPLES) {
    assert.ok(exemplo.titulo.length > 0);
    assert.ok(exemplo.codigo.trim().length > 0);
  }
});

test("validarCodigo rejeita string vazia", () => {
  const r = validarCodigo("");
  assert.equal(r.valido, false);
  assert.match(r.mensagem, /informe um código-fonte/i);
});

test("validarCodigo rejeita entrada composta apenas por espaços", () => {
  const r = validarCodigo("   \n\t ");
  assert.equal(r.valido, false);
});

test("validarCodigo aceita código não vazio", () => {
  const r = validarCodigo("x = 10");
  assert.equal(r.valido, true);
});

test("interpretarResposta reconhece sucesso do backend", () => {
  const r = interpretarResposta(200, {
    mensagem: "Código recebido com sucesso.",
    recebido: true,
  });
  assert.equal(r.tipo, "sucesso");
});

test("interpretarResposta reconhece erro retornado pelo backend", () => {
  const r = interpretarResposta(400, {
    mensagem: "Informe um código-fonte antes de solicitar a análise.",
    recebido: false,
  });
  assert.equal(r.tipo, "erro");
});

test("interpretarResposta trata corpo de resposta inesperado", () => {
  const r = interpretarResposta(500, null);
  assert.equal(r.tipo, "erro");
  assert.match(r.mensagem, /resposta inesperada/i);
});

test("mensagemFalhaComunicacao retorna texto compreensível ao usuário", () => {
  const r = mensagemFalhaComunicacao();
  assert.match(r.mensagem, /não foi possível comunicar/i);
});

// --- Testes de interface (DOM simulado com jsdom) ----------------------

function montarDom() {
  const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
  return new JSDOM(html);
}

test("a tela principal contém os elementos exigidos pela Etapa 2", () => {
  const dom = montarDom();
  const doc = dom.window.document;

  assert.ok(doc.getElementById("exemplo-select"), "seletor de exemplos ausente");
  assert.ok(doc.getElementById("codigo-input"), "área de entrada de código ausente");
  assert.ok(doc.getElementById("analisar-btn"), "botão de análise ausente");
  assert.ok(doc.getElementById("resultado"), "área de resultados ausente");
  assert.match(doc.body.textContent, /python/i, "linguagem analisada não identificada na tela");
});

test("selecionar um exemplo preenche a área de código e permite edição", () => {
  const dom = montarDom();
  inicializarInterface(dom.window.document);

  const select = dom.window.document.getElementById("exemplo-select");
  const textarea = dom.window.document.getElementById("codigo-input");

  select.value = "1";
  select.dispatchEvent(new dom.window.Event("change"));
  assert.equal(textarea.value, EXAMPLES[1].codigo);

  // o usuário ainda pode editar o conteúdo carregado
  textarea.value = EXAMPLES[1].codigo + "extra = 1\n";
  assert.match(textarea.value, /extra = 1/);
});

test("selecionar um novo exemplo substitui o conteúdo anterior", () => {
  const dom = montarDom();
  inicializarInterface(dom.window.document);

  const select = dom.window.document.getElementById("exemplo-select");
  const textarea = dom.window.document.getElementById("codigo-input");

  select.value = "0";
  select.dispatchEvent(new dom.window.Event("change"));
  assert.equal(textarea.value, EXAMPLES[0].codigo);

  select.value = "2";
  select.dispatchEvent(new dom.window.Event("change"));
  assert.equal(textarea.value, EXAMPLES[2].codigo);
});

test("clicar em analisar sem código mostra mensagem de erro, sem chamar o backend", async () => {
  const dom = montarDom();
  let chamouFetch = false;
  global.fetch = async () => {
    chamouFetch = true;
    throw new Error("fetch não deveria ter sido chamado");
  };

  inicializarInterface(dom.window.document);

  const botao = dom.window.document.getElementById("analisar-btn");
  const resultado = dom.window.document.getElementById("resultado");
  const textarea = dom.window.document.getElementById("codigo-input");

  textarea.value = "   ";
  botao.dispatchEvent(new dom.window.Event("click"));
  await new Promise((r) => setTimeout(r, 0));

  assert.match(resultado.textContent, /informe um código-fonte/i);
  assert.ok(resultado.className.includes("erro"));
  assert.equal(chamouFetch, false);
});

test("clicar em analisar com sucesso simulado do backend atualiza a interface", async () => {
  const dom = montarDom();
  global.fetch = async () => ({
    status: 200,
    json: async () => ({ mensagem: "Código recebido com sucesso.", recebido: true }),
  });

  inicializarInterface(dom.window.document);

  const botao = dom.window.document.getElementById("analisar-btn");
  const resultado = dom.window.document.getElementById("resultado");
  const textarea = dom.window.document.getElementById("codigo-input");

  textarea.value = "x = 10";
  botao.dispatchEvent(new dom.window.Event("click"));
  await new Promise((r) => setTimeout(r, 10));

  assert.match(resultado.textContent, /sucesso/i);
  assert.ok(resultado.className.includes("sucesso"));
});

test("resposta de erro do backend (ex.: entrada inválida) é exibida ao usuário", async () => {
  const dom = montarDom();
  global.fetch = async () => ({
    status: 400,
    json: async () => ({
      mensagem: "Informe um código-fonte antes de solicitar a análise.",
      recebido: false,
    }),
  });

  inicializarInterface(dom.window.document);

  const botao = dom.window.document.getElementById("analisar-btn");
  const resultado = dom.window.document.getElementById("resultado");
  const textarea = dom.window.document.getElementById("codigo-input");

  // Um espaço simples passa na validação do frontend, mas poderia ser
  // rejeitado pelo backend em outro cenário; aqui simulamos diretamente
  // uma resposta de erro do servidor para validar o tratamento na tela.
  textarea.value = "codigo_de_teste";
  botao.dispatchEvent(new dom.window.Event("click"));
  await new Promise((r) => setTimeout(r, 10));

  assert.match(resultado.textContent, /informe um código-fonte/i);
  assert.ok(resultado.className.includes("erro"));
});

test("falha de comunicação com o backend exibe mensagem compreensível", async () => {
  const dom = montarDom();
  global.fetch = async () => {
    throw new Error("network down");
  };

  inicializarInterface(dom.window.document);

  const botao = dom.window.document.getElementById("analisar-btn");
  const resultado = dom.window.document.getElementById("resultado");
  const textarea = dom.window.document.getElementById("codigo-input");

  textarea.value = "x = 10";
  botao.dispatchEvent(new dom.window.Event("click"));
  await new Promise((r) => setTimeout(r, 10));

  assert.match(resultado.textContent, /não foi possível comunicar/i);
  assert.ok(resultado.className.includes("erro"));
});
