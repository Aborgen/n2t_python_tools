from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Tuple
from .utils import is_symbol
from .utils import iterate_enum

class Command(ABC):
  @abstractmethod
  def _segment_command(self, command: str) -> Tuple:
    return

  
  @abstractmethod
  def _invalid_format(self, message: str = '') -> Exception:
    return


  @abstractmethod
  def __str__(self) -> str:
    return

  
  @abstractmethod
  def __rpr__(self) -> str:
    return


class ArithmeticCommand(Command):
  class EKeyword(Enum):
    ADD = 'add'
    SUB = 'sub'
    LT  = 'lt'
    EQ  = 'eq'
    GT  = 'gt'
    NEG = 'neg'
    def __str__(self) -> str:
      return self.name


  def __init__(self, command: str):
    self.keyword, self.arg_count = self._segment_command(command)
    

  def _segment_command(self, command: str) -> Tuple[str, int]:
    words = command.split(' ')
    keyword = iterate_enum(self.EKeyword, words[0])

    err = None
    if len(words) > 1:
      err = 'Arithmetic commands can be at most 1 word long'
    elif not keyword:
      err = 'Unknown keyword: {keyword}'

    if err:
      raise self._invalid_format(f'{err}, full command: {command}')

    arg_count = self._number_of_arguments(keyword)
    return (keyword, arg_count)


  def _number_of_arguments(self, keyword: EKeyword) -> int:
    if keyword == self.EKeyword.NEG:
      return 1
    else:
      return 2


  def _invalid_format(self, message: str = '') -> Exception:
    return Exception(f'Invalid ArithmeticCommand: {message}')


  def __str__(self) -> str:
    return self.keyword.value


  def __rpr__(self) -> str:
    return f'Command [type: {type(self)}], keyword: {self.keyword}'
  

class LogicalCommand(Command):
  class EKeyword(Enum):
    AND = 'and'
    OR  = 'or'
    NOT = 'not'
    def __str__(self) -> str:
      return self.name
    

  def __init__(self, command: str):
    self.keyword, self.arg_count = self._segment_command(command)


  def _segment_command(self, command: str) -> Tuple[str, int]:
    words = command.split(' ')
    keyword = iterate_enum(self.EKeyword, words[0])

    err = None
    if len(words) > 1:
      err = 'Logical commands can be at most 1 word long'
    elif not keyword:
      err = 'Unknown keyword: {keyword}'

    if err:
      raise self._invalid_format(f'{err}, full command: {command}')

    arg_count = self._number_of_arguments(keyword)
    return (keyword, arg_count)


  def _number_of_arguments(self, keyword: EKeyword) -> int:
    if keyword == self.EKeyword.NOT:
      return 1
    else:
      return 2


  def _invalid_format(self, message: str = '') -> Exception:
    return Exception(f'Invalid LogicalCommand: {message}')


  def __str__(self) -> str:
    return self.keyword.value


  def __rpr__(self) -> str:
    return f'Command [type: {type(self)}], keyword: {self.keyword}'


class FlowCommand(Command):
  class EKeyword(Enum):
    LABEL   = 'label'
    GOTO    = 'goto'
    IF_GOTO = 'if-goto'
    def __str__(self) -> str:
      return self.name


  def __init__(self, command: str):
    self.keyword, self.symbol = self._segment_command(command)


  def _segment_command(self, command: str) -> Tuple[str, str]:
    words = command.split(' ')
    keyword = iterate_enum(self.EKeyword, words[0])
    symbol = words[1]

    err = []
    if not keyword:
      err.append(f'Unknown keyword: {keyword}')
    if not is_symbol(symbol):
      err.append(f'Invalid symbol provided: {symbol}')
    if err:
      message = f"{', '.join(err)}, full command: {command}"
      raise self._invalid_format(message)

    return (keyword, symbol)


  def _invalid_format(self, message: str = '') -> Exception:
    return Exception(f'FlowCommand error: {message}')


  def __str__(self) -> str:
    return f'{self.keyword.value} {self.symbol}'


  def __rpr__(self) -> str:
    return f'Command [type: {type(self)}], keyword: {self.keyword}, symbol: {self.symbol}'


class MemoryCommand(Command):
  class EKeyword(Enum):
    PUSH = 'push'
    POP  = 'pop'
    def __str__(self) -> str:
      return self.name


  class ESegment(Enum):
    ARG      = 'argument'
    LCL      = 'local'
    THIS     = 'this'
    THAT     = 'that'
    POINTER  = 'pointer'
    TEMP     = 'temp'
    STATIC   = 'static'
    CONSTANT = 'constant'
    def __str__(self) -> str:
      return self.name


  def __init__(self, command: str):
    self.keyword, self.segment, self.index = self._segment_command(command)


  def _segment_command(self, command: str) -> Tuple[str, str, int]:
    words = command.split(' ')
    keyword = iterate_enum(self.EKeyword, words[0])
    segment = iterate_enum(self.ESegment, words[1])
    index   = words[2]

    err = []
    if not keyword:
      err.append(f'Unknown keyword: {keyword}')
    if not segment:
      err.append(f'Unknown segment: {segment}')
    try:
      index = int(index)
    except:
      err.append(f'Index is not a number: {index}')

    if err:
      message = f"{', '.join(err)}, full command: {command}"
      raise self._invalid_format(message)

    return (keyword, segment, index)


  def _invalid_format(self, message: str = '') -> Exception:
    return Exception(f'MemoryCommand error: {message}')


  def __str__(self) -> str:
    return f'{self.keyword.value} {self.segment.value} {self.index}'


  def __rpr__(self) -> str:
    return f'Command [type: {type(self)}], keyword: {self.keyword}, segment: {self.segment}, index: {self.index}'


class FunctionCommand(Command):
  class EKeyword(Enum):
    FUNCTION = 'function'
    CALL     = 'call'
    RETURN   = 'return'
    def __str__(self) -> str:
      return self.name


  saveable_memory_segments = [
    MemoryCommand.ESegment.LCL,
    MemoryCommand.ESegment.ARG,
    MemoryCommand.ESegment.THIS,
    MemoryCommand.ESegment.THAT
  ]


  def __init__(self, command: str):
    self.keyword, self.function_name, self.variable_count = self._segment_command(command)



  def _segment_command(self, command: str) -> Tuple[str, str, int]:
    words = command.split(' ')
    keyword = iterate_enum(self.EKeyword, words[0])

    err = []
    if not keyword:
      err.append(f'Unknown keyword: {keyword}')

    function_name = variable_count = None
    if len(words) > 1:
      function_name = words[1]
      variable_count = words[2]
      if not is_symbol(function_name):
        err.append(f'Invalid function name: {function_name}')
      try:
        variable_count = int(variable_count)
      except:
        err.append(f'Variable count is not a number: {variable_count}')

    if err:
      message = f"{', '.join(err)}, full command: {command}"
      raise self._invalid_format(message)

    return (keyword, function_name, variable_count)


  def _invalid_format(self, message: str = '') -> Exception:
    return Exception(f'FunctionCommand error: {message}')


  def __str__(self) -> str:
    s = '' if not self.function_name else f' {self.function_name} {self.variable_count}'
    return self.keyword.value + s


  def __rpr__(self) -> str:
    return f'Command [type: {type(self)}], keyword: {self.keyword}, function: {self.function_name}, nArgs: {self.variable_count}'
