from dataclasses import dataclass
from tokens import TokenType
from errors import ParserError, EvaluationError


# Nodos del árbol sintáctico abstracto (AST).
@dataclass
class Number:
    value: float


@dataclass
class Variable:
    name: str


@dataclass
class Unary:
    operator: str
    operand: object


@dataclass
class Binary:
    left: object
    operator: str
    right: object


@dataclass
class Assignment:
    name: str
    expression: object


class Parser:
    """
    Parser descendente recursivo.

    Gramática (EBNF):
        programa      = { asignacion } ;
        asignacion    = IDENTIFIER, "=", expresion, ";" ;
        expresion     = termino, { ("+" | "-"), termino } ;
        termino       = factor, { ("*" | "/"), factor } ;
        factor        = NUMBER
                      | IDENTIFIER
                      | ("+" | "-"), factor
                      | "(", expresion, ")" ;
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def _current(self):
        return self.tokens[self.position]

    def _check(self, token_type):
        return self._current().type == token_type

    def _advance(self):
        token = self._current()
        if token.type != TokenType.EOF:
            self.position += 1
        return token

    def _expect(self, token_type, description):
        if not self._check(token_type):
            token = self._current()
            found = token.lexeme if token.lexeme else "fin del archivo"
            raise ParserError(
                f"Se esperaba {description}, pero se encontró {found!r} "
                f"en línea {token.line}, columna {token.column}."
            )
        return self._advance()

    def parse(self):
        statements = []
        while not self._check(TokenType.EOF):
            statements.append(self._assignment())
        return statements

    def _assignment(self):
        name = self._expect(TokenType.IDENTIFIER, "un identificador").lexeme
        self._expect(TokenType.ASSIGN, "'='")
        expression = self._expression()
        self._expect(TokenType.SEMICOLON, "';' al final de la instrucción")
        return Assignment(name, expression)

    def _expression(self):
        node = self._term()
        while self._check(TokenType.PLUS) or self._check(TokenType.MINUS):
            operator = self._advance().lexeme
            right = self._term()
            node = Binary(node, operator, right)
        return node

    def _term(self):
        node = self._factor()
        while self._check(TokenType.MULTIPLY) or self._check(TokenType.DIVIDE):
            operator = self._advance().lexeme
            right = self._factor()
            node = Binary(node, operator, right)
        return node

    def _factor(self):
        if self._check(TokenType.NUMBER):
            return Number(float(self._advance().lexeme))

        if self._check(TokenType.IDENTIFIER):
            return Variable(self._advance().lexeme)

        if self._check(TokenType.PLUS) or self._check(TokenType.MINUS):
            operator = self._advance().lexeme
            return Unary(operator, self._factor())

        if self._check(TokenType.LPAREN):
            self._advance()
            node = self._expression()
            self._expect(TokenType.RPAREN, "')'")
            return node

        token = self._current()
        found = token.lexeme if token.lexeme else "fin del archivo"
        raise ParserError(
            f"Se esperaba un número, variable o '(', pero se encontró {found!r} "
            f"en línea {token.line}, columna {token.column}."
        )


def evaluate(node, variables):
    if isinstance(node, Number):
        return node.value

    if isinstance(node, Variable):
        if node.name not in variables:
            raise EvaluationError(f"La variable {node.name!r} no tiene un valor asignado.")
        return variables[node.name]

    if isinstance(node, Unary):
        value = evaluate(node.operand, variables)
        return value if node.operator == "+" else -value

    if isinstance(node, Binary):
        left = evaluate(node.left, variables)
        right = evaluate(node.right, variables)

        if node.operator == "+":
            return left + right
        if node.operator == "-":
            return left - right
        if node.operator == "*":
            return left * right
        if node.operator == "/":
            if right == 0:
                raise EvaluationError("No se puede dividir entre cero.")
            return left / right

    raise EvaluationError("No se pudo evaluar la expresión.")


def format_number(value):
    if float(value).is_integer():
        return str(int(value))
    return str(value)
