# mips_assemble_tool
assemble, disassemble and generate .COE  
Mips Assemble Tool使用说明

**data文件夹与其中的文件与exe的相对位置不能发生改变，否则无法运行**

1.界面说明  
>左侧为汇编代码输入框，右侧为机器码(汇编结果)输入框，中间为按钮区域

2.功能说明
>Assemble：将左侧的汇编代码汇编为机器码，在右侧输出  
>Disassemble：将右侧的机器码反汇编为汇编代码，在左侧输出  
>Format asm：将左侧的汇编代码进行格式整理，整理为易读形式  
>Show/Hide Line：显示/隐藏行号，当任意一侧有行号时，会先将行号隐藏  
>Clear All：将两侧输入框内容清空  
>Load asm File：将本地的asm文件内容加载到左侧  
>Generate .COE：将左侧汇编代码汇编后按COE格式写入指定文件夹的output.COE文件中，若左侧汇编代码有错误时，则不会写入

3.程序特性及报错说明
>窗口大小为800×400，固定大小，无法缩放  
>两侧的输入框都可以撤销(CTRL+Z)和重做(CTRL+Y)  
>**实现了《数字设计和计算机体系结构》附录B中除了F类、mfc0、mtc0、bclf、bclt、lwcl、swcl外共53条指令，也许以后会补充**  
>详细的报错种类未区分，只会显示是哪一行出错了，也许以后会补充  
>当想要复制任意输入框的code时，请先隐藏行号，不然会将行号一并复制  
>Assemble、Disassemble和Format asm的结果是否带行号取决于点击前该输入框是否带行号  
>汇编(Assemble)之后，若汇编代码有错，则会在右侧报出错误行号，并自动显示左侧输入框的行号，此时Format asm，右侧的报错行号不会改变  
>反汇编(Disassemble)之后，若机器码有错，则会在左侧报出错误行号，并自动显示右侧输入框的行号  

ps：杀毒软件可能会报系统错误然后把exe删掉，别问，问就是pyinstaller的锅...恢复一下就行了。开发时间较短，可能会出一些神奇的bug233
