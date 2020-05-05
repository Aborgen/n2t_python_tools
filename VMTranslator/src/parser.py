from inspect import cleandoc
from .command import ArithmeticCommand
from .command import FlowCommand
from .command import FunctionCommand
from .command import LogicalCommand
from .command import MemoryCommand
from .utils import iterate_enum
from .utils import is_arithmetic_command
from .utils import is_flow_command
from .utils import is_function_command
from .utils import is_logical_command
from .utils import is_memory_command

import textwrap

class Parser():
  def __init__(self, namespace: str):
    self.namespace = namespace
    self.filename = ''
    self.function_name = '$$GLOBAL$$'
    self.command_index = 0


  def set_filename(self, filename: str) -> None:
    self.filename = filename
    self.command_index = 0


  def init_SP(self) -> str:
    assembly =\
    f'''
    @256
    D=A
    @SP
    M=D  // SP = 256
    '''
    return cleandoc(assembly)


  def parse(self, l: str) -> str:
    if is_memory_command(l):
      assembly = self._memory_command_to_assembly(MemoryCommand(l))
    elif is_arithmetic_command(l):
      assembly = self._arithmetic_command_to_assembly(ArithmeticCommand(l))
    elif is_logical_command(l):
      assembly = self._logical_command_to_assembly(LogicalCommand(l))
    elif is_function_command(l):
      assembly = self._function_command_to_assembly(FunctionCommand(l))
    elif is_flow_command(l):
      assembly = self._flow_command_to_assembly(FlowCommand(l))
    else:
      raise TypeError(f'Parser error: unrecognized command format: {l}')

    self.command_index += 1
    return assembly
    

  def _memory_command_to_assembly(self, command: MemoryCommand) -> str:
    if type(command) != MemoryCommand:
      raise TypeError(f'Provided command is not a MemoryCommand: {command}')

    if command.keyword == MemoryCommand.EKeyword.PUSH:
      assembly = self._push_to_assembly(command)
    elif command.keyword == MemoryCommand.EKeyword.POP:
      assembly = self._pop_to_assembly(command)
    else:
      raise TypeError(f'MemoryCommand neither pushes or pops: {command}')

    return assembly


  def _push_to_assembly(self, command: MemoryCommand) -> str:
    if command.segment == MemoryCommand.ESegment.CONSTANT:
      assembly =\
      f'''
      // {command}
      @{command.index}
      D=A
      '''
    elif command.segment == MemoryCommand.ESegment.TEMP:
      assembly =\
      f'''
      // {command}
      @{command.index}
      D=A
      @5    // temp variables are stored in memory starting at RAM[5]
      A=D+A
      D=M
      '''
    elif command.segment == MemoryCommand.ESegment.STATIC:
      assembly =\
      f'''
      // {command}
      @{command.index}
      D=A
      @{self.namespace}${self.filename}.{command.index}
      D=M
      '''
    elif command.segment == MemoryCommand.ESegment.POINTER:
      if command.index == 0:
        section = MemoryCommand.ESegment.THIS
      elif command.index == 1:
        section = MemoryCommand.ESegment.THAT
      else:
        raise ValueError('Index of pointer may only be 0 or 1')

      assembly =\
      f'''
      // {command}
      @{section}
      D=M
      '''
    else:
      assembly =\
      f'''
      // {command}
      @{command.index}
      D=A
      @{command.segment}
      A=D+M
      D=M
      '''

    ending =\
    f'''
    @SP
    A=M
    M=D
    @SP
    M=M+1 // ++SP
    // END
    '''

    return f'{cleandoc(assembly)}\n\n{cleandoc(ending)}'


  def _pop_to_assembly(self, command: MemoryCommand) -> str:
    if command.segment == MemoryCommand.ESegment.CONSTANT:
      raise TypeError('Cannot pop a constant')
    elif command.segment == MemoryCommand.ESegment.TEMP:
      assembly =\
      f'''
      // {command}
      @{command.index}
      D=A
      @5     // temp variables are stored in memory starting at RAM[5]
      D=D+A
      @R13
      M=D

      @SP
      AM=M-1 // --SP
      D=M
      @R13
      A=M
      M=D
      // END
      '''
    elif command.segment == MemoryCommand.ESegment.STATIC:
      assembly =\
      f'''
      // {command}
      @SP
      AM=M-1 // --SP
      D=M
      @{self.namespace}${self.filename}.{command.index}
      M=D
      // END
      '''
    elif command.segment == MemoryCommand.ESegment.POINTER:
      if command.index == 0:
        section = MemoryCommand.ESegment.THIS
      elif command.index == 1:
        section = MemoryCommand.ESegment.THAT
      else:
        raise ValueError('Index of pointer may only be 0 or 1')

      assembly =\
      f'''
      // {command}
      @SP
      AM=M-1 // --SP
      D=M
      @{section}
      M=D
      // END
      '''
    else:
      assembly =\
      f'''
      // {command}
      @{command.index}
      D=A
      @{command.segment}
      D=D+M
      @R13
      M=D

      @SP
      AM=M-1 // --SP
      D=M
      @R13
      A=M
      M=D
      // END
      '''

    return cleandoc(assembly)


  def _arithmetic_command_to_assembly(self, command: ArithmeticCommand) -> str:
    if type(command) != ArithmeticCommand:
      raise TypeError(f'Provided command is not an ArithmeticCommand: {command}')
    
    if command.arg_count == 2:
      preamble =\
      f'''
      // {command}
      @SP
      AM=M-1 // --SP
      D=M
      @y
      M=D    // y = stack.pop()

      @SP
      AM=M-1 // --SP
      D=M
      @x
      M=D    // x = stack.pop()
      '''
      if command.keyword == ArithmeticCommand.EKeyword.ADD:
        assembly =\
        f'''
        @x
        D=M
        @y
        D=D+M // D = x + y
        '''
      elif command.keyword == ArithmeticCommand.EKeyword.SUB:
        assembly =\
        f'''
        @x
        D=M
        @y
        D=D-M // D = x - y
        '''
      elif command.keyword == ArithmeticCommand.EKeyword.LT:
        tag = f'x_lt_y_{self.command_index}'
        assembly =\
        f'''
        @x
        D=M
        @y
        D=D-M
        @{self.namespace}${self.filename}$POSITIVE__{tag} // x - y < 0
        D;JLT
        @{self.namespace}${self.filename}$NEGATIVE__{tag} // else
        0;JMP

        ({self.namespace}${self.filename}$POSITIVE__{tag})
          D=-1
          @{self.namespace}${self.filename}$END__{tag}
          0;JMP
        ({self.namespace}${self.filename}$NEGATIVE__{tag})
          D=0
        ({self.namespace}${self.filename}$END__{tag})
          // Continue
        '''
      elif command.keyword == ArithmeticCommand.EKeyword.EQ:
        tag = f'x_eq_y_{self.command_index}'
        assembly =\
        f'''
        @x
        D=M
        @y
        D=D-M
        @{self.namespace}${self.filename}$POSITIVE__{tag} // x - y == 0
        D;JEQ
        @{self.namespace}${self.filename}$NEGATIVE__{tag} // else
        0;JMP

        ({self.namespace}${self.filename}$POSITIVE__{tag})
          D=-1
          @{self.namespace}${self.filename}$END__{tag}
          0;JMP
        ({self.namespace}${self.filename}$NEGATIVE__{tag})
          D=0
        ({self.namespace}${self.filename}$END__{tag})
          // Continue
        '''
      elif command.keyword == ArithmeticCommand.EKeyword.GT:
        tag = f'x_gt_y_{self.command_index}'
        assembly =\
        f'''
        @x
        D=M
        @y
        D=D-M
        @{self.namespace}${self.filename}$POSITIVE__{tag} // x - y > 0
        D;JGT
        @{self.namespace}${self.filename}$NEGATIVE__{tag} // else
        0;JMP

        ({self.namespace}${self.filename}$POSITIVE__{tag})
          D=-1
          @{self.namespace}${self.filename}$END__{tag}
          0;JMP
        ({self.namespace}${self.filename}$NEGATIVE__{tag})
          D=0
        ({self.namespace}${self.filename}$END__{tag})
          // Continue
        '''
    elif command.arg_count == 1:
      preamble =\
      f'''
      // {command}
      @SP
      AM=M-1 // --SP
      D=M
      @x
      M=D    // x = stack.pop()
      '''
      if command.keyword == ArithmeticCommand.EKeyword.NEG:
        assembly =\
        f'''
        @x
        D=-M   // D = -x
        '''
    else:
      raise NotImplementedError(f'Arithmetic command has an unsupported number of arguments: {command.arg_count}')

    # D register should contain the appropriate value as dictated by command.
    # This bit pushes that value on to the top of the stack.
    ending =\
    f'''
    @SP
    A=M
    M=D
    @SP
    M=M+1 // ++SP
    // END
    '''

    return f'{cleandoc(preamble)}\n\n{cleandoc(assembly)}\n\n{cleandoc(ending)}'


  def _logical_command_to_assembly(self, command: LogicalCommand) -> str:
    if type(command) != LogicalCommand:
      raise TypeError(f'Provided command is not a LogicalCommand: {command}')
    
    if command.arg_count == 2:
      preamble =\
      f'''
      // {command}
      @SP
      AM=M-1 // --SP
      D=M
      @y
      M=D    // y = stack.pop()

      @SP
      AM=M-1 // --SP
      D=M
      @x
      M=D    // x = stack.pop()
      '''
      if command.keyword == LogicalCommand.EKeyword.AND:
        assembly =\
        f'''
        @x
        D=M
        @y
        D=D&M  // D = x & y
        '''
      elif command.keyword == LogicalCommand.EKeyword.OR:
        assembly =\
        f'''
        @x
        D=M
        @y
        D=D|M  // D = x | y
        '''
    elif command.arg_count == 1:
      preamble =\
      f'''
      // {command}
      @SP
      AM=M-1 // --SP
      D=M
      @x
      M=D    // x = stack.pop()
      '''
      if command.keyword == LogicalCommand.EKeyword.NOT:
        assembly =\
        f'''
        @x
        D=!M   // D = !x
        '''

    else:
      raise NotImplementedError(f'Logical command has an unsupported number of arguments: {command.arg_count}')

    # D register should contain the appropriate value as dictated by command.
    # This bit pushes that value on to the top of the stack.
    ending =\
    f'''
    @SP
    A=M
    M=D
    @SP
    M=M+1 // ++SP
    // END
    '''

    return f'{cleandoc(preamble)}\n\n{cleandoc(assembly)}\n\n{cleandoc(ending)}'


  def _function_command_to_assembly(self, command: FunctionCommand) -> str:
    if type(command) != FunctionCommand:
      raise TypeError(f'Provided command is not an FunctionCommand: {command}')

    if command.keyword == FunctionCommand.EKeyword.FUNCTION:
      # For use in FlowCommands
      self.function_name = command.function_name

      function_tag =\
      f'''
      // {command}
      ({command.function_name})
      '''

      init_local =\
      '''
      @0
      D=A
      @SP
      A=M
      M=D
      @SP
      M=M+1 // local {}
      '''
      variables = ''.join([init_local.format(i) for i in range(command.variable_count)])

      assembly = f'{cleandoc(function_tag)}\n{cleandoc(variables)}\n// END'

    if command.keyword == FunctionCommand.EKeyword.CALL:
      return_address = f'Function_Return${self.namespace}${self.filename}.{command.function_name}__{self.command_index}'
      push_return_address =\
      f'''
      // {command}
      @{return_address}
      D=A
      @SP
      A=M
      M=D
      @SP
      M=M+1
      '''

      push_memory =\
      '''
      @{}
      D=M
      @SP
      A=M
      M=D
      @SP
      M=M+1 // Freeze {} pointer
      '''

      segments = ''.join([push_memory.format(keyword, keyword.value) for keyword in FunctionCommand.saveable_memory_segments])

      prepare_stack =\
      f'''
      @{command.variable_count}    // nArgs
      D=A
      @5    // 5 is the number of items pushed to the stack
      D=D+A
      @SP
      D=M-D
      @ARG
      M=D   // argument 0 = SP - (5 + nArgs)

      @SP
      D=M
      @LCL
      M=D
      @{command.function_name}
      0;JMP
      ({return_address})
      // END
      '''

      assembly = f'{cleandoc(push_return_address)}\n\n{cleandoc(segments)}\n\n{cleandoc(prepare_stack)}'

    if command.keyword == FunctionCommand.EKeyword.RETURN:
      assembly =\
      f'''
      // {command}
      @LCL
      D=M
      @R14
      M=D    // Frame pointer

      @5
      D=A
      @R14
      A=M-D
      D=M
      @R13
      M=D    // Store return address

      @SP
      AM=M-1 // --SP
      D=M
      @ARG
      A=M
      M=D    // Store return value in argument[0]

      @ARG
      D=M
      @SP
      M=D+1  // Restore stack pointer

      @R14
      AM=M-1
      D=M
      @THAT
      M=D    // Restore that pointer

      @R14
      AM=M-1
      D=M
      @THIS
      M=D    // Restore this pointer

      @R14
      AM=M-1
      D=M
      @ARG
      M=D    // Restore argument pointer

      @R14
      AM=M-1
      D=M
      @LCL
      M=D    // Restore local pointer

      @R13
      A=M
      0;JMP  // Return to caller
      // END
      '''

    return cleandoc(assembly)

  def _flow_command_to_assembly(self, command: FlowCommand) -> str:
    if type(command) != FlowCommand:
      raise TypeError(f'Provided command is not an FlowCommand: {command}')
    elif not self.function_name:
      raise Exception(f'{command.keyword.value} keyword may only be used within a function')

    label = f'{self.namespace}${self.filename}${self.function_name}${command.symbol}'
    if command.keyword == FlowCommand.EKeyword.LABEL:
      assembly =\
      f'''
      // {command}
      ({label})
      // END
      '''
    elif command.keyword == FlowCommand.EKeyword.GOTO:
      assembly =\
      f'''
      // {command}
      @{label}
      0;JMP
      // END
      '''
    elif command.keyword == FlowCommand.EKeyword.IF_GOTO:
      assembly =\
      f'''
      // {command}
      @SP
      AM=M-1 //--SP
      D=M
      @{label}
      D;JNE
      // END
      '''

    return cleandoc(assembly)
