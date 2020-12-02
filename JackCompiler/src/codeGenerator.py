from __future__ import annotations

from dataclasses import dataclass

from .analyzer.grammar import GrammarObject
from .analyzer.grammar import Identifier
from .analyzer.grammar import ParameterList
from .analyzer.grammar import Subroutine
from .analyzer.grammar import SubroutineList
from .analyzer.grammar import ClassVariableList
from .analyzer.tokenizer import Token

@dataclass
class Symbol():
  name: str
  type: int
  kind: str
  id  : int = -1

class SymbolTable():
  _data       : list[Symbol]
  _kind_counts: dict[str, int]

  def __init__(self) -> None:
    self._data = []
    self._kind_counts = {}


  def __getitem__(self, i: int) -> Symbol:
    return self._data[i]

  def __str__(self) -> None:
    return str(self._data)


  def append(self, symbol: Symbol) -> None:
    if not isinstance(symbol, Symbol):
      raise Exception('Can only append Symbol objects. Received: {symbol}')
  
    if symbol.kind in self._kind_counts:
      self._kind_counts[symbol.kind] += 1
    else:
      self._kind_counts[symbol.kind] = 0

    symbol.id = self._kind_counts[symbol.kind]
    self._data.append(symbol)


  def clear(self) -> None:
    self._data.clear()
    self._kind_counts.clear()


class CodeGenerator():
  _class_name        : Identifier
  _class_symbols     : SymbolTable
  _subroutine_list   : SubroutineList
  _subroutine_symbols: SymbolTable
  _variable_list     : ClassVariableList

  def __init__(self, obj: GrammarObject) -> None:
    if not isinstance(obj, GrammarObject) or obj.label != 'class':
#      raise CompilerException('Malformed object tree')
      raise Exception('Malformed object tree')

    _, class_name, _, variable_list, subroutine_list, _ = obj
    self._class_name = class_name
    self._subroutine_list = subroutine_list
    self._variable_list = variable_list
    self._class_symbols = SymbolTable()
    self._subroutine_symbols = SymbolTable()


  def generate(self) -> tuple:
    self._populate_class_symbols()
    for subroutine in self._subroutine_list:
      self._generate_subroutine_code(subroutine)


  def _generate_subroutine_code(self, subroutine: Subroutine) -> None:
    _, _, _, _, parameter_list, _, _ = subroutine
    self._populate_subroutine_symbols(parameter_list)


  def _populate_class_symbols(self) -> None:
    self._class_symbols.clear()
    for var_type, data_type, *rest in self._variable_list:
      identifiers = [l for l in rest if type(l) == Identifier]
      for identifier in identifiers:
        symbol = Symbol(name=identifier.value, type=data_type.value, kind=var_type.value)
        self._class_symbols.append(symbol)


  def _populate_subroutine_symbols(self, parameter_list: ParameterList) -> None:
    self._subroutine_symbols.clear()
    this = Identifier()
    l = [(self._class_name, Token('this', 'symbol'))]
    # ParameterList is structured like [data_type Identifier, data_type Identifier]. Skip the comma(if any).
    for i in range(0, len(parameter_list), 3):
      l.append((parameter_list[i], parameter_list[i+1]))

    for data_type, identifier in l:
      symbol = Symbol(name=identifier.value, type=data_type.value, kind='argument')
      self._subroutine_symbols.append(symbol)
