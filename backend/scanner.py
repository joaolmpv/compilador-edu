"""
Analisador léxico (scanner) para um subconjunto de Python.

Subconjunto suportado:
  - Palavras reservadas: if, else, elif, while, for, in, def, return,
                         True, False, None, and, or, not, pass, break, continue
  - Identificadores: [a-zA-Z_][a-zA-Z0-9_]*
  - Literais inteiros: sequência de dígitos (sem sinal)
  - Literais de ponto flutuante: dígitos . dígitos
  - Literais de string: delimitados por ' ou " (sem escapamento de multi-linha)
  - Operadores: + - * / % ** // = == != < > <= >= += -= *= /=
  - Delimitadores: ( ) [ ] { } , : .
  - Comentários: # até fim da linha (ignorados — não geram token)
  - Indentação/espaços em branco: ignorados (não geram token)
  - Caracteres não reconhecidos: geram ERRO_LEXICO

O scanner NUNCA lança exceção: todos os problemas são reportados como
tokens de categoria ERRO_LEXICO e a varredura continua no caractere
seguinte, acumulando todos os erros encontrados.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List

# ---------------------------------------------------------------------------
# Estrutura de um token
# ---------------------------------------------------------------------------

@dataclass
class Token:
    tipo: str
    lexema: str
    linha: int
    coluna: int
    mensagem: str | None = field(default=None, repr=False)

    def to_dict(self) -> dict:
        d = {
            "tipo": self.tipo,
            "lexema": self.lexema,
            "linha": self.linha,
            "coluna": self.coluna,
        }
        if self.mensagem is not None:
            d["mensagem"] = self.mensagem
        return d


# ---------------------------------------------------------------------------
# Tabela de tokens fixos
# ---------------------------------------------------------------------------

PALAVRAS_RESERVADAS: set[str] = {
    "if", "else", "elif", "while", "for", "in",
    "def", "return", "True", "False", "None",
    "and", "or", "not", "pass", "break", "continue",
}

# Operadores compostos (mais longos primeiro para evitar casamento curto)
OPERADORES_COMPOSTOS = ["**", "//", "==", "!=", "<=", ">=", "+=", "-=", "*=", "/="]
OPERADORES_SIMPLES   = ["+", "-", "*", "/", "%", "=", "<", ">"]

DELIMITADORES: dict[str, str] = {
    "(": "ABRE_PAREN",
    ")": "FECHA_PAREN",
    "[": "ABRE_COLCH",
    "]": "FECHA_COLCH",
    "{": "ABRE_CHAVE",
    "}": "FECHA_CHAVE",
    ",": "VIRGULA",
    ":": "DOIS_PONTOS",
    ".": "PONTO",
}

# ---------------------------------------------------------------------------
# Scanner principal
# ---------------------------------------------------------------------------

class Scanner:
    """Varre o código-fonte e produz uma lista de Tokens."""

    def __init__(self, codigo: str) -> None:
        self._src = codigo
        self._pos = 0          # posição atual na string
        self._linha = 1
        self._coluna = 1
        self._tokens: List[Token] = []

    # --- helpers de navegação ---

    def _atual(self) -> str | None:
        return self._src[self._pos] if self._pos < len(self._src) else None

    def _proximo(self) -> str | None:
        p = self._pos + 1
        return self._src[p] if p < len(self._src) else None

    def _avancar(self) -> str:
        ch = self._src[self._pos]
        self._pos += 1
        if ch == "\n":
            self._linha += 1
            self._coluna = 1
        else:
            self._coluna += 1
        return ch

    def _adicionar(self, tipo: str, lexema: str, linha: int, coluna: int,
                   mensagem: str | None = None) -> None:
        self._tokens.append(Token(tipo, lexema, linha, coluna, mensagem))

    # --- tokenizadores específicos ---

    def _pular_espacos_e_comentarios(self) -> None:
        while self._atual() is not None:
            ch = self._atual()
            if ch in (" ", "\t", "\r", "\n"):
                self._avancar()
            elif ch == "#":
                # comentário de linha — consome até \n
                while self._atual() is not None and self._atual() != "\n":
                    self._avancar()
            else:
                break

    def _ler_numero(self) -> None:
        linha, coluna = self._linha, self._coluna
        lexema = ""
        while self._atual() is not None and self._atual().isdigit():
            lexema += self._avancar()
        # ponto flutuante?
        if self._atual() == "." and (self._proximo() or "").isdigit():
            lexema += self._avancar()  # consome '.'
            while self._atual() is not None and self._atual().isdigit():
                lexema += self._avancar()
            self._adicionar("LITERAL_FLOAT", lexema, linha, coluna)
        else:
            self._adicionar("LITERAL_INTEIRO", lexema, linha, coluna)

    def _ler_string(self) -> None:
        linha, coluna = self._linha, self._coluna
        delim = self._avancar()  # ' ou "
        lexema = delim
        fechou = False
        while self._atual() is not None:
            ch = self._atual()
            if ch == "\n":
                # string não fechada antes de nova linha
                break
            lexema += self._avancar()
            if ch == delim:
                fechou = True
                break
        if fechou:
            self._adicionar("LITERAL_STRING", lexema, linha, coluna)
        else:
            self._adicionar(
                "ERRO_LEXICO", lexema, linha, coluna,
                f"String não fechada iniciada na linha {linha}, coluna {coluna}.",
            )

    def _ler_identificador(self) -> None:
        linha, coluna = self._linha, self._coluna
        lexema = ""
        while self._atual() is not None and (self._atual().isalnum() or self._atual() == "_"):
            lexema += self._avancar()
        tipo = "PALAVRA_RESERVADA" if lexema in PALAVRAS_RESERVADAS else "IDENTIFICADOR"
        self._adicionar(tipo, lexema, linha, coluna)

    def _ler_operador(self) -> bool:
        linha, coluna = self._linha, self._coluna
        resto = self._src[self._pos:]
        for op in OPERADORES_COMPOSTOS:
            if resto.startswith(op):
                for _ in op:
                    self._avancar()
                self._adicionar("OPERADOR", op, linha, coluna)
                return True
        for op in OPERADORES_SIMPLES:
            if resto.startswith(op):
                self._avancar()
                self._adicionar("OPERADOR", op, linha, coluna)
                return True
        return False

    # --- varredura principal ---

    def tokenizar(self) -> list[dict]:
        while self._atual() is not None:
            self._pular_espacos_e_comentarios()
            if self._atual() is None:
                break

            ch = self._atual()
            linha, coluna = self._linha, self._coluna

            # número
            if ch.isdigit():
                self._ler_numero()
                continue

            # string
            if ch in ('"', "'"):
                self._ler_string()
                continue

            # identificador / palavra reservada
            if ch.isalpha() or ch == "_":
                self._ler_identificador()
                continue

            # delimitador
            if ch in DELIMITADORES:
                self._avancar()
                self._adicionar(DELIMITADORES[ch], ch, linha, coluna)
                continue

            # operador
            if self._ler_operador():
                continue

            # ponto flutuante que começa com '.' (ex.: .5)
            if ch == "." and (self._proximo() or "").isdigit():
                self._ler_numero()
                continue

            # caractere não reconhecido
            self._avancar()
            self._adicionar(
                "ERRO_LEXICO", ch, linha, coluna,
                f"Erro léxico na linha {linha}, coluna {coluna}: "
                f"caractere não reconhecido '{ch}'. "
                f"Verifique se ele faz parte do subconjunto suportado.",
            )

        return [t.to_dict() for t in self._tokens]


# ---------------------------------------------------------------------------
# Função pública
# ---------------------------------------------------------------------------

def analisar_lexico(codigo: str) -> dict:
    """Executa o scanner e retorna o resultado estruturado.

    Retorna:
        {
            "sucesso": bool,   # False se houver qualquer ERRO_LEXICO
            "tokens": [...],   # todos os tokens (inclusive os de erro)
            "erros": [...],    # apenas os tokens com tipo ERRO_LEXICO
        }
    """
    todos = Scanner(codigo).tokenizar()
    erros = [t for t in todos if t["tipo"] == "ERRO_LEXICO"]
    tokens = [t for t in todos if t["tipo"] != "ERRO_LEXICO"]
    return {
        "sucesso": len(erros) == 0,
        "tokens": tokens,
        "erros": erros,
    }
