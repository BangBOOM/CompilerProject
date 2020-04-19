import os,json

class GrammarParser:
    GRAMMAR_DICT = {}
    P_LIST = []
    FIRST = []
    FIRST_VT = {}  # {A:a|A->a...}
    FOLLOW = {}
    VN = set()
    VT = set()
    Z = None
    SELECT = []
    analysis_table = {}
    def __init__(self,path=None):
        if not path:
            path=os.path.abspath('grammar_static/c_like_grammar')
        with open(path, 'r', encoding='utf-8') as f:
            for item in f.readlines():
                vn, tmp = item.strip().split('->')
                if not self.Z:
                    self.Z=vn
                tmp=tmp.split(' ')
                self.P_LIST.append((vn, tmp))
                self.GRAMMAR_DICT.setdefault(vn, []).append(tmp)
                self.VN.add(vn)
        for item in self.P_LIST:
            for x in item[1]:
                if x not in self.VN and x != '$':
                    self.VT.add(x)


    def initList(self):
        self._calFirstvt()
        self._calFirst()
        self._calFollow()
        self._calSelect()
        self._calAnalysisTable()
        path=os.path.abspath('grammar_static/AnalysisTable.json')
        with open(path,'w') as f:
            json.dump(self.analysis_table,f)

    def _calFirstvt(self):
        def helper(vn):
            fir = self.FIRST_VT.setdefault(vn, set([]))
            if not fir:
                for item in self.GRAMMAR_DICT[vn]:
                    for i in item:
                        if i in self.VT:
                            fir.add(i)
                        elif i in self.VN:
                            fir.update(helper(i))
                            if ['$'] in self.GRAMMAR_DICT[i]:
                                continue
                        break
            return fir

        for vn in self.VN:
            helper(vn)

    def _calFirst(self):
        for _, item in self.P_LIST:
            demo = set([])
            for i in item:
                if i in self.VT:
                    demo.add(i)
                elif i in self.VN:
                    demo.update(self.FIRST_VT[i])
                    if ['$'] in self.GRAMMAR_DICT[i]:
                        continue
                break
            self.FIRST.append(demo)

    def _calFollow(self):
        state=dict(zip(list(self.VN),[False]*len(self.VN)))
        def helper(vn):
            if state[vn]==True:
                return
            for x,item in self.P_LIST:
                try:
                    id = item.index(vn)
                    follow = self.FOLLOW.setdefault(vn, set())
                    while True:
                        if id + 1 == len(item):
                            follow.add('#')
                            if x!=vn and not state[x]:
                                helper(x)
                            follow.update(self.FOLLOW[x])
                        elif item[id + 1] in self.VT:
                            follow.add(item[id + 1])
                        elif item[id + 1] in self.VN:
                            follow.update(self.FIRST_VT[item[id + 1]])
                            if ['$'] in self.GRAMMAR_DICT[item[id + 1]]:
                                id += 1
                                continue
                        break
                except:
                    pass
            state[vn]=True
        for vn in self.VN:
            helper(vn)

    def _calSelect(self):
        for p,f in zip(self.P_LIST,self.FIRST):
            if f:
                self.SELECT.append(f)
            else:
                self.SELECT.append(self.FOLLOW[p[0]])

    def _calAnalysisTable(self):
        for vn in self.VN:
            self.analysis_table[vn]=dict([(vt,-1) for vt in self.VT]+[('#',-1)])
        for i,item in enumerate(self.P_LIST):
            for x in self.SELECT[i]:
                self.analysis_table[item[0]][x]=i
