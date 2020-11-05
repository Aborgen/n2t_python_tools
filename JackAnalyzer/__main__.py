import argparse
from pathlib import Path
from .main import JackAnalyzer

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('source', type=str, help='Path to the Jack source')
  parser.add_argument('-o', '--out-file', type=str, help='Name of the output')
  parser.add_argument('--xml-tokens', action='store_true', help='Whether or not to output tokens as an xml file')
  args = parser.parse_args()

  source = Path.cwd() / args.source
  namespace = source.stem
  if not args.out_file:
    out_file = f'{namespace}'
  else:
    out_file = args.out_file

  if source.is_dir():
    out_file = Path.cwd() / f'{namespace}.{out_file}'
    sources = source.iterdir()
  else:
    out_file = Path.cwd() / out_file
    sources = [source]

  for child in sources:
    if child.suffix != '.jack':
      continue

    JackAnalyzer(child, out_file, args.xml_tokens)
