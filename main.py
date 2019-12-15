from grammar import LL1
from qt_gen import QtGen
from optimization import Optimization
# from asm_gen import AsmCodeGen
from asm_gen_x import AsmCodeGen
import os


if __name__ == '__main__':
    grammar_path = os.path.abspath('grammar_static/c_like_grammar')
    path=os.path.abspath('c_input')
    with open(path,'r',encoding='utf-8') as f:
        INPUT=f.readlines()
    ll1=LL1(grammar_path,True)
    ll1.getInput(INPUT)
    res=ll1.analyzeInputString()
    qt = QtGen()
    asm=AsmCodeGen(ll1.syn_table)
    if res=='acc':
        for block in ll1.funcBlocks:
            qt_list=qt.genQt(block)
            # print("四元式：")
            # for item in qt_list:
            #     print(item)
            # print('-'*25)
        op = Optimization(qt.qt_res, ll1.syn_table)
        for b in op.qtLists:
            tmp=op.opt(b)   #划分基本块
            for t in tmp:
                asm.actInfoGen(t)
            # asm.getAsm(tmp)
    else:
        print(res)
    ll1.syn_table.showTheInfo()

