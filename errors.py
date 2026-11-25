class MiniCalcError(Exception):
    """Error base del lenguaje Mini-Calc."""


class LexerError(MiniCalcError):
    """Error durante el análisis léxico."""


class ParserError(MiniCalcError):
    """Error durante el análisis sintáctico."""


class EvaluationError(MiniCalcError):
    """Error al evaluar una expresión."""
