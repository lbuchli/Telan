#!/usr/bin/env python3

import lexer
import parser
import interpreter

def main():
    interpreter.interpret(
        parser.parse(
            lexer.lex(
                "/home/lukas/workspace/python/telan/mandelbrot.tl"
            )
        ), []
    )
    
main()
