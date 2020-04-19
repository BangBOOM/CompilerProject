from collections import namedtuple

Message = namedtuple('Message', 'ErrorType Location ErrorMessage')


class SecTable:
    def __init__(self):
        self.variableDict = {}  # 变量字典   key:name value:variableType
        self.variableType = namedtuple('variable', 'name type addr')
        self.totalSize = 0  # 整体变量占的空间方便汇编代码填写地址

    def addPaVariable(self, token, typ):  # 添加参数
        pass

    def addVariable(self, token, typ, s):  # 添加变量
        message = self.checkHasDefine(token)
        tmp = self.variableType(token.val, typ, self.totalSize)
        self.totalSize += s
        self.variableDict[token.val] = tmp
        return message

    def checkHasDefine(self, token):  # 检查重复定义问题
        if token.val in list(self.variableDict.keys()):
            ErrorType = 'Duplicate identified'
            Location = 'Location:line {line}'.format(line=token.cur_line + 1)
            ErrorMessage = "variable '{token}' duplicate definition".format(token=token.val)
            return Message(ErrorType, Location, ErrorMessage)
        return Message(None, None, None)

    def checkDoDefine(self, token):  # 检查是变量使用时是否定义
        if token.val not in list(self.variableDict.keys()):
            ErrorType = 'Unknown identifier'
            Location = 'Location:line {line}'.format(line=token.cur_line)
            ErrorMessage = "variable '{token}' has no definition".format(token=token.val)
            return Message(ErrorType, Location, ErrorMessage)
        return Message(None, None, None)


class Struct(SecTable):
    def __init__(self, name):
        super().__init__()
        self.structName = name


class Function(SecTable):
    def __init__(self, name, returnType):
        super().__init__()
        self.functionName = name  # 函数名
        self.numOfParameters = 0  # 参数数量
        self.parametersDict = {}  # 参数字典
        self.typeOfParametersList = []  # 参数类型列表
        self.returnType = returnType  # 返回值类型

    def addPaVariable(self, token, typ):  # 添加参数
        message = self.checkHasDefine(token)
        tmp = self.variableType(token.val, typ, -2)
        for key in list(self.variableDict.keys()):
            t = self.variableDict[key]
            self.variableDict[key] = self.variableType(t.name, t.type, t.addr - 2)
        self.variableDict[token.val] = tmp
        self.parametersDict[token.val] = tmp
        self.numOfParameters += 1
        return message


class SYMBOL:
    functionList = []  # Function 集合
    structList = []  # 结构体列表
    allList = []  # 保存结构体和函数
    globalNameList = []  # Function Struct name 集合方便查找重复定义情况
    structNameList = []  # 结构体名用于grammar中定义结构体变量的时候类型识别
    functionNameList = []
    symDict = {}  # {name:secTable}    #用于生成目标代码时查找

    def checkHasDefine(self, token):  # 定义的时候检查是否已经定义
        if token.val in self.globalNameList:
            ErrorType = 'Duplicate identified'
            Location = 'Location:line {line}'.format(line=token.cur_line + 1)
            ErrorMessage = "variable '{token}' duplicate definition".format(token=token.val)
            return Message(ErrorType, Location, ErrorMessage)
        return Message(None, None, None)

    def addFunction(self, token, returnType):  # 添加函数
        message = self.checkHasDefine(token)
        function = Function(token.val, returnType)
        self.functionList.append(function)
        self.allList.append(function)
        self.globalNameList.append(token.val)
        self.functionNameList.append(token.val)
        self.symDict[token.val] = function
        return message

    def addStruct(self, token):  # 添加结构体
        message = self.checkHasDefine(token)
        st = Struct(token.val)
        self.structList.append(st)
        self.allList.append(st)
        self.globalNameList.append(token.val)
        self.structNameList.append(token.val)
        self.symDict[token.val] = st
        return message

    def addVariableToTable(self, token, varType, doseParameter=False):  # 添加新定义的变量
        tmp = self.allList[-1]
        if doseParameter:
            message = tmp.addPaVariable(token, varType)
        else:
            s = 0
            if varType == 'int':
                s = 2
            if varType in self.structNameList:
                s = self.symDict[varType].totalSize
            if '[' in token.val:
                _, n = token.val.split('[')
                n, _ = n.split(']')
                num = eval(n)
                s *= num
                varType = 'array'
            message = tmp.addVariable(token, varType, s)
        return message

    def checkDoDefineInFunction(self, token):  # 检测函数中调用变量的时候变量是否存在
        function = self.functionList[-1]
        message = function.checkDoDefine(token)
        return message

    def checkFunction(self, RES_TOKEN, id):  # 调用函数时候检查函数是否定义
        if RES_TOKEN[id].val not in self.globalNameList:
            ErrorType = 'Unknown identifier'
            Location = 'Location:line {line}'.format(line=RES_TOKEN[id].cur_line)
            ErrorMessage = "variable '{token}' has no definition".format(token=RES_TOKEN[id].val)
            return Message(ErrorType, Location, ErrorMessage)
        else:
            temp_token = RES_TOKEN[id]
            para_num = 0
            while temp_token.val != ")":
                if temp_token.val == "(":
                    para_num = -1
                if (temp_token.val != ','):
                    para_num += 1;
                temp_token = RES_TOKEN[temp_token.id + 1]
            i = self.functionNameList.index(RES_TOKEN[id].val)
            fun = self.functionList[i]
            if (fun.numOfParameters != para_num):
                ErrorType = 'function argument number'
                Location = 'Location:line {line}'.format(line=RES_TOKEN[id].cur_line)
                ErrorMessage = "too many or too few arguement in function '{function}'".format(
                    function=RES_TOKEN[id].val)
                return Message(ErrorType, Location, ErrorMessage)
            return Message(None, None, None)

    def showTheInfo(self):  # 打印符号表的信息
        symbolTableInfoStr = []
        for fun in self.functionList:
            demo = "FuncName:{:<8s} ReturnType:{:<8s} NumOfParameters:{:<3d} Size:{:<3d}".format(
                fun.functionName, fun.returnType, fun.numOfParameters, fun.totalSize
            )
            symbolTableInfoStr.append(demo)
            for _, v in fun.variableDict.items():
                demo = "    VariableName:{:<8s} Type:{:<8s} Addr:{:<3d}".format(
                    v.name, v.type, v.addr
                )
                symbolTableInfoStr.append(demo)
        for struct in self.structList:
            demo = "StructName:{:<8s} Size:{:<3d}".format(
                struct.structName, struct.totalSize
            )
            symbolTableInfoStr.append(demo)
            for _, v in struct.variableDict.items():
                demo = "    VariableName:{:<8s} Type:{:<8s} Addr:{:<3d}".format(
                    v.name, v.type, v.addr
                )
                symbolTableInfoStr.append(demo)
        self.symbolTableInfo = symbolTableInfoStr
