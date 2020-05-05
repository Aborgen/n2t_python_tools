**---Requires at least python 3.7.5---**

This repository contains a collection of tools written during the course [nand2tetris](https://www.nand2tetris.org/course). In the first half of the course, the student is asked to build a (virtual) computer starting only with a NAND logic gate. The second half involves the software layer, which is what this repository is for.

**Assembler** \[DRAFT]\
Usage:  ```python3 Assembler.py [source] [symbol_file].json [OPTIONAL]-o [out_directory]```\
Output: \[source].asm or \[out_directory]

The Assembler takes Hack assembly source files and converts them into a series of 16 bit "binary" strings. Rather than being in binary format, these are strings filled with 0s and 1s.

**VMTranslator**\
Usage:  ```python3 -m VMTranslator [source] [OPTIONAL]-o [out_directory]```\
Output: \[source].asm or \[out_directory]\

The VMTranslator takes Jack virtual machine code and outputs it into Hack assembly language.

