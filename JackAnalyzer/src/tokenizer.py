from dataclasses import dataclass
from enum import Enum
from typing import Generator, Optional
from io import BufferedIOBase

from .categories import keywords, symbols
from .categories import is_integer_constant, is_string_constant, is_identifier
from .exceptions import TokenizerError
from .utils import clean_string_constant

@dataclass
class Token():
  value     : str
  tokenType : str
  line      : int
  word      : int


class Tokenizer():
  class EStatus(Enum):
    ONGOING  = 1
    FINISHED = 2

  _filename  : str
  _row       : int
  _column    : int
  _generator : Generator[Token, None, None]
  _status    : EStatus


  def __init__(self, filename: str) -> None:
    self._filename = filename
    self._row = 1
    self._column = 1
    self._generator = self._init_generator()
    self._status = self.EStatus.ONGOING


  def _init_generator(self) -> None:
    try:
      with open(self._filename, 'r') as f:
        word = ''
        for row, line in enumerate(f, start=1):
          # Need to do this, since words cannot spread over multiple lines. Must be done before updating self._row.
          if len(word) != 0:
            yield word
            word = ''

          self._row = row
          line = line.rstrip('\n')

          inside_string_constant = False
          for column, char in enumerate(line, start=1):
            if not inside_string_constant:
              if char == '"':
                inside_string_constant = True
              elif char in symbols or char == ' ':
                if len(word) > 0:
                  yield word
                  word = ''
                if char in symbols:
                  # Keep track of position of symbols, since this branch bypasses where this would normally happen
                  self._column = column
                  yield char

                continue
            # Allow double quotes inside string constant only in the case that it is escaped (\")
            elif inside_string_constant and char == '"' and word[-1] != '\\':
              inside_string_constant = False

            word += char
            # Keep track of the beginning of each word
            if len(word) == 1:
              self._column = column
          
      if len(word) != 0:
        self._status = self.EStatus.FINISHED
        yield word
    except FileNotFoundError as e:
      self._handle_bad_file(e)
    

  def finished(self) -> bool:
    return self._status == self.EStatus.FINISHED


  def next(self) -> Optional[Token]:
    if self._status == self.EStatus.FINISHED:
      raise TokenizerError('There are no more tokens. Finished.', 0, 0)

    try:
      word = next(self._generator)
    except StopIteration:
      return None

    token = Token(word, 'temp', self._row, self._column)
    if word in keywords:
      token.tokenType = 'keyword'
    elif word in symbols:
      token.tokenType = 'symbol'
    elif is_integer_constant(word):
      token.tokenType = 'intConst'
    elif is_string_constant(word):
      token.value = clean_string_constant(word)
      token.tokenType = 'stringConst'
    elif is_identifier(word):
      token.tokenType = 'identifier'
    else:
      cutoff = 100
      raise TokenizerError(f'Token not recognized: {word[:cutoff] + "..." if len(word) > cutoff else word}', self._row, self._column)

    return token


  def _handle_bad_file(self, e: FileNotFoundError) -> None:
    e.strerror += '\n' + TokenizerError._message(f'File does not exist. Ensure that the provided file is a .jack file and that the file actually exists', self._row, self._column)
    e.filename = f'(Cannot open {self._filename})'
    raise e
