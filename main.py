from grammar import LL1
from qt_gen import QtGen
from optimization import Optimization
import os


if __name__ == '__main__':
    grammar_path = os.path.abspath('grammar_static/c_like_grammar')
    path=os.path.abspath('c_input')
    with open(path,'r',encoding='utf-8') as f:
        INPUT=f.readlines()
    ll1=LL1(grammar_path,True)
    ll1.getInput(INPUT)
    res=ll1.analyzeInputString()
    qt = QtGen(ll1.syn_table)
    op=Optimization(ll1.syn_table)
    if res=='acc':
        for block in ll1.funcBlocks:    #block是一个函数块
            qt.genQt(block)

        for block in qt.qt_res:        #block是一个函数块
            block=op.opt(block)
            # for i in block:            #i是一条四元式
            #     for x in i:
            #         print(x)
            #     print('\n')
            # print("\n\n")
        ll1.syn_table.showTheInfo()

