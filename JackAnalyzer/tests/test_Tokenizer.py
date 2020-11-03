import re
import unittest
from unittest.mock import Mock

from src.exceptions import TokenizerError
from src.tokenizer import Token, Tokenizer

class TestTokenizerIO(unittest.TestCase):
  def test_throws_if_file_does_not_exist(self):
    filename = 'does_not_exist.jack'
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
