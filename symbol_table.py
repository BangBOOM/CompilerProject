from collections import namedtuple

class SYNBL:    #总表的结构
    def __init__(self,name,typ,cat,addr):
        self.name=name  #name标识符名字
        self.typ=typ    #typ指向类型表TAPEL
        self.cat=cat    #CAT种类【f-函数，c-常量，v-变量，vn-换名形参，vt-赋值形参】
        self.addr=addr  #偏移地址

    def name(self):
        return self.name

class TAPEL:    #类型表
    def __init__(self,TVAL,TPOINT):
        self.tval=TVAL  #类型代码【i-整型，c-字符型，b-布尔，a-数组】
        self.tpoint=TPOINT  #TPOINT根据不同的类型指向不同的信息表

class PFINEL:   #函数表
    def __init__(self,LEVEL,OFF,FN,PARAM,ENTRY):
        self.level=LEVEL    #层次号
        self.off=OFF        #自身数据区起始单元相对该函数值区区头的位置
        self.fn=FN          #形参个数
        self.param=PARAM    #指针，指向形参表
        self.entry=ENTRY    #函数目标程序首地址（运行时填写）

class AINFL:    #数组表
    def __init__(self,LOW,UP,CTP,CLEN):
        self.low=LOW    #数组的下界默认0
        self.up=UP
        self.ctp=CTP    #指针指向该维度数组成分类型
        self.clen=CLEN  #数据所占值单元的个数



class SymbolTable:
    SYNBL_TABLE={}



    # SYNBL=namedtuple('SYNBL',['name','typ','cat','addr'])   #总表，name标识符名字，typ指向类型表TAPEL，CAT种类【f-函数，c-常量，v-变量，vn-换名形参，vt-赋值形参】
    # TAPEL=namedtuple('TAPEL',['TVAL','TPOINT']) #类型表 tval 类型代码【i-整型，c-字符型，b-布尔，a-数组】TPOINT根据不同的类型指向不同的信息表

