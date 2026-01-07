#!/usr/bin/python3
import sys
from collections import deque
KEYWORDS = ["break", "else", "if", "for", "int", "return", "void"]

SYMBOLS = set([';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '<', '=', '>'])
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




from dataclasses import dataclass

from typing import List, Tuple, Dict, Set, Optional



Token = Tuple[str, str, int]  




class Node:

    def __init__(self, name: str):

        self.name = name

        self.children: List["Node"] = []

        self.hidden = False

        self.abort = False

        self.matched = False



    def add(self, child: "Node"):

        self.children.append(child)



    def print(self, f, prefix="", is_last=True):
        if hasattr(self, "hidden") and self.hidden:
            return
        visible_children = []
        for c in self.children:
            if hasattr(c, "hidden") and c.hidden:
                continue
            # skip empty nonterminals
            if c.children == [] and c.name not in ("epsilon", "$") and not c.name.startswith("("):
                continue
            visible_children.append(c)

        if prefix == "":
            f.write(self.name + "\n")
        else:
            f.write(prefix + ("└── " if is_last else "├── ") + self.name + "\n")

        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(visible_children):
            child.print(f, child_prefix, i == len(visible_children) - 1)


EPS = "EPSILON"

END = "$"


EXPR_NTS = {

    "Expression","B","H","Simple-expression-zegond","Simple-expression-prime",

    "C","Relop",

    "Additive-expression","Additive-expression-prime","Additive-expression-zegond",

    "D","Addop",

    "Term","Term-prime","Term-zegond",

    "G","Signed-factor","Signed-factor-zegond",

    "Factor","Factor-zegond",

    "Var-call-prime","Var-prime","Factor-prime",

    "Args","Arg-list","Arg-list-prime",

}



SYNC_EXPR = {")", "]", ";", ",", "}"}

@dataclass(frozen=True)

class Sym:

    kind: str  

    name: str



def T(x): return Sym("T", x)

def N(x): return Sym("N", x)



class Parser:

    def __init__(self, tokens: List[Token]):

        self.tokens = tokens

        self.pos = 0

        self.errors: List[str] = []

        self.start_symbol = "Program"

        self.prods: Dict[str, List[List[Sym]]] = self._build_grammar()

        self.nonterminals = set(self.prods.keys())

        self.terminals = self._collect_terminals()

        self.first: Dict[str, Set[str]] = {nt: set() for nt in self.nonterminals}

        self.follow: Dict[str, Set[str]] = {nt: set() for nt in self.nonterminals}

        self.table: Dict[Tuple[str, str], List[Sym]] = {}

        self._compute_first()

        self._compute_follow()

        self._build_parse_table()

        self.sync_tokens: Dict[str, Set[str]] = {
            "Program": {"$"},
            "Declaration-list": {"$", "}"},
            "Declaration": {"int", "void", "$", "}"},
            "Declaration-initial": {";", "(", "["},
            "Declaration-prime": {"int", "void", "$", "}"},
            "Fun-declaration-prime": {"int", "void", "$", "}"},
            "Var-declaration-prime": {"int", "void", "$", "}"},
            "Type-specifier": {"ID"},
            "Params": {")"},
            "Param-list": {")"},
            "Param": {")", ","},
            "Param-prime": {")", ","},
            "Compound-stmt": {"}", "$", "else"},
            "Statement-list": {"}"},
            "Statement": {"}", "else", "int", "void", "if", "for", "return", "break", "ID", "NUM", "(", "+", "-", ";"},
            "Expression-stmt": {"}", "int", "void", "if", "for", "return", "break", "ID", "NUM", "(", "+", "-", ";"},
            "Selection-stmt": {"}", "int", "void", "if", "for", "return", "break", "ID", "NUM", "(", "+", "-", ";"},
            "Else-stmt": {"}", "int", "void", "if", "for", "return", "break", "ID", "NUM", "(", "+", "-", ";"},
            "Iteration-stmt": {"}", "int", "void", "if", "for", "return", "break", "ID", "NUM", "(", "+", "-", ";"},
            "Return-stmt": {"}", "int", "void", "if", "for", "return", "break", "ID", "NUM", "(", "+", "-", ";"},
            "Return-stmt-prime": {"}", "int", "void", "if", "for", "return", "break", "ID", "NUM", "(", "+", "-", ";"},
            "Expression": {";", ")", "]", ",", "}"},
            "B": {";", ")", "]", ",", "}"},
            "H": {";", ")", "]", ",", "}"},
            "Simple-expression-zegond": {";", ")", "]", ",", "}"},
            "Simple-expression-prime": {";", ")", "]", ",", "}"},
            "C": {";", ")", "]", ",", "}"},
            "Relop": {"ID", "NUM", "(", "+", "-"},
            "Additive-expression": {";", ")", "]", ",", "}", "<", "=="},
            "Additive-expression-prime": {";", ")", "]", ",", "}", "<", "=="},
            "Additive-expression-zegond": {";", ")", "]", ",", "}", "<", "=="},
            "D": {";", ")", "]", ",", "}", "<", "=="},
            "Addop": {"ID", "NUM", "(", "+", "-"},
            "Term": {";", ")", "]", ",", "}", "<", "==", "+", "-"},
            "Term-prime": {";", ")", "]", ",", "}", "<", "==", "+", "-"},
            "Term-zegond": {";", ")", "]", ",", "}", "<", "==", "+", "-"},
            "G": {";", ")", "]", ",", "}", "<", "==", "+", "-"},
            "Signed-factor": {";", ")", "]", ",", "}", "<", "==", "+", "-", "*", "/"},
            "Signed-factor-zegond": {";", ")", "]", ",", "}", "<", "==", "+", "-", "*", "/"},
            "Factor": {";", ")", "]", ",", "}", "<", "==", "+", "-", "*", "/"},
            "Factor-prime": {";", ")", "]", ",", "}", "<", "==", "+", "-", "*", "/"},
            "Factor-zegond": {";", ")", "]", ",", "}", "<", "==", "+", "-", "*", "/"},
            "Var-call-prime": {";", ")", "]", ",", "}", "<", "==", "+", "-", "*", "/"},
            "Var-prime": {";", ")", "]", ",", "}", "<", "==", "+", "-", "*", "/"},
            "Args": {")"},
            "Arg-list": {")"},
            "Arg-list-prime": {")"},
        }


    def _lookahead_token(self) -> Token:

        if self.pos >= len(self.tokens):

            last_line = self.tokens[-1][2] if self.tokens else 0

            return (END, END, last_line)

        return self.tokens[self.pos]



    def _advance(self):

        if self.pos < len(self.tokens):

            self.pos += 1



    def _la_symbol(self) -> str:

        ttype, tval, _ = self._lookahead_token()

        if ttype in ("ID", "NUM"):

            return ttype

        if ttype == END:

            return END

        return tval



    def _token_for_tree(self) -> Node:

        ttype, tval, _ = self._lookahead_token()

        if ttype == END:

            return Node("$")

        return Node(f"({ttype}, {tval})")



    # ---------- Grammar ----------

    def _build_grammar(self) -> Dict[str, List[List[Sym]]]:

        P: Dict[str, List[List[Sym]]] = {}



        def add(A: str, rhs: List[Sym]):

            P.setdefault(A, []).append(rhs)



        # Program -> Declaration-list

        add("Program", [N("Declaration-list")])



        # Declaration-list -> Declaration Declaration-list | EPSILON

        add("Declaration-list", [N("Declaration"), N("Declaration-list")])

        add("Declaration-list", [])



        # Declaration -> Declaration-initial Declaration-prime

        add("Declaration", [N("Declaration-initial"), N("Declaration-prime")])



        # Declaration-initial -> Type-specifier ID

        add("Declaration-initial", [N("Type-specifier"), T("ID")])



        # Declaration-prime -> Fun-declaration-prime | Var-declaration-prime

        add("Declaration-prime", [N("Fun-declaration-prime")])

        add("Declaration-prime", [N("Var-declaration-prime")])



        # Var-declaration-prime -> [ NUM ] ; | ;

        add("Var-declaration-prime", [T("["), T("NUM"), T("]"), T(";")])

        add("Var-declaration-prime", [T(";")])



        # Fun-declaration-prime -> ( Params ) Compound-stmt

        add("Fun-declaration-prime", [T("("), N("Params"), T(")"), N("Compound-stmt")])



        # Type-specifier -> int | void

        add("Type-specifier", [T("int")])

        add("Type-specifier", [T("void")])



        # Params -> int ID Param-prime Param-list | void

        add("Params", [T("int"), T("ID"), N("Param-prime"), N("Param-list")])

        add("Params", [T("void")])



        # Param-list -> , Param Param-list | EPSILON

        add("Param-list", [T(","), N("Param"), N("Param-list")])

        add("Param-list", [])



        # Param -> Declaration-initial Param-prime

        add("Param", [N("Declaration-initial"), N("Param-prime")])



        # Param-prime -> [ ] | EPSILON

        add("Param-prime", [T("["), T("]")])

        add("Param-prime", [])



        # Compound-stmt -> { Declaration-list Statement-list }

        add("Compound-stmt", [T("{"), N("Declaration-list"), N("Statement-list"), T("}")])



        # Statement-list -> Statement Statement-list | EPSILON

        add("Statement-list", [N("Statement"), N("Statement-list")])

        add("Statement-list", [])



        # Statement -> Expression-stmt | Compound-stmt | Selection-stmt | Iteration-stmt | Return-stmt

        add("Statement", [N("Expression-stmt")])

        add("Statement", [N("Compound-stmt")])

        add("Statement", [N("Selection-stmt")])

        add("Statement", [N("Iteration-stmt")])

        add("Statement", [N("Return-stmt")])



        # Expression-stmt -> Expression ; | break ; | ;

        add("Expression-stmt", [N("Expression"), T(";")])

        add("Expression-stmt", [T("break"), T(";")])

        add("Expression-stmt", [T(";")])



        # Selection-stmt -> if ( Expression ) Statement Else-stmt

        add("Selection-stmt", [T("if"), T("("), N("Expression"), T(")"), N("Statement"), N("Else-stmt")])



        # Else-stmt -> else Statement | EPSILON

        add("Else-stmt", [T("else"), N("Statement")])

        add("Else-stmt", [])



        # Iteration-stmt -> for ( Expression ; Expression ; Expression ) Compound-stmt

        add("Iteration-stmt", [T("for"), T("("), N("Expression"), T(";"), N("Expression"), T(";"),

                               N("Expression"), T(")"), N("Compound-stmt")])



        # Return-stmt -> return Return-stmt-prime

        add("Return-stmt", [T("return"), N("Return-stmt-prime")])



        # Return-stmt-prime -> Expression ; | ;

        add("Return-stmt-prime", [N("Expression"), T(";")])

        add("Return-stmt-prime", [T(";")])



        # Expression -> Simple-expression-zegond | ID B

        add("Expression", [N("Simple-expression-zegond")])

        add("Expression", [T("ID"), N("B")])



        # B -> = Expression | [ Expression ] H | Simple-expression-prime

        add("B", [T("="), N("Expression")])

        add("B", [T("["), N("Expression"), T("]"), N("H")])

        add("B", [N("Simple-expression-prime")])



        # H -> = Expression | G D C

        add("H", [T("="), N("Expression")])

        add("H", [N("G"), N("D"), N("C")])



        # Simple-expression-zegond -> Additive-expression-zegond C

        add("Simple-expression-zegond", [N("Additive-expression-zegond"), N("C")])



        # Simple-expression-prime -> Additive-expression-prime C

        add("Simple-expression-prime", [N("Additive-expression-prime"), N("C")])



        # C -> Relop Additive-expression | EPSILON

        add("C", [N("Relop"), N("Additive-expression")])
    
        add("C", [])



        # Relop -> == | <

        add("Relop", [T("==")])

        add("Relop", [T("<")])



        # Additive-expression -> Term D

        add("Additive-expression", [N("Term"), N("D")])



        # Additive-expression-prime -> Term-prime D

        add("Additive-expression-prime", [N("Term-prime"), N("D")])



        # Additive-expression-zegond -> Term-zegond D

        add("Additive-expression-zegond", [N("Term-zegond"), N("D")])



        # D -> Addop Term D | EPSILON

        add("D", [N("Addop"), N("Term"), N("D")])

        add("D", [])



        # Addop -> + | -

        add("Addop", [T("+")])

        add("Addop", [T("-")])



        # Term -> Signed-factor G

        add("Term", [N("Signed-factor"), N("G")])



        # Term-prime -> Factor-prime G

        add("Term-prime", [N("Factor-prime"), N("G")])



        # Term-zegond -> Signed-factor-zegond G

        add("Term-zegond", [N("Signed-factor-zegond"), N("G")])



        # G -> * Signed-factor G | / Signed-factor G | EPSILON

        add("G", [T("*"), N("Signed-factor"), N("G")])

        add("G", [T("/"), N("Signed-factor"), N("G")])

        add("G", [])



        # Signed-factor -> + Factor | - Factor | Factor

        add("Signed-factor", [T("+"), N("Factor")])

        add("Signed-factor", [T("-"), N("Factor")])

        add("Signed-factor", [N("Factor")])



        # Signed-factor-zegond -> + Factor | - Factor | Factor-zegond

        add("Signed-factor-zegond", [T("+"), N("Factor")])

        add("Signed-factor-zegond", [T("-"), N("Factor")])

        add("Signed-factor-zegond", [N("Factor-zegond")])



        # Factor -> ( Expression ) | ID Var-call-prime | NUM

        add("Factor", [T("("), N("Expression"), T(")")])

        add("Factor", [T("ID"), N("Var-call-prime")])

        add("Factor", [T("NUM")])



        # Var-call-prime -> ( Args ) | Var-prime

        add("Var-call-prime", [T("("), N("Args"), T(")")])

        add("Var-call-prime", [N("Var-prime")])



        # Var-prime -> [ Expression ] | EPSILON

        add("Var-prime", [T("["), N("Expression"), T("]")])

        add("Var-prime", [])



        # Factor-prime -> ( Args ) | EPSILON

        add("Factor-prime", [T("("), N("Args"), T(")")])

        add("Factor-prime", [])



        # Factor-zegond -> ( Expression ) | NUM

        add("Factor-zegond", [T("("), N("Expression"), T(")")])

        add("Factor-zegond", [T("NUM")])



        # Args -> Arg-list | EPSILON

        add("Args", [N("Arg-list")])

        add("Args", [])



        # Arg-list -> Expression Arg-list-prime

        add("Arg-list", [N("Expression"), N("Arg-list-prime")])



        # Arg-list-prime -> , Expression Arg-list-prime | EPSILON

        add("Arg-list-prime", [T(","), N("Expression"), N("Arg-list-prime")])

        add("Arg-list-prime", [])



        return P



    def _collect_terminals(self) -> Set[str]:

        ts = set()

        for A, alts in self.prods.items():

            for rhs in alts:

                for s in rhs:

                    if s.kind == "T":

                        ts.add(s.name)

        ts.add(END)

        return ts



    # ---------- FIRST/FOLLOW ----------

    def _first_of_sequence(self, seq: List[Sym]) -> Set[str]:

        """Return FIRST(seq) including EPS if nullable."""

        if not seq:

            return {EPS}

        out: Set[str] = set()

        for sym in seq:

            if sym.kind == "T":

                out.add(sym.name)

                return out

            # nonterminal

            out |= (self.first[sym.name] - {EPS})

            if EPS not in self.first[sym.name]:

                return out

        out.add(EPS)

        return out



    def _compute_first(self):

        changed = True

        while changed:

            changed = False

            for A, alts in self.prods.items():

                for rhs in alts:

                    f = self._first_of_sequence(rhs)

                    before = len(self.first[A])

                    self.first[A] |= f

                    if len(self.first[A]) != before:

                        changed = True



    def _compute_follow(self):

        # Start symbol gets $

        self.follow[self.start_symbol].add(END)



        changed = True

        while changed:

            changed = False

            for A, alts in self.prods.items():

                for rhs in alts:

                    for i, B in enumerate(rhs):

                        if B.kind != "N":

                            continue

                        beta = rhs[i + 1:]

                        first_beta = self._first_of_sequence(beta)

                        # add FIRST(beta) - EPS

                        before = len(self.follow[B.name])

                        self.follow[B.name] |= (first_beta - {EPS})

                        if len(self.follow[B.name]) != before:

                            changed = True

                        if EPS in first_beta:

                            before = len(self.follow[B.name])

                            self.follow[B.name] |= self.follow[A]

                            if len(self.follow[B.name]) != before:

                                changed = True



    # ---------- Parse table ----------

    def _build_parse_table(self):
        for A, alts in self.prods.items():
            for rhs in alts:
                first_rhs = self._first_of_sequence(rhs)

                # FIRST(rhs) entries
                for a in (first_rhs - {EPS}):
                    if (A, a) not in self.table:     
                        self.table[(A, a)] = rhs

                # EPSILON entries → FOLLOW(A)
                if EPS in first_rhs:
                    for b in self.follow[A]:
                        if (A, b) not in self.table: 
                            self.table[(A, b)] = rhs


    def parse(self) -> Node:
        root = Node(self.start_symbol)
        stack: List[Tuple[Sym, Node]] = []
        stack.append((T(END), root))
        stack.append((N(self.start_symbol), root))

        while stack:
            top_sym, top_node = stack.pop()
            la_tok = self._lookahead_token()
            la = self._la_symbol()
            line = la_tok[2]

            if top_sym.kind == "T":
                # terminal
                if top_sym.name == END:
                    if la == END:
                        root.add(Node("$"))
                        break
                    self.errors.append(f"#{line} : syntax error, illegal {la_tok[1]}")
                    self._advance()
                    stack.append((top_sym, top_node))
                    continue

                if la == top_sym.name:
                    # match
                    tok_node = self._token_for_tree()
                    top_node.name = tok_node.name
                    top_node.matched = True
                    self._advance()
                else:
                    # terminal mismatch => missing <terminal>
                    self.errors.append(f"#{line} : syntax error, missing {top_sym.name}")
                    top_node.hidden = True
                    top_node.matched = False
                continue

            # nonterminal
            A = top_sym.name
            key = (A, la)
            
            if key in self.table:
                if top_node.abort:
                    continue
                rhs = self.table[key]
                if rhs == []:
              
                    if top_node.abort:
                        continue
                    epsilon_node = Node("epsilon")
                    top_node.add(epsilon_node)
                    continue
                    
                child_nodes: List[Tuple[Sym, Node]] = []
                for sym in rhs:
                    if sym.kind == "N":
                        child = Node(sym.name)
                    else:
                        # Create terminal node with proper format
                        if sym.name in {"ID", "NUM"}:
                            child = Node(f"({sym.name}, )")
                        elif sym.name in KEYWORDS:
                            child = Node(f"(KEYWORD, {sym.name})")
                        else:
                            child = Node(f"(SYMBOL, {sym.name})")
                    top_node.add(child)
                    child_nodes.append((sym, child))
                    
                for sym, child in reversed(child_nodes):
                    stack.append((sym, child))
            else:
                # no table entry
                if la in self.follow[A] or la in self.sync_tokens.get(A, set()):

                    self.errors.append(f"#{line} : syntax error, missing {A}")
                    top_node.abort = True
                    top_node.hidden = True
                    #epsilon_node = Node("epsilon")
                    #top_node.add(epsilon_node)
                    continue
                else:
                    if la == END:
                        # Unexpected EOF
                        self.errors.append(f"#{line} : syntax error, Unexpected EOF")
                        break
                    else:
                        # illegal token
                        if la_tok[0] in ("ID", "NUM"):
                            self.errors.append(f"#{line} : syntax error, illegal {la_tok[0]}")
                        else:
                            self.errors.append(f"#{line} : syntax error, illegal {la_tok[1]}")
                        self._advance()
                        stack.append((top_sym, top_node))

        return root

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
    tree = parser.parse()

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