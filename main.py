from grammar import LL1
from qt_gen import QtGen
import os


if __name__ == '__main__':
    grammar_path = os.path.abspath('grammar_static/c_like_grammar')
    path=os.path.abspath('c_input')
    with open(path,'r',encoding='utf-8') as f:
        INPUT=f.readlines()
    ll1=LL1(grammar_path)
    ll1.getInput(INPUT)
    res=ll1.analyzeInputString()
    if res=='acc':
        qt=QtGen()
        for block in ll1.funcBlocks:
            res=qt.genQt(block)
            print(res)





