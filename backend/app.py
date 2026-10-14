"""
Backend mínimo do software educacional de compiladores.

Nesta primeira etapa, o backend só expõe uma rota de verificação
("Hello, World!") para provar que a cadeia frontend -> backend está
funcionando. As rotas de análise léxica/sintática serão adicionadas
nas próximas etapas do projeto.
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # permite que o frontend (porta diferente) chame o backend


@app.get("/api/hello")
def hello():
    return jsonify(message="Hello, World!")


@app.get("/api/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    # host 0.0.0.0 é necessário para o serviço ser acessível de fora do contêiner
    app.run(host="0.0.0.0", port=5000)
