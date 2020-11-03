import re

keywords = set([
  'class', 'constructor', 'function', 'method', 'field', 'static', 'var',
  'int', 'char', 'boolean', 'void', 'true', 'false',
  'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'
])

symbols = set([
  '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'
])

def is_integer_constant(n: int) -> bool:
  try:
    n = int(n)
  except:
    return False

  return 0 <= n <= 2 ** 15 - 1


def is_string_constant(s: str) -> bool:
  return bool(re.match(r'^"(\\"|[^"])*"$', s))


def is_identifier(s: str) -> bool:
  return bool(re.match('^[a-zA-Z_][a-zA-Z0-9_]*$', s))
