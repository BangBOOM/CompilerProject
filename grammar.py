import os,copy,json
import symbol_table
from lexer import Lexer
from grammarParaser import GrammarParser


class LL1(GrammarParser):
    RES_TOKEN=[]
    syn_table=symbol_table.SYN()
    funcBlocks=[]  #函数块
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
        # self.lex.dict_for_search()

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
        funcBlock = [token]  # 函数块每识别完成一个函数后送入函数四元式生成
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
                if tmp!=['$']:
                    if x=="Funcs":
                        self.__AddFuncToSYN(token.id,token.cur_line)
                    tmp=list(tmp)
                    stack+=tmp[::-1]
            else:
                if w=='#':
                    self.funcBlocks.append(funcBlock)
                    return "acc"
                try:
                    token=TokenList.pop(0)
                    if stack[-1]=='Funcs':
                        self.funcBlocks.append(funcBlock)
                        funcBlock=[]
                    w=getTokenVal(token)
                    funcBlock.append(token)
                except: #TokenList变为空
                    w='#'
        return "error3"

    def __AddFuncToSYN(self,id,cur_line):
        self.syn_table.addFunc(self.RES_TOKEN[id+1].val,self.RES_TOKEN[id].val,cur_line)

