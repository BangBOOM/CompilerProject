# CompilerProject
NEU编译原理课设
## 词法分析
+ `lexer.py` 生成token序列，识别非法字符
+ `grammar.py` 语法分析 LL1自顶向下分析
    + 语法分析过程中进行变量冲突检测
    + 分析成功后将代码按照函数分块送入四元式生成函数
    + 最后拼接生成的四元式
+ `qt_gen.py` 四元式生成，输入的是一个函数块，在其内部再进行更小块的切分分别生成四元式 

+ 把LL1中的分析表用json格式的文件存储，每次调用直接从文件读取无需计算
+ 语法分析部分的工作基本完成，基本的定义出错检验
+ 四元式部分对语义进行进一步检验，函数传参个数等问题。