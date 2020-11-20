from __future__ import annotations

from pathlib import Path
from typing import Union
import xml.etree.cElementTree as ET

from .src.codeWriter import CodeWriter
from .src.grammar import GrammarObject
from .src.parser import Parser
from .src.tokenizer import Token, Tokenizer

def JackAnalyzer(source: Path, out_file: Path, export_tokens: bool = False) -> None:
  tokenizer = Tokenizer(source)
  tokens = []
  while not tokenizer.finished():
    token = tokenizer.next()
    if not token:
      break

    tokens.append(token)


  parser = Parser(tokens, source, out_file, export_tokens)
  obj = parser.parse()
  if export_tokens:
    _export_xml_tokens(tokens, obj, out_file)


def _export_xml_tokens(tokens: list[Token], obj: GrammarObject, out_file: Path) -> None:
  CodeWriter.export_tokens_as_xml(tokens, out_file)
  CodeWriter.export_grammar_objects_as_xml(obj, out_file)
