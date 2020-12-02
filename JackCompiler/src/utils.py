from .categories import is_identifier

data_types = set(['int', 'char', 'boolean', 'void'])
subroutine_types = set(['constructor', 'function', 'method'])

def clean_string_constant(s: str):
  return s[1:-1].replace('\\"', '"')


def validate_data_types(s: str) -> bool:
  return s in data_types or is_identifier(s)


def validate_subroutine_types(s: str) -> bool:
  return s in subroutine_types
