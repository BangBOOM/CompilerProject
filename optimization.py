import copy
from collections import namedtuple
'''
四元式的优化
'''

class Optimization:
    def __init__(self,sym):
        self.symTable=sym       #符号表

    def opt(self,funcBlock):    #每次传入一个函数块，把这个函数块分成基本块并优化
        fBlock=copy.copy(funcBlock)
        res=[]         #二维 res[bloc bloc]
        bloc=[]        #存放基本块
        while fBlock:
            tmp=fBlock.pop(0)
            if tmp[0] in ['wh']:
                res.append(bloc)
                bloc=[tmp]
            elif tmp[0] in ['do','we','if','el','elif','ie','return','continue','break']:
                bloc.append(tmp)
                res.append(bloc)
                bloc=[]
            elif tmp[0]=="FUN":
                res.append([tmp])
            else:
                bloc.append(tmp)
        funcBlock_new=[]
        for b in res:
            # print("----old----")
            # for i in b:
            #     print(i)
            # print("----old----")
            self.optTheBloc(b)
            # print("----new----")
            # for i in self.new_qt:
            #     print(i)
            # print("----new----")
            # print("\n\n")
            funcBlock_new.append(self.new_qt)
        return  funcBlock_new


    def optTheBloc(self,bloc):
        '''
        这部分对基本块进行优化
        :param bloc:
        :return:
        '''
        self.nodes = []
        self.new_qt = []
        self.NODE = namedtuple('NODE', 'op ID signs leftNodeID rightNodeID')
        self.operation=['+', '-', '*', '/', '=','>','<','==','>=','<=']
        for qt in bloc:  # 假设四元式为（op,B,C,A)
            "构造DOG"

            if qt[0] in self.operation:
                if qt[0] in ['=']:  # qt一元运算符
                    idB = self.Get_NODE(qt[1])
                    self.delete_sym(qt[3])
                    self.add_to_node(idB, qt[3])
                else:
                    if qt[1].isdigit() and qt[2].split('.')[-1].isdigit():
                        idP=self.Get_NODE(str(int(eval(qt[1]+qt[0]+qt[2]))))
                        self.delete_sym(qt[3])
                        self.add_to_node(idP, qt[3])
                    else:
                        idB = self.Get_NODE(qt[1])
                        idC = self.Get_NODE(qt[2])
                        idop = self.Get_NODE(qt[0], idB, idC)
                        self.delete_sym(qt[3])
                        self.add_to_node(idop, qt[3])

        # print("所有结点", self.nodes)
        self.generate_new_qt(self.nodes)
        flag = 0
        i = 0
        for qt in bloc:

            if qt[0] not in self.operation:  # 最后一个才可能不是运算四元式

                if flag==1:
                    self.new_qt.append(qt)  # 这部分不需要优化
                else:
                    self.new_qt.insert(i,qt)
                    i=i+1
            else:
                flag=1


    def Get_NODE(self, sym, BofLeftNodeID=None, CofRightNodeID=None):
        "如果存在一个结点含有sym则返回结点id；如果不存在，创一个新结点，对其编号并且返回它的id(sym 可能是操作数或操作符)"
        if sym in self.operation:
            for node in reversed(self.nodes):  # 倒序遍历数组
                if sym == node.op and (sym == '+' or sym == '*'):
                    if (BofLeftNodeID == node.leftNodeID and CofRightNodeID == node.rightNodeID) or (
                            BofLeftNodeID == node.rightNodeID and CofRightNodeID == node.leftNodeID):
                        return node.ID
                if sym == node.op:
                    if (BofLeftNodeID == node.leftNodeID and CofRightNodeID == node.rightNodeID):
                        return node.ID
            else:  # 新建一个结点
                signs = []
                self.nodes.append(self.NODE(sym, len(self.nodes), signs, BofLeftNodeID, CofRightNodeID))
                return len(self.nodes) - 1
        else:  # 不是操作符,是操作数
            for node in reversed(self.nodes):
                if sym in node.signs:
                    return node.ID
            else:
                signs = []
                signs.append(sym)
                self.nodes.append(self.NODE(None, len(self.nodes), signs, None, None))
                return len(self.nodes) - 1

    def delete_sym(self, A):
        "DOG中有A，且A不是主标记，那么删除A"
        for node in self.nodes:
            if A in node.signs and A != node.signs[0]:
                node.signs.remove(A)
                return True
        else:
            return False

    def generate_new_qt(self, NODES):
        for node in NODES:
            qt = []
            if node.leftNodeID == None and node.rightNodeID == None and len(node.signs) > 1:
                for i in range(1, len(node.signs)):
                    if node.signs[i][0] != '@':  # 临时变量前带有一个@
                        qt = ['=', node.signs[0], '_', node.signs[i]]  # Ai=B；
                        self.new_qt.append(qt)
            elif node.leftNodeID != None and node.rightNodeID != None and len(node.signs) > 1:
                qt = [node.op, self.nodes[node.leftNodeID].signs[0], self.nodes[node.rightNodeID].signs[0],
                      node.signs[0]]  # A=B C
                self.new_qt.append(qt)
                for i in range(1, len(node.signs)):
                    if node.signs[i][0] != '@':
                        qt = ['=', node.signs[0], '_', node.signs[i]]  # Ai=B；
                        self.new_qt.append(qt)
            elif node.leftNodeID != None and node.rightNodeID != None:
                qt = [node.op, self.nodes[node.leftNodeID].signs[0], self.nodes[node.rightNodeID].signs[0],
                      node.signs[0]]  # A=B C
                self.new_qt.append(qt)
            # else:
            # print("叶结点:",node)

    def add_to_node(self, nodeID, sym):
        "将sym附加到结点"
        if len(self.nodes[nodeID].signs) != 0 and self.nodes[nodeID].signs[0][0] == '@' and sym[0] != '@':  # 主标记为临时变量就交换位置
            tmp = self.nodes[nodeID].signs[0]
            self.nodes[nodeID].signs[0] = sym
            self.nodes[nodeID].signs.append(tmp)
        else:
            self.nodes[nodeID].signs.append(sym)












