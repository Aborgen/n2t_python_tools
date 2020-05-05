import argparse
from pathlib import Path
from .main import VMTranslator

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('source', type=str, help='Path to the vm source')
  parser.add_argument('-o', '--out-file', type=str, help='Name of the output')
  args = parser.parse_args()

  source = Path.cwd() / args.source
  namespace = source.stem
  if not args.out_file:
    out_file = f'{namespace}.asm'
  else:
    out_file = args.out_file

  out_file = Path.cwd() / out_file
  if source.is_dir():
    source = [child for child in source.iterdir() if child.suffix == '.vm']

  VMTranslator(source, out_file, namespace=namespace)
