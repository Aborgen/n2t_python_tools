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
    token = self._token[self._tokenptr]
    self._tokenptr += 1
    return token


  def _compile_symbol(self, token: Token) -> None:
    if token.token_type != 'symbol':
      raise ParserError(f'Token given is not a symbol! {token.value} [category {token.token_type}]', token.line, token.word)
  def _compile_intConst(self, token: Token) -> None:
    if token.token_type != 'intConst':
      raise ParserError(f'Token given is not an intConst! {token.value} [category {token.token_type}]', token.line, token.word)
  def _compile_stringConst(self, token: Token) -> None:
    if token.token_type != 'stringConst':
      raise ParserError(f'Token given is not a stringConst! {token.value} [category {token.token_type}]', token.line, token.word)
  def _compile_identifier(self, token: Token) -> None:
    if token.token_type != 'identifier':
      raise ParserError(f'Token given is not an identifier! {token.value} [category {token.token_type}]', token.line, token.word)


  def _compile_statements(self) -> list[Statement]:
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

      
  def _compile_if_statement(self, token: Token) -> IfStatement:
    if token.value != 'if':
      raise ParserError()

    statement = ifStatement()
    statement.deposit(token)                    # if
    p_expression = _compile_parenthetical_expression()
    statement.deposit(p_e)                      # ( expression )
    c_b_statements = _compile_curly_bracket_statements()
    statement.deposit(c_b_statements)           # { statement* }

    token = self._next_token()
    statement.deposit(token)                    # ( expression )
    if self._peek_token().value == 'else':
      token = self._next_token()
      statement.deposit(token)                  # else
      c_b_statements = _compile_curly_bracket_statements()
      statement.deposit(c_b_statements)         # { statement* }

    return statement


  def _compile_while_statement(self, token: Token) -> whileStatement:
    if token.value != 'while':
      raise ParserError()

    statement = whileStatement()
    statement.deposit(token)                    # while
    p_expression = _compile_parenthetical_expression()
    statement.deposit(p_e)                      # ( expression )
    c_b_statements = _compile_curly_bracket_statements()
    statement.deposit(c_b_statements)           # { statement* }
    return statement


  def _compile_let_statement(self, token: Token) -> letStatement:
    if token.value != 'let':
      raise ParserError()

    statement = letStatement()
    statement.deposit(token)                    # let
    token = self._next_token()
    statement.deposit(token)                    # identifier
    if self._peek_token().value == '[':
      b_expression = self._compile_bracket_expression()
      statement.deposit(b_expression)           # [expression]

    token = self._next_token()
    statement.deposit(token)                    # =
    expression = self._compile_expression()
    statement.deposit(expression)               # expression
    token = self._next_token()
    statement.deposit(token)                    # ;
    return statement


  def _compile_do_statement(self, token: Token) -> doStatement:
    if token.value != 'do':
      raise ParserError()

    statement = doStatement()
    statement.deposit(token)                    # do
    subroutine = self._compile_subroutine_call()
    statement.deposit(subroutine)               # subroutine
    token = self._next_token()
    statement.deposit(token)                    # ;
    

  def _compile_return_statement(self, token: Token) -> returnStatement:
    if token.value != 'return':
      raise ParserError()

    statement = returnStatement()
    statement.deposit(token)                    # return
    if self._peek_token().value != ';':
      expression = self._compile_expression()
      statement.deposit(expression)             # expression

    token = self._next_token()
    statement.deposit(token)                    # ;


  # Used with if, else, and while
  def _compile_parenthetical_expression(self) -> list[str, Expression, str]:
    l = []
    token = self._next_token()
    l.append(token)                             # (
    if self._peek_token().value != ')':
      expression = self._compile_expression()
      l.append(expression)                      # expression

    token = self._next_token()
    l.append(token)                             # )
    return l


  def _compile_parenthetical_parameters(self) -> list[str, ParameterList, str]:
    l = []
    token = self._next_token()
    l.append(token)                             # (
    if self._peek_token().value != ')':
      expression = self._compile_subroutine_parameters()
      l.append(expression)                      # parameter*

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
    l = []
    token = self._next_token()
    l.append(token)                             # [
    if self._peek_token().value != ']':
      expression = self._compile_expression()
      l.append(expression)                        # expression

    token = self._next_token()
    l.append(token)                             # ]
    return l


  def _compile_class(self) -> None:
    a_class = AClass()
    token = self._next_token()
    a_class.deposit(token)                      # class
    identifier = self._compile_identifier()
    a_class.deposit(identifier)                 # className
    token = self._next_token()
    a_class.deposit(token)                      # {
    fields = self._compile_class_variables()
    a_class.deposit(fields)                     # classVarDec* 
    subroutines = self._compile_subroutines()
    a_class.deposit(subroutines)                # subroutineDec* 
    token = self._next_token()
    a_class.deposit(token)                      # }
    return a_class


  def _compile_class_variables(self) -> None:
    variables = []


  def _compile_class_variables(self) -> List[ClassVariables]:
    outer_token = self._peek_token()
    while token.value == 'static' or token.value == 'field':
      variable = ClassVariableDeclaration()
      token = self._next_token()
      variable.deposit(token)                   # static | field
      token = self._next_token()
      variable.deposit(token)                   # type
      identifier = self._compile_identifier()
      variable.deposit(identifier)              # identifier
      while self._peek_token.value != ';':
        token = self._next_token()
        variable.deposit(token)                 # ,
        identifier = self._compile_identifier()
        variable.deposit(identifier)            # identifier

      token = self._next_token()
      variable.deposit(token)                   # ;

      outer_token = self._peek_token()
        

    return variables



  def _compile_class_variable_declaration(self, token: Token) -> None:


  def _compile_class_subroutine_declaration(self, token: Token) -> None:


  def _compile_class_subroutine_parameters(self, token: Token) -> None:


  def _compile_class_subroutine_body(self, token: Token) -> None:


  def _compile_class_subroutine_variable_declaration(self, token: Token) -> None:

