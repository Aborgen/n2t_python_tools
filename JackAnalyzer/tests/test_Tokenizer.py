import re
import unittest
from pathlib import Path
from unittest.mock import Mock

from src.exceptions import TokenizerError
from src.tokenizer import Token, Tokenizer

TEST_FILES = Path(__file__).parent / 'testFiles'

class TestTokenizerIO(unittest.TestCase):
  def test_throws_if_file_does_not_exist(self):
    filename = TEST_FILES / 'does_not_exist.jack'
    tokenizer = Tokenizer(filename)
    with self.assertRaises(FileNotFoundError):
      tokenizer.next()


  def test_next_method_throws_if_token_does_not_fit_any_category(self):
    tokenizer = Tokenizer('')
    tokenizer._generator = iter(['bad value'])
    with self.assertRaisesRegex(TokenizerError, 'Jack file.+Token not recognized') as e:
      tokenizer.next()


  def test_next_method_returns_a_symbol_token(self):
    tokenizer = Tokenizer('')
    tokenizer._generator = iter([';'])
    token = tokenizer.next()
    expected = Token(';', 'symbol', 1, 1)
    self.assertEqual(token, expected)


  def test_next_method_returns_a_keyword_token(self):
    tokenizer = Tokenizer('')
    tokenizer._generator = iter(['class'])
    token = tokenizer.next()
    expected = Token('class', 'keyword', 1, 1)
    self.assertEqual(token, expected)


  def test_next_method_returns_an_integer_token(self):
    tokenizer = Tokenizer('')
    tokenizer._generator = iter(['700'])
    token = tokenizer.next()
    expected = Token('700', 'intConst', 1, 1)
    self.assertEqual(token, expected)


  def test_next_method_returns_a_string_token(self):
    tokenizer = Tokenizer('')
    tokenizer._generator = iter([r'"\"hello world,\" said the man"'])
    token = tokenizer.next()
    expected = Token('"hello world," said the man', 'stringConst', 1, 1)
    self.assertEqual(token, expected)


  def test_next_method_returns_an_identifier_token(self):
    tokenizer = Tokenizer('')
    tokenizer._generator = iter(['fooBar'])
    token = tokenizer.next()
    expected = Token('fooBar', 'identifier', 1, 1)
    self.assertEqual(token, expected)


  def test_throws_if_next_invoked_while_status_is_FINISHED(self):
    mock_func = Mock()
    tokenizer = Tokenizer('')
    tokenizer._generator = mock_func
    tokenizer._status = Tokenizer.EStatus.FINISHED
    with self.assertRaisesRegex(TokenizerError, '(f|F)inished'):
      tokenizer.next()

    self.assertFalse(mock_func.called)

class TestSyntax(unittest.TestCase):
  def test_throws_if_string_constant_has_missing_end_double_quote(self):
    filename = TEST_FILES / 'MalformedString.jack'
    tokenizer = Tokenizer(filename)
    line = 5
    character = 15
    for i in range(16):
      tokenizer.next()

    with self.assertRaisesRegex(TokenizerError, f'(L|l)ine.*{line}.*(C|c)haracter.*{character}'):
      tokenizer.next()


  def test_throws_if_string_constant_has_unescaped_double_quote_within(self):
    filename = TEST_FILES / 'UnescapedDoubleQuotesInString.jack'
    tokenizer = Tokenizer(filename)
    line = 5
    character = 15
    for i in range(16):
      tokenizer.next()

    with self.assertRaisesRegex(TokenizerError, f'(L|l)ine.*{line}.*(C|c)haracter.*{character}'):
      tokenizer.next()


  def test_returns_tokens_until_exhausted(self):
    expected=[Token('class','keyword',1,1),Token('CorrectSyntax','identifier',1,7),Token('{','symbol',1,21),Token('field','keyword',2,3),Token('String','identifier',2,9),Token('bar','identifier',2,16),Token(';','symbol',2,19),Token('constructor','keyword',4,3),Token('CorrectSyntax','identifier',4,15),Token('new','identifier',4,29),Token('(','symbol',4,32),Token(')','symbol',4,33),Token('{','symbol',4,35),Token('let','keyword',5,5),Token('bar','identifier',5,9),Token('=','symbol',5,13),Token('Hello world!','stringConst',5,15),Token(';','symbol',5,29),Token('return','keyword',6,5),Token('this','keyword',6,12),Token(';','symbol',6,16),Token('}','symbol',7,3),Token('method','keyword',9,3),Token('void','keyword',9,10),Token('greetings','identifier',9,15),Token('(','symbol',9,24),Token(')','symbol',9,25),Token('{','symbol',9,27),Token('do','keyword',10,5),Token('Output','identifier',10,8),Token('.','symbol',10,14),Token('printString','identifier',10,15),Token('(','symbol',10,26),Token('bar','identifier',10,27),Token(')','symbol',10,30),Token(';','symbol',10,31),Token('return','keyword',11,5),Token(';','symbol',11,11),Token('}','symbol',12,3),Token('}','symbol',13,1)]

    filename = TEST_FILES / 'CorrectSyntax.jack'
    tokenizer = Tokenizer(filename)
    tokens = []
    while not tokenizer.finished():
      token = tokenizer.next()
      if not token:
        break
      
      tokens.append(token)

    self.assertEqual(tokens, expected)


  def test_skips_rest_of_line_after_line_comment(self):
    expected=[Token('let','keyword',1,1),Token('foo','identifier',1,5),Token('=','symbol',1,9),Token('5','intConst',1,11),Token(';','symbol',1,12)]
    filename = TEST_FILES / 'IgnoreLineComment.jack'
    tokenizer = Tokenizer(filename)
    tokens = []
    while not tokenizer.finished():
      token = tokenizer.next()
      if not token:
        break
      
      tokens.append(token)

    self.assertEqual(tokens, expected)


  def test_skips_everything_inbetween_multiline_comment(self):
    expected=[Token('let','keyword',5,5),Token('foo','identifier',5,9),Token('=','symbol',5,13),Token('5','intConst',5,15),Token(';','symbol',5,16)]
    filename = TEST_FILES / 'IgnoreMultilineComment.jack'
    tokenizer = Tokenizer(filename)
    tokens = []
    while not tokenizer.finished():
      token = tokenizer.next()
      if not token:
        break
      
      tokens.append(token)

    self.assertEqual(tokens, expected)
