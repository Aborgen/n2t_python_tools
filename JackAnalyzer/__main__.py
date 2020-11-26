import argparse
from pathlib import Path
from .main import JackAnalyzer

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('source', type=str, help='Path to the Jack source')
  parser.add_argument('--xml-tokens', action='store_true', help='Whether or not to output tokens as an xml file')
  args = parser.parse_args()

  source = Path.cwd() / args.source
  if source.is_dir():
    sources = source.iterdir()
  else:
    sources = [source]

  root_dir = Path(source.stem)
  if root_dir.is_dir():
    for item in root_dir.iterdir():
      item.unlink()

    root_dir.rmdir()

  root_dir.mkdir()
  for child in sources:
    if child.suffix != '.jack':
      continue

    out_path = root_dir / child.stem
    JackAnalyzer(child, out_path, args.xml_tokens)
