from pathlib import Path
from typing import List
import xml.etree.cElementTree as ET

from .src.codeWriter import CodeWriter
from .src.tokenizer import Token, Tokenizer

def JackAnalyzer(source: Path, out_file: Path, export_tokens: bool = False) -> None:
  tokenizer = Tokenizer(source)
  tokens = []
  while not tokenizer.finished():
    token = tokenizer.next()
    if not token:
      break

    tokens.append(token)

  if export_tokens:
    self._export_xml_tokens(tokens, out_file)

  parser = Parser(tokens, source, out_file, export_tokens)


def _export_xml_tokens(self, tokens: List[Token], out_file: Path) -> None:

  CodeWriter.export_tokens_as_xml(tokens, out_file)