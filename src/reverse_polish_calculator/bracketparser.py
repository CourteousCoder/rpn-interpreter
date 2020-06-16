class BracketParser:
    def __init__(self, opening, closing):
        self.opening = opening
        self.closing = closing
        self._stack = []
        self._contents = []

    @property
    def contents(self):
        return ' '.join(self._contents)

    @property
    def empty(self):
        return self._contents == [self.opening, self.closing]

    @property
    def valid(self):
        return len(self._stack) == 0

    def parse(self, next_token: str):
        self._contents.append(next_token)
        if next_token == self.opening:
            self._stack.append(None)
        elif next_token == self.closing:
            if self._stack:
                self._stack.pop()
            else:
                raise SyntaxError(f'Syntax Error: Misplaced `{self.closing}` bracket')
        return self

    def reset(self):
        self._stack = []
        self._contents = []
        return self
