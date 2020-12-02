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

#class VMWriter():
#  _f          : TextIO
#  _label_count: int
#  closed      : bool
#
#  def __init__(self) -> None:
#    self._f = None
#    self._label_count = 0
#    self.closed = True
#
#
#  def open(self, out_file: Path) -> None:
#    if not self.closed:
#      raise Exception('Cannot open file: file already opened')
#
#    self._f = open(out_file, 'w+')
#    self.closed = False
#
#
#  def _write(self, l: str) -> None:
#    self._f.write(l)
#
#
#  def write_push(self, segment: ESegment, idx: int) -> None:
#    l = self._write_push_or_pop('push', segment, idx)
#    self._write(l)
#
#
#  def write_pop(self, segment: ESegment, idx: int) -> None:
#    l = self._write_push_or_pop('pop', segment, idx)
#    self._write(l)
#
#
#  def _write_push_or_pop(self, l: str, segment: ESegment, idx: int) -> str:
#    if segment == ESegment.CONST:
#      l += f' const {idx}'
#    elif segment == ESegment.ARG:
#      l += f' arg {idx}'
#    elif segment == ESegment.LOCAL:
#      l += f' local {idx}'
#    elif segment == ESegment.STATIC:
#      l += f' static {idx}'
#    elif segment == ESegment.THIS:
#      l += f' this {idx}'
#    elif segment == ESegment.THAT:
#      l += f' that {idx}'
#    elif segment == ESegment.POINTER:
#      l += f' pointer {idx}'
#
#    return l
