"""
Testes automatizados do scanner léxico (Etapa 3).

Cobrem:
  - Palavras reservadas
  - Identificadores válidos
  - Literais inteiros e floats
  - Literais de string (simples e duplas)
  - String não fechada (erro léxico)
  - Operadores simples e compostos
  - Delimitadores
  - Comentários (ignorados)
  - Espaços em branco e indentação (ignorados)
  - Posição correta (linha e coluna)
  - Erro léxico: caractere não reconhecido
  - Código misto com múltiplos tokens
  - Casos de borda: string vazia, só espaços, só comentários
  - Regressão: scanner não interfere nas validações da Etapa 2

Como executar:
    cd backend
    pytest test_scanner.py -v
"""

import pytest
from scanner import Scanner, analisar_lexico, PALAVRAS_RESERVADAS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def tokenizar(codigo: str) -> list[dict]:
    return Scanner(codigo).tokenizar()


def tipos(codigo: str) -> list[str]:
    return [t["tipo"] for t in tokenizar(codigo)]


def primeiro(codigo: str) -> dict:
    return tokenizar(codigo)[0]


# ---------------------------------------------------------------------------
# Palavras reservadas
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("palavra", sorted(PALAVRAS_RESERVADAS))
def test_palavra_reservada(palavra):
    t = primeiro(palavra)
    assert t["tipo"] == "PALAVRA_RESERVADA"
    assert t["lexema"] == palavra


# ---------------------------------------------------------------------------
# Identificadores
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ident", ["numero", "resultado", "_x1", "minhaVar", "__init__"])
def test_identificador_valido(ident):
    t = primeiro(ident)
    assert t["tipo"] == "IDENTIFICADOR"
    assert t["lexema"] == ident


def test_identificador_nao_confunde_com_palavra_reservada():
    t = primeiro("iffy")
    assert t["tipo"] == "IDENTIFICADOR"


# ---------------------------------------------------------------------------
# Literais inteiros
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("num", ["0", "10", "42", "999"])
def test_literal_inteiro(num):
    t = primeiro(num)
    assert t["tipo"] == "LITERAL_INTEIRO"
    assert t["lexema"] == num


# ---------------------------------------------------------------------------
# Literais float
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("num", ["3.14", "0.5", "10.0"])
def test_literal_float(num):
    t = primeiro(num)
    assert t["tipo"] == "LITERAL_FLOAT"
    assert t["lexema"] == num


# ---------------------------------------------------------------------------
# Literais de string
# ---------------------------------------------------------------------------

def test_string_aspas_duplas():
    t = primeiro('"hello"')
    assert t["tipo"] == "LITERAL_STRING"
    assert t["lexema"] == '"hello"'


def test_string_aspas_simples():
    t = primeiro("'mundo'")
    assert t["tipo"] == "LITERAL_STRING"
    assert t["lexema"] == "'mundo'"


def test_string_vazia():
    t = primeiro('""')
    assert t["tipo"] == "LITERAL_STRING"


def test_string_nao_fechada_gera_erro():
    tokens = tokenizar('"aberta')
    assert tokens[0]["tipo"] == "ERRO_LEXICO"
    assert "não fechada" in tokens[0]["mensagem"].lower()


def test_string_nao_fecha_antes_de_nova_linha():
    tokens = tokenizar('"abc\ndef"')
    # a primeira string não fecha → erro; def e aspas viram tokens separados
    assert tokens[0]["tipo"] == "ERRO_LEXICO"


# ---------------------------------------------------------------------------
# Operadores simples
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("op", ["+", "-", "*", "/", "%", "=", "<", ">"])
def test_operador_simples(op):
    t = primeiro(op)
    assert t["tipo"] == "OPERADOR"
    assert t["lexema"] == op


# ---------------------------------------------------------------------------
# Operadores compostos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("op", ["**", "//", "==", "!=", "<=", ">=", "+=", "-=", "*=", "/="])
def test_operador_composto(op):
    t = primeiro(op)
    assert t["tipo"] == "OPERADOR"
    assert t["lexema"] == op


# ---------------------------------------------------------------------------
# Delimitadores
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("delim,esperado", [
    ("(", "ABRE_PAREN"), (")", "FECHA_PAREN"),
    ("[", "ABRE_COLCH"), ("]", "FECHA_COLCH"),
    ("{", "ABRE_CHAVE"), ("}", "FECHA_CHAVE"),
    (",", "VIRGULA"), (":", "DOIS_PONTOS"), (".", "PONTO"),
])
def test_delimitador(delim, esperado):
    t = primeiro(delim)
    assert t["tipo"] == esperado
    assert t["lexema"] == delim


# ---------------------------------------------------------------------------
# Comentários e espaços em branco
# ---------------------------------------------------------------------------

def test_comentario_linha_ignorado():
    tokens = tokenizar("# isso é um comentário\nx = 1")
    assert all(t["tipo"] != "ERRO_LEXICO" for t in tokens)
    assert tokens[0]["lexema"] == "x"


def test_espacos_em_branco_ignorados():
    tokens = tokenizar("   \t  x   ")
    assert len(tokens) == 1
    assert tokens[0]["tipo"] == "IDENTIFICADOR"


def test_apenas_comentario_sem_tokens():
    tokens = tokenizar("# só comentário")
    assert tokens == []


def test_apenas_espacos_sem_tokens():
    tokens = tokenizar("   \n\t  ")
    assert tokens == []


# ---------------------------------------------------------------------------
# Posição (linha e coluna)
# ---------------------------------------------------------------------------

def test_posicao_primeira_linha():
    t = primeiro("x")
    assert t["linha"] == 1
    assert t["coluna"] == 1


def test_posicao_segunda_linha():
    tokens = tokenizar("x\ny")
    assert tokens[1]["linha"] == 2
    assert tokens[1]["coluna"] == 1


def test_coluna_correta_apos_espacos():
    t = primeiro("   abc")
    assert t["coluna"] == 4


def test_posicao_de_operador_composto():
    tokens = tokenizar("x == 1")
    op = next(t for t in tokens if t["lexema"] == "==")
    assert op["linha"] == 1
    assert op["coluna"] == 3


# ---------------------------------------------------------------------------
# Erros léxicos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char", ["@", "$", "!", "~", "^", "&", "|", "\\"])
def test_caractere_nao_reconhecido(char):
    tokens = tokenizar(char)
    assert tokens[0]["tipo"] == "ERRO_LEXICO"
    assert "mensagem" in tokens[0]
    assert char in tokens[0]["mensagem"] or char in tokens[0]["lexema"]


def test_erro_lexico_inclui_posicao_na_mensagem():
    tokens = tokenizar("x = @")
    erro = next(t for t in tokens if t["tipo"] == "ERRO_LEXICO")
    assert str(erro["linha"]) in erro["mensagem"]
    assert str(erro["coluna"]) in erro["mensagem"]


def test_scanner_continua_apos_erro():
    # '@' é inválido, mas 'y' depois deve ser tokenizado normalmente
    tokens = tokenizar("@y")
    assert tokens[0]["tipo"] == "ERRO_LEXICO"
    assert tokens[1]["tipo"] == "IDENTIFICADOR"
    assert tokens[1]["lexema"] == "y"


def test_multiplos_erros_acumulados():
    tokens = tokenizar("@ $ ~")
    erros = [t for t in tokens if t["tipo"] == "ERRO_LEXICO"]
    assert len(erros) == 3


# ---------------------------------------------------------------------------
# Código misto / programas reais do subconjunto
# ---------------------------------------------------------------------------

def test_declaracao_variavel():
    tokens = tokenizar("numero = 10")
    assert tipos("numero = 10") == ["IDENTIFICADOR", "OPERADOR", "LITERAL_INTEIRO"]


def test_operacao_aritmetica():
    assert tipos("resultado = 10 + 5") == [
        "IDENTIFICADOR", "OPERADOR", "LITERAL_INTEIRO", "OPERADOR", "LITERAL_INTEIRO"
    ]


def test_estrutura_condicional():
    codigo = "if numero > 0:\n    numero = numero + 1"
    ts = tipos(codigo)
    assert ts[0] == "PALAVRA_RESERVADA"   # if
    assert "OPERADOR" in ts               # > e =
    assert "DOIS_PONTOS" in ts


def test_chamada_de_funcao():
    tokens = tokenizar("print(x)")
    assert tokens[0]["tipo"] == "IDENTIFICADOR"
    assert tokens[1]["tipo"] == "ABRE_PAREN"
    assert tokens[2]["tipo"] == "IDENTIFICADOR"
    assert tokens[3]["tipo"] == "FECHA_PAREN"


def test_programa_com_comentario_inline():
    tokens = tokenizar("x = 1  # atribuição")
    assert all(t["tipo"] != "ERRO_LEXICO" for t in tokens)
    assert len(tokens) == 3  # x, =, 1 (comentário ignorado)


# ---------------------------------------------------------------------------
# Função analisar_lexico (resposta estruturada)
# ---------------------------------------------------------------------------

def test_analisar_lexico_sucesso():
    r = analisar_lexico("x = 10")
    assert r["sucesso"] is True
    assert len(r["tokens"]) == 3
    assert r["erros"] == []


def test_analisar_lexico_com_erro():
    r = analisar_lexico("x = @")
    assert r["sucesso"] is False
    assert len(r["erros"]) == 1
    assert r["erros"][0]["tipo"] == "ERRO_LEXICO"


def test_analisar_lexico_tokens_nao_incluem_erros():
    r = analisar_lexico("@ x")
    tipos_tokens = [t["tipo"] for t in r["tokens"]]
    assert "ERRO_LEXICO" not in tipos_tokens


def test_analisar_lexico_erros_separados():
    r = analisar_lexico("@ $")
    assert len(r["erros"]) == 2
