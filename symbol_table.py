from collections import namedtuple

Parameter=namedtuple('Parameter','Name Type DoseFormal ADDR')
class Fun:
    Name=""
    ReturnType=""           #返回类型
    ParameterNum=0          #参数个数
    ParameterNumTypeList=[] #参数类型列表
    ADDR=0                  #偏移地址
    ParametersDict={}
    def addParameterNum(self):
        self.ParameterNum+=1
    def setAddr(self,addr):
        self.ADDR=addr




class SYN:
    Funs=[]
    FunsName=[]




