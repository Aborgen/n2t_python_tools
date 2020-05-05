from pathlib import Path
from typing import List
from typing import Union
from .src.parser import Parser
from .src.codeWriter import CodeWriter

def VMTranslator_loop(source: Path, parser: Parser, writer: CodeWriter) -> None:
  parser.set_filename(filename=source.stem)
  try:
    l = ''
    line_number = 0
    with open(source, 'r') as f:
      while True:
        l = f.readline()
        if not l:
          break

        l = l.strip()
        if not l or (len(l) > 1 and l[:2] == '//'):
          continue

        line_number += 1
        l = l.split('//')[0].strip()
        assembly = parser.parse(l)
        writer.out(assembly)

      print(f'Done translating {line_number} lines')
      print(f'Source:\t{source}\n')

  except Exception as e:
    raise Exception(f'Problem with translating {str(source)} line number {line_number}, [{l}]: {e}')


def VMTranslator(source: Union[List[Path], Path], out_file: Path, namespace: str) -> None:
  try:
    parser = Parser(namespace)
    writer = CodeWriter()
    writer.open(out_file)
    if type(source) == list:
      parser.set_filename('SYSTEM')
      writer.out(parser.init_SP())
      writer.out(parser.parse('call Sys.init 0'))

      for f in source:
        VMTranslator_loop(f, parser, writer)
    else:
      VMTranslator_loop(source, parser, writer)

    writer.close()
    print(f'Out: {out_file}')
  except Exception as e:
    raise Exception(f'Exception encountered while translating, {e}')
