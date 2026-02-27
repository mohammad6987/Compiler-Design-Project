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
    _STATE_START = 0
    _STATE_IN_NUM = 1
    _STATE_IN_ID = 2
    _STATE_IN_SLASH = 3
    _STATE_IN_EQ = 4
    _STATE_IN_COMMENT_LINE = 5
    _STATE_IN_COMMENT_BLOCK = 6
    _STATE_IN_COMMENT_BLOCK_STAR = 7
    _STATE_IN_INVALID_NUM = 8

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
        state = self._STATE_START
        start = 0

        while self.i < self.n:
            c = self.text[self.i]

            if state == self._STATE_START:
                if c in " \t\r\v\f":
                    self.i += 1
                    continue
                if c == "\n":
                    self.line += 1
                    self.i += 1
                    continue
                if c.isdigit():
                    start = self.i
                    state = self._STATE_IN_NUM
                    self.i += 1
                    continue
                if c.isalpha() or c == "_":
                    start = self.i
                    state = self._STATE_IN_ID
                    self.i += 1
                    continue
                if c == "/":
                    state = self._STATE_IN_SLASH
                    self.i += 1
                    continue
                if c == "=":
                    state = self._STATE_IN_EQ
                    self.i += 1
                    continue
                if c in self.SYMBOLS:
                    self.tokens.append(Token("SYMBOL", c, self.line))
                    self.i += 1
                    continue

                self.errors.append((self.line, c, "Illegal Character"))
                self.i += 1
                continue

            if state == self._STATE_IN_NUM:
                if c.isdigit():
                    self.i += 1
                    continue
                if c.isalnum() or c == "_":
                    state = self._STATE_IN_INVALID_NUM
                    self.i += 1
                    continue
                self.tokens.append(Token("NUM", self.text[start:self.i], self.line))
                state = self._STATE_START
                continue

            if state == self._STATE_IN_INVALID_NUM:
                if c.isalnum() or c == "_":
                    self.i += 1
                    continue
                self.errors.append((self.line, self.text[start:self.i], "Invalid Number"))
                state = self._STATE_START
                continue

            if state == self._STATE_IN_ID:
                if c.isalnum() or c == "_":
                    self.i += 1
                    continue
                lexeme = self.text[start:self.i]
                token_type = "KEYWORD" if lexeme in self.KEYWORDS else "ID"
                self.tokens.append(Token(token_type, lexeme, self.line))
                state = self._STATE_START
                continue

            if state == self._STATE_IN_SLASH:
                if self.i >= self.n:
                    self.tokens.append(Token("SYMBOL", "/", self.line))
                    state = self._STATE_START
                    continue
                if c == "/":
                    state = self._STATE_IN_COMMENT_LINE
                    self.i += 1
                    continue
                if c == "*":
                    state = self._STATE_IN_COMMENT_BLOCK
                    self.i += 1
                    continue
                self.tokens.append(Token("SYMBOL", "/", self.line))
                state = self._STATE_START
                continue

            if state == self._STATE_IN_EQ:
                if self.i < self.n and c == "=":
                    self.tokens.append(Token("SYMBOL", "==", self.line))
                    self.i += 1
                    state = self._STATE_START
                    continue
                self.tokens.append(Token("SYMBOL", "=", self.line))
                state = self._STATE_START
                continue

            if state == self._STATE_IN_COMMENT_LINE:
                if c == "\n":
                    self.line += 1
                    self.i += 1
                    state = self._STATE_START
                    continue
                self.i += 1
                continue

            if state == self._STATE_IN_COMMENT_BLOCK:
                if c == "\n":
                    self.line += 1
                if c == "*":
                    state = self._STATE_IN_COMMENT_BLOCK_STAR
                    self.i += 1
                    continue
                self.i += 1
                continue

            if state == self._STATE_IN_COMMENT_BLOCK_STAR:
                if c == "/":
                    self.i += 1
                    state = self._STATE_START
                    continue
                if c == "\n":
                    self.line += 1
                if c == "*":
                    self.i += 1
                    continue
                state = self._STATE_IN_COMMENT_BLOCK
                self.i += 1
                continue

        if state == self._STATE_IN_NUM:
            self.tokens.append(Token("NUM", self.text[start:self.i], self.line))
        elif state == self._STATE_IN_INVALID_NUM:
            self.errors.append((self.line, self.text[start:self.i], "Invalid Number"))
        elif state == self._STATE_IN_ID:
            lexeme = self.text[start:self.i]
            token_type = "KEYWORD" if lexeme in self.KEYWORDS else "ID"
            self.tokens.append(Token(token_type, lexeme, self.line))
        elif state == self._STATE_IN_EQ:
            self.tokens.append(Token("SYMBOL", "=", self.line))
        elif state == self._STATE_IN_SLASH:
            self.tokens.append(Token("SYMBOL", "/", self.line))

        self.tokens.append(Token("EOF", "$", self.line))

    def get_next_token(self):
        try:
            self.current_token = next(self._it)
        except StopIteration:
            self.current_token = Token("EOF", "$", -1)
        return self.current_token
