import os, collections
from collections import namedtuple


class Lexer:
    DICT = {
        'k': collections.OrderedDict(),  # 关键字
        'p': collections.OrderedDict(),  # 界符
        'con': collections.OrderedDict(),  # 常数
        'c': collections.OrderedDict(),  # 字符
        's': collections.OrderedDict(),  # 字符串
        'i': collections.OrderedDict(),  # 标识符
    }
    INPUT = []
    TokenList = []
    CUR_ROW = -1
    CUR_LINE = 0
    Token = namedtuple('Token', 'type index val cur_line')  # 具名元组表示

    def __init__(self):
        path1 = os.path.abspath('lexer_static/keyword_list')
        path2 = os.path.abspath('lexer_static/p_list')
        self.k_list = []
        self.p_list = []
        with open(path1, 'r', encoding='utf-8') as f:
            for i, item in enumerate(f.readlines()):
                item = item.strip()
                self.k_list.append(item)
        with open(path2, 'r', encoding='utf-8') as f:
            for i, item in enumerate(f.readlines()):
                item = item.strip()
                self.p_list.append(item)

    def dict_for_search(self):  # 这个是为了方便检索，其实是设计结构上的一个失误添加的这个
        self.DICT_S = {
            'k': list(self.DICT['k']),
            'p': list(self.DICT['p']),
            'con': list(self.DICT['con']),
            'c': list(self.DICT['c']),
            's': list(self.DICT['s']),
            'i': list(self.DICT['i']),
        }

    def getInput(self, input_list):
        '''
        :param input_list:['...','...'] the string split by '\n'
        :return:
        '''
        self.INPUT = input_list

    def getNextChar(self):
        self.CUR_ROW += 1
        if self.CUR_LINE == len(self.INPUT):
            return "END"
        while self.CUR_ROW == len(self.INPUT[self.CUR_LINE]):
            '''the end of each line or the line is empty'''
            self.CUR_ROW = 0
            self.CUR_LINE += 1
            if self.CUR_LINE == len(self.INPUT):
                return "END"
        return self.INPUT[self.CUR_LINE][self.CUR_ROW]

    def backOneStep(self):
        self.CUR_ROW -= 1

    def __getId(self, demo, typ):
        return self.DICT[typ].setdefault(demo, len(self.DICT[typ]))

    def scanner(self):
        item = self.getNextChar().strip()
        id = None
        demo = None
        typ = None
        if item == '':
            return None
        elif item == "END":
            return ("END")
        elif item.isalpha() or item == '_':
            demo = ""
            while item.isalpha() or item.isdigit() or item == "_":
                demo += item
                if self.CUR_ROW == len(self.INPUT[self.CUR_LINE]) - 1:
                    self.CUR_LINE += 1
                    self.CUR_ROW = 0
                    break
                else:
                    item = self.getNextChar()
            self.backOneStep()
            if demo in self.k_list:
                id = self.__getId(demo, 'k')
                typ = 'k'
            else:
                id = self.__getId(demo, 'i')
                typ = 'i'
        elif item.isdigit():
            demo = ""
            while item.isdigit() or item == ".":
                demo += item
                if self.CUR_ROW == len(self.INPUT[self.CUR_LINE]) - 1:
                    self.CUR_LINE += 1
                    self.CUR_ROW = 0
                    break
                else:
                    item = self.getNextChar()
            self.backOneStep()
            id = self.__getId(demo, 'con')
            typ = 'con'
        elif item == '"':
            demo = '"'
            item = self.getNextChar()
            demo += item
            while item != '"':
                item = self.getNextChar()
                demo += item
            id = self.__getId(demo, 's')
            typ = 's'
        elif item == "'":
            demo = "'"
            for i in range(2):
                item = self.getNextChar()
                demo += item
            id = self.__getId(demo, 'c')
            typ = 'c'
        else:
            item_next = self.getNextChar()

            if item + item_next in self.p_list:
                demo = item + item_next
                id = self.__getId(demo, 'p')
            else:
                demo = item
                id = self.__getId(demo, 'p')
                self.backOneStep()
            typ = 'p'
        return self.Token(typ, id, demo, self.CUR_LINE)

    def analyse(self):
        TOKEN_LIST = []
        while True:
            tmp = self.scanner()
            if tmp == "END":
                break
            if tmp:
                TOKEN_LIST.append(tmp)
        self.dict_for_search()
        self.TokenList = TOKEN_LIST
        return TOKEN_LIST


if __name__ == "__main__":
    lex = Lexer()
    # INPUT=input("input something:").split('\n')         #sample INPUT=['int a=0;','a=a+4;','c='s'']
    INPUT = ['int a=0;', 'a=a+4;', 'c="ss"']
    lex.getInput(INPUT)
    res = lex.analyse()
    for tmp in res:
        print(tmp)
    print(lex.DICT_S)
