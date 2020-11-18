import inspect

from .categories import math_symbols
from .grammar import AClass
from .grammar import ClassVariable
from .grammar import ClassVariableList
from .grammar import ExpressionList
from .grammar import Identifier
from .grammar import ParameterList
from .grammar import StatementList
from .grammar import SubroutineList
from .grammar import SubroutineVariable
from .grammar import SubroutineVariableList
from .grammar import Term
from .grammar import doStatement
from .grammar import ifStatement
from .grammar import letStatement
from .grammar import returnStatement
from .grammar import whileStatement

class Parser():
  _export_xml : bool
  _tokens     : List[token]
  _tokenptr   : int
  _source     : str
  _out_path   : Path

  def __init__(self, tokens: List[Token], source: str, out_path: Path, export_xml: bool) -> None:
    _tokens = tokens
    _tokenptr = 0
    _source = source
    _out_path = out_path
    _export_xml = export_xml


  def parse(self) -> None:
    a_class = self._compile_class()
    return a_class


  def _next_token(self) -> Optional[Token]:
    if self._tokenptr > len(self._tokens) - 1:
      return None

    token = self._tokens[self._tokenptr]
    self._tokenptr += 1
    return token


  def _peek_token(self, n: int = 0) -> Optional[Token]:
    idx = self._tokenptr + n
    if idx >= len(self._tokens);
      return None

    token = self._tokens[idx]
    return token


  def _compile_class(self) -> AClass:
    a_class = AClass()
    token = self._next_token()
    a_class.deposit(token)                      # class
    identifier = self._compile_identifier()
    a_class.deposit(identifier)                 # identifier
    token = self._next_token()
    a_class.deposit(token)                      # {
    variables = self._compile_class_variables_declaration()
    a_class.deposit(variables)                  # class_variable_declaration* 
    subroutines = self._compile_class_subroutines()
    a_class.deposit(subroutines)                # subroutine* 
    token = self._next_token()
    a_class.deposit(token)                      # }
    return a_class


  def _compile_statements(self) -> StatementList:
    statements = StatementList()
    token = self._peek_token()
    while token.value != '}':
      if token.value == 'let':
        statements.append(self._compile_let_statement())
      elif token.value == 'if':
        statements.append(self._compile_if_statement())
      elif token.value == 'while':
        statements.append(self._compile_while_statement())
      elif token.value == 'do':
        statements.append(self._compile_do_statement())
      elif token.value == 'return':
        statements.append(self._compile_return_statement())
      else:
        raise ParserError()

      token = self._peek_token()

    return statements

      
  def _compile_if_statement(self) -> ifStatement:
    statement = ifStatement()
    token = self._next_token()
    statement.deposit(token)                    # if
    self._compile_parenthetical_expression(statement)
                                                # ( expression )
    self._compile_curly_bracket_statements(statement)
                                                # { statement* }

    group = {'optional': []}
    if self._peek_token().value == 'else':
      l = []
      token = self._next_token()
      l.append(token)
      self._compile_curly_bracket_statements(l)
      group['optional'] = l

    statement.deposit(group)                    # (else { statement* })?
    return statement


  def _compile_while_statement(self) -> whileStatement:
    statement = whileStatement()
    token = self._next_token()
    statement.deposit(token)                    # while
    self._compile_parenthetical_expression(statement)
                                                # ( expression )
    self._compile_curly_bracket_statements(statement)
                                                # { statement* }
    return statement


  def _compile_let_statement(self) -> letStatement:
    statement = letStatement()
    token = self._next_token()
    statement.deposit(token)                    # let
    token = self._next_token()
    statement.deposit(token)                    # identifier

    group = {'optional': []}
    if self._peek_token().value == '[':
      l = []
      self._compile_bracket_expression(l)
      group['optional'] = l

    statement.deposit(group)                    # ([expression])?
    token = self._next_token()
    statement.deposit(token)                    # =
    expression = self._compile_expression()
    statement.deposit(expression)               # expression
    token = self._next_token()
    statement.deposit(token)                    # ;
    return statement


  def _compile_do_statement(self) -> doStatement:
    statement = doStatement()
    token = self._next_token()
    statement.deposit(token)                    # do
    subroutine = self._compile_subroutine_call()
    statement.deposit(subroutine)               # subroutine
    token = self._next_token()
    statement.deposit(token)                    # ;
    return statement
    

  def _compile_return_statement(self) -> returnStatement:
    statement = returnStatement()
    token = self._next_token()
    statement.deposit(token)                    # return

    group = {'optional': []}
    if self._peek_token().value != ';':
      expression = self._compile_expression()
      group['optional'].append(expression)

    statement.deposit(group)                    # expression?
    token = self._next_token()
    statement.deposit(token)                    # ;
    return statement


  def _compile_subroutine_call(self, obj: GrammarObject) -> None:
    token = self._next_token()
    obj.deposit(token)                          # identifier

    group = {'optional': []}
    if self._peek_token().value == '.':
      token = self._next_token()
      group['optional'].append(token)
      token = self._next_token()
      group['optional'].append(token)

    obj.deposit(group)                          # (.identifier)?
    token = self._next_token()
    obj.deposit(token)                          # (
    expression_list = self._compile_expression_list()
    obj.deposit(expression_list)                # expressionList
    token = self._next_token()
    obj.deposit(token)                          # )


  def _compile_class_variables_declaration(self) -> ClassVariableList:
    return self._compile_typed_variable_list(keywords=['static', 'field'], variable_container=ClassVariableList, variable_class=ClassVariable)


  def _compile_class_subroutines(self) -> SubroutineList:
    subroutines = SubroutineList()
    while self._peek_token() != '}':
      subroutine = Subroutine()
      self._compile_class_subroutine_declaration(subroutine)
                                                # (constructor | method | function) type identifier (parameter*)
      token = self._next_token()
      subroutine.deposit(token)                 # {
      variables = self._compile_class_subroutine_variables_declaration()
      subroutine.deposit(variables)             # subroutine_variable_declaration*
      statements = self._compile_statements()
      subroutine.deposit(statements)            # statement*
      token = self._next_token()
      subroutine.deposit(token)                 # }

    return subroutines


  def _compile_class_subroutine_declaration(self, subroutine: Subroutine) -> None:
    token = self._next_token()
    subroutine.deposit(token)                   # (constructor | method | function)
    token = self._next_token()
    subroutine.deposit(token)                   # type
    identifier = self._compile_identifier()
    subroutine.deposit(identifier)              # identifier
    token = self._next_token()
    subroutine.deposit(token)                   # (
    parameters = self._compile_class_subroutine_parameters()
    subroutine.deposit(parameters)              # parameter*
    token = self._next_token()
    subroutine.deposit(token)                   # )


  def _compile_class_subroutine_parameters(self) -> ParameterList:
    parameters = ParameterList()
    group = {'optional': []}
    if self._peek_token() != ')':
      token = self._next_token()
      group['optional'].append(token)           # type
      identifier = self._compile_identifier()
      group['optional'].append(identifier)      # identifier

      repeat = {'optional-repeat': []}
      while self._peek_token() != ')':
        token = self._next_token()
        repeat['optional-repeat'].append(token) # ,
        token = self._next_token()
        repeat['optional-repeat'].append(token) # type
        identifier = self._compile_identifier()
        repeat['optional-repeat'].append(identifier)
                                                # identifier

      group['optional'].append(repeat)

    parameters.deposit(group)
    return parameters


  def _compile_class_subroutine_variables_declaration(self) -> SubroutineVariableList:
    return self._compile_typed_variable_list(keywords=['var'], variable_container=SubroutineVariableList, variable_class=SubroutineVariable)


  def _compile_typed_variable_list(self, keywords: list[str], variable_container: Generic[C], variable_class: Generic[G]) -> C:
    if not inspect.isclass(variable_class):
      raise f'The provided value to variable_class must be a class: [{variable_class}{type(variable_class)}]'

    variables = variable_container()
    repeat = {'optional-repeat': []}
    while self._peek_token() in keywords:
      variable = variable_class()
      token = self._next_token()
      variable.deposit(token)                   # keywords[n]
      token = self._next_token()
      variable.deposit(token)                   # type
      identifier = self._compile_identifier()
      variable.deposit(identifier)              # identifier

      inner_repeat = {'optional-repeat': []}
      while self._peek_token.value != ';':
        token = self._next_token()
        inner_repeat['optional-repeat'].append(token)
        identifier = self._compile_identifier()
        inner_repeat['optional-repeat'].append(identifier)

      variable.deposit(inner_repeat)            # (,identifier)*
      token = self._next_token()
      variable.deposit(token)                   # ;
      repeat['optional-repeat'].append([variable])

    variables.deposit(repeat)
    return variables
    

  # Used with if and while
  def _compile_parenthetical_expression(self, obj: GrammarObject) -> None:
    token = self._next_token()
    obj.deposit(token)                          # (
    expression = self._compile_expression()
    obj.deposit(expression)                     # expression
    token = self._next_token()
    obj.deposit(token)                          # )


  def _compile_curly_bracket_statements(self, container: Union[GrammarObject, list]) -> None:
    token1 = self._next_token()
    statements = self._compile_statements()
    token2 = self._next_token()
    if type(container) == GrammarObject:
      container.deposit(token)                  # {
      container.deposit(statements)             # statement*
      container.deposit(token2)                 # }
    elif type(container) == list:
      container.append(token)                   # {
      container.append(statements)              # statement*
      container.append(token2)                  # }
    else:
      raise 'Error'


  def _compile_bracket_expression(self, obj: GrammarObject) -> None:
    token = self._next_token()
    obj.deposit(token)                          # [
    expression = self._compile_expression()
    obj.deposit(expression)                     # expression
    token = self._next_token()
    obj.deposit(token)                          # ]


  def _compile_identifier(self) -> Identifier:
    identifier = Identifier()
    token = self._next_token() 
    identifier.deposit(token)                   # identifier
    return identifier


  def _compile_expression(self) -> Expression:
    expression = Expression
    term = self._compile_term()
    expression.deposit(term)                    # term

    group = {'optional': []}
    while self._peek_token().value in math_symbols:
      token = self._next_token()
      group['optional'].append(token)
      term = self._compile_term()
      group['optional'].append(term)

    expression.deposit(group)                   # ((+ | - | * | / | & | '|' | < | > | =) term)*
    return expression


  def _compile_term(self) -> Term:
    term = Term()
    if self._peek_token().token_type == 'identifier':
      if self._peek_token(1).value == '(':
        self._compile_subroutine_call(term)     # identifier(\.identifier)?( expressionList )
      elif self._peek_token(1).value == '[':
        l = []
        token = self.next_token()
        l.append(token)
        self._compile_bracket_expression(l)
        group = {'group': l}
        term.deposit(group)                     # identifier[ expression ]
      else:
        token = self.next_token()
        term.deposit(token)                     # identifier
    elif self._peek_token().value == '~':
      group = {'group': []}
      token = self._next_token()
      group['group'].append(token)
      term2 = self._compile_term()
      group['group'].append(term2)
      term.deposit(group)                       # ~term
    elif self._peek_token().value == '(':
      l = []
      self.compile_parenthetical_expression(l)
      group = {'group': l}
      term.deposit(group)                       # ( expression )
    else:
      token = self._next_token()
      term.deposit(token)                       # intConst | stringConst | keyword | symbol

    return term
