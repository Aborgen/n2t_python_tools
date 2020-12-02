from __future__ import annotations

from .src.codeGenerator import CodeGenerator
from .src.analyzer.jackanalyzer import JackAnalyzer

def JackCompiler(source: Path, out_path: Path, export_tokens: bool = False) -> None:
  obj = JackAnalyzer(source, out_path, export_tokens)
  generator = CodeGenerator(obj)
  generator.generate()


