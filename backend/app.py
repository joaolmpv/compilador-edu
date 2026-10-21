"""
Backend do software educacional de compiladores.

Etapa 2: além da rota de verificação ("Hello, World!"), o backend agora
expõe a rota /api/analisar, responsável por receber o código-fonte
enviado pela interface web, validar a entrada e devolver uma resposta
estruturada em JSON.

Nesta etapa o backend ainda NÃO realiza análise léxica, sintática ou
semântica: essas funcionalidades serão implementadas nas próximas
etapas. O foco aqui é a validação da entrada e o contrato de
comunicação entre frontend e backend.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # mantido por segurança, embora o nginx já faça proxy same-origin


@app.get("/api/hello")
def hello():
    return jsonify(message="Hello, World!")


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.post("/api/analisar")
def analisar():
    """Recebe o código-fonte, valida a entrada e confirma o recebimento.

    Contrato de comunicação:
        Requisição (JSON): {"codigo": "<código-fonte>"}
        Resposta de sucesso (200): {"mensagem": str, "recebido": true}
        Resposta de erro   (400): {"mensagem": str, "recebido": false}

    Nesta etapa não é realizada nenhuma análise léxica, sintática ou
    semântica: o backend apenas valida a entrada e confirma o
    recebimento, conforme escopo da Etapa 2.
    """
    data = request.get_json(silent=True)

    if data is None or not isinstance(data, dict):
        return jsonify(
            mensagem="Requisição inválida. Envie um JSON com o campo 'codigo'.",
            recebido=False,
        ), 400

    codigo = data.get("codigo")

    if codigo is None:
        return jsonify(
            mensagem="Campo 'codigo' é obrigatório.",
            recebido=False,
        ), 400

    if not isinstance(codigo, str):
        return jsonify(
            mensagem="Campo 'codigo' deve ser uma string.",
            recebido=False,
        ), 400

    if codigo.strip() == "":
        return jsonify(
            mensagem="Informe um código-fonte antes de solicitar a análise.",
            recebido=False,
        ), 400

    # Confirmação de recebimento. A análise léxica/sintática/semântica
    # propriamente dita será implementada nas próximas etapas.
    return jsonify(
        mensagem="Código recebido com sucesso.",
        recebido=True,
    ), 200


@app.errorhandler(404)
def not_found(_err):
    return jsonify(mensagem="Rota não encontrada.", recebido=False), 404


@app.errorhandler(405)
def method_not_allowed(_err):
    return jsonify(mensagem="Método não permitido para esta rota.", recebido=False), 405


@app.errorhandler(Exception)
def handle_unexpected_error(_err):
    # Mensagem genérica — nunca expor detalhes internos ao usuário.
    return jsonify(
        mensagem="Ocorreu um erro inesperado no servidor. Tente novamente.",
        recebido=False,
    ), 500


if __name__ == "__main__":
    # host 0.0.0.0 é necessário para o serviço ser acessível de fora do contêiner
    app.run(host="0.0.0.0", port=5000)
