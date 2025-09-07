import re

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    token_specification = [
        ('NUMBER',   r'\d+(\.\d*)?'),
        ('STRING',   r'"[^"]*"'),
        ('ID',       r'[A-Za-z_]\w*'),
        ('OP',       r'==|!=|<=|>=|<|>|=|\+|-|\*|/'),
        ('NEWLINE',  r'\n'),
        ('SKIP',     r'[ \t]+'),
        ('COLON',    r':'),
        ('LPAREN',   r'\('),
        ('RPAREN',   r'\)'),
        ('COMMA',    r','),
        ('UNKNOWN',  r'.'),
    ]
    def __init__(self, code):
        self.tokens = []
        self.code = code
        self.tokenize()

    def tokenize(self):
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specification)
        get_token = re.compile(tok_regex).match
        pos = 0
        mo = get_token(self.code, pos)
        while mo is not None:
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'NEWLINE':
                self.tokens.append(Token('NEWLINE', '\n'))
            elif kind == 'SKIP':
                pass
            elif kind == 'UNKNOWN':
                if value == '#':
                    next_newline = self.code.find('\n', pos)
                    if next_newline == -1:
                        break
                    pos = next_newline
                    mo = get_token(self.code, pos)
                    continue
                else:
                    self.tokens.append(Token('UNKNOWN', value))
            else:
                self.tokens.append(Token(kind, value))
            pos = mo.end()
            mo = get_token(self.code, pos)
        self.tokens.append(Token('EOF', ''))

class Parser:
    def __init__(self, code):
        self.lexer = Lexer(code)
        self.tokens = self.lexer.tokens
        self.pos = 0
#
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1
#syntax error or validate next tokens 
    def expect(self, type_, value=None):
        token = self.peek()
        if token is None or token.type != type_ or (value is not None and token.value != value):
            raise SyntaxError(f"Expected {type_} {value}, got {token}")
        self.advance()
        return token

    def parse(self):
        stmts = []
        while self.peek() and self.peek().type != 'EOF':
            if self.peek().type == 'NEWLINE':
                self.advance()
                continue
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
        return stmts

    def parse_statement(self):
        token = self.peek()
        if token.type == 'ID':
            if token.value == 'def':
                return self.parse_function()
            elif token.value == 'print':
                return self.parse_print()
            elif token.value == 'if':
                return self.parse_if()
            elif token.value == 'else':
                return None
            elif token.value == 'while':
                return self.parse_while()
            elif token.value == 'for':
                return self.parse_for()
            else:
                next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                if next_token and next_token.type == 'OP' and next_token.value == '=':
                    return self.parse_assignment()
                else:
                    return {'type': 'expr', 'expr': self.parse_expression()}
        elif token.type == 'NEWLINE':
            self.advance()
            return None
        else:
            raise SyntaxError(f"Unexpected token {token}")

    def parse_function(self):
        self.expect('ID', 'def')
        name = self.expect('ID').value
        self.expect('LPAREN')
        params = []
        if self.peek().type != 'RPAREN':
            while True:
                params.append(self.expect('ID').value)
                if self.peek().type == 'COMMA':
                    self.advance()
                else:
                    break
        self.expect('RPAREN')
        self.expect('COLON')
        body = self.parse_block()
        return {'type': 'function', 'name': name, 'params': params, 'body': body}

    def parse_print(self):
        self.expect('ID', 'print')
        self.expect('LPAREN')
        args = []
        while True:
            expr = self.parse_expression()
            args.append(expr)
            if self.peek().type == 'COMMA':
                self.advance()
            else:
                break
        self.expect('RPAREN')
        return {'type': 'print', 'args': args}

    def parse_assignment(self):
        var_token = self.expect('ID')
        self.expect('OP', '=')
        expr = self.parse_expression()
        return {'type': 'assign', 'var': var_token.value, 'expr': expr}

    def parse_expression(self):
        return self.parse_binary_expr()

    def parse_primary(self):
        token = self.peek()
        if token.type == 'ID':
            name = self.expect('ID').value
            if self.peek().type == 'LPAREN':
                self.expect('LPAREN')
                args = []
                if self.peek().type != 'RPAREN':
                    while True:
                        args.append(self.parse_expression())
                        if self.peek().type == 'COMMA':
                            self.advance()
                        else:
                            break
                self.expect('RPAREN')
                return {'type': 'call', 'name': name, 'args': args}
            return {'type': 'var', 'value': name}
        elif token.type == 'STRING':
            return {'type': 'string', 'value': self.expect('STRING').value.strip('"')}
        elif token.type == 'NUMBER':
            return {'type': 'number', 'value': self.expect('NUMBER').value}
        elif token.type == 'LPAREN':
            self.expect('LPAREN')
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        elif token.type == 'UNKNOWN' and token.value == '[':
            self.expect('UNKNOWN', '[')
            elements = []
            while self.peek().value != ']':
                elements.append(self.parse_expression())
                if self.peek().type == 'COMMA':
                    self.advance()
            self.expect('UNKNOWN', ']')
            return {'type': 'list', 'elements': elements}
        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")

    def parse_binary_expr(self, min_precedence=1):
        left = self.parse_primary()
        precedence = {'*':3, '/':3, '+':2, '-':2,
                      '==':1, '!=':1, '<=':1, '>=':1, '<':1, '>':1}
        while True:
            token = self.peek()
            if token.type == 'OP' and token.value in precedence and precedence[token.value] >= min_precedence:
                op = token.value
                op_prec = precedence[op]
                self.advance()
                right = self.parse_binary_expr(op_prec + 1)
                left = {'type': 'binop', 'op': op, 'left': left, 'right': right}
            else:
                break
        return left

    def parse_block(self):
        stmts = []
        while self.peek() and self.peek().type != 'EOF':
            if self.peek().type == 'ID' and self.peek().value == 'else':
                break
            if self.peek().type == 'NEWLINE':
                self.advance()
                continue
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
        return stmts

    def parse_if(self):
        self.expect('ID', 'if')
        condition = self.parse_expression()
        self.expect('COLON')
        body = self.parse_block()
        else_body = None
        if self.peek() and self.peek().type == 'ID' and self.peek().value == 'else':
            self.expect('ID', 'else')
            self.expect('COLON')
            else_body = self.parse_block()
        return {'type': 'if', 'condition': condition, 'body': body, 'else': else_body}

    def parse_while(self):
        self.expect('ID', 'while')
        condition = self.parse_expression()
        self.expect('COLON')
        body = self.parse_block()
        return {'type': 'while', 'condition': condition, 'body': body}

    def parse_for(self):
        self.expect('ID', 'for')
        var_token = self.expect('ID')
        self.expect('ID', 'in')
        if self.peek().type == 'ID' and self.peek().value == 'range':
            self.expect('ID', 'range')
            self.expect('LPAREN')
            num_token = self.expect('NUMBER')
            self.expect('RPAREN')
            self.expect('COLON')
            body = self.parse_block()
            return {'type': 'for', 'var': var_token.value, 'range': int(num_token.value), 'body': body}
        else:
            list_name = self.expect('ID').value
            self.expect('COLON')
            body = self.parse_block()
            return {'type': 'foreach', 'var': var_token.value, 'list': list_name, 'body': body}
