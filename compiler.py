#!/usr/bin/python3
import sys
from collections import deque
KEYWORDS = ["break", "else", "if", "for", "int", "return", "void"]

SYMBOLS = set([';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '<', '=', ])
WHITESPACE_CHARS = set([' ', '\t', '\r', '\v', '\f', '\n'])



class Scanner:
    def __init__(self):
        self.text = ""
        self.pos = 0
        self.length = 0
        self.lineno = 1
        self.tokens_per_line = {}
        self.errors = []
        self.symbol_table = sorted(KEYWORDS.copy())
        self.symbol_table_set = set(self.symbol_table)

    # ------------------ Basic Helpers ------------------

    def peek(self, offset=0):
        index = self.pos + offset
        return None if index >= self.length else self.text[index]

    def advance(self):
        if self.pos >= self.length:
            return None
        ch = self.text[self.pos]
        self.pos += 1
        if ch == '\n':
            self.lineno += 1
        return ch

    def record_token(self, ttype, lexeme):
        if self.lineno not in self.tokens_per_line:
            self.tokens_per_line[self.lineno] = []
        self.tokens_per_line[self.lineno].append((ttype, lexeme))

        if ttype in ("ID", "KEYWORD") and lexeme not in self.symbol_table_set:
            self.symbol_table.append(lexeme)
            self.symbol_table_set.add(lexeme)

    def record_error(self, lexeme, message, line=None):
        line = self.lineno if line is None else line
        self.errors.append((line, lexeme, message))

    def is_symbol(self, ch):
        return ch in SYMBOLS

    def is_whitespace(self, ch):
        return ch in WHITESPACE_CHARS

    def skip_whitespace(self):
        while True:
            c = self.peek()
            if c is None or c not in WHITESPACE_CHARS:
                return
            self.advance()

    # ---------------------------------------------------
    # Comments
    # ---------------------------------------------------

    def consume_line_comment(self):
        while True:
            ch = self.peek()
            if ch is None or ch == '\n':
                return "COMMENT"
            self.advance()

    def consume_block_comment(self, start_line):
        content = ""
        while True:
            ch = self.peek()
            if ch is None:
                short = content[:7] + "..." if len(content) > 7 else content
                self.record_error("/* " + short, "Open comment at EOF", start_line)
                return "ERROR"
            if ch == '*' and self.peek(1) == '/':
                self.advance()
                self.advance()
                return "COMMENT"
            content += self.advance()

    def read_slash_sequence(self):
        start_line = self.lineno
        self.advance()
        nxt = self.peek()

        if nxt == '/':
            self.advance()
            return self.consume_line_comment()

        if nxt == '*':
            self.advance()
            return self.consume_block_comment(start_line)

        return ("SYMBOL", "/")

    def detect_stray_closing_comment(self):
        if self.peek() == '*' and self.peek(1) == '/':
            ln = self.lineno
            lex = self.advance() + (self.advance() or "")
            self.record_error(lex, "Stray closing comment", ln)
            return "ERROR"
        return None

    # ---------------------------------------------------
    # Identifiers
    # ---------------------------------------------------

    def read_identifier_head(self):
        c = self.peek()
        if c is None or not (c.isalpha() or c == '_'):
            return None
        lex = ""
        while True:
            c = self.peek()
            if c is None or not (c.isalnum() or c == '_'):
                break
            lex += self.advance()
        return lex

    def read_illegal_continuation(self):
        chunk = ""
        while True:
            ch = self.peek()
            if ch is None or ch.isspace() or self.is_symbol(ch):
                break
            chunk += self.advance()
        return chunk

    def scan_identifier(self):
        start_line = self.lineno
        lex = self.read_identifier_head()
        if lex is None:
            return None

        nxt = self.peek()
        if nxt is not None and not self.is_whitespace(nxt) and not self.is_symbol(nxt):
            illegal = self.read_illegal_continuation()
            self.record_error(lex + illegal, "Illegal character", start_line)
            return "ERROR"

        if lex in KEYWORDS:
            return ("KEYWORD", lex)

        return ("ID", lex)

    # ---------------------------------------------------
    # Numbers
    # ---------------------------------------------------

    def consume_number_head(self):
        lex = ""
        while True:
            ch = self.peek()
            if ch is None or not ch.isdigit():
                break
            lex += self.advance()
        return lex

    def read_number(self):
        c = self.peek()
        if c is None or not c.isdigit():
            return None

        start_line = self.lineno
        lex = self.consume_number_head()

        if self.peek() is not None and (self.peek().isalpha() or self.peek() == '_'):
            while True:
                ch = self.peek()
                if ch is None or not (ch.isalnum() or ch == '_'):
                    break
                lex += self.advance()
            self.record_error(lex, "Malformed number", start_line)
            return "ERROR"

        if len(lex) > 1 and lex[0] == '0':
            self.record_error(lex, "Malformed number", start_line)
            return "ERROR"

        return ("NUM", lex)

    # ---------------------------------------------------
    # Symbols / Illegal
    # ---------------------------------------------------

    def read_symbol(self):
        c = self.peek()
        if c is None:
            return None

        if c == '=':
            self.advance()
            if self.peek() == '=':
                self.advance()
                return ("SYMBOL", "==")
            return ("SYMBOL", "=")

        if c in SYMBOLS:
            return ("SYMBOL", self.advance())

        return None

    def read_illegal(self):
        ch = self.advance()
        if ch is not None:
            self.record_error(ch, "Illegal character")
        return "ERROR"

    # ---------------------------------------------------
    # Main Tokenizer
    # ---------------------------------------------------

    def next_token(self):
        self.skip_whitespace()
        if self.peek() is None:
            return None

        c = self.peek()
        if c == '/':
            res = self.read_slash_sequence()
            if res == "COMMENT":
                return "COMMENT"
            if res == "ERROR":
                return "ERROR"
            if isinstance(res, tuple):
                return res

        stray = self.detect_stray_closing_comment()
        if stray == "ERROR":
            return "ERROR"

        ident = self.scan_identifier()
        if ident is not None:
            return ident

        num = self.read_number()
        if num is not None:
            return num

        sym = self.read_symbol()
        if sym is not None:
            #self.advance()
            return sym

        return self.read_illegal()

    # ---------------------------------------------------
    # Scan Loop
    # ---------------------------------------------------

    def scan(self):
        while True:
            tok = self.next_token()
            if tok is None:
                return
            if tok in ("COMMENT", "ERROR"):
                continue
            ttype, lex = tok
            self.record_token(ttype, lex)

    # ---------------------------------------------------
    # Output
    # ---------------------------------------------------

    def write_tokens(self):
        with open("tokens.txt", "w", encoding="utf-8") as f:
            for ln in sorted(self.tokens_per_line.keys()):
                f.write(f"{ln}. ")
                for ttype, lex in self.tokens_per_line[ln]:
                    f.write(f"({ttype}, {lex}) ")
                f.write("\n")

    def write_errors(self):
        with open("lexical_errors.txt", "w", encoding="utf-8") as f:
            if not self.errors:
                f.write("No lexical errors found.")
                return
            for line, lex, msg in self.errors:
                f.write(f"{line}. ({lex}, {msg})\n")

    def write_symbol_table(self):
        with open("symbol_table.txt", "w", encoding="utf-8") as f:
            for i, sym in enumerate(self.symbol_table, start=1):
                f.write(f"{i}. {sym}\n")

    def write_outputs(self):
        self.write_tokens()
        self.write_errors()
        self.write_symbol_table()



class Node:
    def __init__(self, name):
        self.name = name
        self.children = []

    def add(self, child):
        self.children.append(child)

    def print(self, f, prefix="", is_last=True):
        if prefix == "":
            f.write(self.name + "\n")
        else:
            f.write(prefix + ("└── " if is_last else "├── ") + self.name + "\n")

        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, c in enumerate(self.children):
            c.print(f, new_prefix, i == len(self.children) - 1)


# =========================================================
# ======================== PARSER =========================
# =========================================================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    def lookahead(self):
        return self.tokens[self.pos]

    def advance(self):
        self.pos += 1

    def match(self, expected):
        tok = self.lookahead()
        if tok[1] == expected:
            node = Node(f"({tok[0]}, {tok[1]})")
            self.advance()
            return node
        else:
            self.errors.append(f"syntax error, missing {expected}")
            return Node(f"(SYMBOL, {expected})")

    def epsilon(self):
        return Node("epsilon")

    # ================= Grammar =================

    def Program(self):
        node = Node("Program")
        node.add(self.Declaration_list())
        node.add(Node("$"))
        return node

    def Declaration_list(self):
        node = Node("Declaration-list")
        if self.lookahead()[1] in {"int", "void"}:
            node.add(self.Declaration())
            node.add(self.Declaration_list())
        else:
            node.add(self.epsilon())
        return node

    def Declaration(self):
        node = Node("Declaration")
        node.add(self.Declaration_initial())
        node.add(self.Declaration_prime())
        return node

    def Declaration_initial(self):
        node = Node("Declaration-initial")
        node.add(self.Type_specifier())
        tok = self.lookahead()
        node.add(Node(f"(ID, {tok[1]})"))
        self.advance()
        return node

    def Declaration_prime(self):
        node = Node("Declaration-prime")
        if self.lookahead()[1] == "(":
            node.add(self.Fun_declaration_prime())
        else:
            node.add(self.Var_declaration_prime())
        return node

    def Var_declaration_prime(self):
        node = Node("Var-declaration-prime")
        node.add(self.match(";"))
        return node

    def Fun_declaration_prime(self):
        node = Node("Fun-declaration-prime")
        node.add(self.match("("))
        node.add(self.Params())
        node.add(self.match(")"))
        node.add(self.Compound_stmt())
        return node

    def Type_specifier(self):
        tok = self.lookahead()
        node = Node("Type-specifier")
        node.add(Node(f"(KEYWORD, {tok[1]})"))
        self.advance()
        return node

    def Params(self):
        node = Node("Params")
        if self.lookahead()[1] == "void":
            node.add(Node("(KEYWORD, void)"))
            self.advance()
        return node

    def Compound_stmt(self):
        node = Node("Compound-stmt")
        node.add(self.match("{"))
        node.add(self.Declaration_list())
        node.add(self.Statement_list())  
        node.add(self.match("}"))
        return node
    
    def Statement_list(self):
        node = Node("Statement-list")
        if self.lookahead()[0] in {"ID", "NUM"} or self.lookahead()[1] in {"(", ";"}:
            node.add(self.Statement())
            node.add(self.Statement_list())
        else:
            node.add(self.epsilon())
        return node


    def Statement(self):
        node = Node("Statement")
        node.add(self.Expression_stmt())
        return node


    def Expression_stmt(self):
        node = Node("Expression-stmt")
        if self.lookahead()[1] == ";":
            node.add(self.match(";"))
        else:
            node.add(self.Expression())
            node.add(self.match(";"))
        return node

    def Expression(self):
        node = Node("Expression")

        if self.lookahead()[0] == "ID":
            node.add(self.match("ID"))
            node.add(self.B())
        else:
            node.add(self.Simple_expression_zegond())

        return node




# =========================================================
# ========================== MAIN =========================
# =========================================================

def main():
    scanner = Scanner()

    with open("input.txt", "r", encoding="utf-8") as f:
        scanner.text = f.read()
        scanner.length = len(scanner.text)

    scanner.scan()

    # ---- FLATTEN TOKENS (CRITICAL FIX) ----
    tokens = []
    for ln in sorted(scanner.tokens_per_line):
        tokens.extend(scanner.tokens_per_line[ln])

    tokens.append(("$", "$"))

    parser = Parser(tokens)
    tree = parser.Program()

    with open("parse_tree.txt", "w", encoding="utf-8") as f:
        tree.print(f)

    with open("syntax_errors.txt", "w", encoding="utf-8") as f:
        if parser.errors:
            for e in parser.errors:
                f.write(e + "\n")
        else:
            f.write("No syntax errors found.")


if __name__ == "__main__":
    main()