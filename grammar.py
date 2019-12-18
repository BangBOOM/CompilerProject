import os, copy, json
import symbol_table
from lexer import Lexer
from grammarParaser import GrammarParser

class LL1(GrammarParser):
    RES_TOKEN = []
    syn_table = symbol_table.SYMBOL()
    funcBlocks = []  # 函数块集合[[],[],[],...]
    def __init__(self, path, doseIniList=False):
        GrammarParser.__init__(self, path)
        self.lex = Lexer()
        path = os.path.abspath('grammar_static/AnalysisTable.json')
        if doseIniList:
            self.initList() #修改文法后重新初始化分析表
        else:
            with open(path, 'r') as f:  #从保存的json文件中读取分析表
                self.analysis_table = json.load(fp=f)

    def getInput(self, INPUT):  # ['12-a+b']
        self.lex.getInput(INPUT)
        self.RES_TOKEN = self.lex.analyse()

    def analyzeInputString(self):
        def getTokenVal(token):
            if token.val in self.syn_table.structNameList:
                return 'st'  # 转换成结构体的笼统形式方便定义的时候类型确认
            if token.type == 'con':
                return 'NUM'
            if token.type == 'i':
                return 'ID'
            return token.val
        stack = ['#', self.Z]
        TokenList = copy.copy(self.RES_TOKEN)
        token = TokenList.pop(0)
        funcBlock = [token]  # 函数块每识别完成一个函数后送入self.funcBlocks
        w = getTokenVal(token)
        while stack:
            x = stack.pop()
            if x != w:
                if x not in self.VN:
                    print("missing '%s' around line %d" % (x, token.cur_line))
                    return "error1"  # 这个位置中止整个程序返回报错信息
                id = self.analysis_table[x][w]
                if id == -1:
                    print("wrong grammar around line %s" % (token.cur_line))
                    return "error2"  # 这个位置中止整个程序返回报错信息
                tmp = self.P_LIST[id][1]
                if tmp != ['$']:  # 进行标识符登记检测
                    tmp = list(tmp)
                    stack += tmp[::-1]
                    self.editSymTable(x,w,token)
            else:
                if w == '#':
                    self.funcBlocks.append(funcBlock)
                    return "acc"
                try:
                    token = TokenList.pop(0)
                    if stack[-1] == 'Funcs':  # 将函数定义
                        self.funcBlocks.append(funcBlock)
                        funcBlock = []
                    w = getTokenVal(token)
                    funcBlock.append(token)
                except:  # TokenList变为空
                    w = '#'
        return "error3"

    def editSymTable(self,x,w,token):
        '''添加符号表，检测定义问题'''
        if x == "Funcs":  # 函数定义
            self.__AddFuncToSYN(token)
        if x == "Struct":
            self.__AddStructToSYN(token)
        if x.startswith("FormalParameters"):  # 函数参数添加
            if token.val != ',':
                self.__AddVariable(token, True)
            else:
                self.__AddVariable(self.RES_TOKEN[token.id + 1], True)
        if x == "LocalVarDefine":  # 变量定义
            self.__AddVariable(token)
        if x == "NormalStatement" or (x == "F" and w == "ID"):
            self.__CheckVarToken(token)
        if x == "FuncCallFollow":
            id = token.id
            if w == "=":
                id += 1
            else:
                id -= 1
            self.__CheckFunToken(self.RES_TOKEN[id])

    def __AddFuncToSYN(self, token):  # 添加函数到符号表的总表
        self.syn_table.addFunction(self.RES_TOKEN[token.id + 1], token.val)

    def __AddStructToSYN(self, token):  # 添加结构体到符号表总表
        self.syn_table.addStruct(self.RES_TOKEN[token.id + 1])

    def __AddVariable(self, token, doseParameter=False):    #变量定义添加到符号表
        self.syn_table.addVariableToTable(self.RES_TOKEN[token.id + 1], token.val, doseParameter)

    def __CheckVarToken(self, token):  # 检测函数调用变量时变量是否定义
        if '.' not in token.val and '[' not in token.val:   #数组和结构体目前不检测变量是否定义问题
            self.syn_table.checkDoDefineInFunction(token)

    def __CheckFunToken(self, token):  # 检测函数是否定义
        self.syn_table.checkDoDefineFunction(token)

if __name__ == '__main__':
    grammar_path = os.path.abspath('grammar_static/c_like_grammar')
    path = os.path.abspath('c_input')
    with open(path, 'r', encoding='utf-8') as f:
        INPUT = f.readlines()
    ll1 = LL1(grammar_path, True)
    ll1.getInput(INPUT)
    res = ll1.analyzeInputString()
    print(res)
    ll1.syn_table.showTheInfo()