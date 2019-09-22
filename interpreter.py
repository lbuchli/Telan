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
    def call(self, arguments, local):
        # check argument count
        if len(arguments) < self.minargs:
            return self._err(arguments[-1], "Expected at least " + str(self.minargs) + " arguments")
        if self.maxargs != -1 and len(arguments) > self.maxargs:
            return self._err(arguments[self.maxargs], "Expected at most " + str(self.maxargs) + " arguments")
        
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
        result = self.action(arguments, local)
        return lexer.Token("OTHER", "NULL", arguments[0].position) if result == None else result
        
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

def interpret(root, local):
    command = interpret(root.children[0], local) if isinstance(root.children[0], parser.ASTNode) else root.children[0]
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
                arguments.append(interpret(x, local))
        else:
            print("PARSER: " + x)
            return null
    
    # predefined functions
    if command.value in COMMANDS:
        return COMMANDS[command.value].call(arguments, local)
    # userdefined functions
    elif command.value in variables and isinstance(variables[command.value], parser.ASTNode):
        func = variables[command.value].children
        minargs = int(func[0].value)
        maxargs = int(func[1].value)
        # filter out whitespace
        rawtypes = filter(lambda elem: elem.ttype != "WHITE", func[2].children)
        types = [token.value for token in rawtypes]
        def code(arguments, local):
            return interpret(func[3], arguments)
        return Command(code, minargs, maxargs, types).call(arguments, local)
    # no function
    else:
        print_err(command.position, "Unknown command: " + command.value)
        return lexer.Token("OTHER", "ERROR", command.position)


###############################################################################
#                               Reusable Tokens                               #
###############################################################################
    
def true(pos):
    return lexer.Token("BOOL", "true", pos)

def false(pos):
    return lexer.Token("BOOL", "false", pos)

def null(pos):
    return lexer.Token("OTHER", "NULL", pos)


###############################################################################
#                                   Commands                                  #
###############################################################################
                
def add(args, _):
    result = 0.0
    for arg in args:
        result += float(arg.value)
    return lexer.Token("NUMBER", str(result), args[0].position)

def sub(args, _):
    result = float(args[0].value)
    for arg in args[1:]:
        result -= float(arg.value)
    return lexer.Token("NUMBER", str(result), args[0].position)

def mul(args, _):
    result = 1.0
    for arg in args:
        result *= float(arg.value)
    return lexer.Token("NUMBER", str(result), args[0].position)

def div(args, _):
    result = float(args[0].value)
    for arg in args[1:]:
        result /= float(arg.value)
    return lexer.Token("NUMBER", str(result), args[0].position)

def ifelse(args, _):
    if args[0].value == "true":
        return args[1]
    else:
        return args[2]

def last(args, _):
    return args[-1]

def eq(args, _):
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

def gt(args, _):
    if float(args[0].value) > float(args[1].value):
        return true(args[0].position)
    else:
        return false(args[0].position)

def lt(args, _):
    if float(args[0].value) < float(args[1].value):
        return true(args[0].position)
    else:
        return false(args[0].position)

def lnot(args, _):
    return false(args[0].position) if args[0].value == "true" else true(args[0].position)

def land(args, _):
    for arg in args:
        if arg.value != "true":
            return false(arg.position)
    return true(args[0].position)

def lor(args, _):
    for arg in args:
        if arg.value == "true":
            return true(arg.position)
    return false(args[0].position)

def io_input(args, _):
    return lexer.Token(args[0].value, input(args[1].value if len(args) > 1 else ""), args[0].position)

def io_print(args, _):
    for arg in args:
        print(arg.value, end='')
    print()

def v_set(args, _):
    variables[args[0].value] = args[1]

def v_setf(args, _):
    variables[args[0].value] = parser.ASTNode(args[1:], args[0].position)

def v_load(args, _):
    if args[0].value in variables:
        return variables[args[0].value]

def v_get(args, local):
    index = int(args[0].value)
    if len(local) > index:
        return local[index]
    else:
        return null(args[0].position)

def c_while(args, local):
    while True:
        result = interpret(args[0], local)
        if result.ttype == "BOOL" and result.value != "true":
            break
        for arg in args[1:]:
            interpret(arg, local)

def c_exec(args, _):
    for arg in args[:-1]:
        interpret(arg)
    return interpret(args[-1])

def concat(args, _):
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
    "setf":   Command(v_setf, 5, 5, ["ANY", "NUMBER", "NUMBER", "AST", "AST"]),
    "get":    Command(v_get, 1, 1, ["NUMBER"]), 
    "load":   Command(v_load, 1, 1, ["ANY"]),
    "while":  Command(c_while, 2, -1, ["AST"]),
    "exec":   Command(c_exec, 1, -1, ["AST"]),
    "concat": Command(concat, 1, -1, ["ANY"])
}
