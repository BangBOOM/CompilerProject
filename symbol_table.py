from collections import namedtuple


class SecTable:
    def __init__(self):
        self.variableDict = {}  # 变量字典   key:name value:variableType
        self.variableType = namedtuple('variable', 'name type addr')
        self.totalSize = 0  # 整体变量占的空间方便汇编代码填写地址
        Message = namedtuple('Message', 'ErrorType Location ErrorMessage')
        self.Message=Message(None,None,None)

    def addPaVariable(self, token, typ):  # 添加参数
        pass

    def addVariable(self, token, typ, s):  # 添加变量
        self.checkHasDefine(token)
        tmp = self.variableType(token.val, typ, self.totalSize)
        self.totalSize += s
        self.variableDict[token.val] = tmp

    def checkHasDefine(self, token):  # 检查重复定义问题
        if token.val in list(self.variableDict.keys()):
            ErrorType = 'Duplicate identified'
            Location = 'Location:line {line}'.format(line=token.cur_line+1)
            ErrorMessage = "variable '{token}' duplicate definition".format(token=token.val)
            error3 = namedtuple('Message', 'ErrorType Location ErrorMessage')
            self.Message=error3(ErrorType, Location, ErrorMessage)
            #self.Message(ErrorType, Location, ErrorMessage)
            #raise ValueError('error variable duplicate definition in line ',
                             #token.cur_line + 1, token.val)

    def checkDoDefine(self, token):  # 检查是变量使用时是否定义
        if token.val not in list(self.variableDict.keys()):
            ErrorType = 'Unknown identifier'
            Location = 'Location:line {line}'.format(line=token.cur_line)
            ErrorMessage = "variable '{token}' has no definition".format(token=token.val)
            error4 = namedtuple('Message', 'ErrorType Location ErrorMessage')
            self.Message = error4(ErrorType, Location, ErrorMessage)
            #self.Message(ErrorType, Location, ErrorMessage)

            #raise ValueError('error variable has no definition in line ',
                             #token.cur_line + 1, token.val)


class Struct(SecTable):
    def __init__(self, name):
        super().__init__()
        self.structName = name


class Function(SecTable):
    def __init__(self, name, returnType):
        super().__init__()
        self.functionName = name  # 函数名
        self.numOfParameters = 0  # 参数数量
        self.parametersDict={}      #参数字典
        self.typeOfParametersList = []  # 参数类型列表
        self.returnType = returnType  # 返回值类型

    def addPaVariable(self, token, typ):  # 添加参数
        tmp = self.variableType(token.val, typ, -2)
        for key in list(self.variableDict.keys()):
            t = self.variableDict[key]
            self.variableDict[key] = self.variableType(t.name, t.type, t.addr - 2)
        self.variableDict[token.val] = tmp
        self.parametersDict[token.val]=tmp
        self.numOfParameters += 1


class SYMBOL:
    functionList = []  # Function 集合
    structList = []  # 结构体列表
    allList = []  # 保存结构体和函数
    globalNameList = []  # Function Struct name 集合方便查找重复定义情况
    structNameList = []  # 结构体名用于grammar中定义结构体变量的时候类型识别
    functionNameList=[]
    symDict = {}  # {name:secTable}    #用于生成目标代码时查找
    Message = namedtuple('Message', 'ErrorType Location ErrorMessage')
    def checkHasDefine(self, token):  # 定义的时候检查是否已经定义
        if token.val in self.globalNameList:
            ErrorType = 'Duplicate identified'
            Location = 'Location:line {line}'.format(line=token.cur_line+1)
            ErrorMessage = "variable '{token}' duplicate definition".format(token=token.val)
            self.Message(ErrorType, Location, ErrorMessage)
    def addFunction(self, token, returnType):  # 添加函数
        self.checkHasDefine(token)
        function = Function(token.val, returnType)
        self.functionList.append(function)
        self.allList.append(function)
        self.globalNameList.append(token.val)
        self.functionNameList.append(token.val)
        self.symDict[token.val] = function
        return self.Message
    def addStruct(self, token):  # 添加结构体
        self.checkHasDefine(token)
        st = Struct(token.val)
        self.structList.append(st)
        self.allList.append(st)
        self.globalNameList.append(token.val)
        self.structNameList.append(token.val)
        self.symDict[token.val] = st
        return self.Message
    def addVariableToTable(self, token, varType, doseParameter=False):  #添加新定义的变量
        tmp = self.allList[-1]
        if doseParameter:
            tmp.addPaVariable(token, varType)
        else:
            s = 0
            if varType == 'int':
                s = 2
            if varType in self.structNameList:
                s = self.symDict[varType].totalSize
            if '[' in token.val:
                _,n=token.val.split('[')
                n,_=n.split(']')
                num = eval(n)
                s *= num
                varType = 'array'
            tmp.addVariable(token, varType, s)

    def checkDoDefineInFunction(self, token):  # 检测函数中调用变量的时候变量是否存在
        function = self.functionList[-1]
        function.checkDoDefine(token)
        return function.Message

    def checkFunction(self, RES_TOKEN,id):  # 调用函数时候检查函数是否定义,参数个数是否正确，参数类型是否正确
        if RES_TOKEN[id].val not in self.globalNameList:
            ErrorType = 'Unknown identifier'
            Location = 'Location:line {line}'.format(line=RES_TOKEN[id].cur_line)
            ErrorMessage = "variable '{token}' has no definition".format(token=RES_TOKEN[id].val)
            Message = namedtuple('Message', 'ErrorType Location ErrorMessage')
            self.Message(ErrorType, Location, ErrorMessage)
            return self.Message
        else:
            temp_token = RES_TOKEN[id]
            para_num = 0
            while temp_token.val != ")":
                if temp_token.val == "(":
                    para_num = -1
                if (temp_token.val != ','):
                    para_num += 1;
                temp_token = RES_TOKEN[temp_token.id + 1]
            i=self.functionNameList.index(RES_TOKEN[id].val)
            fun = self.functionList[i]
            if (fun.numOfParameters != para_num):
                ErrorType = 'function argument number'
                Location = 'Location:line {line}'.format(line=RES_TOKEN[id].cur_line)
                ErrorMessage = "too many or too few arguement in function '{function}'".format(function=RES_TOKEN[id].val)
                return self.Message(ErrorType, Location, ErrorMessage)
            return self.Message(None,None,None)


    def showTheInfo(self):  # 打印符号表的信息
        for fun in self.functionList:
            print("function: %s. ReturnType %s. NumOfParameters %d. size %d"
                  % (fun.functionName, fun.returnType, fun.numOfParameters, fun.totalSize))
            for _, v in fun.variableDict.items():
                print("    variable: name %s type: %s addr: %s" % v)

        for struct in self.structList:
            print("struct: name %s size %d"
                  % (struct.structName, struct.totalSize))
            for _, v in struct.variableDict.items():
                print("    variable: name %s type: %s addr: %s" % v)
