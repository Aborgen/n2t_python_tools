from __future__ import annotations # Needed to refer to GrammarObject within Grammarobject

import inspect
from dataclasses import dataclass
from typing import Union

from .exceptions import ParserError
from .tokenizer import Token

class GrammarObject():
  _keywords : list[Union[Token, GrammarObject]]
  _ptr      : int
  children  : list[Union[Token, GrammarObject]]
  label     : Optional[str]

  def __init__(self, label: Optional[str], keywords: Union[list[GrammarObject], str]) -> None:
    self._keywords = keywords
    self._ptr = 0
    self.children = []
    self.label = label


  def deposit(self, obj: Union[Token, GrammarObject]) -> None:
    if self._ptr >= len(self._keywords):
      raise 'Tried to deposit too many objects'

    expected = self._expected()
    self._deposit(obj, expected)
    self._ptr += 1


  def _deposit(self, obj: Union[Token, GrammarObject, dict], expected: Union[Token, GrammarObject, dict]) -> None:
    if not self._is_comparable(obj, expected):
      raise ParserError('Token given does not match what is expected')

    if type(expected) == dict:
      key = list(expected.keys())[0]
      if key == 'optional':
        if len(obj[key]) > 0:
          self._deposit_group(obj[key], expected[key])
      elif key == 'group':
        self._deposit_group(obj[key], expected[key])
      elif key == 'optional-repeat':
        if len(obj[key]) == 0:
          return

        for group in obj[key]:
          self._deposit_group(group, expected[key])
      elif key == 'any':
        if type(obj) == dict:
          successful_deposit = False
          for v in expected[key]:
            if type(v) == dict:
              try:
                self._deposit(obj, v)
                successful_deposit = True
                break
              except ParserError as e:
                pass

          if not successful_deposit:
            raise ParserError(f'Expected anything in {str(expected[key])}, but got {obj}')
        elif not any(obj == v or inspect.isclass(v) and isinstance(obj, v) for v in expected[key]):
          raise ParserError(f'Not a correct option: {obj} not among {str(expected[key])}')
        else:
          self.children.append(obj)
      else:
        raise ParserError(f'Unrecognized key: {key}')
    else:
      self.children.append(obj)


  def _deposit_group(self, group: list[Union[Token, GrammarObject, dict]], template: list[Union[Token, GrammarObject, dict]]) -> None:
    if type(group) != list or type(template) != list:
      raise ParserError('Must be list')
    elif len(group) != len(template):
      raise ParserError('Must be same length')

    for a, b in zip(group, template):
      self._deposit(a, b)


  def _is_comparable(self, obj: Union[Token, GrammarObject, dict], expected: Union[Token, GrammarObject, dict]) -> bool:
    if type(obj) == type(expected) == Token:
      return obj == expected
    elif type(expected) == dict:
      if not (len(expected) == 1):
        raise 'Dict should only have one key'
      
      return True
    else:
      return inspect.isclass(expected) and isinstance(obj, expected)


  def _expected(self) -> Union[Token, GrammarObject]:
    if self._ptr >= len(self._keywords):
      raise ParserError()

    return self._keywords[self._ptr]


# class Identifier { ClassVariableList SubroutineList }
class AClass(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('class', 'keyword'), Identifier, Token('{', 'symbol'), ClassVariableList, SubroutineList, Token('}', 'symbol')]
    super().__init__('class', keywords)

# let Identifier([Expression])? = Expression;
class letStatement(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      Token('let', 'keyword'), Identifier,
      {'optional': [
        Token('[', 'symbol'),
        Expression,
        Token(']', 'symbol')
      ]},
      Token('=', 'symbol'), Expression, Token(';', 'symbol')
    ]
    super().__init__('letStatement', keywords)

# if (Expression) { StatementList } (else { statement* })?
class ifStatement(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      Token('if', 'keyword'), Token('(', 'symbol'), Expression, Token(')', 'symbol'), Token('{', 'symbol'), StatementList, Token('}', 'symbol'),
      {'optional': [
        Token('else', 'keyword'),
        Token('{', 'symbol'),
        StatementList,
        Token('}', 'symbol')
      ]}
    ]
    super().__init__('ifStatement', keywords)

# while (expression) { statement* }
class whileStatement(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('while', 'keyword'), Token('(', 'symbol'), Expression, Token(')', 'symbol'), Token('{', 'symbol'), StatementList, Token('}', 'symbol')]
    super().__init__('whileStatement', keywords)

# do subroutineCall;
class doStatement(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('do', 'keyword'), SubroutineCall, Token(';', 'symbol')]
    super().__init__('doStatement', keywords)

# identifier(\.identifier)?( expressionList )
class SubroutineCall(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      Identifier,
      {'optional': [
        Token('.', 'symbol'),
        Identifier
      ]},
      Token('(', 'symbol'), ExpressionList, Token(')', 'symbol')
    ]
    super().__init__(None, keywords)

# return expression?;
class returnStatement(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      Token('return', 'keyword'),
      {'optional': [
        Expression
      ]},
      Token(';', 'symbol')
    ]
    super().__init__('returnStatement', keywords)

# (constructor | function | method) type identifier ( parameter* ) { localVariable* statement* }
class Subroutine(GrammarObject):
  def __init__(self) -> None:
    keywords = [SubroutineType, DataType, Identifier, Token('(', 'symbol'), ParameterList, Token(')', 'symbol'), SubroutineBody]
    super().__init__('subroutineDec', keywords)

# subroutine*
class SubroutineList(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'optional-repeat': [
        Subroutine
      ]}
    ]
    super().__init__(None, keywords)

# (type identifier (, type identifier)*)?
class ParameterList(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'optional': [
        DataType,
        Identifier,
        {'optional-repeat': [
          Token(',', 'symbol'),
          DataType,
          Identifier
        ]}
      ]}
    ]
    super().__init__('parameterList', keywords)

# { SubroutineVariableList StatementList }
class SubroutineBody(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('{', 'symbol'), SubroutineVariableList, StatementList, Token('}', 'symbol')]
    super().__init__('subroutineBody', keywords)

class DataType(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'any': [
        Token('int', 'keyword'),
        Token('char', 'keyword'),
        Token('boolean', 'keyword'),
        Token('void', 'keyword'),
        Identifier
      ]}
    ]
    super().__init__(None, keywords)

class SubroutineType(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'any': [
        Token('constructor', 'keyword'),
        Token('function', 'keyword'),
        Token('method', 'keyword')
      ]}
    ]
    super().__init__(None, keywords)

class ClassVariableType(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'any': [
        Token('static', 'keyword'),
        Token('field', 'keyword')
      ]}
    ]
    super().__init__(None, keywords)

class SubroutineVariableType(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'any': [
        Token('var', 'keyword')
      ]}
    ]
    super().__init__(None, keywords)

class Identifier(GrammarObject):
  def __init__(self) -> None:
    keywords = [Token('', 'identifier')]
    super().__init__(None, keywords)


  def deposit(self, obj: Token) -> None:
    if self._ptr >= len(self._keywords):
      raise 'Tried to deposit too many objects'
    elif type(obj) != Token or obj.token_type != 'identifier':
      raise ParserError()

    self._keywords[0].value = obj.value
    super().deposit(obj)

# ClassVariableType DataType Identifier (, Identifier)*;
class ClassVariable(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      ClassVariableType, DataType, Identifier,
      {'optional-repeat': [
        Token(',', 'symbol'),
        Identifier
      ]},
      Token(';', 'symbol')
    ]
    super().__init__('varDec', keywords)

# ClassVariable*
class ClassVariableList(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'optional-repeat': [
        ClassVariable
      ]}
    ]
    super().__init__(None, keywords)

# SubroutineVariableType DataType Identifier (, Identifier)*;
class SubroutineVariable(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      SubroutineVariableType, DataType, Identifier,
      {'optional-repeat': [
        Token(',', 'symbol'),
        Identifier
      ]},
      Token(';', 'symbol')
    ]
    super().__init__('varDec', keywords)

class SubroutineVariableList(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'optional-repeat': [
        SubroutineVariable
      ]}
    ]
    super().__init__(None, keywords)

# (letStatement | ifStatement | whileStatement | returnStatement | doStatement)*
class StatementList(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'optional-repeat': [
        {'any': [
          letStatement,
          ifStatement,
          doStatement,
          whileStatement,
          returnStatement
        ]}
      ]}
    ]
    super().__init__('statements', keywords)

class Term(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'any': [
        Token('', 'integerConstant'),
        Token('', 'stringConstant'),
        Token('true', 'keyword'),
        Token('false', 'keyword'),
        Token('null', 'keyword'),
        Token('this', 'keyword'),
        Token('-', 'symbol'),
        Identifier,
        SubroutineCall,
        {'group': [
          Token('(', 'symbol'),
          Expression,
          Token(')', 'symbol')
        ]},
        {'group': [
          Identifier,
          Token('[', 'symbol'),
          Expression,
          Token(']', 'symbol')
        ]},
        {'group': [
          Token('~', 'symbol'),
          Term
        ]}
      ]}
    ]
    super().__init__('term', keywords)


  def deposit(self, obj: Union[Token, GrammarObject]) -> None:
    if self._ptr >= len(self._keywords):
      raise 'Tried to deposit too many objects'

    expected = self._expected()
    if type(obj) == Token and (obj.token_type == 'stringConstant' or obj.token_type == 'integerConstant'):
      for v in expected['any']:
        if obj.token_type == v.token_type:
          v.value = obj.value
          break

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

class ExpressionList(GrammarObject):
  def __init__(self) -> None:
    keywords = [
      {'optional': [
        Expression,
        {'optional-repeat': [
          Token(',', 'symbol'),
          Expression
        ]}
      ]}
    ]
    super().__init__('expressionList', keywords)
