import copy
'''
四元式的优化
'''

class Optimization:
    def __init__(self,sym):
        self.symTable=sym       #符号表


    def opt(self,funcBlock):    #每次传入一个函数块，把这个函数块分成基本块并优化
        fBlock=copy.copy(funcBlock)
        res=[]         #二维 res[bloc bloc]
        bloc=[]        #存放基本块
        while fBlock:
            tmp=fBlock.pop(0)
            if tmp[0] in ['wh']:
                res.append(bloc)
                bloc=[tmp]
            elif tmp[0] in ['do','we','if','el','elif','ie','return']:
                bloc.append(tmp)
                res.append(bloc)
                bloc=[]
            elif tmp[0]=="FUN":
                res.append([tmp])
            else:
                bloc.append(tmp)
        # for b in res:
        #     self.optTheBloc(b)
        return  res


    # def optTheBloc(self,bloc):
    #     '''
    #     这部分对基本块进行优化
    #     :param bloc:
    #     :return:
    #     '''












