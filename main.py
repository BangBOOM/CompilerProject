from lexer import Lexer
from grammar import LL1
import os
if __name__ == '__main__':
    lex=Lexer()
    grammar_path = os.path.abspath('grammar_static/c_like_grammar')
    path=os.path.abspath('c_input')
    with open(path,'r',encoding='utf-8') as f:
        INPUT=[l.strip('\n') for l in f.readlines()]
    ll1=LL1(grammar_path)
    ll1.getInput(INPUT)
    res=ll1.analyzeInputString()
    print(res)





