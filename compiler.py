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
        self.tokens_per_line[self.lineno].append((ttype, lexeme , self.lineno))

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

    def __repr__(self, level=0):
        ret = "    " * level + repr(self.name) + "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret
    
    def print(self, f, prefix="", is_last=True):
        
        if prefix == "":
            f.write(self.name + "\n")
        else:
            f.write(prefix + ("└── " if is_last else "├── ") + self.name + "\n")

        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            last = i == len(self.children) - 1
            child.print(f, child_prefix, last)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

        # ================= Follow sets =================
        self.follow = {
            "Program": {"$"},
            "Declaration-list": {"$", "}"},
            "Declaration": {"int", "void", "}", "$"},
            "Declaration-initial": {";", "(", "["},
            "Declaration-prime": {";", "{"},
            "Fun-declaration-prime": {";", "{"},
            "Var-declaration-prime": {";", "{"},
            "Params": {")"},
            "Param-list": {")"},
            "Param": {")"},
            "Param-prime": {",", ")"},
            "Compound-stmt": {"}", "$"},
            "Statement-list": {"}"},
            "Statement": {"}", "else"},
            "Expression-stmt": {";", "}"},
            "Expression": {";", ")", "]", ","},
            "Return-stmt-prime": {";"},
            "B": {";", "]"},
            "H": {";", "]"},
            "C": {";", ")", "]"},
            "D": {";", ")", "]"},
            "G": {";", ")", "]"},
            "Var-call-prime": {";", ")", "]"},
            "Var-prime": {";", ")", "]"},
            "Factor-prime": {"*", "/", "+", "-", ";", ")", "]"},
            "Args": {")"},
            "Arg-list-prime": {")"},
        }

    # =================== Utilities ===================
    def lookahead(self):
        if self.pos >= len(self.tokens):
            return ("$", "$", self.tokens[-1][2] if self.tokens else 0)
        return self.tokens[self.pos]

    def advance(self):
        if self.pos < len(self.tokens):
            self.pos += 1

    def panic(self, follow_set):
        while self.lookahead()[1] not in follow_set and self.lookahead()[0] != "$":
            self.advance()

    def match(self, expected, follow_set=None):
        tok = self.lookahead()
        if tok[1] == expected:
            node = Node(f"({tok[0]}, {tok[1]})")
            self.advance()
            return node
        self.errors.append(f"#{tok[2]} : syntax error, missing {expected}")
        if follow_set is None:
            follow_set = {expected}
        self.panic(follow_set)
        if self.lookahead()[1] == expected:
            self.advance()
        return Node(f"(SYMBOL, {expected})")

    def match_type(self, expected_type, follow_set=None):
        tok = self.lookahead()
        if tok[0] == expected_type:
            node = Node(f"({tok[0]}, {tok[1]})")
            self.advance()
            return node
        self.errors.append(f"#{tok[2]} : syntax error, missing {expected_type}")
        if follow_set is None:
            follow_set = {expected_type}
        self.panic(follow_set)
        if self.lookahead()[0] == expected_type:
            self.advance()
        return Node(f"({expected_type}, )")

    def epsilon(self):
        return Node("epsilon")

    # =================== Grammar ===================
    def Program(self):
        node = Node("Program")
        node.add(self.Declaration_list())

        tok = self.lookahead()
        if tok[0] == "$":
            # reached proper EOF
            node.add(Node("$"))
        else:
            # some leftover token that is not expected at the top-level
            self.errors.append(f"#{tok[2]} : syntax error, illegal {tok[1]}")
            # optionally skip until EOF
            while self.lookahead()[0] != "$":
                self.advance()
            node.add(Node("$"))

        return node

    def Declaration_list(self):
        node = Node("Declaration-list")
        la_type, la_val, _ = self.lookahead()  # lookahead token
        # If the lookahead indicates the start of a declaration
        if la_val in {"int", "void"}:
            # Add the first declaration
            node.add(self.Declaration())
            # Recursively process the rest of the declaration list
            node.add(self.Declaration_list())
        else:
            # Empty production
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
        la_type, la_val, la_line = self.lookahead()
        if la_type == "ID":
            node.add(Node(f"(ID, {la_val})"))
            self.advance()
        else:
            self.errors.append(f"#{la_line} : syntax error, missing ID")
            self.panic(self.follow["Declaration-initial"])
            node.add(Node("(ID, )"))
        return node

    def Declaration_prime(self):
        node = Node("Declaration-prime")
        la = self.lookahead()[1]
        if la == "(":
            node.add(self.Fun_declaration_prime())
        elif la in {";", "["}:
            node.add(self.Var_declaration_prime())
        else:
            # This is an error - missing semicolon or other issue
            # But we should NOT skip to the next function
            # Just log error and try to continue in current context
            line = self.lookahead()[2]
            self.errors.append(f"#{line} : syntax error, missing Declaration-prime")
            
            # Check what comes next - if it's something that could be a statement,
            # then this was probably a missing semicolon
            next_la = self.lookahead()[1]
            if next_la in {"return", "if", "for", "{", "break", ";"} or \
            self.lookahead()[0] in {"ID", "NUM"} or \
            next_la in {"(", "+", "-"}:
                # This looks like the start of a statement, so just add epsilon
                # and let the statement list handle it
                node.add(self.epsilon())
            else:
                # Something else - might be end of function or next declaration
                # Don't panic, just add epsilon
                node.add(self.epsilon())
        return node

    def Var_declaration_prime(self):
        node = Node("Var-declaration-prime")
        la = self.lookahead()[1]
        if la == "[":
            node.add(self.match("["))
            node.add(self.match_type("NUM"))
            node.add(self.match("]"))
            # Check for missing semicolon after array declaration
            if self.lookahead()[1] == ";":
                node.add(self.match(";"))
            else:
                line = self.lookahead()[2]
                self.errors.append(f"#{line} : syntax error, missing ;")
                # Don't panic, just continue
        elif la == ";":
            node.add(self.match(";"))
        else:
            # Missing semicolon for simple variable declaration
            line = self.lookahead()[2]
            self.errors.append(f"#{line} : syntax error, missing ;")
            # Don't add the semicolon node, just continue
        return node
    def Fun_declaration_prime(self):
        node = Node("Fun-declaration-prime")
        node.add(self.match("("))
        
        # Parse params
        params_node = self.Params()
        node.add(params_node)
        
        # After params, check if we should continue
        # If params had an error, don't try to parse the rest
        la = self.lookahead()[1]
        if la == ")":
            node.add(self.match(")"))
            node.add(self.Compound_stmt())
        else:
            # Log error for missing )
            line = self.lookahead()[2]
            self.errors.append(f"#{line} : syntax error, missing )")
            # Don't try to parse Compound_stmt
        
        return node

    def Type_specifier(self):
        la_type, la_val, la_line = self.lookahead()
        node = Node("Type-specifier")
        if la_val in {"int", "void"}:
            node.add(Node(f"(KEYWORD, {la_val})"))
            self.advance()
        else:
            self.errors.append(f"#{la_line} : syntax error, missing type specifier")
            self.panic(self.follow["Declaration-initial"])
            node.add(Node("(KEYWORD, )"))
        return node

    # =================== Params ===================
    def Params(self):
        node = Node("Params")
        la_type, la_val, la_line = self.lookahead()
        if la_val == "void":
            node.add(self.match("void"))
        elif la_val == "int":
            node.add(self.match("int"))
            la_type, la_val, la_line = self.lookahead()
            if la_type == "ID":
                node.add(Node(f"(ID, {la_val})"))
                self.advance()
                node.add(self.Param_prime())
                node.add(self.Param_list())
            else:
                # CRITICAL: On error, return immediately without parsing more
                self.errors.append(f"#{la_line} : syntax error, missing ID")
                # Don't add any more children, just return
                # Don't call panic, don't add epsilon nodes
                return node
        else:
            self.errors.append(f"#{la_line} : syntax error, illegal {la_val}")
            # Don't panic, just return the node as is
        return node

    def Param_list(self):
        node = Node("Param-list")
        if self.lookahead()[1] == ",":
            node.add(self.match(","))
            node.add(self.Param())
            node.add(self.Param_list())
        else:
            node.add(self.epsilon())
        return node

    def Param(self):
        node = Node("Param")
        node.add(self.Declaration_initial())
        node.add(self.Param_prime())
        return node

    def Param_prime(self):
        node = Node("Param-prime")
        if self.lookahead()[1] == "[":
            node.add(self.match("["))
            node.add(self.match("]"))
        else:
            node.add(self.epsilon())
        return node

    # =================== Compound Statement ===================
    def Compound_stmt(self):
        node = Node("Compound-stmt")
        node.add(self.match("{"))
        node.add(self.Declaration_list())
        node.add(self.Statement_list())
        # Check for missing closing brace
        if self.lookahead()[1] == "}":
            node.add(self.match("}"))
        else:
            line = self.lookahead()[2]
            self.errors.append(f"#{line} : syntax error, missing }}")
            # Don't add the closing brace node
        return node

    def Statement_list(self):
        node = Node("Statement-list")
        la = self.lookahead()[1]
        if la == "}":
            node.add(self.epsilon())
        elif la == "$":
            # Unexpected EOF
            self.errors.append(f"#{self.lookahead()[2]} : syntax error, Unexpected EOF")
            node.add(self.epsilon())
        else:
            try:
                node.add(self.Statement())
                node.add(self.Statement_list())
            except Exception as e:
                # If Statement fails, add epsilon and continue
                self.errors.append(f"#{self.lookahead()[2]} : syntax error in statement")
                node.add(self.epsilon())
        return node

    def Statement(self):
        node = Node("Statement")
        tok = self.lookahead()
        la_val = tok[1]
        la_type = tok[0]

        if la_val == "{":
            node.add(self.Compound_stmt())
        elif la_val == "if":
            node.add(self.Selection_stmt())
        elif la_val == "for":
            node.add(self.Iteration_stmt())
        elif la_val == "return":
            node.add(self.Return_stmt())
        elif la_val == "break":
            node.add(self.Expression_stmt())
        elif la_val == ";" or la_type in {"ID", "NUM"} or la_val in {"(", "+", "-"}:
            node.add(self.Expression_stmt())
        elif la_val in {"int", "void"}:  
            # This could be a declaration in statement position
            # Check if it's a function declaration (has '(' after ID)
            # Save current position
            current_pos = self.pos
            
            # Skip type
            self.advance()
            
            # Check if next is ID
            if self.lookahead()[0] == "ID":
                self.advance()  # Skip ID
                
                # Check if next is '('
                if self.lookahead()[1] == "(":
                    # This is a function declaration in statement position - major error
                    # Restore position and log error
                    self.pos = current_pos
                    self.errors.append(f"#{tok[2]} : syntax error, illegal {la_val}")
                    # Skip until we find something that looks like a statement start
                    # or end of block
                    while self.lookahead()[1] not in {"}", "int", "void", "if", "for", "return", "{", ";", "$"}:
                        self.advance()
                    node.add(self.epsilon())
                else:
                    # This is a variable declaration like "int x;"
                    self.pos = current_pos
                    self.errors.append(f"#{tok[2]} : syntax error, illegal {la_val}")
                    self.advance()  # Skip the type keyword
                    node.add(self.Expression_stmt())  # Parse the remaining as expression-stmt
            else:
                self.pos = current_pos
                self.errors.append(f"#{tok[2]} : syntax error, illegal {la_val}")
                self.panic({";", "}", "else", "$"})
                node.add(self.epsilon())
        else:
            self.errors.append(f"#{tok[2]} : syntax error, illegal {la_val}")
            self.panic({";", "}", "else", "$"})
            if self.lookahead()[1] == ";":
                node.add(self.match(";"))
            else:
                node.add(self.epsilon())
        return node

    # =================== Statements ===================
    def Expression_stmt(self):
        node = Node("Expression-stmt")
        la_type, la_val, la_line = self.lookahead()
        if la_val == ";":
            node.add(self.match(";"))
        elif la_type in {"ID", "NUM"} or la_val in {"(", "+", "-"}:
            node.add(self.Expression())
            # Check for missing semicolon
            if self.lookahead()[1] == ";":
                node.add(self.match(";"))
            else:
                self.errors.append(f"#{self.lookahead()[2]} : syntax error, missing ;")
                # Don't panic, just continue
        elif la_val == "break":
            node.add(self.match("break"))
            # Check for missing semicolon
            if self.lookahead()[1] == ";":
                node.add(self.match(";"))
            else:
                self.errors.append(f"#{self.lookahead()[2]} : syntax error, missing ;")
                # Don't panic, just continue
        else:
            self.errors.append(f"#{la_line} : syntax error, illegal {la_val}")
            self.panic({";", "}", "$"})
            if self.lookahead()[1] == ";":
                node.add(self.match(";"))
            else:
                node.add(self.epsilon())
        return node

    def Selection_stmt(self):
        node = Node("Selection-stmt")
        node.add(self.match("if"))
        node.add(self.match("("))
        node.add(self.Expression())
        # Check for missing closing paren
        if self.lookahead()[1] == ")":
            node.add(self.match(")"))
        else:
            line = self.lookahead()[2]
            self.errors.append(f"#{line} : syntax error, missing )")
        node.add(self.Statement())
        node.add(self.Else_stmt())
        return node

    def Else_stmt(self):
        node = Node("Else-stmt")
        if self.lookahead()[1] == "else":
            node.add(self.match("else"))
            node.add(self.Statement())
        else:
            node.add(self.epsilon())
        return node

    def Iteration_stmt(self):
        node = Node("Iteration-stmt")
        node.add(self.match("for"))
        node.add(self.match("("))
        node.add(self.Expression())
        node.add(self.match(";"))
        node.add(self.Expression())
        node.add(self.match(";"))
        node.add(self.Expression())
        node.add(self.match(")"))
        node.add(self.Compound_stmt())
        return node

    def Return_stmt(self):
        node = Node("Return-stmt")
        node.add(self.match("return"))
        node.add(self.Return_stmt_prime())
        return node

    def Return_stmt_prime(self):
        node = Node("Return-stmt-prime")
        if self.lookahead()[1] == ";":
            node.add(self.match(";"))
        else:
            # Could have expression without semicolon
            node.add(self.Expression())
            # Check for missing semicolon
            if self.lookahead()[1] == ";":
                node.add(self.match(";"))
            else:
                self.errors.append(f"#{self.lookahead()[2]} : syntax error, missing ;")
                # Don't panic, just continue
        return node

    # =================== Expression ===================
    def Expression(self):
        node = Node("Expression")
        la_type, la_val, la_line = self.lookahead()
        if la_type == "ID":
            node.add(Node(f"(ID, {la_val})"))
            self.advance()
            node.add(self.B())
        elif la_type == "NUM" or la_val in {"(", "+", "-"}:
            node.add(self.Simple_expression_zegond())
        else:
            self.errors.append(f"#{la_line} : syntax error, illegal Expression")
            self.panic({";", ")", "]", ",", "}", "$"})
            node.add(self.epsilon())
        return node

    # =================== B, H, Simple-expression ===================
    def B(self):
        node = Node("B")
        la = self.lookahead()[1]
        if la == "=":
            node.add(self.match("="))
            node.add(self.Expression())
        elif la == "[":
            node.add(self.match("["))
            node.add(self.Expression())
            node.add(self.match("]"))
            node.add(self.H())
        else:
            node.add(self.Simple_expression_prime())
        return node

    def H(self):
        node = Node("H")
        la = self.lookahead()[1]
        if la == "=":
            node.add(self.match("="))
            node.add(self.Expression())
        else:
            node.add(self.G())
            node.add(self.D())
            node.add(self.C())
        return node

    def Simple_expression_zegond(self):
        node = Node("Simple-expression-zegond")
        node.add(self.Additive_expression_zegond())
        node.add(self.C())
        return node

    def Simple_expression_prime(self):
        node = Node("Simple-expression-prime")
        node.add(self.Additive_expression_prime())
        node.add(self.C())
        return node

    # =================== C, Relop, Additive ===================
    def C(self):
        node = Node("C")
        la = self.lookahead()[1]
        if la in {"<", "=="}:
            node.add(self.Relop())
            node.add(self.Additive_expression())
        else:
            node.add(self.epsilon())
        return node

    def Relop(self):
        node = Node("Relop")
        la = self.lookahead()[1]
        if la in {"==", "<"}:
            node.add(self.match(la))
        else:
            self.errors.append(f"#{self.lookahead()[2]} : syntax error, missing relop")
            node.add(self.epsilon())
        return node

    def Additive_expression(self):
        node = Node("Additive-expression")
        node.add(self.Term())
        node.add(self.D())
        return node

    def Additive_expression_prime(self):
        node = Node("Additive-expression-prime")
        node.add(self.Term_prime())
        node.add(self.D())
        return node

    def Additive_expression_zegond(self):
        node = Node("Additive-expression-zegond")
        node.add(self.Term_zegond())
        node.add(self.D())
        return node

    def D(self):
        node = Node("D")
        la = self.lookahead()[1]
        if la in {"+", "-"}:
            node.add(self.Addop())
            node.add(self.Term())
            node.add(self.D())
        else:
            node.add(self.epsilon())
        return node

    def Addop(self):
        node = Node("Addop")
        la = self.lookahead()[1]
        if la in {"+", "-"}:
            node.add(self.match(la))
        else:
            self.errors.append(f"#{self.lookahead()[2]} : syntax error, missing addop")
            node.add(self.epsilon())
        return node

    # =================== Term / Factor ===================
    def Term(self):
        node = Node("Term")
        node.add(self.Signed_factor())
        node.add(self.G())
        return node

    def Term_prime(self):
        node = Node("Term-prime")
        node.add(self.Factor_prime())
        node.add(self.G())
        return node

    def Term_zegond(self):
        node = Node("Term-zegond")
        node.add(self.Signed_factor_zegond())
        node.add(self.G())
        return node

    def G(self):
        node = Node("G")
        la = self.lookahead()[1]
        if la in {"*", "/"}:
            node.add(self.match(la))
            node.add(self.Signed_factor())
            node.add(self.G())
        else:
            node.add(self.epsilon())
        return node

    def Signed_factor(self):
        node = Node("Signed-factor")
        la = self.lookahead()[1]
        if la in {"+", "-"}:
            node.add(self.match(la))
            node.add(self.Factor())
        else:
            node.add(self.Factor())
        return node

    def Signed_factor_zegond(self):
        node = Node("Signed-factor-zegond")
        la = self.lookahead()[1]
        if la in {"+", "-"}:
            node.add(self.match(la))
            node.add(self.Factor_zegond())
        else:
            node.add(self.Factor_zegond())
        return node

    def Factor(self):
        node = Node("Factor")
        la_type, la_val, la_line = self.lookahead()
        if la_val == "(":
            node.add(self.match("("))
            node.add(self.Expression())
            node.add(self.match(")"))
        elif la_type == "ID":
            node.add(Node(f"(ID, {la_val})"))
            self.advance()
            node.add(self.Var_call_prime())
        elif la_type == "NUM":
            node.add(Node(f"(NUM, {la_val})"))
            self.advance()
        else:
            self.errors.append(f"#{la_line} : syntax error, illegal Factor")
            self.panic({"+", "-", "*", "/", ";", ")", "]", "$"})
            node.add(self.epsilon())
        return node

    def Factor_zegond(self):
        node = Node("Factor-zegond")
        la_type, la_val, la_line = self.lookahead()
        if la_type == "NUM":
            node.add(Node(f"(NUM, {la_val})"))
            self.advance()
        elif la_val == "(":
            node.add(self.match("("))
            node.add(self.Expression())
            node.add(self.match(")"))
        else:
            self.errors.append(f"#{la_line} : syntax error, illegal Factor-zegond")
            self.panic({"+", "-", "*", "/", ";", ")", "]", "$"})
            node.add(self.epsilon())
        return node

    # =================== Var / Args ===================
    def Var_call_prime(self):
        node = Node("Var-call-prime")
        la = self.lookahead()[1]
        if la == "(":
            node.add(self.match("("))
            node.add(self.Args())
            node.add(self.match(")"))
        else:
            node.add(self.Var_prime())
        return node

    def Var_prime(self):
        node = Node("Var-prime")
        la = self.lookahead()[1]
        if la == "[":
            node.add(self.match("["))
            node.add(self.Expression())
            node.add(self.match("]"))
        else:
            node.add(self.epsilon())
        return node

    def Factor_prime(self):
        node = Node("Factor-prime")
        if self.lookahead()[1] == "(":
            node.add(self.match("("))
            node.add(self.Args())
            node.add(self.match(")"))
        else:
            node.add(self.epsilon())
        return node

    def Args(self):
        node = Node("Args")
        if self.lookahead()[1] == ")":
            node.add(self.epsilon())
        else:
            node.add(self.Arg_list())
        return node

    def Arg_list(self):
        node = Node("Arg-list")
        node.add(self.Expression())
        node.add(self.Arg_list_prime())
        return node

    def Arg_list_prime(self):
        node = Node("Arg-list-prime")
        if self.lookahead()[1] == ",":
            node.add(self.match(","))
            node.add(self.Expression())
            node.add(self.Arg_list_prime())
        else:
            node.add(self.epsilon())
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

    tokens = []
    for ln in sorted(scanner.tokens_per_line):
        tokens.extend(scanner.tokens_per_line[ln])

    tokens.append(("$", "$" , scanner.lineno))

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