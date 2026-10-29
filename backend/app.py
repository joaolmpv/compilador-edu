"""
Backend do software educacional de compiladores.

Etapa 3: o endpoint /api/analisar agora executa o analisador léxico
(scanner) sobre o código-fonte recebido e retorna a lista de tokens
classificados, a lista de erros léxicos e um indicador de sucesso.

As rotas /api/hello e /api/health são mantidas (regressão das Etapas 1
e 2). O contrato de /api/analisar é atualizado para incluir "tokens",
"erros" e "sucesso" na resposta, conforme documentado no README.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

from scanner import analisar_lexico

app = Flask(__name__)
CORS(app)


@app.get("/api/hello")
def hello():
    return jsonify(message="Hello, World!")


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.post("/api/analisar")
def analisar():
    """Valida a entrada e executa o scanner léxico.

    Contrato de comunicação (Etapa 3):
        Requisição  (JSON): {"codigo": "<código-fonte>"}
        Resposta 200:
            {
                "sucesso": bool,
                "tokens": [{"tipo", "lexema", "linha", "coluna"}, ...],
                "erros":  [{"tipo", "lexema", "linha", "coluna", "mensagem"}, ...]
            }
        Resposta 400 (entrada inválida):
            {"mensagem": str, "recebido": false}
    """
    data = request.get_json(silent=True)

    if data is None or not isinstance(data, dict):
        return jsonify(
            mensagem="Requisição inválida. Envie um JSON com o campo 'codigo'.",
            recebido=False,
        ), 400

    codigo = data.get("codigo")

    if codigo is None:
        return jsonify(mensagem="Campo 'codigo' é obrigatório.", recebido=False), 400

    if not isinstance(codigo, str):
        return jsonify(mensagem="Campo 'codigo' deve ser uma string.", recebido=False), 400

    if codigo.strip() == "":
        return jsonify(
            mensagem="Informe um código-fonte antes de solicitar a análise.",
            recebido=False,
        ), 400

    resultado = analisar_lexico(codigo)
    return jsonify(resultado), 200


@app.errorhandler(404)
def not_found(_err):
    return jsonify(mensagem="Rota não encontrada.", recebido=False), 404


@app.errorhandler(405)
def method_not_allowed(_err):
    return jsonify(mensagem="Método não permitido para esta rota.", recebido=False), 405


@app.errorhandler(Exception)
def handle_unexpected_error(_err):
    return jsonify(
        mensagem="Ocorreu um erro inesperado no servidor. Tente novamente.",
        recebido=False,
    ), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
