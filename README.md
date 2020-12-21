**---Requires at least python 3.8---**

This repository contains a collection of tools written during the course [nand2tetris](https://www.nand2tetris.org/course). In the first half of the course, the student is asked to build a (virtual) computer starting only with a NAND logic gate. The second half involves the software layer, which is what this repository is for.

**Assembler** \[DRAFT]\
Usage:  ```python3 Assembler.py [source] [symbol_file].json [OPTIONAL]-o [output]```\
Output: \[source].asm or \[output]

The Assembler takes Hack assembly source files and converts them into a series of 16 bit "binary" strings. Rather than being in binary format, these are strings filled with 0s and 1s.

**VMTranslator**\
Usage:  ```python3 -m VMTranslator [source] [OPTIONAL]-o [output]```\
Output: \[source].asm or \[output]

The VMTranslator takes Jack virtual machine code and outputs it into Hack assembly language. Source can be a single .vm file, or a directory.

**JackCompiler**\
Usage:  ```python3 -m JackCompiler [source]```\
Output: \[source].vm or \[compiled directory]

The JackCompiler is stage one of the Jack two-tier compiler, and it compiles jack files into Jack virtual machine code. Source can be a single .jack file, or a directory.


