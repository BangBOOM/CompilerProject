from collections import namedtuple


class Function:
    def __init__(self,name,returnType,funAddr):
        self.functionName=name              #函数名
        self.numOfParameters=0              #参数数量
        self.typeOfParametersList=[]        #参数类型列表
        self.returnType=returnType          #返回值类型
        self.variableDict={}                #变量字典   key:name value:variableType
        self.variableType=namedtuple('variable','name type addr')
        self.addrOfFunction=funAddr         #函数相对程序入口函数的便宜地址
        self.addrOfVariable=0               #变量相对函数入口的偏移地址

    def incVariableAddr(self):
        self.addrOfVariable+=1
        return self.addrOfVariable

    def addVariable(self,token,typ,doseParameter=False):    #添加参数
        self.checkHasDefine(token)
        tmp=self.variableType(token.val,typ,self.incVariableAddr())
        self.variableDict[token.val] = tmp
        if doseParameter:                   #若是参数则在参数列表里添加
            self.typeOfParametersList.append(typ)
            self.numOfParameters+=1

    def checkHasDefine(self,token):    #检查重复定义问题
        if token.val in list(self.variableDict.keys()):
            raise ValueError('error variable duplicate definition in line ',
                             token.cur_line+1,token.val)

    def checkDoDefine(self,token):      #检查是变量否定义
        if token.val not in list(self.variableDict.keys()):
            raise ValueError('error variable has no definition in line ',
                             token.cur_line+1,token.val)


class SYMBOL:
    curAddr=0
    functionList=[]         #Function 集合
    functionNameList=[]     #Function name 集合方便查找重复定义情况

    def incCurAddr(self):
        self.curAddr+=1
        return self.curAddr

    def checkHasDefine(self,token):
        if token.val in self.functionNameList:
            raise ValueError('error variable duplicate definition in line ',
                             token.cur_line + 1)


    def addFunction(self,token,returnType):
        self.checkHasDefine(token)
        function=Function(token.val,returnType,self.incCurAddr())
        self.functionList.append(function)
        self.functionNameList.append(token.val)

    def addVariableToFunction(self,token,varType,doseParameter=False):
        function=self.functionList[-1]
        function.addVariable(token,varType,doseParameter)

    def checkDoDefineInFunction(self,token):
        function = self.functionList[-1]
        function.checkDoDefine(token)

    def checkDoDefineFunction(self,token):
        if token.val not in self.functionNameList:
            raise ValueError('error variable duplicate definition in line ',
                             token.cur_line + 1,token.val)

    def showTheInfo(self):  #打印符号表的信息
        for fun in self.functionList:
            print("function: %s. ReturnType %s. ADDR %d. NumOfParameters %d."
                  %(fun.functionName,fun.returnType,fun.addrOfFunction,fun.numOfParameters))
            for _,v in fun.variableDict.items():
                print("    variable: name %s type: %s addr: %s"%v)






