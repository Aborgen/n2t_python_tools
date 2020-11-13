import inspect

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
    p_expression = _compile_parenthetical_expression()
    statement.deposit(p_e)                      # ( expression )
    c_b_statements = _compile_curly_bracket_statements()
    statement.deposit(c_b_statements)           # { statement* }
    if self._peek_token().value == 'else':
      token = self._next_token()
      statement.deposit(token)                  # (else
      c_b_statements = _compile_curly_bracket_statements()
      statement.deposit(c_b_statements)         # { statement* })?

    return statement


  def _compile_while_statement(self) -> whileStatement:
    statement = whileStatement()
    token = self._next_token()
    statement.deposit(token)                    # while
    p_expression = _compile_parenthetical_expression()
    statement.deposit(p_e)                      # ( expression )
    c_b_statements = _compile_curly_bracket_statements()
    statement.deposit(c_b_statements)           # { statement* }
    return statement


  def _compile_let_statement(self) -> letStatement:
    statement = letStatement()
    token = self._next_token()
    statement.deposit(token)                    # let
    token = self._next_token()
    statement.deposit(token)                    # identifier
    if self._peek_token().value == '[':
      b_expression = self._compile_bracket_expression()
      statement.deposit(b_expression)           # ([expression])?

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
    if self._peek_token().value != ';':
      expression = self._compile_expression()
      statement.deposit(expression)             # expression?

    token = self._next_token()
    statement.deposit(token)                    # ;
    return statement


  def _compile_class_variables_declaration(self) -> list[ClassVariable]:
    return self._compile_parameter_or_variable_list(keywords=['static', 'field'], variable_class=ClassVariable)


  def _compile_class_subroutines(self) -> list[Subroutine]:
    subroutines = []
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
    if self._peek_token() != ')':
      self._compile_class_subroutine_parameters(subroutine)
                                                # parameter*
    token = self._next_token()
    subroutine.deposit(token)                   # )


  def _compile_class_subroutine_parameters(self, subroutine: Subroutine) -> None:
    while True:
      token = self._next_token()
      subroutine.deposit(token)                 # type
      identifier = self._compile_identifier()
      subroutine.deposit(identifier)            # identifier
      if self._peek_token() == ')':
        break

      token = self._next_token()
      subroutine.deposit(token)                 # ,


  def _compile_class_subroutine_variables_declaration(self) -> list[SubroutineVariable]:
    return self._compile_parameter_or_variable_list(keywords=['var'], variable_class=SubroutineVariable)


  def _compile_parameter_or_variable_list(self, keywords: list[str], variable_class: Generic[G]) -> list[G]:
    if not inspect.isclass(variable_class):
      raise f'The provided class is not of type class: {variable_class}'

    variables = []
    while self._peek_token() in keywords:
      variable = obj()
      token = self._next_token()
      variable.deposit(token)                   # keywords[n]
      token = self._next_token()
      variable.deposit(token)                   # type
      identifier = self._compile_identifier()
      variable.deposit(identifier)              # identifier
      while self._peek_token.value != ';':
        token = self._next_token()
        variable.deposit(token)                 # (,
        identifier = self._compile_identifier()
        variable.deposit(identifier)            # identifier)*

      token = self._next_token()
      variable.deposit(token)                   # ;

    return variables
    

  # Used with if, else, and while
  def _compile_parenthetical_expression(self) -> list[str, Expression, str]:
    if self._peek_token().value != '(':
      raise ParserError()

    l = []
    token = self._next_token()
    l.append(token)                             # (
    expression = self._compile_expression()
    l.append(expression)                        # expression
    token = self._next_token()
    l.append(token)                             # )
    return l


  def _compile_curly_bracket_statements(self) -> list[str, Expression, str]:
    l = []
    token = self._next_token()
    l.append(token)                             # {
    if self._peek_token().value != '}':
      statements = self._compile_statements()
      if statements:
        l.append(expression)                    # statement*

    token = self._next_token()
    l.append(token)                             # }
    return l


  def _compile_bracket_expression(self) -> list[str, Expression, str]:
    if self._peek_token().value != '[':
      raise ParserError()

    l = []
    token = self._next_token()
    l.append(token)                             # [
    expression = self._compile_expression()
    l.append(expression)                        # expression
    token = self._next_token()
    l.append(token)                             # ]
    return l


  def _compile_identifier(self) -> Identifier:
    identifier = Identifier()
    token = self._next_token() 
    identifier.deposit(token)                   # identifier
    return identifier
