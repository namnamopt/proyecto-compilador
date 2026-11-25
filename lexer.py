from tokens import Token, TokenType
from errors import LexerError


class Lexer:
    """
    Analizador léxico de Mini-Calc.

    Los bucles de reconocimiento implementan autómatas finitos:
    - Identificador: [A-Za-z_][A-Za-z0-9_]*
    - Número: dígitos, opcionalmente seguidos de punto y más dígitos
    """

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    def _current(self):
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def _advance(self):
        char = self._current()
        if char is not None:
            self.position += 1
            if char == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        return char

    def _read_number(self):
        start = self.position
        line, column = self.line, self.column

        while self._current() is not None and self._current().isdigit():
            self._advance()

        if self._current() == ".":
            dot_position = self.position
            self._advance()
            if self._current() is None or not self._current().isdigit():
                raise LexerError(
                    f"Número decimal incompleto en línea {line}, columna {column}."
                )
            while self._current() is not None and self._current().isdigit():
                self._advance()

        lexeme = self.source[start:self.position]
        return Token(TokenType.NUMBER, lexeme, line, column)

    def _read_identifier(self):
        start = self.position
        line, column = self.line, self.column

        # Estado inicial: letra o guion bajo.
        self._advance()
        # Estado de continuación: letra, dígito o guion bajo.
        while self._current() is not None and (
            self._current().isalnum() or self._current() == "_"
        ):
            self._advance()

        return Token(
            TokenType.IDENTIFIER,
            self.source[start:self.position],
            line,
            column,
        )

    def tokenize(self):
        tokens = []

        single_char_tokens = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLY,
            "/": TokenType.DIVIDE,
            "=": TokenType.ASSIGN,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            ";": TokenType.SEMICOLON,
        }

        while self._current() is not None:
            char = self._current()

            if char.isspace():
                self._advance()
                continue

            if char.isdigit():
                tokens.append(self._read_number())
                continue

            if char.isalpha() or char == "_":
                tokens.append(self._read_identifier())
                continue

            if char in single_char_tokens:
                line, column = self.line, self.column
                self._advance()
                tokens.append(Token(single_char_tokens[char], char, line, column))
                continue

            raise LexerError(
                f"Carácter no reconocido {char!r} en línea {self.line}, "
                f"columna {self.column}."
            )

        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens
