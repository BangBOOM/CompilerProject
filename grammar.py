import os,copy,json
import symbol_table
from lexer import Lexer
from grammarParaser import GrammarParser


class LL1(GrammarParser):
    RES_TOKEN=[]
    syn_table=symbol_table.SYMBOL()
    funcBlocks=[]  #函数块集合[[],[],[],...]
    def __init__(self,path,doseIniList=False):
        GrammarParser.__init__(self,path)
        self.lex=Lexer()
        path=os.path.abspath('grammar_static/AnalysisTable.json')
        if doseIniList:
            self.initList()
        else:
            with open(path,'r') as f:
                self.analysis_table=json.load(fp=f)

    def getInput(self,INPUT):  # ['12-a+b']
        self.lex.getInput(INPUT)
        self.RES_TOKEN=self.lex.analyse()

    def analyzeInputString(self):
        def getTokenVal(token):
            if token.type == 'con':
                return 'NUM'
            if token.type == 'i':
                return 'ID'
            return token.val
        stack=['#',self.Z]
        TokenList=copy.copy(self.RES_TOKEN)
        token=TokenList.pop(0)
        funcBlock = [token]  # 函数块每识别完成一个函数后送入self.funcBlocks
        w=getTokenVal(token)
        while stack:
            x=stack.pop()
            if x!=w:
                if x not in self.VN:
                    print(x)
                    return "error1" #这个位置中止整个程序返回报错信息
                id=self.analysis_table[x][w]
                if id==-1:
                    print(x,w)
                    print('stack:',stack)
                    return "error2" #这个位置中止整个程序返回报错信息
                tmp=self.P_LIST[id][1]
                if tmp!=['$']:  #进行标识符登记检测
                    tmp=list(tmp)
                    stack+=tmp[::-1]
                    if x=="Funcs":  #函数定义
                        self.__AddFuncToSYN(token)
                    if x=="FormalParameters":  #函数参数添加
                        if token.val!=',':
                            self.__AddVariableToFun(token,True)
                        else:
                            self.__AddVariableToFun(self.RES_TOKEN[token.id+1],True)
                    if x=="LocalVarDefine": #函数内部变量定义
                        self.__AddVariableToFun(token)
                    if x=="NormalStatement" or (x=="F" and w=="ID" ):
                        self.__CheckVarToken(token)
                    if x=="FuncCallFollow":
                        id=token.id
                        if w=="=":
                            id+=1
                        else:
                            id-=1
                        self.__CheckFunToken(self.RES_TOKEN[id])

            else:
                if w=='#':
                    self.funcBlocks.append(funcBlock)
                    return "acc"
                try:
                    token=TokenList.pop(0)
                    if stack[-1]=='Funcs':  #将函数定义
                        self.funcBlocks.append(funcBlock)
                        funcBlock=[]
                    w=getTokenVal(token)
                    funcBlock.append(token)
                except: #TokenList变为空
                    w='#'
        return "error3"

    def __AddFuncToSYN(self,token): #添加函数到符号表的总表
        self.syn_table.addFunction(self.RES_TOKEN[token.id+1],token.val)

    def __AddVariableToFun(self,token,doseParameter=False):
        self.syn_table.addVariableToFunction(self.RES_TOKEN[token.id+1],token.val,doseParameter)

    def __CheckVarToken(self,token):    #检测变量是否定义
        self.syn_table.checkDoDefineInFunction(token)

    def __CheckFunToken(self,token):    #检测函数是否定义
        self.syn_table.checkDoDefineFunction(token)
