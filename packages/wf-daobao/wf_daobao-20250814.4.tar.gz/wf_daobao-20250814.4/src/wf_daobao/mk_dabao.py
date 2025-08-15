# -*- encoding:utf-8 -*-
import json
import os
import shutil
import datetime
import sys
import pyperclip
# if __package__:  
from wf_daobao import json_peizhilei
# else:
# import json_peizhilei
#生成安装包 pipreqs .
#pip install -r requirements.txt
#pip install pyinstaller==5.8.0

class DaoBao:
    def __init__(self,lj=""):
        self.lj=lj
        #主文件绝对路径
        self.运行文件绝对路径  = os.path.realpath(sys.argv[0])
        self.根目录 = os.path.dirname(self.运行文件绝对路径)
        self.创建打包附件文件夹(lj=self.lj)
        
        self.入口文件绝对路径=os.path.join(self.待打包位置位置,self.主文件名) 
        #时间
        self.日期格式化=str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    def 判断是否根目录(self,lj=""):
        if os.path.exists(lj):            
            根目录=lj
        else:
            根目录=self.根目录
        print("根目录",根目录)
        
        return 根目录
    def 创建附件目录(self,lj=""):
        self.打包附件路径 = os.path.join(lj,"________打包附件")
        if os.path.isdir(self.打包附件路径)==False:
            os.mkdir(self.打包附件路径) 
        self.配置路径=os.path.join(self.打包附件路径, "________打包附件.json")
         # json创建配置文件--------------------------
        self.peizhi=json_peizhilei.Peizhi(lj=self.配置路径)
        return self.打包附件路径
    def 创建打包附件文件夹(self,lj=""):
        self.根目录s=self.判断是否根目录(lj=lj)
        self.创建附件目录s=self.创建附件目录(lj=self.根目录s)
        
        self.peizhi字典=self.peizhi.读取配置(mrz=[])

        self.待打包位置位置=self.peizhi字典.get("待打包位置位置")
        self.虚拟环境位置=self.peizhi字典.get("虚拟环境位置")
        self.虚拟环境文件夹名称=self.peizhi字典.get("虚拟环境文件夹名称")
        self.主文件名=self.peizhi字典.get("主文件名")
        self.py模版字典=self.peizhi字典.get("py模版字典")
        self.配置列表=self.peizhi字典.get("配置列表")
      
        




    def tjmk(self,mm):
        """1生成：绝对路径和模块名"""
        #模块绝对名路径
        zhs0=os.path.join(self.待打包位置位置,mm).replace("\\","/")
        # zhs0=os.path.abspath(mm)
        #模块名
        wjm=os.path.basename(zhs0)
        zhs1=wjm.split(".")[0]
        zhs2="-p {0} --hidden-import {1} ".format(zhs0,zhs1)
        return zhs2
    def get_folder_name(self,path):
        """取文件夹名"""
        # 使用 os.path.basename 获取路径的最后一个部分
        # 如果路径以斜杠结尾，则先使用 os.path.dirname 去掉最后的斜杠（如果需要）
        # 不过 os.path.basename 本身对这种情况也是安全的
        folder_name = os.path.basename(os.path.normpath(path))
        return folder_name
    def scml(self,模块文件字典,入口文件绝对路径,配置文件列表):    
        """2.添加模块"""
        #主文件绝对路径
        strs=入口文件绝对路径
        #模块名{}    
        if 模块文件字典!=False: 
            for i in 模块文件字典:
                strs+=" {}".format(self.tjmk(模块文件字典.get(i)))
        #--add-data="data:data"
        if 配置文件列表!=False:
            for j in 配置文件列表:
                peizhi=os.path.join(self.待打包位置位置,j).replace("\\","/") 
                # peizhi=os.path.abspath(j)
                if os.path.isfile(peizhi):
                    j="."
                else:
                    j=self.get_folder_name(j)
                strs+=' --add-data="{};{}"'.format(os.path.abspath(peizhi).replace("\\","/"),j)
        return strs

   
    def 生成打包命令(self,入口文件绝对路径,模块文件字典,配置文件列表,日期格式化,dblj,wjm="3.打包命令.txt",shu="4"):
        """3.文件名，时间，模块文件名，主文件名"""
        xnlj=os.path.join(dblj,wjm)
        tt=open(xnlj,"w")
        tt.write("-------打包时间：{}-------\npip install pyinstaller==5.13.0\n".format(日期格式化))
        入口文件绝对路径=入口文件绝对路径.replace("\\","/")
        tt.write("-----------------------\n1.单文件，无黑框\n")
        单文件无黑框=r"pyinstaller -F -w {}".format(self.scml(模块文件字典,入口文件绝对路径,配置文件列表))
        tt.write(单文件无黑框)

        tt.write("\n\n2.单文件，有黑框\n")
        单文件有黑框=r"pyinstaller -F {}".format(self.scml(模块文件字典,入口文件绝对路径,配置文件列表))
        tt.write(单文件有黑框)

        tt.write("\n\n3.多文件，无黑框\n")
        多文件无黑框=r"pyinstaller -w {}".format(self.scml(模块文件字典,入口文件绝对路径,配置文件列表))
        tt.write(多文件无黑框)

        tt.write("\n\n4.多文件，有黑框\n")
        多文件带有黑框=r"pyinstaller {}".format(self.scml(模块文件字典,入口文件绝对路径,配置文件列表))
        tt.write(多文件带有黑框)

        tt.close()
        
        jg=""
        if shu=="1":
            jg=单文件无黑框
        elif shu=="2":
            jg=单文件有黑框
        elif shu=="3":
            jg=多文件无黑框
        elif shu=="4":
            jg=多文件带有黑框
        print(wjm,"完成")
        return jg
        




    def yinhangpeizhifuzhi(self,yuanwenjian,mubiaowenjian):
        """复制：源文件，目标文件"""
        ywj1=os.path.abspath(yuanwenjian)
        mbwj1=mubiaowenjian
        shutil.copy(ywj1,mbwj1)
        print("-------\n源路径：{}\n复制到目录路径：{}-------".format(ywj1,mbwj1))


    def 创建虚拟环境(self,虚拟环境文件夹,dblj,wjm="4创建虚拟环境.bat"):
        """导出包:xnhj：虚拟环境路径,dblj:附件文件夹,wjm:文件名"""
        xnstr="""
    cd /d {1}
    python -m venv {0}
    cd {1}/{0}
    echo cmd /k "{1}/{0}/Scripts/activate.bat" > new_script.bat
    cmd /k "{1}/{0}/Scripts/activate.bat"
    """.format(虚拟环境文件夹,self.虚拟环境位置)
        xnlj=os.path.join(dblj,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        print(wjm,"完成")
    def 启动虚拟环境(self,虚拟环境文件夹,dblj,wjm="5启动虚拟环境.bat"):
        """导出包:xnhj：虚拟环境路径,dblj:附件文件夹,wjm:文件名"""
        xnstr='cmd /k "cd /d {1}/{0} && {1}/{0}/Scripts/activate.bat"'.format(虚拟环境文件夹,self.虚拟环境位置)
        xnlj=os.path.join(dblj,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        print(wjm,"完成")
    def 打开文件夹(self,虚拟环境文件夹,dblj,wjm="6打开文件夹.bat"):
        """导出包:xnhj：虚拟环境路径,dblj:附件文件夹,wjm:文件名"""
        xnstr='start {1}/{0}'.format(虚拟环境文件夹,self.虚拟环境位置)
        xnlj=os.path.join(dblj,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        print(wjm,"完成")

    def 导出包(self,xnhj,dblj,wjm="7.导出包.bat"):
        """导出包:xnhj：虚拟环境路径,dblj:附件文件夹,wjm:文件名"""
        #f_path2:附件文件夹，xnhj：虚拟环境路径
 
        xnstr='cmd /k "cd /d {0} && {2}/{1}/Scripts/activate.bat && pip freeze > requirements.txt"'.format(dblj,xnhj,self.虚拟环境位置)
        xnlj=os.path.join(dblj,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        print(wjm,"完成")
    def 批量安装包(self,xnhj,dblj,wjm="2.4.批量安装包.bat"):
        """导出包:xnhj：虚拟环境路径,dblj:附件文件夹,wjm:文件名"""
        xnstr='cmd /k "cd /d {0} && {2}/{1}/Scripts/activate.bat && pip install -r requirements.txt"'.format(dblj,xnhj,self.虚拟环境位置)
        xnlj=os.path.join(dblj,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        print(wjm,"完成")

    #递归导出包名
    def diguibianli(self,lj):
        for root, dirs, files in os.walk(lj):
            for file in files:
                wj=os.path.join(root,file)
                if wj.endswith(".py") :               
                    if os.path.isfile(wj):
                        print(wj)
    #print(os.listdir(lj))
    #导出包名
    def bianli(self,lj,dblj,wjm="2.导出包名.txt"):
    #主文件绝对路径
        运行文件绝对路径  = os.path.realpath(sys.argv[0])
        print("运行文件绝对路径:",运行文件绝对路径)
        运行文件上一级路径 = os.path.dirname(运行文件绝对路径)
        strs1=""
        strs2="pip install pyinstaller==5.8.0\n"
        for i in os.listdir(lj):
            ljs = os.path.join(运行文件上一级路径,i)
            if ljs.endswith(".py") and ljs.endswith("00_打包附件.py")==False:               
                if os.path.isfile(ljs) :
                    with open(ljs,"r",encoding="utf-8") as wj:
                        s=0
                        for j in wj:
                            s+=1
                            if j.find("import") != -1 and j[0].find("#") ==-1:   
                                if strs1.find(j.strip()) ==-1:
                                    strs1+=j  
                                    strs2+=j.replace("import", "pip install") 
        xnlj=os.path.join(dblj,wjm)           
        with open(xnlj,"w",encoding="utf-8") as xwj:
            xwj.write(strs2)                        
        return strs2
    def bianli2(self,lj,dblj,wjm="2.2导出包名pipreqs.bat"):
        # file_path  = os.path.realpath(sys.argv[0])
        # f_path1 = os.path.dirname(file_path)
        strs2='cmd /k "cd /d {} &&  pipreqs .'.format(lj)
        xnlj=os.path.join(dblj,wjm)
        with open(xnlj,"w",encoding="gbk") as xwj:
            xwj.write(strs2)   
        print(wjm,"完成")                   
        return strs2
    def 打包工具安装(self,xnhj,dblj,wjm="2.3打包工具安装_pyinstaller_5.8.bat"):
        xnstr='cmd /k "cd /d {1}/{0} && {1}/{0}/Scripts/activate.bat && pip install pyinstaller==5.8.0"'.format(xnhj,self.虚拟环境位置)
        xnlj=os.path.join(dblj,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        print(wjm,"完成")
    def pandas安装(self,xnhj,dblj,wjm="2.1.pandas安装_.bat"):
        xnstr='cmd /k "cd /d {1}/{0} && {1}/{0}/Scripts/activate.bat && pip install pandas==2.2.3 && pip install openpyxl==3.1.2 && pip install xlrd==2.0.1"'.format(xnhj,self.虚拟环境位置)
        xnlj=os.path.join(dblj,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        print(wjm,"完成")
    def 加密模块(self,xnhj,dblj,wjm="10.加密模块.bat"):
        lj=os.path.join(dblj,wjm)
        wz="""
@echo off
chcp 65001 > nul
REM 切换到上级目录
cd /d ..
echo 当前目录已切换至：%cd%
REM 遍历并加密所有.py文件
for %%f in (*.py) do (
    echo 正在加密文件：%%f
    pyarmor g "%%f"
)
echo 所有.py文件加密完成
pause
"""
        with open(lj,"w",encoding="utf-8") as pp:
            pp.write(wz)
        
    def 生成打包附件(self,待打包位置=""):
        待打包位置=r"{}".format(待打包位置)
        self.创建打包附件文件夹(lj=待打包位置)
        print("待打包位置:",self.创建附件目录s)
        #复制config.xls
        #self.yinhangpeizhifuzhi("config.xls",r"D:\xn\yin_hang\dist\config.xls")
        #self.yinhangpeizhifuzhi("config.xls",r"D:\xn\yin_hang_win7.38\dist\config.xls")
        #生成pyinstaller
        
        self.创建虚拟环境(self.虚拟环境文件夹名称,self.创建附件目录s,wjm="2.创建虚拟环境.bat")
        self.启动虚拟环境(self.虚拟环境文件夹名称,self.创建附件目录s,wjm="3.启动虚拟环境.bat")
        self.打开文件夹(self.虚拟环境文件夹名称,self.创建附件目录s,wjm="4.打开文件夹.bat")        
        self.pandas安装(self.虚拟环境文件夹名称,self.创建附件目录s,wjm="5.安装pandas_openpyxl_xlrd.bat")
        self.打包工具安装(self.虚拟环境文件夹名称,self.创建附件目录s,wjm="6.安装打包工具_pyinstaller_5.8.bat")
        self.bianli2(self.待打包位置位置,self.创建附件目录s,wjm="7.1安装前导出模块名pipreqs.bat")
        self.导出包(self.虚拟环境文件夹名称,self.创建附件目录s,wjm="7.2安装后导出模块名.bat")
        self.批量安装包(self.虚拟环境文件夹名称,self.创建附件目录s,wjm="8.批量安装包.bat")
        # self.bianli(运行文件上一级路径,打包附件路径,wjm="2.1.导出包名.txt")
        self.生成打包命令(os.path.join(self.待打包位置位置,self.主文件名) ,self.py模版字典,self.配置列表,self.日期格式化,dblj=self.创建附件目录s,wjm="9.--------打包代码--------.txt")        
        self.加密模块(self.虚拟环境文件夹名称,self.创建附件目录s,wjm="10.加密模块.bat")
        print("完成！")

def main(): 
    路径=input("请录入路径:>>") 
    if 路径=="":
        daobao=DaoBao()
    else:
        daobao=DaoBao(r"{}".format(路径))
    zfc="""=================================
    请输入:【首次请选1】
    【1.生成打包附件】
    【2.创建虚拟环境.bat】
    【3.启动虚拟环境.bat】
    【4.打开文件夹.bat】
    【5.安装pandas_openpyxl_xlrd.bat】
    【6.安装打包工具_pyinstaller_5.8.bat】
    【7.1安装前导出模块名pipreqs.bat】
    【7.2安装后导出模块名.bat】
    【7.3把requirements.txt复制到打包附件文件夹中】
    【8.批量安装包.bat】
    【9.复制代码：多文件带有黑框】    
    【10.加密模块.bat】    
    【0.退出】\n>>"""
    while True:
        jg=input(zfc)
        if jg=="0":
            break
        elif jg=="1":
            daobao.生成打包附件(待打包位置=daobao.判断是否根目录(lj=daobao.lj))
        elif jg=="2":
            os.startfile(os.path.join(daobao.创建附件目录s,"2.创建虚拟环境.bat"))
        elif jg=="3":
            os.startfile(os.path.join(daobao.创建附件目录s,"3.启动虚拟环境.bat"))
        elif jg=="4":
            os.startfile(os.path.join(daobao.创建附件目录s,"4.打开文件夹.bat"))
        elif jg=="5":
            os.startfile(os.path.join(daobao.创建附件目录s,"5.安装pandas_openpyxl_xlrd.bat"))
        elif jg=="6":
            os.startfile(os.path.join(daobao.创建附件目录s,"6.安装打包工具_pyinstaller_5.8.bat"))
        elif jg=="7.1":
            os.startfile(os.path.join(daobao.创建附件目录s,"7.1安装前导出模块名pipreqs.bat"))
        elif jg=="7.2":
            os.startfile(os.path.join(daobao.创建附件目录s,"7.2安装后导出模块名.bat"))
        elif jg=="7.3":
            shutil.copy(os.path.join(daobao.lj, "requirements.txt"), os.path.join(daobao.创建附件目录s, "requirements.txt"))
        elif jg=="8":
            os.startfile(os.path.join(daobao.创建附件目录s,"8.批量安装包.bat"))
        elif jg=="9":
            pyperclip.copy(daobao.生成打包命令(os.path.join(daobao.待打包位置位置,daobao.主文件名) ,daobao.py模版字典,daobao.配置列表,daobao.日期格式化,dblj=daobao.创建附件目录s,wjm="9.--------打包代码--------.txt"))   
            print("复制完成！") 
        elif jg=="10":
            os.chdir(daobao.创建附件目录s)
            os.startfile(os.path.join(daobao.创建附件目录s,"10.加密模块.bat"))
        else:
            print(zfc)
            # 
        
if "__main__"==__name__: 
    main()  
    
    
   
