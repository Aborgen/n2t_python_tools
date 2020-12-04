from __future__ import annotations

from .src.analyzer.jackanalyzer import JackAnalyzer
from .src.codeGenerator import CodeGenerator
from .src.codeWriter import VMWriter

def JackCompiler(source: Path, out_path: Path, export_tokens: bool = False) -> None:
  writer = VMWriter()
  writer.open(out_path)
  obj = JackAnalyzer(source, out_path, export_tokens)
  generator = CodeGenerator(obj, writer)
  generator.generate()


