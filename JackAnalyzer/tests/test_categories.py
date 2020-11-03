import unittest

from src.categories import is_integer_constant, is_string_constant, is_identifier

class CategoriesValidators(unittest.TestCase):
  def test_is_integer_constant_returns_false_if_input_cannot_be_cast_to_int(self):
    for value in ['hunter2', '@@', b'\xde\xad\xbe\xef']:
      with self.subTest():
        self.assertFalse(is_integer_constant(value))


  def test_is_integer_constant_returns_false_if_input_is_out_of_range(self):
    for value in ['-1', 2 ** 15, '999999']:
      with self.subTest():
        self.assertFalse(is_integer_constant(value))


  def test_is_integer_constant_returns_true_if_input_is_in_range(self):
    for value in ['0', 2 ** 15 - 1, '99']:
      with self.subTest():
        self.assertTrue(is_integer_constant(value))


  def test_is_string_constant_returns_false_if_not_sandwiched_between_double_quotation_marks(self):
    self.assertFalse(is_string_constant('hello world'))


  def test_is_string_constant_returns_false_if_mismatched_double_quotation_marks(self):
    self.assertFalse(is_string_constant('"hello world'))


  def test_is_string_constant_returns_false_if_non_escaped_double_quotations_appear_other_than_extremities(self):
    self.assertFalse(is_string_constant('"The man said "hello world""'))


  def test_is_string_constant_returns_true_if_sandwiched_between_double_quotation_marks(self):
    self.assertTrue(is_string_constant('"hello world"'))


  def test_is_string_constant_returns_true_if_escaped_double_quotations_appear_between_outer(self):
    self.assertTrue(is_string_constant(r'"The man said \"hello world\""'))


  def test_is_identifier_returns_false_if_input_does_not_begin_with_letter_or_underscore(self):
    for value in ['42Street', '$var', '100dalmations']:
      with self.subTest():
        self.assertFalse(is_identifier(value))


  def test_is_identifier_returns_false_if_contains_anything_other_than_alphanumeric_and_underscore(self):
    for value in ['Fab-Lab', 'Old and Bold', 'fl33tw00dm@ck']:
      with self.subTest():
        self.assertFalse(is_identifier(value))


  def test_is_identifier_returns_true_if_contains_only_alphanumeric_and_underscore(self):
    for value in ['fooBar', 'result', 'a2int']:
      with self.subTest():
        self.assertTrue(is_identifier(value))
