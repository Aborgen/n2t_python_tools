import inspect
from dataclasses import dataclass

from .tokenizer import Token


class GrammarObject():
  _keywords : list
  _ptr      : int
  children  : Union[list[GrammarObject], str]
  label:    : str

  def __init__(self, keywords: Union[list[GrammarObject], str], label: str) -> None:
    self._keywords = keywords
    self._ptr = 0
    self.children = []
    self.label = label


  def __init__(self, children: Union[list[GrammarObject], str]) -> None:
    self.children = children


  def deposit(self, obj: Union[Token, GrammarObject]) -> None:
    if self._ptr > len(self._keywords) - 1:
      raise 'Tried to deposit too many objects'

    expected = self._expected()
    self._deposit(obj, expected)


  def _deposit(self, obj: Union[Token, GrammarObject, dict], expected: Union[Token, GrammarObject, dict] -> None:
    if not _is_comparable(obj, expected):
      raise ParserError('Statement!')

    if type(expected) == Token:
      obj = GrammarObject(children=obj.value)
    elif type(expected) == dict:
      key = list(expected.keys())[0]
      if key == 'optional':
        self._deposit_group(obj, expected[key])
      elif key == 'optional-repeat':
        if type(obj) != list:
          raise ParserError()

        for group in obj:
          self._deposit_group(group, expected[key])
      elif key == 'any' and obj not in expected[key]:
        raise ParserError(f'Not a correct option: {obj} not among [{", ".join(expected[key]}]')
      else:
        raise ParserError(f'Unrecognized key: {key}')

    self._ptr += 1
    self.children.append(obj)


    def _deposit_group(self, group: list, template: list) -> None:
      if type(group) != list or type(template) != list:
        raise ParserError('Must be list')
      elif len(group) != len(template):
        raise ParserError('Must be same length')

      for a, b in zip(group, template):
        self._deposit(a, b)


  def _is_comparable(self, obj: Union[Token, GrammarObject, dict], expected: Union[Token, GrammarObject, dict] -> bool:
    if type(obj) == Token and type(expected) == Token:
      return obj == expected
    elif type(expected) == dict:
      if len(expected) != 1:
        raise 'Dict should only have one key'
      else:
        return True
    else:
      return inspect.isclass(expected) and isinstance(obj, expected)


  def _expected_keyword(self) -> str:
    if self._ptr > len(self._keywords) - 1:
      raise ParserError()

    return self._keywords[self._ptr]


# class identifier { class_variable_declaration* subroutine* }
class AClass(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('class', 'keyword'), Identifier, Token('{', 'symbol'), ClassVariableList, SubroutineList, Token('}', 'symbol')]
    super().__init__('class', keywords)

# let identifier([expression])? = expression;
class letStatement(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('let', 'keyword'), Identifier, {'optional': [Token('[', 'symbol'), Expression, Token(']', 'symbol')]}, Token('=', 'symbol'), Expression, Token(';', 'symbol')] 
    super().__init__('letStatement', keywords)

# if (expression) { statement* } (else { statement* })?
class ifStatement(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('if', 'keyword'), Token('(', 'symbol'), Expression, Token(')', 'symbol'), Token('{', 'symbol'), Statements, Token('}', 'symbol'), {'optional': [Token('else', 'keyword'), Token('{', 'symbol'), Statements, Token('}', 'symbol')}]
    super().__init__('ifStatement', keywords)

# while (expression) { statement* }
class whileStatement(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('while', 'keyword'), Token('(', 'symbol', Expression, Token(')', 'symbol'), Token('{', 'symbol'), Statements, Token('}', 'symbol')]
    super().__init__('whileStatement', keywords)

# do subroutineCall;
class doStatement(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('do', 'keyword'), SubroutineCall, Token(';', 'symbol')]
    super().__init__('doStatement', keywords)

# return expression?;
class returnStatement(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('return', 'keyword'), {'optional': [Expression]}, Token(';', 'symbol')]
    super().__init__('returnStatement', keywords)

# (constructor | function | method) type identifier (parameter*) { localVariable* statement* }
class Subroutine(GrammarObject):
  def __init__(self) -> None:
    keywords = [SubroutineType, DataType, Identifier, Token('(', 'symbol'), {'optional': [ParameterList]}, Token(')', 'symbol'), SubroutineBody]
    super().__init__('subroutineDec', keywords)


  def deposit(self, obj: Union[Token, GrammarObject, dict]) -> None:
    if self._ptr > len(self._keywords) - 1:
      raise 'Tried to deposit too many objects'

    expected = self._expected()
    if type(expected) == Token and type(obj) == Token and expected.value in ['subroutine_type', 'data_type']:
      if expected.value == 'subroutine_type' and not validate_subroutine_type(obj.value):
        raise ParserError()
      elif expected.value == 'data_type' and not validate_data_type(obj.value):
        raise ParserError()

      expected.value, expected.token_type = obj.value, obj.token_type

    self._deposit(obj, expected)
    self._ptr += 1
    
class ParameterList(GrammarObject):
  def __init__(self) -> None:
    keywords = [DataType, Identifier, {'optional-repeat': [Token(',', 'symbol'), Identifier]}]
    super().__init__('parameterList', keywords)

class SubroutineBody(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('{', 'symbol'), {'optional': [LocalVariableList]}, {'optional': [Statements]}, Token('}', 'symbol')]
    super().__init__('subroutineBody', keywords)


class DataType(GrammarObject):
  def __init__(self) -> None:
    keywords = [{'any': [Token('int', 'keyword'), Token('char', 'keyword'), Token('boolean', 'keyword'), Identifier}]
    super().__init__(None, keywords)

class SubroutineType(GrammarObject):
  def __init__(self) -> None:
    keywords = [{'any': [Token('constructor', 'keyword'), Token('function', 'keyword'), Token('method', 'keyword')]}]
    super().__init__(None, keywords)

class VariableType(GrammarObject):
  def __init__(self) -> None:
    keywords = [{'any': [Token('static', 'field')}]
    super().__init__(None, keywords)

class Identifier(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('', 'identifier')]
    super().__init__(None, keywords)


  def deposit(self, obj: Token) -> None:
    if not type(obj) == Token or not obj.token_type == 'identifier'):
      raise ParserError()

    self._keywords[0].value = obj.value
    super().deposit(obj)

class ClassVariable(GrammarObject):
  def __init__(self) -> None:
    keywords = [VariableType, DataType, Identifier, {'optional-repeat': [Token(',', 'symbol'), Identifier]}, Token(';', 'symbol')]
    super().__init__('classVarDec', keywords)

class SubroutineVariable(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('var', 'keyword'), DataType, Identifier, {'optional-repeat': [Token(',', 'symbol'), Identifier]}, Token(';', 'symbol')]
    super().__init__('varDec', keywords)

class Statements(GrammarObject):
  def __init__(self) -> None:
    keywords = [{'optional-repeat': [{'any': [letStatement, ifStatement, whileStatement, returnStatement]}]}]]}]
    super().__init__('varDec', keywords)

class Term(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'any': [
        Token('', 'integerConst'),
        Token('', 'stringConst'),
        Token('true', 'keyword'),
        Token('false', 'keyword'),
        Token('null', 'keyword'),
        Token('this', 'keyword'),
        Token('-', 'symbol'),
        Token('~', 'keyword'),
        Identifier, SubroutineCall,
        { 'group': [Identifier, Token('(', 'symbol'), Expression, Token(')', 'symbol')] },
        { 'group': [Identifier, Token('[', 'symbol'), Expression, Token(']', 'symbol')] },
      ]},
      Term
    ]
    super().__init__('term', keywords)


  def deposit(self, obj: Union[Token, GrammarObject]) -> None:
    if self._ptr > len(self._keywords) - 1:
      raise 'Tried to deposit too many objects'

    expected = self._expected()
    if type(expected) == Token and type(obj) == Token
      if (obj.token_type == 'integerConst' and expected.token_type == 'integerConst') or (obj.token_type == 'stringConst' and expected.token_type == 'stringConst'):
        expected.value = obj.value

    self._deposit(obj, expected)
    self._ptr += 1

class Expression(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      Term,
      {'optional-repeat': [
        {'any': [
          Token('+', 'symbol'),
          Token('-', 'symbol'),
          Token('*', 'symbol'),
          Token('/', 'symbol'),
          Token('&', 'symbol'),
          Token('|', 'symbol'),
          Token('<', 'symbol'),
          Token('>', 'symbol'),
          Token('=', 'symbol')
        ]},
        Term
      ]}
    ]
    super().__init__('expression', keywords)

