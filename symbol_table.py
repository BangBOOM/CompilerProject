from collections import namedtuple

Parameter=namedtuple('Parameter','Name Type DoseFormal ADDR')
class Fun:
    Name=""
    ReturnType=""           #返回类型
    ParameterNum=0          #参数个数
    ParameterNumTypeList=[] #参数类型列表
    ADDR=0                  #偏移地址
    ParametersDict={}
    def __init__(self,Name,ReturnType,addr):
        self.Name=Name
        self.ReturnType=ReturnType
        self.ADDR=addr


    def addParameterNum(self):
        self.ParameterNum+=1
    def setAddr(self,addr):
        self.ADDR=addr




class SYN:
    Cur_Addr=0
    Funs=[]
    FunsName=[]


    def incCurAddr(self):
        self.Cur_Addr+=1
        return self.Cur_Addr

    def addFunc(self,Name,ReturnType,cur_line):
        if Name in self.FunsName:
            raise ValueError("error: define the func repeatedly in line:",cur_line+1)
        else:
            fun=Fun(Name,ReturnType,self.incCurAddr())
            self.Funs.append(fun)
            self.FunsName.append(Name)







