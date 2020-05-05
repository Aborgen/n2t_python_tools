from enum import Enum
import re
from typing import Optional

def iterate_enum(ETarget: Enum, s: str) -> Optional[Enum]:
  for e in ETarget:
    if s == e.value:
      return e

  return None


def is_arithmetic_command(l: str) -> bool:
  from .command import ArithmeticCommand
  return bool(iterate_enum(ArithmeticCommand.EKeyword, l))


def is_flow_command(l: str) -> bool:
  from .command import FlowCommand
  pattern = '^(?P<keyword>[a-zA-Z-]+) (?P<symbol>[a-zA-Z0-9_.:]+)$'
  result = re.match(pattern, l)
  return (
          result and
          iterate_enum(FlowCommand.EKeyword, result.group('keyword')) and
          is_symbol(result.group('symbol'))
         )


def is_function_command(l: str) -> bool:
  from .command import FunctionCommand
  pattern = '^(?P<keyword>[a-zA-Z]+)(?: (?P<function_name>[0-9a-zA-Z_.:]+) (?P<variable_count>[0-9]+))?$'
  result = re.match(pattern, l)

  r = result and iterate_enum(FunctionCommand.EKeyword, result.group('keyword'))
  if result and result['function_name']:
    r = r and is_symbol(result.group('function_name'))

  return r


def is_logical_command(l: str) -> bool:
  from .command import LogicalCommand
  return bool(iterate_enum(LogicalCommand.EKeyword, l))


def is_memory_command(l: str) -> bool:
  from .command import MemoryCommand
  pattern = '^(?P<keyword>[a-zA-Z]+) (?P<segment>[a-zA-Z]+) (?P<index>[0-9]+)$'
  result = re.match(pattern, l)
  return (
          result and
          iterate_enum(MemoryCommand.EKeyword, result.group('keyword')) and
          iterate_enum(MemoryCommand.ESegment, result.group('segment'))
         )


def is_symbol(l: str) -> bool:
  return re.match('^[a-zA-Z_.:]{1}[a-zA-Z0-9_.:]*$', l)
