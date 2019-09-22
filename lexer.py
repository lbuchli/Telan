#!/usr/bin/env python3

import re

class Position:
    def __init__(self, line, char):
        self.line = line
        self.char = char

class Token:
    def __init__(self, ttype, value, position):
        self.ttype = ttype
        self.value = value
        self.position = position


TOKENS = [
    ("PAREN",  "\(|\)"),
    ("NUMBER", "[0-9]*(\.[0-9]+)?"),
    ("STRING", "\"[^\"]*\""),
    ("BOOL",   "(true)|(false)"),
    ("IDENT",  "[a-zA-Z][0-9_\-a-zA-Z]*"),
    ("WHITE",  "\s"),
    ("OTHER", ".")
]

def lex(filename):
    source = open(filename, "r")
    tokens = []
    linenbr = 1
    for line in source:
        # skip comments
        if line[0] == "#":
            continue
        
        # search through the line until the whole line is tokenized
        pivot = 0
        while pivot < len(line)-1:
            for token in TOKENS:
                found = re.search("\A("+token[1]+")", line[pivot:])
                first = found.group(0) if found else ""
                if len(first) > 0:
                    pivot += len(first)
                    if token[0] == "STRING":
                        first = first[1:-1] # remove "
                    tokens.append(Token(token[0], first, Position(linenbr, pivot)))
                    break
        
        linenbr += 1
                
    return tokens


