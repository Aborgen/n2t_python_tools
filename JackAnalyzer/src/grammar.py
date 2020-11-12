import inspect
from dataclasses import dataclass

from .tokenizer import Token

class ExpectedToken(Token):
  def __init__(self, value: str, token_type: str) -> None:
    super()__init__(value, token_type, -1, -1)

class GrammarObject():
  _keywords : list
  _ptr      : int
  children  : Union[list[GrammarObject], str]

  def __init__(self) -> None:
    self._keywords = []
    self._ptr = 0
    self.children = []


  def __init__(self, children: Union[list[GrammarObject], str]) -> None:
    self.children = children


  def deposit(self, obj: Union[Token, GrammarObject]) -> None:
    if self._ptr > len(self._keywords) - 1:
      raise 'Tried to deposit too many objects'

    expected = self._expected()
    self._deposit(obj, expected)
    self._ptr += 1


  def _deposit(self, obj: Union[Token, GrammarObject, dict], expected: Union[ExpectedToken, GrammarObject, dict] -> None:
    if not _is_comparable(obj, expected):
      raise ParserError('Statement!')

    if type(obj) == Token:
      obj = GrammarObject(obj.value)
    elif type(obj) == dict:
      if 'optional' not in obj or 'optional' not in expected or len(obj['optional']) != len(expected['optional']:
        raise ParserError('Statement!')
        
      for a, b in zip(obj['optional'], expected['optional']):
        self._deposit(a, b)

    self.children.append(obj)


  def _is_comparable(self, obj: Union[Token, GrammarObject, dict], expected: Union[ExpectedToken, GrammarObject, dict] -> bool:
    if type(obj) == Token and expected == ExpectedToken:
      return obj.value == expected.value and obj.token_type == expected.token_type
    elif type(obj) == dict and expected == dict:
      return 'optional' in obj and 'optional' in expected and len(obj['optional']) == len(expected['optional'])
    else:
      return inspect.isclass(expected) and isinstance(obj, expected)


  def _expected_keyword(self) -> str:
    if self._ptr > len(self._keywords) - 1:
      raise ParserError()

    return self._keywords[self._ptr]


# class identifier { class_variable_declaration* subroutine* }
class AClass(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [ExpectedToken('class', 'keyword'), Identifier, ExpectedToken('{', 'symbol'), ClassVariableList, SubroutineList, ExpectedToken('}', 'symbol')]

# let identifier([expression])? = expression;
class letStatement(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [ExpectedToken('let', 'keyword'), Identifier, {'optional': [ExpectedToken('[', 'symbol'), Expression, ExpectedToken(']', 'symbol')]},ExpectedToken('=', 'symbol'), Expression, ExpectedToken(';', 'symbol')] 

# if (expression) { statement* } (else { statement* })?
class ifStatement(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [ExpectedToken('if', 'keyword'), ExpectedToken('(', 'symbol'), Expression, ExpectedToken(')', 'symbol'), ExpectedToken('{', 'symbol'), Statements, ExpectedToken('}', 'symbol'), {'optional': [ExpectedToken('else', 'keyword'), ExpectedToken('{', 'symbol'), Statements, ExpectedToken('}', 'symbol')}]

# while (expression) { statement* }
class whileStatement(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [ExpectedToken('while', 'keyword'), ExpectedToken('(', 'symbol', Expression, ExpectedToken(')', 'symbol'), ExpectedToken('{', 'symbol'), Statements, ExpectedToken('}', 'symbol')]

# do subroutineCall;
class doStatement(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [ExpectedToken('do', 'keyword'), SubroutineCall, ExpectedToken(';', 'symbol')]

# return expression?;
class returnStatement(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [ExpectedToken('return', 'keyword'), {'optional': [Expression]}, ExpectedToken(';', 'symbol')]

# (constructor | function | method) type identifier (parameter*) { localVariable* statement* }
class Subroutine(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [SubroutineType, DataType, Identifier, ExpectedToken('(', 'symbol'), {'optional': [ParameterList]}, ExpectedToken(')', 'symbol'), ExpectedToken('{', 'symbol'), {'optional': [LocalVariableList, Statements]}, ExpectedToken('}', 'symbol')]


  def deposit(self, obj: Union[Token, GrammarObject, dict]) -> None:
    if self._ptr > len(self._keywords) - 1:
      raise 'Tried to deposit too many objects'

    expected = self._expected()
    if type(obj) == ExpectedToken and expected.value in ['subroutine_type', 'data_type']:
      if expected.value == 'subroutine_type' and not validate_subroutine_type(obj.value):
        raise ParserError()
      elif expected.value == 'data_type' and not validate_data_type(obj.value):
        raise ParserError()

      expected.value, expected.token_type = obj.value, obj.token_type

    self._deposit(obj, expected)
    self._ptr += 1
    
class DataType(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [{'any': [ExpectedToken('int', 'keyword'), ExpectedToken('char', 'keyword'), ExpectedToken('boolean', 'keyword'), Identifier}]

class SubroutineType(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [{'any': [ExpectedToken('constructor', 'keyword'), ExpectedToken('function', 'keyword'), ExpectedToken('method', 'keyword')]}]

class VariableType(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [{'any': [ExpectedToken('static', 'field')}]

class Identifier(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [ExpectedToken('', 'identifier')]


  def deposit(self, obj: Token) -> None:
    if not type(obj) == Token or not obj.token_type == 'identifier'):
      raise ParserError()

    self._keywords[0].value = obj.value
    super().deposit(obj)

class ClassVariable(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [VariableType, DataType, Identifier, {'optional-repeat': [ExpectedToken(',', 'symbol'), Identifier]}, ExpectedToken(';', 'symbol')]

class Subroutine(GrammarObject):
  def __init__(self) -> None:
    super().__init__()
    self._keywords = [SubroutineType, {'any': ['void', DataType]}, Identifier, ExpectedToken('(', 'symbol'), ParameterList, ExpectedToken(')', 'symbol'), SubroutineBody]

