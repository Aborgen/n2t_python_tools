import unittest
from unittest.mock import Mock, patch

from .mocks import MockToken
from src.grammar import GrammarObject

class GrammarObjectMethods(unittest.TestCase):
  def test_deposit_invokes_private_deposit_method(self):
    obj = GrammarObject(label=None, keywords=['a'])
    mock_deposit = Mock()
    mock_expected = Mock()
    obj._deposit = mock_deposit
    obj._expected = mock_expected

    self.assertEqual(obj._ptr, 0)
    obj.deposit('a')

    self.assertTrue(mock_deposit.called)
    self.assertTrue(mock_expected.called)
    self.assertEqual(obj._ptr, 1)


  def test_deposit_raises_exception_if_cannot_deposit_more(self):
    obj = GrammarObject(label=None, keywords=['a'])
    mock_deposit = Mock()
    mock_expected = Mock()
    obj._deposit = mock_deposit
    obj._expected = mock_expected

    self.assertEqual(obj._ptr, 0)
    obj.deposit('a')
    with self.assertRaises(Exception):
      obj.deposit('b')

    self.assertTrue(mock_deposit.call_count == 1)
    self.assertTrue(mock_expected.call_count == 1)
    self.assertEqual(obj._ptr, 1)


  def test_private__deposit_group__method(self):
    obj = GrammarObject(label=None, keywords=[])
    mock_deposit = Mock()
    obj._deposit = mock_deposit
    
    obj._deposit_group(group=['a', 'b', 'c'], template=['a', 'b', 'c'])
    
    self.assertTrue(mock_deposit.call_count == 3)


  def test__deposit_group__raises_exception_if_any_argument_is_not_a_list(self):
    obj = GrammarObject(label=None, keywords=[])
    mock_deposit = Mock()
    obj._deposit = mock_deposit
    
    for group, template in [('a', ['a']), (['a'], 'a')]:
      with self.subTest(group=group, template=template):
        with self.assertRaisesRegex(Exception, 'list'):
          obj._deposit_group(group=group, template=template)
        
        self.assertTrue(mock_deposit.call_count == 0)


  def test__deposit_group__raises_exception_if_arguments_do_not_have_the_same_length(self):
    obj = GrammarObject(label=None, keywords=[])
    mock_deposit = Mock()
    obj._deposit = mock_deposit
    
    with self.assertRaisesRegex(Exception, 'length'):
      obj._deposit_group(group=['a', 'b'], template=['a'])
    
    self.assertTrue(mock_deposit.call_count == 0)


  def test__is_comparable__returns_true_if_two_tokens_are_equal(self):
    obj = GrammarObject(label=None, keywords=[])
    with patch('src.grammar.Token', MockToken):
      result = obj._is_comparable(MockToken(1), MockToken(1))

    self.assertTrue(result)


  def test__is_comparable__returns_false_if_two_tokens_are_not_equal(self):
    obj = GrammarObject(label=None, keywords=[])
    with patch('src.grammar.Token', MockToken):
      result = obj._is_comparable(MockToken(1), MockToken(5))

    self.assertFalse(result)


  def test__is_comparable__returns_true_if_expected_paramater_is_a_dict_with_a_single_key(self):
    obj = GrammarObject(label=None, keywords=[])
    result = obj._is_comparable('a', {'key': []})
    self.assertTrue(result)


  def test__is_comparable__throws_exception_if_expected_paramater_is_a_dict_without_exactly_one_key(self):
    obj = GrammarObject(label=None, keywords=[])
    for d in [{}, {'key1':[], 'key2': []}]:
      with self.subTest(d=d):
        with self.assertRaisesRegex(Exception, 'one key'):
          obj._is_comparable('a', d)


  def test__is_comparable__returns_false_if_expected_parameter_is_not_a_Token_or_dict_or_class_type(self):
    obj = GrammarObject(label=None, keywords=[])
    for expected in [1, 'a', list(), True]:
      with self.subTest(expected=expected):
        result = obj._is_comparable('a', expected)
        self.assertFalse(result)


  def test__is_comparable__returns_true_if_expected_parameter_is_a_class_and_obj_parameter_is_instance_of_expected(self):
    obj = GrammarObject(label=None, keywords=[])
    result = obj._is_comparable({}, dict)
    self.assertTrue(result)


  def test__expected__returns_next_keyword(self):
    obj = GrammarObject(label=None, keywords=['a'])
    result = obj._expected()
    self.assertEqual(result, 'a')


  def test__expected__raises_exception_if_there_are_no_more_keywords(self):
    obj = GrammarObject(label=None, keywords=[])
    with self.assertRaisesRegex(Exception, 'no more keywords'):
      obj._expected()


  def test__deposit__raises_exception_if_result_of__is_comparable__is_false(self):
    obj = GrammarObject(label=None, keywords=[])
    mock_comparable = Mock(return_value=False)
    mock_syntax_error = Mock(side_effect=Exception)
    obj._is_comparable = mock_comparable
    obj._syntax_error = mock_syntax_error

    with self.assertRaises(Exception):
      obj._deposit(MockToken(1), MockToken(1))

    self.assertTrue(mock_comparable.called)
    self.assertTrue(mock_syntax_error.called)


  def test__deposit__invokes__deposit_group__if_expected_is_dict_and_key_is_optional_and_value_length_is_greater_than_zero(self):
    obj = GrammarObject(label=None, keywords=[])
    mock_comparable = Mock(return_value=True)
    mock_deposit_group = Mock()
    obj._is_comparable = mock_comparable
    obj._deposit_group = mock_deposit_group

    obj._deposit({'optional': ['a']}, {'optional': ['a']})

    self.assertTrue(mock_comparable.called)
    self.assertTrue(mock_deposit_group.called_with(['a'], ['a']))


  def test__deposit__does_not_invoke__deposit_group__if_expected_is_dict_and_key_is_optional_and_value_length_is_zero(self):
    obj = GrammarObject(label=None, keywords=[])
    mock_comparable = Mock(return_value=True)
    mock_deposit_group = Mock()
    obj._is_comparable = mock_comparable
    obj._deposit_group = mock_deposit_group

    obj._deposit({'optional': []}, {'optional': []})

    self.assertTrue(mock_comparable.called)
    self.assertFalse(mock_deposit_group.called)


  def test__deposit__invokes__deposit_group__if_expected_is_dict_and_key_is_group(self):
    obj = GrammarObject(label=None, keywords=[])
    mock_comparable = Mock(return_value=True)
    mock_deposit_group = Mock()
    obj._is_comparable = mock_comparable
    obj._deposit_group = mock_deposit_group

    obj._deposit({'group': ['a', 'b', 'c']}, {'group': ['a', 'b', 'c']})

    self.assertTrue(mock_comparable.called)
    self.assertTrue(mock_deposit_group.called_with(['a', 'b', 'c'], ['a', 'b', 'c']))


  def test__deposit__invokes__deposit_group__for_each_group_if_expected_is_dict_and_key_is_optional_repeat_and_length_of_value_is_greater_than_zero(self):
    obj = GrammarObject(label=None, keywords=[])
    mock_comparable = Mock(return_value=True)
    mock_deposit_group = Mock()
    obj._is_comparable = mock_comparable
    obj._deposit_group = mock_deposit_group

    obj._deposit({'optional-repeat': [['a', 'b', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c']]}, {'optional-repeat': ['a', 'b','c']})

    self.assertTrue(mock_comparable.called)
    self.assertEqual(mock_deposit_group.call_count, 3)
    self.assertTrue(mock_deposit_group.called_with(['a', 'b', 'c'], ['a', 'b', 'c']))


  def test__deposit__does_not_invoke__deposit_group__if_expected_is_dict_and_key_is_optional_repeat_and_length_of_value_is_zero(self):
    obj = GrammarObject(label=None, keywords=[])
    mock_comparable = Mock(return_value=True)
    mock_deposit_group = Mock()
    obj._is_comparable = mock_comparable
    obj._deposit_group = mock_deposit_group

    obj._deposit({'optional-repeat': []}, {'optional-repeat': []})

    self.assertTrue(mock_comparable.called)
    self.assertFalse(mock_deposit_group.called)


  def test__deposit__does_not_raise_exception_if_expected_is_dict_and_key_is_any_and_given_object_matches(self):
    obj = GrammarObject(label=None, keywords=[])
    mock_comparable = Mock(return_value=True)
    mock_syntax_error = Mock(side_effect=Exception)
    obj._is_comparable = mock_comparable
    obj._syntax_error = mock_syntax_error

    obj._deposit(1, {'any': [1, 2, 3, {'group': [MockToken(1), MockToken(5)]}]})

    self.assertTrue(mock_comparable.called)
    self.assertEqual(obj.children[0], 1)
    self.assertFalse(mock_syntax_error.called)


  def test__deposit__raises_exception_if_expected_is_dict_and_key_is_any_and_given_object_does_not_match(self):
    obj = GrammarObject(label=None, keywords=[])
    mock_comparable = Mock(return_value=True)
    mock_syntax_error = Mock(side_effect=Exception)
    obj._is_comparable = mock_comparable
    obj._syntax_error = mock_syntax_error

    with self.assertRaises(Exception):
      obj._deposit(MockToken('a'), {'any': [MockToken(1), {'group': [MockToken(2), MockToken(5)]}, 'hello']})

    self.assertTrue(mock_comparable.called)
    self.assertEqual(len(obj.children), 0)
    self.assertTrue(mock_syntax_error.called)
