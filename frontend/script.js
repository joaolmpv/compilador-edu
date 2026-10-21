/**
 * Interface web do software educacional de compiladores (Etapa 2).
 *
 * Este arquivo é organizado em duas partes:
 *  1) Lógica pura (testável sem DOM): exemplos, validação de entrada e
 *     interpretação das respostas do backend.
 *  2) Integração com o DOM: liga a lógica aos elementos da página.
 *
 * A separação permite testar a lógica com Node.js (sem navegador) e
 * testar a interface com jsdom, conforme documentado no README.
 */

// --- 1) Lógica pura -------------------------------------------------

// Exemplos disponíveis. Cada um corresponde a uma construção do
// subconjunto de Python definido no README (variáveis, operadores
// aritméticos e estrutura condicional).
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
];

const BACKEND_ENDPOINT = "/api/analisar";

/**
 * Valida o código informado pelo usuário antes do envio ao backend.
 * @param {string} codigo
 * @returns {{valido: boolean, mensagem?: string}}
 */
function validarCodigo(codigo) {
  if (typeof codigo !== "string" || codigo.trim() === "") {
    return {
      valido: false,
      mensagem: "Informe um código-fonte antes de solicitar a análise.",
    };
  }
  return { valido: true };
}

/**
 * Traduz a resposta do backend em um objeto de exibição padronizado.
 * @param {number} httpStatus
 * @param {any} corpo
 * @returns {{tipo: "sucesso"|"erro", mensagem: string}}
 */
function interpretarResposta(httpStatus, corpo) {
  if (corpo && typeof corpo.mensagem === "string") {
    return {
      tipo: corpo.recebido ? "sucesso" : "erro",
      mensagem: corpo.mensagem,
    };
  }
  return {
    tipo: "erro",
    mensagem: "Resposta inesperada do servidor.",
  };
}

/**
 * Mensagem padrão exibida quando a requisição falha antes de obter
 * qualquer resposta do backend (rede indisponível, servidor fora do ar).
 */
function mensagemFalhaComunicacao() {
  return {
    tipo: "erro",
    mensagem:
      "Não foi possível comunicar com o servidor. Verifique a conexão e tente novamente.",
  };
}

// --- 2) Integração com o DOM ----------------------------------------

/**
 * Liga os elementos da página aos manipuladores de evento. Recebe o
 * `document` como parâmetro para poder ser testada com jsdom.
 * @param {Document|null} doc
 */
function inicializarInterface(doc) {
  const document_ = doc || (typeof document !== "undefined" ? document : null);
  if (!document_) return;

  const select = document_.getElementById("exemplo-select");
  const textarea = document_.getElementById("codigo-input");
  const botao = document_.getElementById("analisar-btn");
  const resultado = document_.getElementById("resultado");

  function mostrarResultado(tipo, mensagem) {
    resultado.textContent = mensagem;
    resultado.className = "resultado " + tipo;
  }

  if (select && textarea) {
    select.addEventListener("change", () => {
      const indice = select.value;
      if (indice === "") return;
      const exemplo = EXAMPLES[Number(indice)];
      if (exemplo) {
        textarea.value = exemplo.codigo;
      }
    });
  }

  if (botao && textarea && resultado) {
    botao.addEventListener("click", async () => {
      const codigo = textarea.value;
      const validacao = validarCodigo(codigo);

      if (!validacao.valido) {
        mostrarResultado("erro", validacao.mensagem);
        return;
      }

      mostrarResultado("carregando", "Analisando código...");

      try {
        const resposta = await fetch(BACKEND_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ codigo }),
        });

        let corpo = null;
        try {
          corpo = await resposta.json();
        } catch (_err) {
          corpo = null;
        }

        const interpretado = interpretarResposta(resposta.status, corpo);
        mostrarResultado(interpretado.tipo, interpretado.mensagem);
      } catch (_err) {
        const falha = mensagemFalhaComunicacao();
        mostrarResultado(falha.tipo, falha.mensagem);
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
    interpretarResposta,
    mensagemFalhaComunicacao,
    inicializarInterface,
  };
}
