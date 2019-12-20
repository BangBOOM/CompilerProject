from grammar import LL1
from qt_gen import QtGen
from optimization import Optimization
from asm_gen_x import AsmCodeGen
import os,copy
class CCompiler:
    def __init__(self):
        self.grammar_path = os.path.abspath('grammar_static/c_like_grammar')
    def getInputFromWebAndAnalyze(self,INPUT):
        ll1 = LL1(self.grammar_path)
        ll1.getInput(INPUT)
        res=ll1.analyzeInputString()
        if res[0]=='acc':
            qt=QtGen(ll1.syn_table)
            for block in ll1.funcBlocks:
                qt.genQt(block)
            op=Optimization(ll1.syn_table)
            qtLists=qt.qt_res
            qtbf=copy.deepcopy(qtLists)
            # for item in qtLists:
            #     for i in item:
            #         print(i)
            qtListAfterOpt=[]
            for item in qtLists:    #基本块划分并优化
                qtListAfterOpt.append(op.opt(item))
            qtaf=copy.deepcopy(qtListAfterOpt)
            # print("\n")
            # for item in qtListAfterOpt:
            #     for i in item:
            #         for x in i:
            #             print(x)
            #         print('\n')
            asm=AsmCodeGen(ll1.syn_table,qtListAfterOpt)
            asm_code=asm.allAsmCode
            return {
                'state':res,
                'sym':ll1.syn_table.symbolTableInfo,
                'qtbf':qtbf,
                'qtaf':qtaf,
                'asm':asm_code
            }
        else:
            return res

if __name__=="__main__":
    path = os.path.abspath('c_input')
    with open(path, 'r', encoding='utf-8') as f:
        INPUT = f.readlines()
    cc=CCompiler()
    res=cc.getInputFromWebAndAnalyze(INPUT)
    for item in res['sym']:
        print(item)
    for item in res['qtbf']:
        for i in item:
            print(i)

    print('\n')
    for item in res['qtaf']:
        for i in item:
            for x in i:
                print(x)
    print('\n')

    for item in res['asm']:
        print(item)



