import argparse
from io import TextIOWrapper
import json
from pathlib import Path
import re
from typing import Dict, List




class SymbolTable():
  next_address = 16
  first_reserved_address = 16384
  def __init__(self, initial_symbols: Dict[str, int] = {}):
    self._symbols = initial_symbols
    

  def length() -> int:
    return len(self._symbols)


  def push(self, key: str, value: int = None) -> None:
    if key in self._symbols:
      return

    if not value:
      if self.next_address == self.first_reserved_address:
        raise Exception(f'Too many symbols! Length: {len(self._symbols)}')

      value = self.next_address
      self.next_address += 1

    self._symbols[key] = value


  def __getitem__(self, key) -> int:
    return self._symbols[key]


  def has_symbol(self, key) -> bool:
    return key in self._symbols


  def keys(self) -> List[str]:
    return list(self._symbols.keys())


class Assembler():
  def __init__(self, filename: Path, out_filename: Path = Path('out.hack'), symbols: SymbolTable = None):
    self.current_instruction = 0
    self.line_number = 0
    self.symbol_table = symbols or SymbolTable()
    self.source = self._open_file(filename, mode='read')
    self.out_file = self._open_file(out_filename, mode='write')
    self.finished = False
    self.done_first_pass = False

  
  def assemble(self) -> None:
    if self.finished:
      raise Exception('Assembly has already been done')

    l = ''
    try:
      self._first_pass()

      while True:
        l = self._next()
        if not l:
          break

        instruction = self._translate_symbol(l)
        # If l is a tag definition
        if not instruction:
          continue
        elif self._is_c_instruction(instruction):
          binary_string = self._parse_c_instruction(instruction)
        elif self._is_a_instruction(instruction):
          binary_string = self._parse_a_instruction(instruction)
        else:
          raise Exception(f'Syntax error: instruction number ({self.current_instruction}), {instruction}')
          
        self._out(binary_string)

    except Exception as e:
      line_number = self.line_number-1 if self.line_number > 0 else 0
      raise Exception(f'Assembly error: line number {line_number}, {l}. Original error:\n{e}')

      self.finished = True
      self._destructor()

  # Add all tags to symbol_table
  def _first_pass(self) -> None:
    if self.done_first_pass:
      return

    while True:
      l = self._next()
      if not l:
        break

      if not self._is_tag(l):
        continue

      symbol = l[1:-1]
      if self.symbol_table.has_symbol(symbol):
        Exception(f'Symbol table error: redefinition of already existing tag, {symbol}')

      # Tags point to the instruction located directly below them
      self.symbol_table.push(symbol, self.current_instruction)

    self.source.seek(0)
    self.done_first_pass = True
    self.current_instruction = 0
    self.line_number = 0


  def _next(self) -> str:
    if self.finished:
      return None

    next_line = ''
    while True:
      l = self.source.readline()
      if l == '':
        next_line = None
        break

      self.line_number += 1
      l = l.strip()
      if not l or (len(l) > 1 and l[:2] == '//'):
        continue

      next_line = l.split('//')[0].strip()
      break

    if next_line and not self._is_tag(next_line):
      self.current_instruction += 1

    return next_line
  

  def _open_file(self, filename: Path, mode: str = 'read') -> TextIOWrapper:
    if mode == 'write':
      f = open(filename, 'w+')
    elif mode == 'read':
      f = open(filename, 'r')
    else:
      raise NotImplementedError

    return f


  def _out(self, binary_string: str) -> None:
    self.out_file.write(binary_string)
    self.out_file.write('\n')


  def _translate_symbol(self, symbol: str) -> str:
    if self._is_variable(symbol):
      s = symbol[1:]
    elif self._is_tag(symbol):
      return None
    else:
      return symbol
    
    if not self.symbol_table.has_symbol(s):
      self.symbol_table.push(s)

    address = self.symbol_table[s]
    return f'@{address}'


  def _is_c_instruction(self, instruction: str) -> bool:
    pattern = "^([AMD]{1,2}=)?((D(&|\|)[AM])|(![AMD])|((\-)?[AMD])((\+|-)[AMD1])?|0|(\-)?1){1}(;( )?(JGT|JEQ|JGE|JLT|JNE|JLE|JMP))?$"
    return bool(re.match(pattern, instruction))


  def _is_a_instruction(self, instruction: str) -> bool:
    pattern = '^@[0-9]*$'
    return bool(re.match(pattern, instruction))


  def _is_variable(self, instruction: str) -> bool:
    pattern = '^@[a-zA-Z][a-zA-Z0-9_\.\$]*$'
    return bool(re.match(pattern, instruction))


  def _is_tag(self, instruction: str) -> bool:
    pattern = '^\([a-zA-Z][a-zA-Z0-9_\.\$]*\)$'
    return bool(re.match(pattern, instruction))


  def _parse_a_instruction(self, instruction: str):
    if not self._is_a_instruction(instruction):
      raise Exception(f'Not a valid A instruction: {instruction}')

    address = int(instruction[1:])
    return format(address, '016b')


  def _parse_c_instruction(self, instruction: str):
    # Use rpartition to ensure that instructions that look like comp; jmp are
    # parsed correctly.
    destination, _, rest = instruction.rpartition('=')
    computation, _, jump = rest.partition(';')
    comp = [0,0,0,0,0,0,0]
    dest = [0,0,0]
    jmp  = [0,0,0]
    if destination:
      if 'A' in destination:
        dest[0] = 1
      if 'M' in destination:
        dest[2] = 1
      if 'D' in destination:
        dest[1] = 1

    if computation == '0':
      comp = [0,1,0,1,0,1,0]
    elif computation == '1':
      comp = [0,1,1,1,1,1,1]
    elif computation == '-1':
      comp = [0,1,1,1,0,1,0]
    elif computation == 'D':
      comp = [0,0,0,1,1,0,0]
    elif computation == 'A':
      comp = [0,1,1,0,0,0,0]
    elif computation == 'M':
      comp = [1,1,1,0,0,0,0]
    elif computation == '!D':
      comp = [0,0,0,1,1,0,1]
    elif computation == '!A':
      comp = [0,1,1,0,0,0,1]
    elif computation == '!M':
      comp = [1,1,1,0,0,0,1]
    elif computation == '-D':
      comp = [0,0,0,1,1,1,1]
    elif computation == '-A':
      comp = [0,1,1,0,0,1,1]
    elif computation == '-M':
      comp = [1,1,1,0,0,1,1]
    elif computation == 'D+1':
      comp = [0,0,1,1,1,1,1]
    elif computation == 'A+1':
      comp = [0,1,1,0,1,1,1]
    elif computation == 'M+1':
      comp = [1,1,1,0,1,1,1]
    elif computation == 'D-1':
      comp = [0,0,0,1,1,1,0]
    elif computation == 'A-1':
      comp = [0,1,1,0,0,1,0]
    elif computation == 'M-1':
      comp = [1,1,1,0,0,1,0]
    elif computation == 'D+A':
      comp = [0,0,0,0,0,1,0]
    elif computation == 'D+M':
      comp = [1,0,0,0,0,1,0]
    elif computation == 'D-A':
      comp = [0,0,1,0,0,1,1]
    elif computation == 'D-M':
      comp = [1,0,1,0,0,1,1]
    elif computation == 'A-D':
      comp = [0,0,0,0,1,1,1]
    elif computation == 'M-D':
      comp = [1,0,0,0,1,1,1]
    elif computation == 'D&A':
      comp = [0,0,0,0,0,0,0]
    elif computation == 'D&M':
      comp = [1,0,0,0,0,0,0]
    elif computation == 'D|A':
      comp = [0,0,1,0,1,0,1]
    elif computation == 'D|M':
      comp = [1,0,1,0,1,0,1]
    else:
      raise NotImplementedError(f'C-instruction error: unrecognized computation: {comp}')

    if jump:
      if jump == 'JGT':
        jmp = [0,0,1]
      elif jump == 'JEQ':
        jmp = [0,1,0]
      elif jump == 'JGE':
        jmp = [0,1,1]
      elif jump == 'JLT':
        jmp = [1,0,0]
      elif jump == 'JNE':
        jmp = [1,0,1]
      elif jump == 'JLE':
        jmp = [1,1,0]
      elif jump == 'JMP':
        jmp = [1,1,1]
      else:
        raise NotImplementedError(f'C-instruction error: unrecognized jump: {jump}')

    return ''.join(str(num) for num in [1,1,1]+comp+dest+jmp)


  def _destructor(self) -> None:
    self.source.close()
    self.out_file.close()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('assembly', type=str, help='Path to the hack assembly file')
  parser.add_argument('symbols', type=str, help='Path to the reserved assembly symbols')
  parser.add_argument('-o', '--out-file', type=str, help='Name of the output')
  args = parser.parse_args()

  current_directory = Path.cwd()
  with open(current_directory / args.symbols, 'r') as f:
    symbols = SymbolTable(json.load(f))

  source = current_directory / args.assembly
  output = 'out.hack'
  if args.out_file:
    output = current_directory / args.out_file
  assembler = Assembler(source, output, symbols=symbols)
  assembler.assemble()
