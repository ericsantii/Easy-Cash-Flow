import ply.lex as lex

reserved = {'create': 'CREATE', 'earn': 'EARN', 'lose': 'LOSE', 'remove': 'REMOVE', 'display': 'DISPLAY',
            'length': 'LENGTH', 'combine': 'COMBINE', 'substract': 'SUBSTRACT', 'pw': 'PW',
            'fw': "FW", 'cfd': 'CFD'
            }

# List of token names.
tokens = [
             'EMPTY',
             'LPAREN',
             'RPAREN',
             'EQUAL',
             'RANGE',
             'INTEGER',
             'FLOAT',
             'ID',
             'COMMA',
         ] + list(reserved.values())

# Regular expression rules for simple tokens
t_EMPTY = r'\n'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUAL = r'\='
t_COMMA = r'\,'


# A regular expression for non-reserved words
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_VAR(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'VAR')
    return t


# A regular expression rule with some action code
def t_RANGE(t):
    r'\d+\:\d+'
    t.value = reserved.get(t.value, 'RANGE')
    return t


def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()
