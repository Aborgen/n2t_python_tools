from pathlib import Path
from typing import List, Union
import xml.etree.cElementTree as ET

from .grammar import GrammarObject
from .tokenizer import Token

class CodeWriter():
  @staticmethod
  def export_tokens_as_xml(tokens: List[Token], out_file: Path) -> None:
    out_file = out_file.parent / f'{out_file.name}.tokens.xml'
    root = ET.Element('tokens')
    for token in tokens:
      CodeWriter.construct_tree(root, token)

    CodeWriter.finish_and_export_xml(root, out_file)
    print(f'Successfully tokenized: {out_file}')


  @staticmethod
  def export_grammar_objects_as_xml(obj: GrammarObject, out_file: Path) -> None:
    out_file = out_file.parent / f'{out_file.name}.grammar.xml'
    root = ET.Element(obj.label)
    for elem in obj.children:
      CodeWriter.construct_tree(root, elem)

    CodeWriter.finish_and_export_xml(root, out_file)
    print(f'Successfully parsed grammar: {out_file}')


  @staticmethod
  def construct_tree(root: ET.Element, obj: Union[Token, GrammarObject]) -> None:
    if type(obj) == Token:
      node = ET.SubElement(root, obj.token_type).text = obj.value
    elif isinstance(obj, GrammarObject):
      node = ET.SubElement(root, obj.label) if obj.label else root
      for child in obj.children:
        CodeWriter.construct_tree(node, child)
    else:
      print(obj)
      raise Exception(f'CodeWriter does not recognize the type of provided object: {type(obj)}. [Token, GrammarObject] are supported')


  @staticmethod
  def finish_and_export_xml(root: ET.Element, out_file) -> None:
    tree = ET.ElementTree(root)
    tree.write(out_file, encoding='utf-8', xml_declaration=True)
