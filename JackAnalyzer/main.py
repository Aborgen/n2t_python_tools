from pathlib import Path
from typing import Union, List

from .src.tokenizer import Tokenizer

def JackAnalyzer(source: Union[List[Path], Path], out_file: Path, namespace: str) -> None:
  tokenizer = Tokenizer(source)
  tokens = []
  while not tokenizer.finished():
    token = tokenizer.next()
    if not token:
      break

    tokens.append(token)

  print(tokens)
