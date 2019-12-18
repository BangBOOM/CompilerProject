from collections import namedtuple

class AsmCodeGen:
    qtx=namedtuple('qtx','val actInfo')
    op2asm={
        '+':'ADD',
        '-':'SUB',
        '*':'MUL',
        '/':'DIV',
        '<':'JAE',
        '>':'JBE',
        '>=':'JB',
        '<=':'JA',
        '==':'JNE',
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
            if x.val in ['<','<=','>','>=','==']:
                return ["CMP R,%s"%(y.val),"%s "%self.op2asm[x.val]]
            else:
                return ["%s R,%s"%(self.op2asm[x.val],y.val)]
        def ST(x):
            return "ST R,%s"%(x.val)

        asmCode=[]          #生成的目标代码
        #记录↓
        startOfWhile=[]     #记录while语句开始地址
        judgeOfWhile=[]     #记录while中判断句的位置待填写跳转信息
        judgeOfIf=[]        #记录if判断句的位置待填写跳转信息
        jmpToEnd=[]         #记录if跳转到结束的位置跳转信息待填

        for bloc in funcBlock:
            self.actInfoGen(bloc)

            RDL=None
            codes=[]
            for i,item in enumerate(bloc):
                if item[0].val in list(self.op2asm.keys()): #双目运算
                    if RDL==None:
                        codes.append(LD(item[1]))
                        codes+=DOP(item[0],item[2])
                    else:
                        if RDL.actInfo:
                            codes.append(ST(RDL))
                        if RDL==item[1]:
                            codes+=DOP(item[0],item[2])
                        elif RDL==item[2] and item[0].val in ['+','*','==']:
                            codes+=DOP(item[0],item[1])
                        else:
                            codes.append(LD(item[1]))
                            codes+=DOP(item[0], item[2])
                    if item[0].val in  ['<','<=','>','>=','==']:
                        if codes[0].startswith("while") :
                            judgeOfWhile.append((len(asmCode),len(codes)-1))
                        else:
                            judgeOfIf.append((len(asmCode),len(codes)-1))
                    RDL=item[-1]
                elif item[0].val=='=':
                    if RDL==None:
                        codes.append(LD(item[1]))
                    else:
                        if RDL.actInfo:
                            codes.append(ST(RDL))
                        if RDL!=item[1] and RDL!=item[-1]:
                            codes.append(LD(item[1]))
                    codes.append(ST(item[-1]))
                    RDL=None

                elif item[0].val=='continue':
                    if RDL and RDL.actInfo:
                        codes.append(ST(RDL))
                    codes.append('JMP '+startOfWhile[-1])
                elif item[0].val=='el':
                    if RDL and RDL.actInfo:
                        codes.append(ST(RDL))
                    codes.append('JMP ')
                    jmpToEnd.append((len(asmCode),len(codes)-1))
                    codes.append('next'+str(self.id)+':')
                    x,y=judgeOfIf.pop()
                    # print("="*20)
                    # print(x,y)
                    # print(asmCode)
                    asmCode[x][y] += 'next' + str(self.id)
                    self.id+=1
                elif item[0].val=='ie':
                    if RDL and RDL.actInfo:
                        codes.append(ST(RDL))
                    codes.append('endif' + str(self.id) + ':')
                    while jmpToEnd:
                        x,y=jmpToEnd.pop()
                        asmCode[x][y]+='endif' + str(self.id)
                    self.id += 1
                elif item[0].val=='wh':
                    codes.append('while' + str(self.id) + ':')
                    startOfWhile.append('while' + str(self.id))
                    self.id += 1
                elif item[0].val=='we':
                    tgt=startOfWhile.pop()
                    codes.append('JMP '+tgt)
                    codes.append('endWhile' + str(self.id) + ':')
                    x,y=judgeOfWhile.pop()
                    asmCode[x][y]+='endWhile' + str(self.id)
                    self.id += 1
                elif item[0].val=='return':
                    if RDL!=item[1]:
                        codes.append(LD(item[1]))
                    codes.append("RET")
                elif item[0].val=='FUN':
                    codes.append(item[1].val+':')
                elif item[0].val=='push':
                    if RDL==None:
                        codes.append(LD(item[1]))
                    elif RDL!=item[0]:
                        codes.append(ST(RDL))
                        codes.append(LD(item[1]))
                    codes.append("PUSH R")
                elif item[0].val=='call':
                    codes.append("CALL %s"%item[1].val)
                elif item[0].val=='callr':
                    codes.append("CALL %s"%item[1].val)
                    codes.append(ST(item[-1]))

            asmCode.append(codes)
            # for c in codes:
            #     print(c)
            # print('\n')

        for item in asmCode:
            for i in item:
                print(i)



    def actInfoGen(self,bloc):
        '''
        传入代码块添加活跃信息，同时基于符号表填写临时变量的偏移地址
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
        # print(actTable)
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
        # print('\n\n')



from grammar import LL1
from qt_gen import QtGen
from optimization import Optimization
import os
if __name__=='__main__':
    grammar_path = os.path.abspath('grammar_static/c_like_grammar')
    path = os.path.abspath('c_input')
    with open(path, 'r', encoding='utf-8') as f:
        INPUT = f.readlines()
    ll1 = LL1(grammar_path)
    ll1.getInput(INPUT)
    res = ll1.analyzeInputString()
    qt = QtGen(ll1.syn_table)
    if res == 'acc':
        for block in ll1.funcBlocks:
            qt.genQt(block)
        op = Optimization(ll1.syn_table)
        qtLists=qt.qt_res   #按照函数分成的大块
        qtListAfterOpt=[]   #基于函数块再其内部划分更小的块
        for item in qtLists:
            qtListAfterOpt.append(op.opt(item))
        for item in qtListAfterOpt:
            for i in item:
                for b in i: #i是基本块
                    print(b)
                print('\n')
            print('-'*30)

        asm=AsmCodeGen(ll1.syn_table,qtListAfterOpt)
        ll1.syn_table.showTheInfo()
    else:
        print(res)



'''
函数中:
I:
ID.X=10这种情况其中ID是函数的参数且是定义的结构体，这种情况往函数中传的是地址
MOV BX , SS:[BP-XX] #XX是ID的参数相对函数的偏移地址在栈中
MOV AX , 10
MOV DS:[BX+XX] , AX #XX是结构体中变量的偏移地址在内存中
若ID是函数中定义的结构体变量
MOV AX , 10
MOV SS:[BP+IDX+XX] , AX

II:
VAR=ID.X 这种情况VAR是函数中的变量 ID是参数结构体
MOV BX , SS:[BP-XX]
MOV AX , DS:[BX+XX]
MOV SS:[BP+XX] , AX
若ID是函数中的变量
MOV AX , SS:[BP+IDX+XX]
MOV SS:[BP+XX] , AX

III:
FUN(ID) 这种情况调用函数ID是结构体
MOV AX , OFFSET ID
PUSH AX

'''















