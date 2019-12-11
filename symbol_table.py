from collections import namedtuple

Parameter=namedtuple('Parameter','Name Type DoseFormal ADDR')
class Fun:
    def __init__(self,Name,ReturnType,addr):
        self.Name=Name
        self.ReturnType=ReturnType
        self.ADDR=addr
        self.ParameterNum = 0  # 参数个数
        self.ParameterNumTypeList = []  # 参数类型列表
        self.ParametersDict = {}
        self.paraType = namedtuple('para', 'name type addr')
        self.pAddr=0

    def incParameterNum(self):
        self.ParameterNum+=1

    def incPADDR(self):
        self.pAddr+=1
        return self.pAddr

    def addParameterToDict(self,name,typ):
        tmp=self.paraType(name,typ,self.incPADDR())
        self.ParametersDict[name]=tmp







class SYN:
    Cur_Addr=0
    Funs=[]
    FunsName=[]

    def incCurAddr(self):
        self.Cur_Addr+=1
        return self.Cur_Addr

    def addFunc(self,Name,ReturnType,cur_line):
        '''

        :param Name:        函数名
        :param ReturnType:  返回类型
        :param cur_line:    函数定义的当前行数用于报错信息
        :return:
        '''
        if Name in self.FunsName:
            raise ValueError("error: define the func repeatedly in line:",cur_line+1)
        else:
            fun=Fun(Name,ReturnType,self.incCurAddr())
            self.Funs.append(fun)
            self.FunsName.append(Name)

    def addParaToFun(self,name,typ,cur_line,doseIncPN):
        fun=self.Funs[-1]
        if name not in self.FunsName:   #变量不与函数名重复
            if name not in list(fun.ParametersDict.keys()): #内部变量不重名
                if doseIncPN:   #是否是函数的参数变量
                    fun.incParameterNum()
                fun.addParameterToDict(name,typ)
            else:
                raise ValueError("error:repeat define para in line:",cur_line+1)
        else:
            raise ValueError("error in line:", cur_line + 1)
        print('fun:name:',fun.Name,)
        print('fun Para Num:',fun.ParameterNum)
        print('fun addr:',fun.ADDR)
        print(fun.ParametersDict)
        print("---------")

    def checkFunParas(self,name,cur_line):
        fun = self.Funs[-1]
        if name not in list(fun.ParametersDict.keys()):
            raise ValueError("error: val not define in line:",cur_line+1)







