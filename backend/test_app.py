"""
Testes automatizados do backend (Etapa 2).

Cobrem:
- As rotas herdadas da Etapa 1 (/api/hello, /api/health).
- A nova rota /api/analisar: casos válidos e todos os casos de erro
  exigidos pela Etapa 2 (entrada vazia, apenas espaços, campo ausente,
  tipo inválido, corpo que não é JSON).
- Tratamento de rota inexistente, método não permitido e erro
  inesperado (sem expor detalhes internos).

Como executar:
    cd backend
    pip install -r requirements-dev.txt
    pytest -v
"""

from unittest.mock import patch

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    # Garante que o errorhandler genérico seja de fato usado nos testes,
    # em vez de o Flask repropagar a exceção para fins de depuração.
    app.config["PROPAGATE_EXCEPTIONS"] = False
    with app.test_client() as test_client:
        yield test_client


# --- Rotas herdadas da Etapa 1 ---

def test_hello(client):
    resp = client.get("/api/hello")
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "Hello, World!"


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


# --- /api/analisar: casos válidos ---

@pytest.mark.parametrize(
    "codigo",
    [
        "numero = 10",
        "resultado = 10 + 5",
        "if numero > 0:\n    numero = numero + 1",
    ],
)
def test_analisar_codigo_valido(client, codigo):
    """Etapa 3: resposta agora retorna tokens/erros/sucesso em vez de recebido/mensagem."""
    resp = client.post("/api/analisar", json={"codigo": codigo})
    data = resp.get_json()
    assert resp.status_code == 200
    assert "sucesso" in data
    assert "tokens" in data
    assert "erros" in data
    assert isinstance(data["tokens"], list)
    assert isinstance(data["erros"], list)


# --- /api/analisar: validações de entrada ---

def test_analisar_codigo_vazio(client):
    resp = client.post("/api/analisar", json={"codigo": ""})
    data = resp.get_json()
    assert resp.status_code == 400
    assert data["recebido"] is False
    assert "informe um código-fonte" in data["mensagem"].lower()


def test_analisar_codigo_apenas_espacos(client):
    resp = client.post("/api/analisar", json={"codigo": "   \n\t  "})
    data = resp.get_json()
    assert resp.status_code == 400
    assert data["recebido"] is False
    assert "informe um código-fonte" in data["mensagem"].lower()


def test_analisar_campo_ausente(client):
    resp = client.post("/api/analisar", json={})
    data = resp.get_json()
    assert resp.status_code == 400
    assert "obrigatório" in data["mensagem"].lower()


def test_analisar_campo_tipo_errado(client):
    resp = client.post("/api/analisar", json={"codigo": 123})
    assert resp.status_code == 400


def test_analisar_corpo_nao_e_objeto(client):
    resp = client.post("/api/analisar", json=["codigo", "x = 1"])
    assert resp.status_code == 400


def test_analisar_sem_json(client):
    resp = client.post(
        "/api/analisar", data="isso não é json", content_type="text/plain"
    )
    data = resp.get_json()
    assert resp.status_code == 400
    assert data["recebido"] is False


# --- Tratamento de rotas/métodos e erros inesperados ---

def test_rota_inexistente(client):
    resp = client.get("/api/nao-existe")
    assert resp.status_code == 404
    assert resp.get_json()["recebido"] is False


def test_metodo_nao_permitido(client):
    resp = client.get("/api/analisar")
    assert resp.status_code == 405
    assert resp.get_json()["recebido"] is False


def test_erro_inesperado_nao_expoe_detalhes(client):
    # Simula uma falha interna inesperada (ex.: bug não previsto) e garante
    # que o usuário recebe apenas uma mensagem genérica, nunca o detalhe.
    with patch("flask.Request.get_json", side_effect=RuntimeError("falha interna simulada")):
        resp = client.post("/api/analisar", json={"codigo": "x = 1"})

    data = resp.get_json()
    assert resp.status_code == 500
    assert data["recebido"] is False
    assert "falha interna simulada" not in data["mensagem"]
    assert "ocorreu um erro inesperado" in data["mensagem"].lower()


# --- Regressão explícita: mudanças desta etapa não devem quebrar a Etapa 1 ---

def test_regressao_rotas_etapa1_continuam_ok(client):
    assert client.get("/api/hello").status_code == 200
    assert client.get("/api/health").status_code == 200
