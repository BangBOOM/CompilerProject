import os, copy, json
from grammarParaser import GrammarParser


class QtGen(GrammarParser):  # 四元式生成
    t_id = 0
    qt_res = []

    def __init__(self, syn):
        GrammarParser.__init__(self)
        self.syn_table = syn
        translation_grammar_path = os.path.abspath('grammar_static/translation_grammar')
        self.P_LIST = []
        with open(translation_grammar_path, 'r', encoding='utf-8') as f:
            for item in f.readlines():
                vn, tmp = item.strip().split('->')
                tmp = tmp.split(' ')
                self.P_LIST.append((vn, tmp))
        path = os.path.abspath('grammar_static/AnalysisTable.json')
        with open(path, 'r') as f:
            self.analysis_table = json.load(fp=f)

    def genQt(self, funcBlock):
        qtList = []
        SEM_STACK = []  #
        SYMBOL_STACK = []  # 语义符号栈
        SYN = ['#', self.Z]
        TokenList = copy.copy(funcBlock)
        self.t_id = 0

        def getTokenVal(token):
            if token.val in self.syn_table.structNameList:
                return 'st'  # 转换成结构体的笼统形式方便定义的时候类型确认
            if token.type == 'con':
                return 'NUM'
            if token.type == 'i':
                return 'ID'
            return token.val

        def catch(x, val):
            deal, symbol = x.split('_')
            if deal == '@SAVE':
                SYMBOL_STACK.append(symbol)
            if deal == '@PUSH':
                SEM_STACK.append(val)
            if deal == '@GEQ':
                if symbol in ["el", "ie", "wh", "we", "break", "continue"]:
                    qtList.append([symbol, '_', '_', '_'])
                else:
                    s = SYMBOL_STACK.pop()
                    if s == '=' or s == 'callr':  # callr有返回值的函数调用,call无返回值的函数调用
                        tmp2 = SEM_STACK.pop()
                        tmp1 = SEM_STACK.pop()
                        qtList.append([s, tmp2, '_', tmp1])
                    elif s in ['if', 'elif', 'do', 'FUN', 'return', 'push', 'call']:
                        tmp = SEM_STACK.pop()
                        qtList.append([s, tmp, '_', '_'])
                    else:
                        tmp2 = SEM_STACK.pop()
                        tmp1 = SEM_STACK.pop()
                        t = '@t' + str(self.t_id)
                        self.t_id += 1
                        SEM_STACK.append(t)
                        qtList.append([s, tmp1, tmp2, t])

        token = TokenList.pop(0)
        w = getTokenVal(token)
        val = None
        while SYN:
            x = SYN.pop()
            if x[0] == '@':  # 判断是三种语义信息SAVE GEQ PUSH而非VN
                catch(x, val)
                continue
            if x != w:
                id = self.analysis_table[x][w]
                tmp = self.P_LIST[id][1]
                if tmp != ['$']:
                    tmp = list(tmp)
                    SYN += tmp[::-1]
            else:
                val = token.val
                if w == '#':
                    break
                try:
                    token = TokenList.pop(0)
                    w = getTokenVal(token)
                except:
                    w = '#'
        self.qt_res.append(qtList)
