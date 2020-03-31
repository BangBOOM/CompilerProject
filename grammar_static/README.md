# The Grammar of C_Like_Language

## Some Definition
| Name | Mean | Type |
| :------| :------ | :------ |
| Program | 程序入口 | VN |
| Funcs | 函数定义 | VN |
| Type | 类型 | VN |
| ID | 标识符（非关键字） | VT |
| FormalParameters | 参数列表 | VN |
| CodeBody | 代码块 | VN |
| LocalDefineList | 变量申请 | VN |
| CodeList | 处理语句 | VN |
| Code | 语句块 | VN |
| NormalStatement | 变量赋值 | VN |
| Operation | 表达式语句 | VN |
| IfStatement | If语句 | VN |
| JudgeStatement | 判断 | VN |
| IFStatementFollow | else or else if | VN |
| ElsePart | else | VN |
| ElseIFPart | else if | VN |
| CompareSymbol | 比较符号 | VN |
| LoopStatement | 循环语句 | VN |
| FuncCall | 函数调用 | VN |
| Args| 参数 | VN|
| Struct | 结构体 |VN
|st | 结构体变量定义的时候规约使用 |VT 

## Main Function
+ 函数定义
+ while循环语句
+ if判断语句
+ 语句嵌套
+ 一个CodeBody中变量定义与变量调用目前必须是两个部分
+ 一个函数为一个模块不可以在函数之外声明语句
+ 考虑添加全局Global Variables模块
+ 支持int,float,char类型不支持数组
+ 函数传参不支持算术表达式

## Translation Grammar
+ 翻译文法用于翻译一整个函数，基于LL1文法添加语义
