#!/usr/bin/env python3

import lexer
import parser


###############################################################################
#                            Command Representation                           #
###############################################################################

def print_err(position, message):
    print("Line " + str(position.line) +
          " Chr " + str(position.char) +
          ": " + message)

class Command:
    def __init__(self, action, minargs=0, maxargs=0, types=[]):
        self.minargs = minargs # the min number of arguments (e.g. 1)
        self.maxargs = maxargs # the max number of arguments (e.g. 2)
        self.types = types     # the types of arguments (e.g. ["NUMBER", "ANY", "AST"])
        self.action = action   # what to do when the command is called (gets passed the arguments)
    
    # call the command if arguments match the commands constraints
    def call(self, arguments):
        # check argument count
        if len(arguments) < self.minargs:
            return self._err(arguments[-1], "Expected at least " + str(self.minargs) + " arguments")
        if self.maxargs != -1 and len(arguments) > self.maxargs:
            return self._err(arguments[self.maxargs], "Expected at most " + str(self.maxargs) + "arguments")
        
        # check argument type
        arg_index = 0
        for t in self.types:
            if not self._checktype(arguments[arg_index], t):
                return self._err(arguments[arg_index], "Expected argument of type " + t)
            arg_index += 1
        for arg in arguments[arg_index:]:
            if not self._checktype(arg, self.types[-1]):
                return self._err(arguments[arg_index], "Expected argument of type " + self.types[-1])
        
        # all tests passed, let's call the command
        return self.action(arguments)
        
    # prints an error to the screen and returns an error token
    def _err(self, token, message):
        print_err(token.position, message)
        return lexer.Token("OTHER", "ERROR", token.position)
    
    # checks the type of an argument.
    # Available types: "ANY", "AST", "ANY/AST", or any of the lexer types
    def _checktype(self, arg, atype):
        if atype == "ANY/AST":
            return True
        elif isinstance(arg, lexer.Token):
            return atype == "ANY" or atype == arg.ttype
        elif isinstance(arg, parser.ASTNode):
            return atype == "AST"
        return False


###############################################################################
#                                 Interpreter                                 #
###############################################################################

variables = {}

def interpret(root):
    command = interpret(root.children[0]) if isinstance(root.children[0], parser.ASTNode) else root.children[0]
    arguments = []
    leave_next = False
    for x in root.children[1:]:
        if isinstance(x, lexer.Token):
            if x.ttype == "OTHER" and x.value == "'":
                leave_next = True
            elif x.ttype != "WHITE": # ignore whitespace
                arguments.append(x)
                leave_next = False
        elif isinstance(x, parser.ASTNode):
            if leave_next:
                arguments.append(x)
            else:
                arguments.append(interpret(x))
        else:
            print("PARSER: " + x)
            return null
    
    if command.value in COMMANDS:
        return COMMANDS[command.value].call(arguments)
    else:
        print_err(command.position, "Unknown command: " + command.value)
        return Token("OTHER", "ERROR", command.position)


###############################################################################
#                               Reusable Tokens                               #
###############################################################################
    
def true(pos):
    return lexer.Token("BOOL", "true", pos)

def false(pos):
    return lexer.Token("BOOL", "false", pos)


###############################################################################
#                                   Commands                                  #
###############################################################################
                
def add(args):
    result = 0.0
    for arg in args:
        result += float(arg.value)
    return lexer.Token("NUMBER", str(result), args[0].position)

def sub(args):
    result = float(args[0].value)
    for arg in args[1:]:
        result -= float(arg.value)
    return lexer.Token("NUMBER", str(result), args[0].position)

def mul(args):
    result = 1.0
    for arg in args:
        result *= float(arg.value)
    return lexer.Token("NUMBER", str(result), args[0].position)

def div(args):
    result = float(args[0].value)
    for arg in args[1:]:
        result /= float(arg.value)
    return lexer.Token("NUMBER", str(result), args[0].position)

def ifelse(args):
    if args[0].value == "true":
        return args[1]
    else:
        return args[2]

def last(args):
    return args[-1]

def eq(args):
    if args[0].ttype == args[1].ttype:
        if args[0].ttype == "NUMBER":
            if float(args[0].value) == float(args[1].value):
                return true(args[0].position)
            else:
                return false(args[0].position)
        else:
            if args[0].value == args[1].value:
                return true(args[0].position)
            else:
                return false(args[0].position)
    else:
        return false(args[0].position)

def gt(args):
    if float(args[0].value) > float(args[1].value):
        return true(args[0].position)
    else:
        return false(args[0].position)

def lt(args):
    if float(args[0].value) < float(args[1].value):
        return true(args[0].position)
    else:
        return false(args[0].position)

def lnot(args):
    return false(args[0].position) if args[0].value == "true" else true(args[0].position)

def land(args):
    for arg in args:
        if arg.value != "true":
            return false(arg.position)
    return true(args[0].position)

def lor(args):
    for arg in args:
        if arg.value == "true":
            return true(arg.position)
    return false(args[0].position)

def io_input(args):
    return lexer.Token(args[0].value, input(args[1].value if len(args) > 1 else ""), args[0].position)

def io_print(args):
    for arg in args:
        print(arg.value),

def v_set(args):
    variables[args[0].value] = args[1]

def v_load(args):
    if args[0].value in variables:
        return variables[args[0]].value
    else:
        return lexer.Token("OTHER", "NULL", args[0].position)

def c_while(args):
    while True:
        result = interpret(args[0])
        if result.ttype == "BOOL" and result.value != "true":
            break
        for arg in args[1:]:
            interpret(arg)

def c_exec(args):
    for arg in args[:-1]:
        interpret(arg)
    return interpret(args[-1])

def concat(args):
    result = ""
    for arg in args:
        result += arg.value
    return lexer.Token("STRING", result, args[0].position)


###############################################################################
#                              Command Dictionary                             #
###############################################################################

COMMANDS = {
    "+":      Command(add, 2, -1, ["NUMBER"]),
    "-":      Command(sub, 2, -1, ["NUMBER"]),
    "*":      Command(mul, 2, -1, ["NUMBER"]),
    "/":      Command(div, 2, -1, ["NUMBER"]),
    "ifelse": Command(ifelse, 3, 3, ["BOOL", "ANY/AST", "ANY/AST"]),
    "last":   Command(last, 1, -1, ["ANY/AST"]),
    "eq":     Command(eq, 2, 2, ["ANY"]),
    "gt":     Command(gt, 2, 2, ["NUMBER"]),
    "lt":     Command(lt, 2, 2, ["NUMBER"]),
    "not":    Command(lnot, 1, 1, ["BOOL"]),
    "and":    Command(land, 2, -1, ["BOOL"]),
    "or":     Command(lor, 2, -1, ["BOOL"]),
    "input":  Command(io_input, 1, 2, ["STRING"]),
    "print":  Command(io_print, 1, -1, ["ANY"]),
    "set":    Command(v_set, 2, 2, ["ANY", "ANY/AST"]),
    "load":   Command(v_load, 2, 2, ["ANY"]),
    "while":  Command(c_while, 2, -1, ["AST"]),
    "exec":   Command(c_exec, 1, -1, ["AST"]),
    "concat": Command(concat, 1, -1, ["ANY"])
}
