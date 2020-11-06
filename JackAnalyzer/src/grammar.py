from dataclasses import dataclass

class GrammarObject():
  _keywords : list
  _ptr      : int
  children  : list

  def deposit(self, obj: Union[Token, GrammarObject]) -> None:
    if self._ptr > len(self._keywords):
      raise ParserError('Statement!', obj.line, obj.word)

    expected = self._expected()
    self._deposit(obj, expected)
    self._ptr += 1


  def _deposit(self, obj: Union[Token, GrammarObject, dict], expected: Union[str, GrammarObject, dict] -> None:
    if type(obj) not in [Token, GrammarObject, dict]:
      raise ParserError('Statement!')
    elif type(obj) == Token and type(expected) == str and obj.value != expected: 
      raise ParserError('Statement!')
    elif type(obj) != type(expected):
      raise ParserError('Statement!')

    if type(obj) == dict:
      if 'optional' not in obj or 'optional' not in expected or len(obj['optional']) != len(expected['optional']:
        raise ParserError('Statement!')
        
      for a, b in zip(obj['optional'], expected['optional']):
        self._deposit(a, b)

    self.children.append(token)


  def _expected_keyword(self) -> str:
    if self._ptr >= len(self._keywords):
      raise ParserError()

    return self._keywords[self._ptr]


class AClass(GrammarObject):
  def __init__(self) -> None:
    self._keywords = ['class', Identifier, '{', {'optional': [ClassVariableList]}, {'optional': [SubroutineList]}, '}']
    self._ptr = 0
    self.children = []


# let identifier([expression])? = expression;
class letStatement(GrammarObject):
  def __init__(self) -> None:
    self._keywords = ['let', Identifier, {'optional': ['[', Expression, ']']},'=', Expression, ';'] 
    self._ptr = 0
    self.children = []

# if (expression) { statement* } else { statement* }
class ifStatement(GrammarObject):
  def __init__(self) -> None:
    self._keywords = ['if', '(', Expression, ')', '{', Statements, '}', 'else', '{', Statements, '}']
    self._ptr = 0
    self.children = []

# while (expression) { statement* }
class whileStatement(GrammarObject):
  def __init__(self) -> None:
    self._keywords = ['while', '(', Expression, ')', '{', Statements, '}']
    self._ptr = 0
    self.children = []

# do subroutineCall;
class doStatement(GrammarObject):
  def __init__(self) -> None:
    self._keywords = ['do', SubroutineCall, ';']
    self._ptr = 0
    self.children = []

# return expression?;
class returnStatement(GrammarObject):
  def __init__(self) -> None:
    self._keywords = ['return', {'optional': [Expression]}, ';']
    self._ptr = 0
    self.children = []

# (constructor | function | method) type identifier (parameter*) { localVariable* statement* }
class Subroutine(GrammarObject):
  def __init__(self) -> None:
    self._keywords = [subroutine_types, data_types, Identifier, '(', {'optional': [ParameterList]}, ')', '{', {'optional': [LocalVariableList, Statements]}, '}']
    self._ptr = 0
    self.children = []


data_types = set(['int', 'char', 'boolean', 'void', Identifier])
subroutine_types = set(['constructor', 'function', 'method'])

@dataclass
class SubroutineList():
  _data: list[Subroutine]

  def __getitem__(self, key) -> Subroutine:
    return self._data[key]


  def __iter__(self):
    return iter(self._data)

@dataclass
class ClassVariableList():
  _data: list[ClassVariable]

  def __getitem__(self, key) -> ClassVariable:
    return self._data[key]


  def __iter__(self):
    return iter(self._data)
