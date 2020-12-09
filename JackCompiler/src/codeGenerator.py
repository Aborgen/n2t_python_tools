from __future__ import annotations

from dataclasses import dataclass

from .analyzer.grammar import ClassVariableList
from .analyzer.grammar import Expression
from .analyzer.grammar import ExpressionList
from .analyzer.grammar import GrammarObject
from .analyzer.grammar import Identifier
from .analyzer.grammar import ParameterList
from .analyzer.grammar import Subroutine
from .analyzer.grammar import SubroutineCall
from .analyzer.grammar import SubroutineList
from .analyzer.grammar import Term
from .analyzer.grammar import doStatement
from .analyzer.grammar import ifStatement
from .analyzer.grammar import letStatement
from .analyzer.grammar import returnStatement
from .analyzer.grammar import whileStatement
from .analyzer.tokenizer import Token
from .codeWriter import VMWriter

@dataclass
class Symbol():
  name: str
  type: int
  kind: str
  id  : int = -1

class SymbolTable():
  _data       : dict[str, Symbol]
  _kind_counts: dict[str, int]

  def __init__(self) -> None:
    self._data = {}
    self._kind_counts = {}


  def __getitem__(self, key: str) -> Symbol:
    return self._data[key]


  def __str__(self) -> str:
    return str(self._data)


  def __len__(self) -> int:
    return len(self._data)


  def __contains__(self, name: str) -> bool:
    return name in self._data


  def __iter__(self) -> Symbol:
    values = self._data.values()
    yield from values


  def insert(self, symbol: Symbol) -> None:
    if not isinstance(symbol, Symbol):
      raise Exception('Can only insert Symbol objects. Received: {symbol}')
  
    if symbol.name not in self._data:
      if symbol.kind in self._kind_counts:
        self._kind_counts[symbol.kind] += 1
      else:
        self._kind_counts[symbol.kind] = 0

    symbol.id = self._kind_counts[symbol.kind]
    self._data[symbol.name] = symbol


  def clear(self) -> None:
    self._data.clear()
    self._kind_counts.clear()


class CodeGenerator():
  _class_name        : Identifier
  _class_symbols     : SymbolTable
  _subroutine_list   : SubroutineList
  _subroutine_symbols: SymbolTable
  _variable_list     : ClassVariableList
  _writer            : VMWriter

  def __init__(self, obj: GrammarObject, writer: VMWriter) -> None:
    if not isinstance(obj, GrammarObject) or obj.label != 'class':
#      raise CompilerException('Malformed object tree')
      raise Exception('Malformed object tree')

    _, class_name, _, variable_list, subroutine_list, _ = obj
    self._class_name = class_name
    self._subroutine_list = subroutine_list
    self._variable_list = variable_list
    self._class_symbols = SymbolTable()
    self._subroutine_symbols = SymbolTable()
    self._writer = writer


  def generate(self) -> tuple:
    self._populate_class_symbols()
    for subroutine in self._subroutine_list:
      self._generate_subroutine_code(subroutine)


  def _generate_subroutine_code(self, subroutine: Subroutine) -> None:
    function_kind, _, subroutine_name, _, parameter_list, _, subroutine_body = subroutine
    _, variable_list, statement_list, _ = subroutine_body
    arg_count, local_count = self._populate_subroutine_symbols(parameter_list, variable_list, function_kind)

    self._writer.write_function(f'{self._class_name.value}.{subroutine_name.value}', variable_count=local_count)
    if function_kind.value == 'constructor':
      self._generate_for_constructor()
    elif function_kind.value == 'method':
      self._generate_for_method_memory_setup()

    self._generate_for_statements(statement_list)


  # Need to set aside block of memory for newly instantiated object
  def _generate_for_constructor(self) -> None:
    '''
    push constant arg_count
    call Memory.alloc 1
    pop pointer 0 # sets THIS segment to the base address of the newly constructed object
    '''
    field_count = 0
    for symbol in self._class_symbols:
      if symbol.kind != 'static':
        field_count += 1

    if field_count > 0:
      self._writer.write_push('constant', field_count)
      self._writer.write_subroutine_call('Memory.alloc', 1)
      self._writer.write_pop('pointer', 0)


  # Sets THIS segment to point to base address of object in methods
  def _generate_for_method_memory_setup(self) -> None:
    '''
    push argument 0 # arg0 is always base address of object
    pop pointer 0
    '''
    self._writer.write_push('argument', 0)
    self._writer.write_pop('pointer', 0)


  def _generate_for_statements(self, statement_list: StatementList) -> None:
    for statement in statement_list:
      if type(statement) == doStatement:
        self._generate_for_do(statement)
      elif type(statement) == letStatement:
        self._generate_for_let(statement)
      elif type(statement) == ifStatement:
        self._generate_for_if(statement)
      elif type(statement) == returnStatement:
        self._generate_for_return(statement)
      elif type(statement) == whileStatement:
        self._generate_for_while(statement)
      else:
        raise NotImplementedError


  def _generate_for_do(self, statement: doStatement) -> None:
    '''
    [compile subroutine call]
    pop temp 0
    push constant 0
    '''
    subroutine_name = statement[1]
    self._generate_for_subroutine_call(subroutine_name)
    # do statements implicitly throw away the return value thats on the top of the stack.
    self._writer.write_pop('temp', 0)


  # let var = expression;  :: First generate for expression on RHS. Then, pop to var.
  # TODO: Extend for array access.
  def _generate_for_let(self, statement: letStatement) -> None:
    '''
    [compile expression]
    pop this n
    '''
    _, var, _, expression, _ = statement
    self._generate_for_expression(expression)
    symbol = self._fetch_symbol(var)
    self._writer.write_pop(symbol.kind, symbol.id)


  def _generate_for_if(self, statement: ifStatement) -> None:
    '''
    [compile expression]
    neg
    if-goto L1
    [compile statements_if]
    goto L2
    label L1
    [compile statements_else]
    label L2
    '''
    # if ( expression ) { statements }
    _, _, expression, _, _, statements_if, _ = statement[:7]
    # We negate the result from compiling the expression, because the resulting code is cleaner.
    self._generate_for_expression(expression)
    self._writer.write_logic('~')
    # if expression is false, goto statements_else
    label1 = self._writer.write_goto(prefix='if')
    self._generate_for_statements(statements_if)
    label2 = self._writer.write_goto()
    self._writer.write_label(label1)
    statements_else = statement[9] if len(statement) > 7 else []
    self._generate_for_statements(statements_else)
    self._writer.write_label(label2)


  # return (expression)?;
  def _generate_for_return(self, statement: returnStatement) -> None:
    if len(statement) > 2:
      self._generate_for_expression(statement[1])
    else:
      self._writer.write_push('constant', 0)

    self._writer.write_return()


  def _generate_for_while(self, statement: whileStatement) -> None:
    '''
    label L1
    [compile expression]
    neg
    if-goto L2
    [compile statement_list]
    goto L1
    label L2
    '''
    _, _, expression, _, _, statement_list, _ = statement
    label1 = self._writer.write_label()
    self._generate_for_expression(expression)
    self._writer.write_logic('~')
    label2 = self._writer.write_goto(prefix='if')
    self._generate_for_statements(statement_list)
    self._writer.write_goto(label1)
    self._writer.write_label(label2)


  def _generate_for_expression(self, expression: Expression) -> None:
    '''
    [compile term+]
    [compile operation*]
    '''
    term_list = []
    operator_stack = []
    # Terms are first written FIFO, and operations are written LIFO afterwards
    for i, value in enumerate(expression):
      # Term
      if i % 2 == 0:
        term_list.append(value)
      # Operator
      else:
        operator_stack.append(value)


    for term in term_list:
      self._generate_for_term(term)

    while len(operator_stack) > 0:
      operator = operator_stack.pop()
      if operator.value in ['&', '|']:
        self._writer.write_logic(operator.value)
      else:
        self._writer.write_arithmetic(operator.value)


  def _generate_for_term(self, term: Term) -> None:
    '''
    (push constant n) | (push segment n) | [compile subroutine call] | [compile term] | [compile expression]
                                                                     | operator
    '''
    if type(term) != Term:
      raise Exception(f'Not a term: {term}')

    if len(term) == 1:
      obj = term[0]
      if type(obj) == Token:
        if obj.value == 'this':
          self._writer.write_push('pointer', 0)
          return
        elif obj.value in ['true', 'false', 'null']:
          n = '0'
        else:
          n = obj.value

        self._writer.write_push('constant', n)
        # -1 == true according to specification
        if obj.value == 'true':
          self._writer.write_logic('~')
      elif type(obj) == Identifier:
        symbol = self._fetch_symbol(obj)
        self._writer.write_push(symbol.kind, symbol.id)
      elif type(obj) == SubroutineCall:
        self._generate_for_subroutine_call(obj)
    # operator Term
    elif len(term) == 2:
      operator, term1 = term
      self._generate_for_term(term1)
      self._writer.write_logic(operator.value)
    # Term operator Term
    elif len(term) == 3:
      _, expression, _ = term
      self._generate_for_expression(expression)
    else:
      raise Exception('Encountered empty Term GrammarObject')


  # f(exp1, exp2, ..., expn)
  def _generate_for_subroutine_call(self, subroutine_call: SubroutineCall) -> None:
    '''
    [[ for expression in args [compile expression] ]]
    function name n
    '''
    # Specification states that Subroutines can either be single identifiers, or identifier.identifier, as in the invocation of a class method. Doing it this way allows for future extension to arbitrarily long identifier chains.
    identifiers = []
    expression_list = None
    for obj in subroutine_call:
      if type(obj) == Identifier:
        identifiers.append(obj.value)
      # SubroutineCalls are guaranteed to have an ExpressionList. It could be an empty one.
      elif type(obj) == ExpressionList:
        expression_list = obj
        break

    # Filter comma Tokens.
    expressions = [l for l in expression_list if type(l) == Expression]
    for expression in expressions:
      self._generate_for_expression(expression)

    method = '.'.join(identifiers)
    self._writer.write_subroutine_call(method, len(expressions))


  def _populate_class_symbols(self) -> None:
    self._class_symbols.clear()
    self._aggregate_variable_symbols(self._variable_list, self._class_symbols)
    for symbol in self._class_symbols:
      if symbol.kind == 'field':
        symbol.kind = 'this'


  def _populate_subroutine_symbols(self, parameter_list: ParameterList, variable_list: SubroutineVariableList, function_kind: Token) -> None:
    self._subroutine_symbols.clear()
    if function_kind.value == 'method':
      symbol = Symbol(name='this', type=self._class_name, kind='argument')
      self._subroutine_symbols.insert(symbol)

    # ParameterList is structured like [data_type Identifier, data_type Identifier]. Skip the comma(if any).
    l = []
    for i in range(0, len(parameter_list), 3):
      l.append((parameter_list[i], parameter_list[i+1]))
    # Aggregate parameter symbols
    for data_type, identifier in l:
      symbol = Symbol(name=identifier.value, type=data_type.value, kind='argument')
      self._subroutine_symbols.insert(symbol)

    arg_count = len(l)
    local_count = self._aggregate_variable_symbols(variable_list, self._subroutine_symbols)
    return (arg_count, local_count)


  def _aggregate_variable_symbols(self, variable_list: GrammarObject, container: SymbolTable) -> int:
    var_count = 0
    for var_type, data_type, *rest in variable_list:
      identifiers = [l for l in rest if type(l) == Identifier]
      for identifier in identifiers:
        symbol = Symbol(name=identifier.value, type=data_type.value, kind=var_type.value)
        container.insert(symbol)
        var_count += 1

    return var_count


  def _symbol_exists(self, identifier: Identifier) -> bool:
    if type(identifier) != Identifier:
      raise Exception(f'Must pass identifier. Received \'{type(identifier)}\'')

    token = identifier[0]
    return token.value in self._subroutine_symbols or token.value in self._class_symbols


  # First check to see if a symbol with the name exists in the subroutine-level symbols, then the class-level symbols.
  def _fetch_symbol(self, identifier: Identifier) -> Symbol:
    if type(identifier) != Identifier:
      raise Exception(f'Must pass identifier. Received \'{type(identifier)}\'')

    token = identifier[0]
    if token.value in self._subroutine_symbols:
      return self._subroutine_symbols[token.value]
    elif token.value in self._class_symbols:
      return self._class_symbols[token.value]
    else:
#      raise CompilerException('Tried to use variable that has not been declared', obj.line, obj.word)
      raise Exception(f'Tried to use variable that has not been declared at {token.line}, {token.word}')
