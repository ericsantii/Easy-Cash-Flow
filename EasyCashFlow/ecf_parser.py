import cashflow_tools as cft
import ply.yacc as yac
from ecf_lex import tokens

memory = {}



def p_action(p):
    '''
    action : function_earn
            | function_lose
            | function_remove
            | function_pw
            | function_fw
            | function_display
            | function_length
            | variable
            | EMPTY

    '''


def p_function_earn(p):
    '''
    function_earn : EARN LPAREN FLOAT COMMA INTEGER COMMA ID RPAREN
                | EARN LPAREN INTEGER COMMA INTEGER COMMA ID RPAREN
    '''
    memory.get(p[7])[p[5]] += p[3]


def p_function_lose(p):
    '''
    function_lose : LOSE LPAREN FLOAT COMMA INTEGER COMMA ID RPAREN
                | LOSE LPAREN INTEGER COMMA INTEGER COMMA ID RPAREN
    '''
    memory.get(p[7])[p[5]] += -p[3]


def p_function_remove(p):
    '''
    function_remove : REMOVE LPAREN INTEGER COMMA ID RPAREN
    '''
    memory.get(p[5])[p[3]] = 0


def p_function_pw(p):
    '''
    function_pw : PW LPAREN FLOAT COMMA INTEGER COMMA ID RPAREN
                | PW LPAREN INTEGER COMMA INTEGER COMMA ID RPAREN
    '''
    cft.pv(p[3], p[5], memory.get(p[7]))


def p_function_fw(p):
    '''
    function_fw : FW LPAREN FLOAT COMMA INTEGER COMMA ID RPAREN
                | FW LPAREN INTEGER COMMA INTEGER COMMA ID RPAREN
    '''
    cft.fw(p[3], p[5], memory.get(p[7]))


def p_function_display(p):
    '''
    function_display : DISPLAY LPAREN ID RPAREN
    '''
    hi = cft.cashflow(memory.get(p[3]))
    cft.cfloplot(hi)


def p_function_length(p):
    '''
    function_length : LENGTH LPAREN ID RPAREN
    '''
    print("The length of the cash flow is", len(memory.get(p[3])))


def p_variable_combine(p):
    '''
    variable_combine : COMBINE LPAREN ID COMMA ID RPAREN
    '''
    p[0] = cft.combine(memory.get(p[3]), memory.get(p[5]))


def p_variable_subtract(p):
    '''
    variable_subtract : SUBTRACT LPAREN ID COMMA ID RPAREN
    '''
    p[0] = cft.substract(memory.get(p[3]), memory.get(p[5]))


def p_variable_create(p):
    '''
    variable_create : CREATE LPAREN INTEGER RPAREN
    '''
    p[0] = cft.startPlot(p[3])


def p_variable(p):
    '''
    variable : CFD ID EQUAL variable_create
                | CFD ID EQUAL variable_combine
                | CFD ID EQUAL variable_subtract


    '''
    memory[p[2]] = p[4]




parser = yac.yacc()
