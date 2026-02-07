import sys


class Token:
    def __init__(self, token_type, lexeme, line):
        self.type = token_type
        self.lexeme = lexeme
        self.line = line

    def __str__(self):
        return f"({self.type}, {self.lexeme})"


class Scanner:
    KEYWORDS = {"break", "else", "for", "if", "int", "return", "void"}
    SYMBOLS = set(";:,[](){}+-*/=<")

    def __init__(self, filename):
        self.tokens = []
        self.errors = []
        self.current_token = None

        try:
            with open(filename, encoding="utf-8") as f:
                self.scan(f.read())
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
            sys.exit(1)

        self._it = iter(self.tokens)

    # --------------------------------------------------
    # Main driver
    # --------------------------------------------------
    def scan(self, text):
        self.text = text
        self.n = len(text)
        self.i = 0
        self.line = 1

        while self.i < self.n:
            c = self.text[self.i]

            if self._handle_whitespace(c):
                continue
            if self._handle_comment(c):
                continue
            if self._handle_number(c):
                continue
            if self._handle_identifier(c):
                continue
            if self._handle_symbol(c):
                continue

            self._handle_illegal(c)

        self.tokens.append(Token("EOF", "$", self.line))

    def _handle_whitespace(self, c):
        if c in " \t\r\v\f":
            self.i += 1
            return True
        if c == "\n":
            self.line += 1
            self.i += 1
            return True
        return False

    def _handle_comment(self, c):
        if c == "/" and self.i + 1 < self.n:
            nxt = self.text[self.i + 1]

            # single-line comment
            if nxt == "/":
                self.i += 2
                while self.i < self.n and self.text[self.i] != "\n":
                    self.i += 1
                return True

            # multi-line comment
            if nxt == "*":
                self.i += 2
                while self.i < self.n:
                    if self.text[self.i] == "\n":
                        self.line += 1
                    if self.i + 1 < self.n and self.text[self.i:self.i + 2] == "*/":
                        self.i += 2
                        break
                    self.i += 1
                return True

        return False

    def _handle_number(self, c):
        if not c.isdigit():
            return False

        start = self.i
        while self.i < self.n and self.text[self.i].isdigit():
            self.i += 1

        if self.i < self.n and (self.text[self.i].isalnum() or self.text[self.i] == "_"):
            while self.i < self.n and (self.text[self.i].isalnum() or self.text[self.i] == "_"):
                self.i += 1
            self.errors.append((self.line, self.text[start:self.i], "Invalid Number"))
        else:
            self.tokens.append(Token("NUM", self.text[start:self.i], self.line))

        return True

    def _handle_identifier(self, c):
        if not (c.isalpha() or c == "_"):
            return False

        start = self.i
        while self.i < self.n and (self.text[self.i].isalnum() or self.text[self.i] == "_"):
            self.i += 1

        lexeme = self.text[start:self.i]
        token_type = "KEYWORD" if lexeme in self.KEYWORDS else "ID"
        self.tokens.append(Token(token_type, lexeme, self.line))
        return True

    def _handle_symbol(self, c):
        if self.i + 1 < self.n and self.text[self.i:self.i + 2] == "==":
            self.tokens.append(Token("SYMBOL", "==", self.line))
            self.i += 2
            return True

        if c in self.SYMBOLS:
            self.tokens.append(Token("SYMBOL", c, self.line))
            self.i += 1
            return True

        return False

    def _handle_illegal(self, c):
        self.errors.append((self.line, c, "Illegal Character"))
        self.i += 1

    def get_next_token(self):
        try:
            self.current_token = next(self._it)
        except StopIteration:
            self.current_token = Token("EOF", "$", -1)
        return self.current_token
