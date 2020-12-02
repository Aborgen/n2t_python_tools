from dataclasses import dataclass

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


  def append(self, symbol: Symbol) -> None:
    if not isinstance(symbol, Symbol):
      raise Exception('Can only append Symbol objects. Received: {symbol}')
  
    if symbol.kind in self._kind_counts:
      self._kind_counts[symbol.kind] += 1
    else:
      self._kind_counts[symbol.kind] = 0

    symbol.id = self._kind_counts[symbol.kind]
    self._data.append(symbol)


class CodeGenerator():
  _obj               : GrammarObject
  _class_symbols     : SymbolTable
  _subroutine_symbols: SymbolTable

  def __init__(self, obj: GrammarObject) -> None:
    self._obj = obj


  def generate(self) -> tuple:

