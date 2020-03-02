# CompilerProject
NEU编译原理课设基于LL1文法,最终展示是用Django搭建的网站形式，本仓库不包含网页代码。

[网站链接](https://justyan.top/compiler/index)

网站使用时可以输入此文件[c_input](c_input)中的示例代码尝试，也可以根据本项目定义的文法使用。

网站功能，最上方是代码输入框，符号表，下一层是汇编代码，未优化的四元式，优化后的四元式。

## 主要功能

1. 支持类型：
    + 整形，初始化与赋值需要分开 
        + `int a;`
        + `a=10;`
    + 整形数组,不支持定义时赋值
        + `int a[10];`
        + `a[0]=10`;
    + 结构体，结构体中可包含整形，整形数组，具体结构体如何定义查看 [c_like_grammar](grammar_static/c_like_grammar)
        + ```
          struct Demo{
            int id[10];
            int gpa;
          };
          ```
2. 支持`while`循环,`if else/elif`判断，并且可嵌套
    + ```
      while(d<10){
        d=d+1;
        if(d>0){
        d=d-10;
        continue;
        }
        d=d-2;
        d=d-3;
        }
      ```
3. 支持函数定义调用，参数传递在数组和结构体时默认传递地址

## 词法分析
+ `lexer.py` 生成token序列，识别非法字符
+ `grammar.py` 语法分析 LL1自顶向下分析
    + 语法分析过程中进行变量冲突检测
    + 分析成功后将代码按照函数分块送入四元式生成函数
    + 最后拼接生成的四元式
+ `qt_gen.py` 四元式生成，输入的是一个函数块，在其内部再进行更小块的切分分别生成四元式
## 部分时间线 
+ 2019-12-12
    + 把LL1中的分析表用json格式的文件存储，每次调用直接从文件读取无需计算
    + 语法分析部分的工作基本完成，变量重复定义，未定义检验，函数调用部分未检验
+ 2019-12-13
    + 对函数调用的时候的参数个数进行检测，添加报错信息
    + 函数到四元式的转换
    + 四元式中添加变量的活跃信息
    + 函数调用部分转四元式
    + 返回信息转四元式
+ 2019-12-18
    + 四元式转目标代码
    + 目标代码跳转信息填写


## 文件介绍：
+ `lexer.py` 词法分析
+ `grammarParaser.py` 生成LL1分析表
+ `grammar.py` LL1语法分析，同时填写符号表，产生报错信息
+ `symbol_table.py` 符号表
+ `qt_gen.py` 四元式生成
+ `optimization.py` 四元式划分基本块，DAG优化
+ `asm_gen_x.py` 目标代码生成
  + 计算活跃信息，位置信息
  + 生成汇编代码过程中添加跳转信息
+ `clikercompiler.py` 程序入口
