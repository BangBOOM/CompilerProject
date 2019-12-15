from collections import namedtuple

'''
根据优化后的代码块生成汇编语言
目前只是基本尝试这部分写的很乱需要全部重写。
'''


class AsmCodeGen:
    def __init__(self, sym):
        self.symTable = sym

    def getAsm(self, funcBlock):
        '''
        :param funcBlock:   一个被划分基本块的函数块
        :return:
        '''

        '''函数头部'''
        res = [funcBlock[0][0][1] + ':']  # 第一个基本块为函数定义，这里是添加函数的名字
        res.append("push bp")  # 保护bp解决函数调用的情况
        res.append("mov bp,sp")
        '''函数体'''
        for bloc in funcBlock[1:]:
            self.actInfoGen(bloc)
            RDL=None
            CODE=[]
            for item in bloc:
                if item[0] in ['+','-','*','/','<=','>=','<','>','==']:
                    if RDL==None:
                        if isinstance(item[1],str):
                            CODE.append("LD R,%s"%(item[1]))
                        else:
                            CODE.append("LD R,%s"%(item[1].val))
                        if isinstance(item[2],str):
                            CODE.append("%s R,%s" % (item[0],item[2]))
                        else:
                            CODE.append("%s R,%s" % (item[0],item[2].val))
                    elif RDL==item[1]:
                        if item[1].act==True:
                            CODE.append("ST R,%s"%(item[1].val))
                        if isinstance(item[2],str):
                            CODE.append("%s R,%s"%(item[0],item[2]))
                        else:
                            CODE.append("%s R,%s"%(item[0],item[2].val))

                    elif RDL==item[2]:
                        if item[2].act==True:
                            CODE.append("ST R,%s"%(item[2]))
                        if isinstance(item[1],str):
                            CODE.append("LD R,%s"%(item[1]))
                        else:
                            CODE.append("LD R,%s"%(item[1].val))
                        if isinstance(item[2],str):
                            CODE.append("%s R,%s" % (item[0], item[2]))
                        else:
                            CODE.append("%s R,%s" % (item[0], item[2].val))
                    else:
                        if RDL.act==True:
                            CODE.append("ST R,%s"%(RDL.val))
                        if isinstance(item[1],str):
                            CODE.append("LD R,%s"%(item[1]))
                        else:
                            CODE.append("LD R,%s" % (item[1].val))
                        if isinstance(item[2],str):
                            CODE.append("%s R,%s"%(item[0],item[2].val))
                    RDL=item[-1]
                elif item[0]=='=':
                    if RDL==None:
                        if isinstance(item[1],str):
                            CODE.append("LD R,%s"%item[1])
                        else:
                            CODE.append("LD R,%s"%item[1].val)
                    elif RDL==item[1]:
                        if item[1].act==True:
                            CODE.append("ST R,%s"%item[1].val)
                    elif RDL!=item[-1]:
                        if RDL.act==True:
                            CODE.append("ST R,%s"%RDL.val)
                        if isinstance(item[1], str):
                            CODE.append("LD R,%s" % item[1])
                        else:
                            CODE.append("LD R,%s" % item[1].val)
                    RDL=item[-1]
                elif item[0]=='if':
                    if RDL==None:
                        if isinstance(item[1], str):
                            CODE.append("LD R,%s" % item[1])
                        else:
                            CODE.append("LD R,%s" % item[1].val)
                        CODE.append("FJ R,?")
                    elif RDL==item[1]:
                        if item[1].act:
                            CODE.append("ST R,%s"%(item[1].val))
                        CODE.append("FJ R,?")
                        RDL=None
                    else:
                        if RDL.act:
                            CODE.append("ST R,%s"%(RDL.val))
                        if isinstance(item[1], str):
                            CODE.append("LD R,%s" % item[1])
                        else:
                            CODE.append("LD R,%s" % item[1].val)
                        CODE.append("FJ R,?")
                        RDL=None
                elif item[0]=='return':
                    if RDL==None:
                        if isinstance(item[1], str):
                            CODE.append("LD R,%s" % item[1])
                        else:
                            CODE.append("LD R,%s" % item[1].val)
                    elif RDL==item[1]:
                        if item[1].act:
                            CODE.append("ST R,%s"%(item[1].val))
                        RDL=None
                    else:
                        if RDL.act:
                            CODE.append("ST R,%s"%(RDL.val))
                        if isinstance(item[1], str):
                            CODE.append("LD R,%s" % item[1])
                        else:
                            CODE.append("LD R,%s" % item[1].val)
                        RDL=None



            for t in CODE:
                print(t)
            print("-" * 20)


    def actInfoGen(self, bloc):
        '''
        :param bloc:    输入基本块，构造添加变量的活跃信息
        :return:
        '''
        actTable = {}
        qt_x = namedtuple('qt_x', 'val act')  # 四元式中的值
        for tmp in bloc:
            for item in tmp[1:]:
                if item == '_':
                    continue
                if item[0] == '@':
                    actTable[item] = False
                elif (item not in self.symTable.functionNameList) and (not item[0].isdigit()):
                    actTable[item] = True
        # print(bloc)
        # print(actTable)
        for tmp in bloc[::-1]:  # tmp是四元式
            if tmp[-1] != '_' and not tmp[-1].isdigit():
                tmp[-1] = qt_x(tmp[-1], actTable[tmp[-1]])
                actTable[tmp[-1].val] = False
            if tmp[-2] != '_' and not tmp[-2].isdigit():
                tmp[-2] = qt_x(tmp[-2], actTable[tmp[-2]])
            if tmp[-3] not in self.symTable.functionNameList and not tmp[-3].isdigit() and tmp[-3] != '_':
                tmp[-3] = qt_x(tmp[-3], actTable[tmp[-3]])
                actTable[tmp[-3].val] = True
                if isinstance(tmp[-2], qt_x):
                    actTable[tmp[-2].val] = True
        # print(bloc)
        # print("-" * 20)
