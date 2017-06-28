import cashflow_tools as cft
import ply.yacc as yac
from ecf_lex import tokens

memory = {}



def p_action(p):
    '''
    action : fuction_earn
            | fuction_lose
            | fuction_remove
            | fuction_pw
            | fuction_fw
            | fuction_display
            | fuction_length
            | variable
            | EMPTY

    '''


def p_fuction_earn(p):
    '''
    fuction_earn : EARN LPAREN FLOAT COMMA INTEGER COMMA ID RPAREN
                | EARN LPAREN INTEGER COMMA INTEGER COMMA ID RPAREN
    '''
    memory.get(p[7])[p[5]] += p[3]


def p_fuction_lose(p):
    '''
    fuction_lose : LOSE LPAREN FLOAT COMMA INTEGER COMMA ID RPAREN
                | LOSE LPAREN INTEGER COMMA INTEGER COMMA ID RPAREN
    '''
    memory.get(p[7])[p[5]] += -p[3]


def p_fuction_remove(p):
    '''
    fuction_remove : REMOVE LPAREN INTEGER COMMA ID RPAREN
    '''
    memory.get(p[5])[p[3]] = 0


def p_fuction_pw(p):
    '''
    fuction_pw : PW LPAREN FLOAT COMMA INTEGER COMMA ID RPAREN
                | PW LPAREN INTEGER COMMA INTEGER COMMA ID RPAREN
    '''
    cft.pv(p[3], p[5], memory.get(p[7]))


def p_fuction_fw(p):
    '''
    fuction_fw : FW LPAREN FLOAT COMMA INTEGER COMMA ID RPAREN
                | FW LPAREN INTEGER COMMA INTEGER COMMA ID RPAREN
    '''
    cft.fw(p[3], p[5], memory.get(p[7]))


def p_fuction_display(p):
    '''
    fuction_display : DISPLAY LPAREN ID RPAREN
    '''
    hi = cft.cashflow(memory.get(p[3]))
    cft.cfloplot(hi)


def p_fuction_length(p):
    '''
    fuction_length : LENGTH LPAREN ID RPAREN
    '''
    print("The length of the cash flow is", len(memory.get(p[3])))


def p_variable_combine(p):
    '''
    variable_combine : COMBINE LPAREN ID COMMA ID RPAREN
    '''
    p[0] = cft.combine(memory.get(p[3]), memory.get(p[5]))


def p_variable_substract(p):
    '''
    variable_substract : SUBSTRACT LPAREN ID COMMA ID RPAREN
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
                | CFD ID EQUAL variable_substract


    '''
    memory[p[2]] = p[4]




parser = yac.yacc()
