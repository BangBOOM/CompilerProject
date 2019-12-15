from collections import namedtuple

class AsmCodeGen:
    qtx=namedtuple('qtx','val actInfo')
    op2asm={
        '+':'ADD',
        '-':'SUB',
        '*':'MUL',
        '/':'DIV',
        '<':'LT',
        '>':'GT',
        '>=':'GTE',
        '<=':'LTE',
        '==':'EQ',
    }
    id=0
    def __init__(self,sym,allCode):
        self.symTable=sym       #符号表传入
        self.allCode=allCode    #优化后的代码传入
        for funcBlock in self.allCode:
            self.getAsm(funcBlock)

    def getAsm(self,funcBlock):
        '''
        函数块目标代码生成
        :param funcBlock:划分基本块后的函数块
        :return:
        '''

        def LD(x):
            return "LD R,%s"%(x.val)
        def DOP(x,y):
            return "%s R,%s"%(x,y.val)
        def ST(x):
            return "ST R,%s"%(x.val)

        asmCode=[]  #生成的目标代码
        ifJumpStack=[]
        for bloc in funcBlock:
            self.actInfoGen(bloc)
            RDL=None
            codes=[]
            for item in bloc:
                if item[0].val in list(self.op2asm.keys()): #双目运算
                    w=self.op2asm[item[0].val]
                    if RDL==None:
                        codes.append(LD(item[1]))
                        codes.append(DOP(w,item[2]))
                    else:
                        if RDL.actInfo:
                            codes.append(ST(RDL))
                        elif RDL==item[1]:
                            codes.append(DOP(w,item[2]))
                        elif RDL==item[2] and w in ['+','*','==']:
                            codes.append(DOP(w,item[1]))
                        else:
                            codes.append(LD(item[1]))
                            codes.append(DOP(w, item[2]))
                    RDL=item[-1]

                elif item[0].val=='=':
                    if RDL==None:
                        codes.append(LD(item[1]))
                    else:
                        if RDL.actInfo:
                            codes.append(ST(RDL))
                        if RDL!=item[1] and RDL!=item[-1]:
                            codes.append(LD(item[1]))
                    RDL=item[-1]

                elif item[0].val=='if' or item[0].val=='elif' or item[0].val=='do':
                    if RDL==None:
                        codes.append(LD(item[1]))
                    else:
                        if RDL.actInfo:
                            codes.append(ST(RDL))
                        if RDL!=item[1]:
                            codes.append(LD(item[1]))
                    codes.append("FJ R,")
                    ifJumpStack.append(len(codes) - 1)  # 将跳转指令的index传入
                    RDL=None
                elif item[0].val=='el':
                    if RDL and RDL.actInfo:
                        codes.append(ST(RDL))
                    codes.append('next'+str(self.id)+':')
                    self.id+=1
                elif item[0].val=='ie':
                    if RDL and RDL.actInfo:
                        codes.append(ST(RDL))
                    codes.append('next' + str(self.id) + ':')
                    self.id += 1
                elif item[0].val=='wh':
                    codes.append('next' + str(self.id) + ':')
                    self.id += 1
                elif item[0].val=='we':
                    codes.append('next' + str(self.id) + ':')
                    self.id += 1

            print(codes)









    def actInfoGen(self,bloc):
        '''
        传入代码块添加活跃信息
        :param bloc:
        :return:
        '''
        actTable = {}
        for tmp in bloc:
            for item in tmp[1:]:
                if item=='_' or item.isdigit():
                    continue
                if item[0]=='@':   #临时变量
                    actTable[item]=False
                elif item not in self.symTable.functionNameList:    #标识符且不是函数名称
                    actTable[item]=True
        for tmp in bloc[::-1]:  #倒序标注活跃信息  qtx=namedtuple('qtx','val actInfo') 使用这个具名元组 不具备活跃信息的actInfo=None
            demo=None
            if tmp[-1]=='_':
                demo=self.qtx(tmp[-1],None)
            elif tmp[-1]!='_':
                demo=self.qtx(tmp[-1],actInfo=actTable[tmp[-1]])
                actTable[tmp[-1]]=False
            tmp[-1]=demo
            if tmp[-2]=='_' or tmp[-2].isdigit():
                demo=self.qtx(tmp[-2],None)
            elif tmp[-2]!='_' and not tmp[-2].isdigit():
                demo=self.qtx(tmp[-2],actInfo=actTable[tmp[-2]])
            tmp[-2]=demo
            if tmp[-3]=='_' or tmp[-3].isdigit() or tmp[-3] in self.symTable.functionNameList:
                demo=self.qtx(tmp[-3],None)
            elif tmp[-3]!='_' and not tmp[-3].isdigit() and tmp[-3] not in self.symTable.functionNameList:
                demo=self.qtx(tmp[-3],actInfo=actTable[tmp[-3]])
                actTable[tmp[-3]]=True
            tmp[-3]=demo
            if tmp[-2].actInfo!=None:
                actTable[tmp[-2].val]=True
            tmp[0]=self.qtx(tmp[0],None)
        # for x in bloc:
        #     for y in x:
        #         print(y)
        #     print('-'*20)
        # print('*'*20)



from grammar import LL1
from qt_gen import QtGen
from optimization import Optimization
import os
if __name__=='__main__':
    grammar_path = os.path.abspath('grammar_static/c_like_grammar')
    path = os.path.abspath('c_input')
    with open(path, 'r', encoding='utf-8') as f:
        INPUT = f.readlines()
    ll1 = LL1(grammar_path, True)
    ll1.getInput(INPUT)
    res = ll1.analyzeInputString()
    qt = QtGen()
    if res == 'acc':
        for block in ll1.funcBlocks:
            qt.genQt(block)
        op = Optimization(ll1.syn_table)
        qtLists=qt.qt_res   #按照函数分成的大块
        qtListAfterOpt=[]   #基于函数块再其内部划分更小的块
        for item in qtLists:
            qtListAfterOpt.append(op.opt(item))
        # for item in qtListAfterOpt:
        #     for i in item:
        #         print(i)
        #     print('_'*40)
        # print(qtListAfterOpt)
        asm=AsmCodeGen(ll1.syn_table,qtListAfterOpt)


    else:
        print(res)
    ll1.syn_table.showTheInfo()









