from pathlib import Path
from typing import List
import xml.etree.cElementTree as ET

from .src.codeWriter import CodeWriter
from .src.tokenizer import Token, Tokenizer

def JackAnalyzer(source: Path, out_file: Path, export_tokens: bool = False) -> None:
  writer = CodeWriter()
  tokenizer = Tokenizer(source)
  tokens = []
  while not tokenizer.finished():
    token = tokenizer.next()
    if not token:
      break

    tokens.append(token)

  if export_tokens:
    CodeWriter.export_tokens_as_xml(tokens, out_file)
