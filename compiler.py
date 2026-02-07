#!/usr/bin/python3
# Mohammad Zare 	    401106006
# Amir Mohammad Rashidi 401105967
from anytree import RenderTree, ContStyle
from scanner import Scanner
from parser import Parser
import logging

INPUT_FILE = "input.txt"
TOKENS_FILE = "tokens.txt"
PARSE_TREE_FILE = "parse_tree.txt"
SYNTAX_ERRORS_FILE = "syntax_errors.txt"


def write_parse_tree(root, filename: str):
    if root is None:
        return
    with open(filename, "w", encoding="utf-8") as file:
        for prefix, _, node in RenderTree(root, style=ContStyle()):
            file.write(f"{prefix}{node.name}\n")


def write_syntax_errors(errors, filename: str):
    with open(filename, "w", encoding="utf-8") as file:
        if not errors:
            file.write("No syntax errors found.\n")
        else:
            file.write("\n".join(errors))
            file.write("\n")


def main():
    scanner = Scanner(INPUT_FILE)
    parser = Parser(scanner)

    try:
        parser.parse()
    except Exception:
        #print("got EOF Error!")
        pass

    write_parse_tree(parser.root, PARSE_TREE_FILE)
    write_syntax_errors(parser.errors, SYNTAX_ERRORS_FILE)


if __name__ == "__main__":
    main()
