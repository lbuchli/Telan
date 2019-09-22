#!/usr/bin/env python

class ASTNode:
    def __init__(self, children, position):
        self.children = children
        self.position = position

def parse(tokens):
    node_stack = [ASTNode([], tokens[0].position)]
    for token in tokens:
        if token.ttype == "PAREN":
            if token.value ==  "(":
                node_stack.append(ASTNode([], token.position))
                node_stack[-2].children.append(node_stack[-1])
            else:
                node_stack.pop()
        else:
            node_stack[-1].children.append(token)

    if len(node_stack) > 1:
        return ASTNode(["ERROR"], node_stack[-1].position)

    return node_stack[0]
