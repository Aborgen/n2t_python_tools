---Requires at least python 3.7.5---

This repository contains a collection of tools written during the course nand2tetris [https://www.nand2tetris.org/course].

Assembler.py [DRAFT]
Usage:  python3 Assembler.py [source] [symbol_file].json [OPTIONAL]-o [out_directory]
Output: [source].asm | [out_directory]
Description: The Assembler takes HACK assembly source files and converts them into a series of "binary" strings. Rather than being in binary format, these are strings of length 16 filled with 0s and 1s.

VMTranslator
Usage:  python3 -m VMTranslator [source] [OPTIONAL]-o [out_directory]
Output: [source].asm | [out_directory]
Description: The VMTranslator takes virtual machine code and outputs it into HACK assembly language.

