from collections import namedtuple
import re

class AsmCodeGen:
    qtx = namedtuple('qtx', 'val actInfo addr1 addr2 dosePointer ')  # 变量名 活跃信息 一级地址相对于函数 二级地址相对于结构体数组 是否是指针
    op2asm = {
        '+': 'ADD',
        '-': 'SUB',
        '*': 'MUL',
        '/': 'DIV',
        '<': 'JAE',
        '>': 'JBE',
        '>=': 'JB',
        '<=': 'JA',
        '==': 'JNE',
    }
    id = 0

    def __init__(self, sym, allCode):
        self.symTable = sym  # 符号表传入
        self.allCode = allCode  # 优化后的代码传入
        self.allAsmCode=[]     # 目标代码的头部
        self.funcsAsmCode=[]    # 所有函数块的目标代码
        self.mainAsmCode=[]        # 主函数目标代码
        for funcBlock in self.allCode:
            self.getAsm(funcBlock)
        self.getAll()
        # for item in self.allAsmCode:
        #     print(item)


    def getAll(self):
        for struct in self.symTable.structList:
            self.allAsmCode.append("%s STRUCT"%struct.structName)
            for k,v in struct.variableDict.items():
                if v.type=='int':
                    self.allAsmCode.append("%s dw ?"%k)
                if v.type=='array':
                    n,m=k.split('[')
                    m,_=m.split(']')
                    self.allAsmCode.append("%s dw %s DUP (0)"%(n,m))
            self.allAsmCode.append("%s ENDS"%struct.structName)
        self.allAsmCode.append("DSEG SEGMENT")
        mainSYM=self.symTable.symDict['main']
        for k,v in mainSYM.variableDict.items():
            if v.type=='int':
                self.allAsmCode.append("%s dw ?"%k)
            elif v.type == 'array':
                n, m = k.split('[')
                m, _ = m.split(']')
                self.allAsmCode.append("%s dw %s DUP (0)" % (n, m))
            else:
                self.allAsmCode.append("%s %s <?>"%(k,v.type))
        self.allAsmCode.append("DSEG ENDS")
        self.allAsmCode+=[
            "SSEG SEGMENT STACK",
            "STK DB	40 DUP (0)",
            "SSEG ENDS",
        ]
        self.allAsmCode+=[
            "CSEG SEGMENT",
            "ASSUME CS:CSEG,DS:DSEG,SS:SSEG"
        ]
        for res in self.mainAsmCode:
            for item in res:
                for i in item:
                    self.allAsmCode.append(i)
        for res in self.funcsAsmCode:
            for item in res:
                for i in item:
                    self.allAsmCode.append(i)


    def getAsm(self, funcBlock):

        '''
        函数块目标代码生成
        :param funcBlock:划分基本块后的函数块
        :return:
        '''
        funcName = funcBlock[0][0][1]
        if funcName != 'main':  #函数部分的目标代码生成
            for bloc in funcBlock:  #对所有代码块添加活跃信息
                self.actFunInfoGen(bloc, funcName)
            res=self.genFunAsm(funcBlock, funcName)
            self.funcsAsmCode.append(res)
            '''打印一个函数的目标代码'''
            # for item in res:
            #     for i in item:
            #         print(i)
                # print('\n')
        else:   #主函数目标代码
            '''主函数中的变量会添加到DATA段临时变量会放入栈中'''
            for bloc in funcBlock:
                self.actFunInfoGen(bloc,funcName)
            res=self.genMainAsm(funcBlock,funcName)
            self.mainAsmCode.append(res)



    def genMainAsm(self,funcBlock,funcName):
        '''
        生成主函数的目标代码
        '''
        funcTable=self.symTable.symDict[funcName]
        def LD(x):
            res=[]
            if x.val in list(funcTable.variableDict.keys()):    #特殊情况传地址的时候使用
                if funcTable.variableDict[x.val].type in self.symTable.structNameList:
                    res.append("MOV AX,OFFSET %s"%x.val)
                    return res

            if x.val.isdigit():  # x是立即数
                res.append("MOV AX,%s" % x.val)
            elif x.val.startswith('@'):
                res.append("MOV AX,SS:[BP-%d]"%x.addr1)
            elif '[' in x.val:
                t,n=x.split('[')
                n,_=n.split(']')
                n=eval(n)
                res.append("MOV BX,OFFSET %s"%t)
                res.append("MOV AX,DS:[BX+%d]"%(n*2))
            else:
                res.append("MOV AX,%s"%x.val)
            return res

        def ST(x):
            res=[]
            if x.val.startswith('@'):
                res.append("MOV SS:[BP-%d],AX" % x.addr1)
            elif '[' in x.val:
                t, n = x.val.split('[')
                n, _ = n.split(']')
                n = eval(n)
                res.append("MOV BX,OFFSET %s" % t)
                res.append("MOV DS:[BX+%d],AX" % (n * 2))
            else:
                res.append("MOV %s,AX" % x.val)
            return res


        def DOP(x,y):
            res=[]
            if x.val in ['<', '<=', '>', '>=', '==']:
                if y.val.isdigit():
                    res.append("CMP AX,%s" % y.val)
                elif '[' in y.val:
                    t, n = y.split('[')
                    n, _ = n.split(']')
                    n = eval(n)
                    res.append("MOV BX,OFFSET %s" % t)
                    res.append("CMP AX,DS:[BX+%d]" %(n*2))
                else:
                    res.append("CMP AX,%s"%y.val)
                res.append("%s " % self.op2asm[x.val])

            elif x.val in ['+','-']:
                if y.val.isdigit():
                    res.append("%s AX,%s" % (self.op2asm[x.val], y.val))
                elif '[' in y.val:
                    t, n = y.split('[')
                    n, _ = n.split(']')
                    n = eval(n)
                    res.append("MOV BX,OFFSET %s" % t)
                    res.append("%s AX,DS:[BX+%d]" %(self.op2asm[x.val],n*2))
                else:
                    res.append("%s AX,%s"%(self.op2asm[x.val],y.val))
            elif x.val in ['*','/']:
                if y.val.isdigit():
                    res.append("%s %s" % (self.op2asm[x.val], y.val))
                elif '[' in y.val:
                    t, n = y.split('[')
                    n, _ = n.split(']')
                    n = eval(n)
                    res.append("MOV BX,OFFSET %s" % t)
                    res.append("%s DS:[BX+%d]" %(self.op2asm[x.val],n*2))
                else:
                    res.append("%s %s"%(self.op2asm[x.val],y.val))

            return res

        asmCode = []  # 生成的目标代码
        # 记录↓
        startOfWhile = []  # 记录while语句开始地址
        judgeOfWhile = []  # 记录while中判断句的位置待填写跳转信息
        judgeOfIf = []  # 记录if判断句的位置待填写跳转信息
        jmpToEnd = []  # 记录if跳转到结束的位置跳转信息待填
        for bloc in funcBlock:
            RDL = None
            codes = []
            for i, item in enumerate(bloc):
                if item[0].val in list(self.op2asm.keys()):  # 是运算符
                    if RDL == None:
                        codes += LD(item[1])
                        codes += DOP(item[0], item[2])
                    else:
                        if RDL.actInfo:
                            codes += ST(RDL)
                        if RDL == item[1]:
                            codes += DOP(item[0], item[2])
                        elif RDL == item[2] and item[0].val in ['+', '*', '==']:
                            codes += DOP(item[0], item[1])
                        else:
                            codes += LD(item[1])
                            codes += DOP(item[0], item[2])
                    if item[0].val in ['<', '<=', '>', '>=', '==']:
                        if codes[0].startswith("while"):
                            judgeOfWhile.append((len(asmCode), len(codes) - 1))
                        else:
                            judgeOfIf.append((len(asmCode), len(codes) - 1))
                    RDL = item[-1]

                elif item[0].val == '=':
                    if RDL == None:
                        codes += LD(item[1])
                    elif RDL == item[1]:
                        codes += ST(item[1])
                    elif RDL != item[1] and RDL != item[-1]:
                        if RDL.actInfo:
                            codes += ST(RDL)
                        codes += LD(item[1])
                    RDL = item[-1]
                elif item[0].val == 'continue':
                    if RDL and RDL.actInfo:
                        codes += ST(RDL)
                    codes.append('JMP ' + startOfWhile[-1])
                elif item[0].val == 'el':
                    if RDL and RDL.actInfo:
                        codes += ST(RDL)
                    codes.append('JMP ')
                    jmpToEnd.append((len(asmCode), len(codes) - 1))
                    codes.append('next' + str(self.id) + ':')
                    x, y = judgeOfIf.pop()
                    asmCode[x][y] += 'next' + str(self.id)
                    self.id += 1
                elif item[0].val == 'ie':
                    if RDL and RDL.actInfo:
                        codes += ST(RDL)
                    codes.append('endif' + str(self.id) + ':')
                    while jmpToEnd:
                        x, y = jmpToEnd.pop()
                        asmCode[x][y] += 'endif' + str(self.id)
                    self.id += 1
                elif item[0].val == 'wh':
                    codes.append('while' + str(self.id) + ':')
                    startOfWhile.append('while' + str(self.id))
                    self.id += 1
                elif item[0].val == 'we':
                    tgt = startOfWhile.pop()
                    codes.append('JMP ' + tgt)
                    codes.append('endWhile' + str(self.id) + ':')
                    x, y = judgeOfWhile.pop()
                    asmCode[x][y] += 'endWhile' + str(self.id)
                    self.id += 1
                elif item[0].val == 'push':
                    if RDL == None:
                        codes += LD(item[1])
                    elif RDL != item[0]:
                        codes += ST(RDL)
                        codes += LD(item[1])
                    codes.append("PUSH AX")
                elif item[0].val == 'call':
                    codes.append("CALL %s" % item[1].val)
                elif item[0].val == 'callr':
                    codes.append("CALL %s" % item[1].val)
                    codes+= ST(item[-1])
                elif item[0].val == 'FUN':
                    codes.append("%s:" % item[1].val)
                    codes.append("MOV BP,SP")
                    codes.append("SUB SP,20")
                elif item[0].val == 'return':
                    if RDL:
                        if RDL != item[1]:
                            if RDL.actInfo:
                                codes += ST(RDL)
                            codes += LD(item[1])
                    codes.append("MOV SP,BP")
                    codes.append("MOV AX,4C00H")
                    codes.append("INT 21H")
                    codes.append("CSEG ENDS")
                    codes.append("END main")

            asmCode.append(codes)
        return asmCode


    def genFunAsm(self, funcBlock, funcName):
        '''
        生成函数部分的汇编代码
        '''

        def LD(x):
            res = []
            if x.val.isdigit():  # x是立即数
                res.append("MOV AX,%s" % x.val)
            elif x.dosePointer:  # x是结构体指针
                res.append("MOV BX,SS:[BP+%d]" % abs(x.addr1))
                res.append("MOV AX,DS:[BX+%d]" % x.addr2)
            else:
                if x.addr1 < 0:
                    res.append("MOV AX,SS:[BP+%d-%d]" % (abs(x.addr1), x.addr2))
                else:
                    res.append("MOV AX,SS:[BP-%d-%d]" % (x.addr1, x.addr2))
            return res

        def DOP(x, y):
            res = []
            if x.val in ['<', '<=', '>', '>=', '==']:
                if y.val.isdigit():
                    res.append("CMP AX,%s" % y.val)
                elif y.dosePointer:
                    res.append("MOV BX,SS:[BP+%d]" % abs(y.addr1))
                    res.append("CMP AX,DS:[BX+%d]" % y.addr2)
                else:
                    if y.addr1 < 0:
                        res.append("CMP AX,SS:[BP+%d-%d]" % (abs(y.addr1), y.addr2))
                    else:
                        res.append("CMP AX,SS:[BP-%d-%d]" % (y.addr1, y.addr2))
                res.append("%s "%self.op2asm[x.val])

            elif x.val in ['+', '-']:
                if y.val.isdigit():
                    res.append("%s AX,%s" % (self.op2asm[x.val], y.val))
                elif y.dosePointer:
                    res.append("MOV BX,SS:[BP+%d]" % abs(y.addr1))
                    res.append("%s AX,DS:[BX+%d]" % (self.op2asm[x.val], y.addr2))
                else:
                    if y.addr1 < 0:
                        res.append("%s AX,SS:[BP+%d-%d]" % (self.op2asm[x.val], abs(y.addr1), y.addr2))
                    else:
                        res.append("%s AX,SS:[BP-%d-%d]" % (self.op2asm[x.val], y.addr1, y.addr2))

            elif x.val in ['*', '/']:
                if y.val.isdigit():
                    res.append("%s %s" % (self.op2asm[x.val], y.val))
                elif y.dosePointer:
                    res.append("MOV BX,SS:[BP+%d]" % abs(y.addr1))
                    res.append("%s DS:[BX+%d]" % (self.op2asm[x.val], y.addr2))
                else:
                    if y.addr1 < 0:
                        res.append("%s SS:[BP+%d-%d]" % (self.op2asm[x.val], abs(y.addr1), y.addr2))
                    else:
                        res.append("%s SS:[BP-%d-%d]" % (self.op2asm[x.val], y.addr1, y.addr2))
            return res

        def ST(x):
            res = []
            if x.dosePointer:
                res.append("MOV BX,SS:[BP+%d]" % abs(x.addr1))
                res.append("MOV DS:[BX+%d],AX" % x.addr2)
            else:
                if x.addr1 < 0:
                    res.append("MOV SS:[BP+%d-%d],AX" % (abs(x.addr1), x.addr2))
                else:
                    res.append("MOV SS:[BP-%d-%d],AX" % (x.addr1, x.addr2))
            return res

        asmCode = []  # 生成的目标代码
        # 记录↓
        startOfWhile = []  # 记录while语句开始地址
        judgeOfWhile = []  # 记录while中判断句的位置待填写跳转信息
        judgeOfIf = []  # 记录if判断句的位置待填写跳转信息
        jmpToEnd = []  # 记录if跳转到结束的位置跳转信息待填
        for bloc in funcBlock:
            RDL = None
            codes = []
            for i, item in enumerate(bloc):
                if item[0].val in list(self.op2asm.keys()):  # 是运算符
                    if RDL == None:
                        codes += LD(item[1])
                        codes += DOP(item[0], item[2])
                    else:
                        if RDL.actInfo:
                            codes += ST(RDL)
                        if RDL == item[1]:
                            codes += DOP(item[0], item[2])
                        elif RDL == item[2] and item[0].val in ['+', '*', '==']:
                            codes += DOP(item[0], item[1])
                        else:
                            codes += LD(item[1])
                            codes += DOP(item[0], item[2])
                    if item[0].val in ['<', '<=', '>', '>=', '==']:
                        if codes[0].startswith("while"):
                            judgeOfWhile.append((len(asmCode), len(codes) - 1))
                        else:
                            judgeOfIf.append((len(asmCode), len(codes) - 1))
                    RDL = item[-1]

                elif item[0].val == '=':
                    if RDL == None:
                        codes += LD(item[1])
                    elif RDL == item[1]:
                        codes += ST(item[1])
                    elif RDL != item[1] and RDL != item[-1]:
                        if RDL.actInfo:
                            codes += ST(RDL)
                        codes += LD(item[1])
                    RDL = item[-1]
                elif item[0].val == 'FUN':
                    codes.append("%s PROC NEAR" % item[1].val)
                    codes.append("PUSH BP")
                    codes.append("MOV BP,SP")
                    codes.append("SUB SP,20")
                elif item[0].val == 'return':
                    if RDL:
                        if RDL != item[1]:
                            if RDL.actInfo:
                                codes += ST(RDL)
                            codes += LD(item[1])
                    else:
                        codes+=LD(item[1])
                    codes.append("MOV SP,BP")
                    codes.append("POP BP")
                    numOfPar = self.symTable.symDict[funcName].numOfParameters
                    codes.append("RET %d" % (numOfPar * 2))
                    codes.append("%s ENDP"%funcName)

                elif item[0].val == 'continue':
                    if RDL and RDL.actInfo:
                        codes += ST(RDL)
                    codes.append('JMP ' + startOfWhile[-1])
                elif item[0].val == 'el':
                    if RDL and RDL.actInfo:
                        codes += ST(RDL)
                    codes.append('JMP ')
                    jmpToEnd.append((len(asmCode), len(codes) - 1))
                    codes.append('next' + str(self.id) + ':')
                    x, y = judgeOfIf.pop()
                    asmCode[x][y] += 'next' + str(self.id)
                    self.id += 1
                elif item[0].val == 'ie':
                    if RDL and RDL.actInfo:
                        codes += ST(RDL)
                    codes.append('endif' + str(self.id) + ':')
                    while jmpToEnd:
                        x, y = jmpToEnd.pop()
                        asmCode[x][y] += 'endif' + str(self.id)
                    self.id += 1
                elif item[0].val == 'wh':
                    codes.append('while' + str(self.id) + ':')
                    startOfWhile.append('while' + str(self.id))
                    self.id += 1
                elif item[0].val == 'we':
                    tgt = startOfWhile.pop()
                    codes.append('JMP ' + tgt)
                    codes.append('endWhile' + str(self.id) + ':')
                    x, y = judgeOfWhile.pop()
                    asmCode[x][y] += 'endWhile' + str(self.id)
                    self.id += 1
                elif item[0].val == 'push':
                    if RDL == None:
                        codes += LD(item[1])
                    elif RDL != item[0]:
                        codes += ST(RDL)
                        codes += LD(item[1])
                    codes.append("PUSH AX")
                elif item[0].val == 'call':
                    codes.append("CALL %s" % item[1].val)
                elif item[0].val == 'callr':
                    codes.append("CALL %s" % item[1].val)
                    codes+= ST(item[-1])

            asmCode.append(codes)
        return asmCode

    def actFunInfoGen(self, bloc, funcName):
        '''
        传入函数代码块添加活跃信息，同时基于符号表填写临时变量的偏移地址
        :param bloc:基本块
        :param funcName:函数名
        :return:
        '''
        actTable = {}
        funcTable = self.symTable.symDict[funcName]  # 获取对应函数的符号表
        maxSizeOfFunc = funcTable.totalSize
        if funcName=='main':
            maxSizeOfFunc=0
        t_table = {}  # 临时变量栈地址存放
        for tmp in bloc:
            for item in tmp[1:]:
                if item == '_' or item.isdigit():
                    continue
                if item.startswith('@') and item not in list(t_table.keys()):  # 临时变量
                    actTable[item] = False
                    t_table[item] = maxSizeOfFunc
                    maxSizeOfFunc += 2
                elif item not in self.symTable.functionNameList:  # 标识符且不是函数名称
                    actTable[item] = True

        def helper(x):
            if x == '_' or x.isdigit() or x in self.symTable.functionNameList:
                return self.qtx(x, None, None, None, None)
            if x.startswith('@'):
                res = self.qtx(x, actTable[x], t_table[x] + 2, 0, False)
            else:
                if funcName=='main':
                    res=self.qtx(x,actTable[x],None,None,None)
                else:
                    if '.' in x:
                        x1, x2 = x.split('.')  # x1结构体 x2结构体中的变量
                        x_info = funcTable.variableDict[x1]
                        add1 = x_info.addr
                        st = self.symTable.symDict[x_info.type]  # 获得对应类型的结构体
                        add2 = st.variableDict[x2].addr  # 获得对应结构体中id的位置信息
                        if add1 < 0:  # 参数中说明传的是结构体的地址
                            res = self.qtx(x, actTable[x], add1 - 2, add2, True)
                        else:  # 函数中定义的结构体整个结构体内容都在栈空间
                            res = self.qtx(x, actTable[x], add1 + 2, add2, False)
                    else:
                        x_info = funcTable.variableDict[x]
                        add1 = x_info.addr
                        if add1 < 0:
                            res = self.qtx(x, actTable[x], add1 - 2, 0, False)
                        else:
                            res = self.qtx(x, actTable[x], add1 + 2, 0, False)
            return res

        for tmp in bloc[::-1]:
            tmp[-1] = helper(tmp[-1])
            if tmp[-1].actInfo:
                actTable[tmp[-1].val] = False
            tmp[-2] = helper(tmp[-2])
            tmp[-3] = helper(tmp[-3])
            if tmp[-3].actInfo != None:
                actTable[tmp[-3].val] = True
            if tmp[-2].actInfo != None:
                actTable[tmp[-2].val] = True
            tmp[0] = self.qtx(tmp[0], None, None, None, None)

        '''打印添加活跃信息后的情况'''
        # for x in bloc:
        #     for y in x:
        #         print(y)
        #     print('-'*20)
        # print('\n\n')


from grammar import LL1
from qt_gen import QtGen
from optimization import Optimization
import os

if __name__ == '__main__':
    grammar_path = os.path.abspath('grammar_static/c_like_grammar')
    path = os.path.abspath('c_input')
    with open(path, 'r', encoding='utf-8') as f:
        INPUT = f.readlines()
    ll1 = LL1(grammar_path)
    ll1.getInput(INPUT)
    res = ll1.analyzeInputString()
    qt = QtGen(ll1.syn_table)
    ll1.syn_table.showTheInfo()
    if res == 'acc':
        for block in ll1.funcBlocks:
            qt.genQt(block)
        op = Optimization(ll1.syn_table)
        qtLists = qt.qt_res  # 按照函数分成的大块
        qtListAfterOpt = []  # 基于函数块再其内部划分更小的块
        for item in qtLists:
            qtListAfterOpt.append(op.opt(item))
        for item in qtListAfterOpt:
            for i in item:
                for b in i:  # i是基本块
                    print(b)
                print('\n')
            print('-' * 30)

        asm = AsmCodeGen(ll1.syn_table, qtListAfterOpt)

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
