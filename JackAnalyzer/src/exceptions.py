class TokenizerError(Exception):
  def __init__(self, message: str, row: int, column: int) -> None:
    full_message = TokenizerError._message(message, row, column)
    super().__init__(full_message)


  @staticmethod
  def _message(message, row, column) -> str:
    return f'[TokenizerError] While tokenizing a Jack file, the following exception occured. [Line {row} Character {column}] {message}'

class ParserError(Exception):
  def __init__(self, message: str, row: int = 0, column: int = 0) -> None:
    full_message = ParserError._message(message, row, column)
    super().__init__(full_message)

  @staticmethod
  def _message(message, row, column) -> str:
    return f'[ParserError] While parsing a Jack file, the following exception occured. [Line {row} Character {column}] {message}'
