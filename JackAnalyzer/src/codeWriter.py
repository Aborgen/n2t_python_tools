from pathlib import Path
from typing import List, Union
import xml.etree.ElementTree as ET

from .grammar import GrammarObject
from .tokenizer import Token

class CodeWriter():
  @staticmethod
  def export_tokens_as_xml(tokens: List[Token], out_path: Path) -> None:
    out_path = out_path.parent / f'{out_path.name}T.xml'
    root = ET.Element('tokens')
    for token in tokens:
      CodeWriter.construct_tree(root, token)

    CodeWriter.finish_and_export_xml(root, out_path)
    print(f'Successfully tokenized: {out_path}')


  @staticmethod
  def export_grammar_objects_as_xml(obj: GrammarObject, out_path: Path) -> None:
    out_path = out_path.parent / f'{out_path.name}.xml'
    root = ET.Element(obj.label)
    for elem in obj.children:
      CodeWriter.construct_tree(root, elem)

    CodeWriter.finish_and_export_xml(root, out_path)
    print(f'Successfully parsed grammar: {out_path}')


  @staticmethod
  def construct_tree(root: ET.Element, obj: Union[Token, GrammarObject]) -> None:
    if type(obj) == Token:
      node = ET.SubElement(root, obj.token_type).text = f' {obj.value} '
    elif isinstance(obj, GrammarObject):
      node = ET.SubElement(root, obj.label) if obj.label else root
      for child in obj.children:
        CodeWriter.construct_tree(node, child)

      # This is done because the provided test files has empty tags extend to the next line, and I cannot figure out how to collapse them into a self closing tag.
      if len(obj.children) == 0:
        node.text = '\n'
    else:
      print(obj)
      raise Exception(f'CodeWriter does not recognize the type of provided object: {type(obj)}. [Token, GrammarObject] are supported')


  @staticmethod
  def finish_and_export_xml(root: ET.Element, out_path) -> None:
    tree = ET.ElementTree(root)
    tree.write(out_path, encoding='utf-8', xml_declaration=False, short_empty_elements=False)
