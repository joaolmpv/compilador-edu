/**
 * Interface web do software educacional de compiladores (Etapa 3).
 *
 * Organização:
 *   1) Lógica pura (testável sem DOM): exemplos, validação, interpretação
 *      de respostas e geração de HTML dos resultados léxicos.
 *   2) Integração com o DOM: liga a lógica aos elementos da página.
 */

// ─── 1) Lógica pura ────────────────────────────────────────────────────────

const EXAMPLES = [
  {
    titulo: "Exemplo 1 — Declaração e inicialização de variável",
    codigo: "numero = 10\n",
  },
  {
    titulo: "Exemplo 2 — Operação aritmética",
    codigo: "resultado = 10 + 5\n",
  },
  {
    titulo: "Exemplo 3 — Estrutura condicional",
    codigo: "numero = 10\nif numero > 0:\n    numero = numero + 1\n",
  },
  {
    titulo: "Exemplo 4 — Erro léxico intencional",
    codigo: "x = 10\ny = x @ 5\n",  // '@' não é reconhecido
  },
];

const BACKEND_ENDPOINT = "/api/analisar";

// Mapa de tipo → nome legível ao usuário
const TIPO_LABEL = {
  PALAVRA_RESERVADA: "Palavra reservada",
  IDENTIFICADOR:     "Identificador",
  LITERAL_INTEIRO:   "Literal inteiro",
  LITERAL_FLOAT:     "Literal float",
  LITERAL_STRING:    "Literal string",
  OPERADOR:          "Operador",
  ABRE_PAREN:        "Delimitador",
  FECHA_PAREN:       "Delimitador",
  ABRE_COLCH:        "Delimitador",
  FECHA_COLCH:       "Delimitador",
  ABRE_CHAVE:        "Delimitador",
  FECHA_CHAVE:       "Delimitador",
  VIRGULA:           "Delimitador",
  DOIS_PONTOS:       "Delimitador",
  PONTO:             "Delimitador",
};

// Para fins de badge/CSS, agrupamos delimitadores numa classe só
function badgeClass(tipo) {
  if (tipo.startsWith("ABRE_") || tipo.startsWith("FECHA_") ||
      ["VIRGULA","DOIS_PONTOS","PONTO"].includes(tipo)) return "DELIMITADOR";
  return tipo;
}

function validarCodigo(codigo) {
  if (typeof codigo !== "string" || codigo.trim() === "") {
    return { valido: false, mensagem: "Informe um código-fonte antes de solicitar a análise." };
  }
  return { valido: true };
}

function mensagemFalhaComunicacao() {
  return {
    tipo: "erro",
    mensagem: "Não foi possível comunicar com o servidor. Verifique a conexão e tente novamente.",
  };
}

/**
 * Gera o HTML da tabela de tokens.
 * @param {Array} tokens
 * @returns {string}
 */
function htmlTabelaTokens(tokens) {
  if (tokens.length === 0) return "<tr><td colspan='5' style='color:#94a3b8;text-align:center'>Nenhum token identificado.</td></tr>";
  return tokens.map((t, i) => {
    const cls = badgeClass(t.tipo);
    const label = TIPO_LABEL[t.tipo] || t.tipo;
    return `<tr>
      <td>${i + 1}</td>
      <td class="td-tipo"><span class="badge ${cls}">${label}</span></td>
      <td>${escHtml(t.lexema)}</td>
      <td>${t.linha}</td>
      <td>${t.coluna}</td>
    </tr>`;
  }).join("");
}

/**
 * Gera o HTML da tabela de erros.
 * @param {Array} erros
 * @returns {string}
 */
function htmlTabelaErros(erros) {
  return erros.map(e =>
    `<tr>
      <td>${e.linha}</td>
      <td>${e.coluna}</td>
      <td style="color:var(--erro)">${escHtml(e.lexema)}</td>
      <td style="color:var(--texto-suave)">${escHtml(e.mensagem || "")}</td>
    </tr>`
  ).join("");
}

/**
 * Gera HTML da contagem de tokens por categoria.
 * @param {Array} tokens
 * @returns {string}
 */
function htmlContagemCategorias(tokens) {
  const contagem = {};
  for (const t of tokens) {
    const label = TIPO_LABEL[t.tipo] || t.tipo;
    contagem[label] = (contagem[label] || 0) + 1;
  }
  return Object.entries(contagem)
    .sort((a, b) => b[1] - a[1])
    .map(([label, n]) => `<span class="contagem-item">${label}: <strong>${n}</strong></span>`)
    .join("");
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ─── 2) Integração com o DOM ───────────────────────────────────────────────

function inicializarInterface(doc) {
  const document_ = doc || (typeof document !== "undefined" ? document : null);
  if (!document_) return;

  const select        = document_.getElementById("exemplo-select");
  const textarea      = document_.getElementById("codigo-input");
  const botao         = document_.getElementById("analisar-btn");
  const resultadoMsg  = document_.getElementById("resultado-msg");
  const resultadoLexico = document_.getElementById("resultado-lexico");
  const secaoErros    = document_.getElementById("secao-erros");
  const tabelaErrosBody  = document_.querySelector("#tabela-erros tbody");
  const tabelaTokensBody = document_.querySelector("#tabela-tokens tbody");
  const contagemDiv   = document_.getElementById("contagem-categorias");
  const resumoDiv     = document_.getElementById("resumo-tokens");

  function mostrarMsg(tipo, mensagem) {
    resultadoMsg.textContent = mensagem;
    resultadoMsg.className = "resultado " + tipo;
    resultadoMsg.style.display = "";
    resultadoLexico.style.display = "none";
  }

  function mostrarLexico(data) {
    resultadoMsg.style.display = "none";
    resultadoLexico.style.display = "";

    const { tokens, erros, sucesso } = data;

    // resumo
    const status = sucesso
      ? `✅ Análise léxica concluída — ${tokens.length} token(s) identificado(s).`
      : `⚠ Análise léxica concluída com ${erros.length} erro(s) léxico(s). `
        + `${tokens.length} token(s) identificado(s) fora das regiões com erro.`;
    resumoDiv.textContent = status;

    // erros
    if (erros.length > 0) {
      secaoErros.style.display = "";
      tabelaErrosBody.innerHTML = htmlTabelaErros(erros);
    } else {
      secaoErros.style.display = "none";
    }

    // tokens
    tabelaTokensBody.innerHTML = htmlTabelaTokens(tokens);
    contagemDiv.innerHTML = htmlContagemCategorias(tokens);
  }

  // seleção de exemplo
  if (select && textarea) {
    select.addEventListener("change", () => {
      const indice = select.value;
      if (indice === "") return;
      const ex = EXAMPLES[Number(indice)];
      if (ex) textarea.value = ex.codigo;
    });
  }

  // botão de análise
  if (botao && textarea) {
    botao.addEventListener("click", async () => {
      const codigo = textarea.value;
      const validacao = validarCodigo(codigo);
      if (!validacao.valido) {
        mostrarMsg("erro", validacao.mensagem);
        return;
      }

      mostrarMsg("carregando", "Analisando código...");
      botao.disabled = true;

      try {
        const resp = await fetch(BACKEND_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ codigo }),
        });

        let corpo = null;
        try { corpo = await resp.json(); } catch (_) { corpo = null; }

        if (resp.ok && corpo && "tokens" in corpo) {
          mostrarLexico(corpo);
        } else {
          const msg = corpo?.mensagem || "Resposta inesperada do servidor.";
          mostrarMsg("erro", msg);
        }
      } catch (_) {
        const f = mensagemFalhaComunicacao();
        mostrarMsg(f.tipo, f.mensagem);
      } finally {
        botao.disabled = false;
      }
    });
  }
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => inicializarInterface(document));
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    EXAMPLES,
    validarCodigo,
    mensagemFalhaComunicacao,
    htmlTabelaTokens,
    htmlTabelaErros,
    htmlContagemCategorias,
    badgeClass,
    escHtml,
    inicializarInterface,
  };
}
