from pathlib import Path
from typing import List, TextIO, Union
import xml.etree.ElementTree as ET

from .analyzer.grammar import GrammarObject
from .analyzer.tokenizer import Token

class XMLWriter():
  @staticmethod
  def export_tokens_as_xml(tokens: List[Token], out_path: Path) -> None:
    out_path = out_path.parent / f'{out_path.name}T.xml'
    root = ET.Element('tokens')
    for token in tokens:
      XMLWriter.construct_tree(root, token)

    XMLWriter.finish_and_export_xml(root, out_path)
    print(f'Successfully tokenized: {out_path}')


  @staticmethod
  def export_grammar_objects_as_xml(obj: GrammarObject, out_path: Path) -> None:
    out_path = out_path.parent / f'{out_path.name}.xml'
    root = ET.Element(obj.label)
    for elem in obj.children:
      XMLWriter.construct_tree(root, elem)

    XMLWriter.finish_and_export_xml(root, out_path)
    print(f'Successfully parsed grammar: {out_path}')


  @staticmethod
  def construct_tree(root: ET.Element, obj: Union[Token, GrammarObject]) -> None:
    if type(obj) == Token:
      node = ET.SubElement(root, obj.token_type).text = f' {obj.value} '
    elif isinstance(obj, GrammarObject):
      node = ET.SubElement(root, obj.label) if obj.label else root
      for child in obj.children:
        XMLWriter.construct_tree(node, child)

      # This is done because the provided test files has empty tags extend to the next line, and I cannot figure out how to collapse them into a self closing tag.
      if len(obj.children) == 0:
        node.text = '\n'
    else:
      print(obj)
      raise Exception(f'XMLWriter does not recognize the type of provided object: {type(obj)}. [Token, GrammarObject] are supported')


  @staticmethod
  def finish_and_export_xml(root: ET.Element, out_path) -> None:
    tree = ET.ElementTree(root)
    tree.write(out_path, encoding='utf-8', xml_declaration=False, short_empty_elements=False)

class VMWriter():
  _f          : TextIO
  _filenameo  : str
  _label_count: int
  closed      : bool

  def __init__(self) -> None:
    self._f = None
    self._filename = None
    self._label_count = 0
    self.closed = True


  def open(self, out_path: Path) -> None:
    if not self.closed:
      raise Exception('Cannot open file: file already opened')

    out_path = out_path.with_suffix('.vm')
    self._filename = out_path.stem
    self._f = open(out_path, 'w+')
    self.closed = False


  def write_push(self, segment: str, idx: int) -> None:
    self._write(f'push {segment} {idx}')


  def write_pop(self, segment: str, idx: int) -> None:
    self._write(f'pop {segment} {idx}')


  def write_arithmetic(self, operator: str) -> None:
    if operator == '+':
      s = 'add'
    elif operator == '-':
      s = 'sub'
    elif operator == '<':
      s = 'lt'
    elif operator == '=':
      s = 'eq'
    elif operator == '>':
      s = 'gt'
    elif operator == '*':
      self.write_subroutine_call('Math.multiply', 2)
      return
    elif operator == '/':
      self.write_subroutine_call('Math.divide', 2)
      return
    else:
#      raise CompilerException(f'Unknown operator: {operator}')
      raise Exception(f'Unknown operator: {operator}')

    self._write(s)


  def write_logic(self, operator: str) -> None:
    if operator == '&':
      s = 'and'
    elif operator == '|':
      s = 'or'
    elif operator == '-':
      s = 'neg'
    elif operator == '~':
      s = 'not'
    else:
#      raise CompilerException(f'Unknown operator: {operator}')
      raise Exception(f'Unknown operator: {operator}')

    self._write(s)


  def write_function(self, name: str, variable_count: int) -> None:
    self._write(f'function {name} {variable_count}')


  def write_subroutine_call(self, method: str, argument_count: int) -> None:
    self._write(f'call {method} {argument_count}')


  def write_return(self) -> None:
    self._write('return')


  def write_label(self, label: str = None) -> str:
    if not label:
      label = self._generate_new_label()

    self._write(f'label {label}')
    return label


  def write_goto(self, label: str = None, prefix: str = None) -> str:
    if not label:
      label = self._generate_new_label()

    if prefix:
      goto = f'{prefix}-goto'
    else:
      goto = 'goto'

    self._write(f'{goto} {label}')
    return label


  def _generate_new_label(self) -> str:
    label = f'L{self._label_count}'
    self._label_count += 1
    return label

  def _write(self, s: str) -> None:
    self._f.write(s)
    self._f.write('\n')
