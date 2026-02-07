
from anytree import Node
class Parser:
    FIRST = {
        "Program": {"int", "void", "$"},
        "Declaration-list": {"int", "void"},
        "Declaration": {"int", "void"},
        "Declaration-initial": {"int", "void"},
        "Declaration-prime": {"(", ";", "["},
        "Var-declaration-prime": {";", "["},
        "Fun-declaration-prime": {"("},
        "Type-specifier": {"int", "void"},
        "Params": {"int", "void"},
        "Param-list": {","},
        "Param": {"int", "void"},
        "Param-prime": {"["},
        "Compound-stmt": {"{"},
        "Statement-list": {"ID", "NUM", ";", "(", "{", "break", "if", "for", "return", "+", "-"},
        "Statement": {"ID", "NUM", ";", "(", "{", "break", "if", "for", "return", "+", "-"},
        "Expression-stmt": {"ID", "NUM", "(", "+", "-", "break", ";"},
        "Selection-stmt": {"if"},
        "Else-stmt": {"else"},
        "Iteration-stmt": {"for"},
        "Return-stmt": {"return"},
        "Expression": {"ID", "NUM", "(", "+", "-"},
        "Simple-expression-zegond": {"NUM", "(", "+", "-"},
        "Additive-expression": {"ID", "NUM", "(", "+", "-"},
        "Term": {"ID", "NUM", "(", "+", "-"},
        "Factor": {"ID", "NUM", "("},
        "Args": {"ID", "NUM", "(", "+", "-"},
    }

    FOLLOW = {
        "Program": {"$"},

        "Declaration-list": {
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'for', 'return', '+', '-', '$'
        },

        "Declaration": {
            'int', 'void',
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'for', 'return', '+', '-', '$'
        },

        "Declaration-initial": {'[', ';', '('},

        "Declaration-prime": {
            'int', 'void',
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'for', 'return', '+', '-', '$'
        },

        "Var-declaration-prime": {
            'int', 'void',
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'for', 'return', '+', '-', '$'
        },

        "Fun-declaration-prime": {
            'int', 'void',
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'for', 'return', '+', '-', '$'
        },

        "Type-specifier": {'ID'},

        "Params": {')'},

        "Param-list": {')'},

        "Param": {',', ')'},

        "Param-prime": {',', ')'},

        "Compound-stmt": {
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'else', 'for', 'return', '+', '-', '$'
        },

        "Statement-list": {'}'},

        "Statement": {
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'else', 'for', 'return', '+', '-', '$'
        },

        "Expression-stmt": {
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'else', 'for', 'return', '+', '-', '$'
        },

        "Selection-stmt": {
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'else', 'for', 'return', '+', '-', '$'
        },

        "Else-stmt": {
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'else', 'for', 'return', '+', '-', '$'
        },

        "Iteration-stmt": {
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'else', 'for', 'return', '+', '-', '$'
        },

        "Return-stmt": {
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'else', 'for', 'return', '+', '-', '$'
        },

        "Return-stmt-prime": {
            'ID', 'NUM', ';', '(', '{', '}', 'break',
            'if', 'else', 'for', 'return', '+', '-', '$'
        },

        "Expression": {']', ';', ')', ','},

        "B": {']', ';', ')', ','},

        "H": {']', ';', ')', ','},

        "Simple-expression-zegond": {']', ';', ')', ','},

        "Simple-expression-prime": {']', ';', ')', ','},

        "C": {']', ';', ')', ','},

        "Additive-expression": {']', ';', ')', ','},

        "Additive-expression-prime": {
            ']', ';', ')', ',', '==', '<'
        },

        "Additive-expression-zegond": {
            ']', ';', ')', ',', '==', '<'
        },

        "D": {']', ';', ')', ',', '==', '<'},

        "Term": {
            ']', ';', ')', ',', '==', '<', '+', '-'
        },

        "Term-prime": {
            ']', ';', ')', ',', '==', '<', '+', '-'
        },

        "Term-zegond": {
            ']', ';', ')', ',', '==', '<', '+', '-'
        },

        "G": {
            ']', ';', ')', ',', '==', '<', '+', '-'
        },

        "Signed-factor": {
            ']', ';', ')', ',', '==', '<', '+', '-', '*', '/'
        },

        "Signed-factor-zegond": {
            ']', ';', ')', ',', '==', '<', '+', '-', '*', '/'
        },

        "Factor": {
            ']', ';', ')', ',', '==', '<', '+', '-', '*', '/'
        },

        "Factor-prime": {
            ']', ';', ')', ',', '==', '<', '+', '-', '*', '/'
        },

        "Var-call-prime": {
            ']', ';', ')', ',', '==', '<', '+', '-', '*', '/'
        },

        "Var-prime": {
            ']', ';', ')', ',', '==', '<', '+', '-', '*', '/'
        },

        "Factor-zegond": {
            ']', ';', ')', ',', '==', '<', '+', '-', '*', '/'
        },

        "Args": {')'},

        "Arg-list": {')'},

        "Arg-list-prime": {')'},
    }

    TERMINALS = ['ID', 'NUM', ';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '=', '<', '==', 'break',
                 'else', 'for', 'if', 'int', 'return', 'void', '$']

    def __init__(self, scanner):
        self.scanner = scanner
        self.errors = []
        self.root = None
        self.token = self.scanner.get_next_token()
        self.update_lookahead()

    def update_lookahead(self):
        if self.token.type in ['ID', 'NUM', 'EOF']:
            self.lookahead = self.token.type
            if self.lookahead == 'EOF': self.lookahead = '$'
        else:
            self.lookahead = self.token.lexeme

    def get_next_token(self):
        self.token = self.scanner.get_next_token()
        self.update_lookahead()

    def match(self, expected_token, parent):
        if self.lookahead == expected_token:
            Node(f"({self.token.type}, {self.token.lexeme})", parent=parent)
            self.get_next_token()
        else:
            if self.lookahead == '$':
                self.errors.append(f"#{self.token.line} : syntax error, Unexpected EOF")
                raise EOFError("Unexpected EOF")
            self.errors.append(f"#{self.token.line} : syntax error, missing {expected_token}")

    def panic(self, node, parent, caller_func):
        node.parent = None 
        if self.lookahead == '$':
            self.errors.append(f"#{self.token.line} : syntax error, Unexpected EOF")
            raise EOFError("Unexpected EOF")

        self.errors.append(f"#{self.token.line} : syntax error, illegal {self.lookahead}")
        self.get_next_token()
        caller_func(parent)



    def parse(self):
        self.root = Node("Program")
        self.Program(self.root)
        return self.root

    def Program(self, parent):
        if self.lookahead in ['int', 'void', '$']:
            self.Declaration_list(parent)

            while self.lookahead != '$':
                self.errors.append(f"#{self.token.line} : syntax error, illegal {self.lookahead}")
                self.get_next_token()

            Node("$", parent=parent)

        else:
            if self.lookahead == '$':
                self.errors.append(f"#{self.token.line} : syntax error, missing Program")
            else:
                self.errors.append(f"#{self.token.line} : syntax error, illegal {self.lookahead}")
                self.get_next_token()
                self.Program(parent)


    def Declaration_list(self, parent):
        node = Node("Declaration-list", parent=parent)
        if self.lookahead in ['int', 'void']:
            self.Declaration(node)
            self.Declaration_list(node)
        elif self.lookahead in ['ID', 'NUM', ';', '(', '{', '}', 'break', 'if', 'for', 'return', '+', '-', '$']:
            Node("epsilon", parent=node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', '{', '}', 'break', 'if', 'for', 'return', '+', '-', '$']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Declaration-list")
                node.parent = None
            else:
                self.panic(node, parent, self.Declaration_list)

    def Declaration(self, parent):
        node = Node("Declaration", parent=parent)
        if self.lookahead in ['int', 'void']:
            self.Declaration_initial(node)
            self.Declaration_prime(node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', 'int', 'void', '{', '}', 'break', 'if', 'for', 'return', '+',
                                  '-', '$']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Declaration")
                node.parent = None
            else:
                self.panic(node, parent, self.Declaration)


    def Declaration_initial(self, parent):
        node = Node("Declaration-initial", parent=parent)
        if self.lookahead in ['int', 'void']:
            self.Type_specifier(node)
            self.match('ID', node)
        else:
            if self.lookahead in ['[', ';', '(', ')', ',']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Declaration-initial")
                node.parent = None
            else:
                self.panic(node, parent, self.Declaration_initial)

    def Declaration_prime(self, parent):
        node = Node("Declaration-prime", parent=parent)
        if self.lookahead == '(':
            self.Fun_declaration_prime(node)
        elif self.lookahead in [';', '[']:
            self.Var_declaration_prime(node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', 'int', 'void', '{', '}', 'break', 'if', 'for', 'return', '+',
                                  '-', '$']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Declaration-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Declaration_prime)

    def Var_declaration_prime(self, parent):
        node = Node("Var-declaration-prime", parent=parent)
        if self.lookahead == '[':
            self.match('[', node)
            self.match('NUM', node)
            self.match(']', node)
            self.match(';', node)
        elif self.lookahead == ';':
            self.match(';', node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', 'int', 'void', '{', '}', 'break', 'if', 'for', 'return', '+',
                                  '-', '$']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Var-declaration-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Var_declaration_prime)

    def Fun_declaration_prime(self, parent):
        node = Node("Fun-declaration-prime", parent=parent)
        if self.lookahead == '(':
            self.match('(', node)
            self.Params(node)
            self.match(')', node)
            self.Compound_stmt(node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', 'int', 'void', '{', '}', 'break', 'if', 'for', 'return', '+',
                                  '-', '$']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Fun-declaration-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Fun_declaration_prime)

    def Type_specifier(self, parent):
        node = Node("Type-specifier", parent=parent)
        if self.lookahead == 'int':
            self.match('int', node)
        elif self.lookahead == 'void':
            self.match('void', node)
        else:
            if self.lookahead == 'ID':
                self.errors.append(f"#{self.token.line} : syntax error, missing Type-specifier")
                node.parent = None
            else:
                self.panic(node, parent, self.Type_specifier)

    def Params(self, parent):
        node = Node("Params", parent=parent)
        if self.lookahead == 'int':
            self.match('int', node)
            self.match('ID', node)
            self.Param_prime(node)
            self.Param_list(node)
        elif self.lookahead == 'void':
            self.match('void', node)
        else:
            if self.lookahead == ')':
                self.errors.append(f"#{self.token.line} : syntax error, missing Params")
                node.parent = None
            else:
                self.panic(node, parent, self.Params)

    def Param_list(self, parent):
        node = Node("Param-list", parent=parent)
        if self.lookahead == ',':
            self.match(',', node)
            self.Param(node)
            self.Param_list(node)
        elif self.lookahead == ')':
            Node("epsilon", parent=node)
        else:
            if self.lookahead == ')':
                self.errors.append(f"#{self.token.line} : syntax error, missing Param-list")
                node.parent = None
            else:
                self.panic(node, parent, self.Param_list)

    def Param(self, parent):
        node = Node("Param", parent=parent)
        if self.lookahead in ['int', 'void']:
            self.Declaration_initial(node)
            self.Param_prime(node)
        else:
            if self.lookahead in [')', ',']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Param")
                node.parent = None
            else:
                self.panic(node, parent, self.Param)

    def Param_prime(self, parent):
        node = Node("Param-prime", parent=parent)
        if self.lookahead == '[':
            self.match('[', node)
            self.match(']', node)
        elif self.lookahead in [')', ',']:
            Node("epsilon", parent=node)
        else:
            if self.lookahead in [')', ',']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Param-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Param_prime)

    def Compound_stmt(self, parent):
        node = Node("Compound-stmt", parent=parent)
        if self.lookahead == '{':
            self.match('{', node)
            self.Declaration_list(node)
            self.Statement_list(node)
            self.match('}', node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', 'int', 'void', '{', '}', 'break', 'if', 'else', 'for',
                                  'return', '+', '-', '$']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Compound-stmt")
                node.parent = None
            else:
                self.panic(node, parent, self.Compound_stmt)

    def Statement_list(self, parent):
        node = Node("Statement-list", parent=parent)
        if self.lookahead in ['ID', 'NUM', ';', '(', '{', 'break', 'if', 'for', 'return', '+', '-']:
            self.Statement(node)
            self.Statement_list(node)
        elif self.lookahead == '}':
            Node("epsilon", parent=node)
        else:
            if self.lookahead == '}':
                self.errors.append(f"#{self.token.line} : syntax error, missing Statement-list")
                node.parent = None
            else:
                self.panic(node, parent, self.Statement_list)

    def Statement(self, parent):
        node = Node("Statement", parent=parent)
        if self.lookahead in ['ID', 'NUM', ';', '(', 'break', '+', '-']:
            self.Expression_stmt(node)
        elif self.lookahead == '{':
            self.Compound_stmt(node)
        elif self.lookahead == 'if':
            self.Selection_stmt(node)
        elif self.lookahead == 'for':
            self.Iteration_stmt(node)
        elif self.lookahead == 'return':
            self.Return_stmt(node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', '{', '}', 'break', 'if', 'else', 'for', 'return', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Statement")
                node.parent = None
            else:
                self.panic(node, parent, self.Statement)

    def Expression_stmt(self, parent):
        node = Node("Expression-stmt", parent=parent)
        if self.lookahead in ['ID', 'NUM', '(', '+', '-']:
            self.Expression(node)
            self.match(';', node)
        elif self.lookahead == 'break':
            self.match('break', node)
            self.match(';', node)
        elif self.lookahead == ';':
            self.match(';', node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', '{', '}', 'break', 'if', 'else', 'for', 'return', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Expression-stmt")
                node.parent = None
            else:
                self.panic(node, parent, self.Expression_stmt)

    def Selection_stmt(self, parent):
        node = Node("Selection-stmt", parent=parent)
        if self.lookahead == 'if':
            self.match('if', node)
            self.match('(', node)
            self.Expression(node)
            self.match(')', node)
            self.Statement(node)
            self.Else_stmt(node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', '{', '}', 'break', 'if', 'else', 'for', 'return', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Selection-stmt")
                node.parent = None
            else:
                self.panic(node, parent, self.Selection_stmt)

    def Else_stmt(self, parent):
        node = Node("Else-stmt", parent=parent)
        if self.lookahead == 'else':
            self.match('else', node)
            self.Statement(node)
        elif self.lookahead in ['ID', 'NUM', ';', '(', '{', '}', 'break', 'if', 'else', 'for', 'return', '+', '-']:
            Node("epsilon", parent=node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', '{', '}', 'break', 'if', 'else', 'for', 'return', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Else-stmt")
                node.parent = None
            else:
                self.panic(node, parent, self.Else_stmt)

    def Iteration_stmt(self, parent):
        node = Node("Iteration-stmt", parent=parent)
        if self.lookahead == 'for':
            self.match('for', node)
            self.match('(', node)
            self.Expression(node)
            self.match(';', node)
            self.Expression(node)
            self.match(';', node)
            self.Expression(node)
            self.match(')', node)
            self.Compound_stmt(node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', '{', '}', 'break', 'if', 'else', 'for', 'return', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Iteration-stmt")
                node.parent = None
            else:
                self.panic(node, parent, self.Iteration_stmt)

    def Return_stmt(self, parent):
        node = Node("Return-stmt", parent=parent)
        if self.lookahead == 'return':
            self.match('return', node)
            self.Return_stmt_prime(node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', '{', '}', 'break', 'if', 'else', 'for', 'return', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Return-stmt")
                node.parent = None
            else:
                self.panic(node, parent, self.Return_stmt)

    def Return_stmt_prime(self, parent):
        node = Node("Return-stmt-prime", parent=parent)
        if self.lookahead in ['ID', 'NUM', '(', '+', '-']:
            self.Expression(node)
            self.match(';', node)
        elif self.lookahead == ';':
            self.match(';', node)
        else:
            if self.lookahead in ['ID', 'NUM', ';', '(', '{', '}', 'break', 'if', 'else', 'for', 'return', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Return-stmt-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Return_stmt_prime)

    def Expression(self, parent):
        node = Node("Expression", parent=parent)
        if self.lookahead in ['NUM', '(', '+', '-']:
            self.Simple_expression_zegond(node)
        elif self.lookahead == 'ID':
            self.match('ID', node)
            self.B(node)
        else:
            if self.lookahead in [']', ';', ')', ',']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Expression")
                node.parent = None
            else:
                self.panic(node, parent, self.Expression)

    def B(self, parent):
        node = Node("B", parent=parent)
        if self.lookahead == '=':
            self.match('=', node)
            self.Expression(node)
        elif self.lookahead == '[':
            self.match('[', node)
            self.Expression(node)
            self.match(']', node)
            self.H(node)
        elif self.lookahead in [']', ';', '(', ')', ',', '==', '<', '+', '-', '*', '/']:
            self.Simple_expression_prime(node)
        else:
            if self.lookahead in [']', ';', ')', ',']:
                self.errors.append(f"#{self.token.line} : syntax error, missing B")
                node.parent = None
            else:
                self.panic(node, parent, self.B)

    def H(self, parent):
        node = Node("H", parent=parent)
        if self.lookahead == '=':
            self.match('=', node)
            self.Expression(node)
        elif self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-', '*', '/']:
            self.G(node)
            self.D(node)
            self.C(node)
        else:
            if self.lookahead in [']', ';', ')', ',']:
                self.errors.append(f"#{self.token.line} : syntax error, missing H")
                node.parent = None
            else:
                self.panic(node, parent, self.H)

    def Simple_expression_zegond(self, parent):
        node = Node("Simple-expression-zegond", parent=parent)
        if self.lookahead in ['NUM', '(', '+', '-']:
            self.Additive_expression_zegond(node)
            self.C(node)
        else:
            if self.lookahead in [']', ';', ')', ',']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Simple-expression-zegond")
                node.parent = None
            else:
                self.panic(node, parent, self.Simple_expression_zegond)

    def Simple_expression_prime(self, parent):
        node = Node("Simple-expression-prime", parent=parent)
        if self.lookahead in [']', ';', '(', ')', ',', '==', '<', '+', '-', '*', '/']:
            self.Additive_expression_prime(node)
            self.C(node)
        else:
            if self.lookahead in [']', ';', ')', ',']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Simple-expression-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Simple_expression_prime)

    def C(self, parent):
        node = Node("C", parent=parent)
        if self.lookahead in ['==', '<']:
            self.Relop(node)
            self.Additive_expression(node)
        elif self.lookahead in [']', ';', ')', ',']:
            Node("epsilon", parent=node)
        else:
            if self.lookahead in [']', ';', ')', ',']:
                self.errors.append(f"#{self.token.line} : syntax error, missing C")
                node.parent = None
            else:
                self.panic(node, parent, self.C)

    def Relop(self, parent):
        node = Node("Relop", parent=parent)
        if self.lookahead == '==':
            self.match('==', node)
        elif self.lookahead == '<':
            self.match('<', node)
        else:
            if self.lookahead in ['ID', 'NUM', '(', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Relop")
                node.parent = None
            else:
                self.panic(node, parent, self.Relop)

    def Additive_expression(self, parent):
        node = Node("Additive-expression", parent=parent)
        if self.lookahead in ['ID', 'NUM', '(', '+', '-']:
            self.Term(node)
            self.D(node)
        else:
            if self.lookahead in [']', ';', ')', ',']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Additive-expression")
                node.parent = None
            else:
                self.panic(node, parent, self.Additive_expression)

    def Additive_expression_prime(self, parent):
        node = Node("Additive-expression-prime", parent=parent)
        if self.lookahead in [']', ';', '(', ')', ',', '==', '<', '+', '-', '*', '/']:
            self.Term_prime(node)
            self.D(node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Additive-expression-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Additive_expression_prime)

    def Additive_expression_zegond(self, parent):
        node = Node("Additive-expression-zegond", parent=parent)
        if self.lookahead in ['NUM', '(', '+', '-']:
            self.Term_zegond(node)
            self.D(node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Additive-expression-zegond")
                node.parent = None
            else:
                self.panic(node, parent, self.Additive_expression_zegond)

    def D(self, parent):
        node = Node("D", parent=parent)
        if self.lookahead in ['+', '-']:
            self.Addop(node)
            self.Term(node)
            self.D(node)
        elif self.lookahead in [']', ';', ')', ',', '==', '<']:
            Node("epsilon", parent=node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<']:
                self.errors.append(f"#{self.token.line} : syntax error, missing D")
                node.parent = None
            else:
                self.panic(node, parent, self.D)

    def Addop(self, parent):
        node = Node("Addop", parent=parent)
        if self.lookahead == '+':
            self.match('+', node)
        elif self.lookahead == '-':
            self.match('-', node)
        else:
            if self.lookahead in ['ID', 'NUM', '(', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Addop")
                node.parent = None
            else:
                self.panic(node, parent, self.Addop)

    def Term(self, parent):
        node = Node("Term", parent=parent)
        if self.lookahead in ['ID', 'NUM', '(', '+', '-']:
            self.Signed_factor(node)
            self.G(node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Term")
                node.parent = None
            else:
                self.panic(node, parent, self.Term)

    def Term_prime(self, parent):
        node = Node("Term-prime", parent=parent)
        if self.lookahead in [']', ';', '(', ')', ',', '==', '<', '+', '-', '*', '/']:
            self.Factor_prime(node)
            self.G(node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Term-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Term_prime)

    def Term_zegond(self, parent):
        node = Node("Term-zegond", parent=parent)
        if self.lookahead in ['NUM', '(', '+', '-']:
            self.Signed_factor_zegond(node)
            self.G(node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Term-zegond")
                node.parent = None
            else:
                self.panic(node, parent, self.Term_zegond)

    def G(self, parent):
        node = Node("G", parent=parent)
        if self.lookahead == '*':
            self.match('*', node)
            self.Signed_factor(node)
            self.G(node)
        elif self.lookahead == '/':
            self.match('/', node)
            self.Signed_factor(node)
            self.G(node)
        elif self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-']:
            Node("epsilon", parent=node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-']:
                self.errors.append(f"#{self.token.line} : syntax error, missing G")
                node.parent = None
            else:
                self.panic(node, parent, self.G)

    def Signed_factor(self, parent):
        node = Node("Signed-factor", parent=parent)
        if self.lookahead == '+':
            self.match('+', node)
            self.Factor(node)
        elif self.lookahead == '-':
            self.match('-', node)
            self.Factor(node)
        elif self.lookahead in ['ID', 'NUM', '(']:
            self.Factor(node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-', '*', '/']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Signed-factor")
                node.parent = None
            else:
                self.panic(node, parent, self.Signed_factor)

    def Signed_factor_zegond(self, parent):
        node = Node("Signed-factor-zegond", parent=parent)
        if self.lookahead == '+':
            self.match('+', node)
            self.Factor(node)
        elif self.lookahead == '-':
            self.match('-', node)
            self.Factor(node)
        elif self.lookahead in ['NUM', '(']:
            self.Factor_zegond(node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-', '*', '/']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Signed-factor-zegond")
                node.parent = None
            else:
                self.panic(node, parent, self.Signed_factor_zegond)

    def Factor(self, parent):
        node = Node("Factor", parent=parent)
        if self.lookahead == '(':
            self.match('(', node)
            self.Expression(node)
            self.match(')', node)
        elif self.lookahead == 'ID':
            self.match('ID', node)
            self.Var_call_prime(node)
        elif self.lookahead == 'NUM':
            self.match('NUM', node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-', '*', '/']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Factor")
                node.parent = None
            else:
                self.panic(node, parent, self.Factor)

    def Var_call_prime(self, parent):
        node = Node("Var-call-prime", parent=parent)
        if self.lookahead == '(':
            self.match('(', node)
            self.Args(node)
            self.match(')', node)
        elif self.lookahead in ['[', ']', ';', ')', ',', '==', '<', '+', '-', '*', '/']:
            self.Var_prime(node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-', '*', '/']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Var-call-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Var_call_prime)

    def Var_prime(self, parent):
        node = Node("Var-prime", parent=parent)
        if self.lookahead == '[':
            self.match('[', node)
            self.Expression(node)
            self.match(']', node)
        elif self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-', '*', '/']:
            Node("epsilon", parent=node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-', '*', '/']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Var-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Var_prime)

    def Factor_prime(self, parent):
        node = Node("Factor-prime", parent=parent)
        if self.lookahead == '(':
            self.match('(', node)
            self.Args(node)
            self.match(')', node)
        elif self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-', '*', '/']:
            Node("epsilon", parent=node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-', '*', '/']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Factor-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Factor_prime)

    def Factor_zegond(self, parent):
        node = Node("Factor-zegond", parent=parent)
        if self.lookahead == '(':
            self.match('(', node)
            self.Expression(node)
            self.match(')', node)
        elif self.lookahead == 'NUM':
            self.match('NUM', node)
        else:
            if self.lookahead in [']', ';', ')', ',', '==', '<', '+', '-', '*', '/']:
                self.errors.append(f"#{self.token.line} : syntax error, missing Factor-zegond")
                node.parent = None
            else:
                self.panic(node, parent, self.Factor_zegond)

    def Args(self, parent):
        node = Node("Args", parent=parent)
        if self.lookahead in ['ID', 'NUM', '(', '+', '-']:
            self.Arg_list(node)
        elif self.lookahead == ')':
            Node("epsilon", parent=node)
        else:
            if self.lookahead == ')':
                self.errors.append(f"#{self.token.line} : syntax error, missing Args")
                node.parent = None
            else:
                self.panic(node, parent, self.Args)

    def Arg_list(self, parent):
        node = Node("Arg-list", parent=parent)
        if self.lookahead in ['ID', 'NUM', '(', '+', '-']:
            self.Expression(node)
            self.Arg_list_prime(node)
        else:
            if self.lookahead == ')':
                self.errors.append(f"#{self.token.line} : syntax error, missing Arg-list")
                node.parent = None
            else:
                self.panic(node, parent, self.Arg_list)

    def Arg_list_prime(self, parent):
        node = Node("Arg-list-prime", parent=parent)
        if self.lookahead == ',':
            self.match(',', node)
            self.Expression(node)
            self.Arg_list_prime(node)
        elif self.lookahead == ')':
            Node("epsilon", parent=node)
        else:
            if self.lookahead == ')':
                self.errors.append(f"#{self.token.line} : syntax error, missing Arg-list-prime")
                node.parent = None
            else:
                self.panic(node, parent, self.Arg_list_prime)
