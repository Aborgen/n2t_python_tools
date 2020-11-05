from pathlib import Path
from typing import List
import xml.etree.cElementTree as ET

from .tokenizer import Token

class CodeWriter():
  @staticmethod
  def export_tokens_as_xml(tokens: List[Token], out_file: Path) -> None:
    out_file = out_file.parent / (out_file.name + '.xml')
    root = ET.Element('tokens')
    for token in tokens:
      ET.SubElement(root, token.tokenType).text = token.value

    tree = ET.ElementTree(root)
    tree.write(out_file, encoding='utf-8', xml_declaration=True)
    print(f'Successfully tokenized: {out_file}')
