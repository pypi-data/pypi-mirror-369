#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 25.03.17
import os,sys, cns
import winsound

class ProX(cns.sqlX):
    sqld = {}
    tmpl = {}
    def __init__(self, init_path='', **kwargs):
        SQLD = kwargs.get('sqld', {})
        TMPL = kwargs.get('tmpl', {})
        ProX.sqld.update(SQLD)
        ProX.tmpl.update(TMPL)

        self.str = init_path
        self.Beep = kwargs.get('Beep', None) # 提示音
        if self.Beep:
            winsound.Beep(800, 500) # 评率, 发生时长毫秒

        kwargs = dict(
            conn = kwargs.get('conn', 0),
            usr = kwargs.get('usr', 'test'),
            pwd = kwargs.get('pwd', 'test'),
            host = kwargs.get('host', 'localhost'),
            db = kwargs.get('db', 'test'),
            port = kwargs.get('port', 3306),
            conn_args = kwargs.get('conn_args', {'ssl':{}}),  # ssl:{'ca':"root.cer", 'cert':"user.cer", 'key':"user.key"}
            tmpl = ProX.tmpl
        ) 
        super().__init__(**kwargs)  # 调用父类的初始化方法 

        self.status = 0             # 系统状态 0 正常，其他不正常
        self.file_path = os.path.realpath(sys.argv[0])   # 文件完整路径
        self.file_dir = os.path.dirname(self.file_path)  # 文件所在目录
        self.file_name = os.path.splitext(os.path.basename(self.file_path)) #文件名

        self.timex = cns.DateTimeX(kwargs.get('date', None)) #.get("{[年月日.时分秒||复位]}")[2:]
        self.cmdx = cns.cmdX(self.file_dir)
        self.strx = cns.strX()


    def to_db(self, **kwargs):
        '''EXCEL, csv 文档写入数据库'''
        kwargs = dict(       
            path = kwargs.get('path', ''),       # 读取路径
            header = kwargs.get('header', 0),    # 表头行
            ydrop = kwargs.get('ydrop', 0),      # 删除列
            xdrop = kwargs.get('xdrop', 0),      # 删除行，合计
            mode = kwargs.get('mode', 'append'), # 模式: 增量|覆盖|覆盖+增量(多文件单表)  append | replace | repapp
            recol = kwargs.get('recol', 0),      # 需修改字段名
            columns = kwargs.get('columns', 0),  # 选择字段
            fnames = kwargs.get('fnames', 0),    # 文件名
            ext = kwargs.get('ext', None),       # 文件扩展名            
            tname = kwargs.get('tname', None),   # 目标表名Mysql
            addcol = kwargs.get('addcol', 0),    # 增加列，通常是日期 {'字段名':'值',}
            delrec = kwargs.get('delrec', 0),    # 根据表中某一列关键字删除数据,防止重复 {'时间':'2020', '来源':'慧眼'}
            filt_col_str = kwargs.get('filt_col_str', ['\n',',',' ','%']),  # 过滤字段中字符
            converters = kwargs.get('converters', None),  # 可以在读取的时候对列数据进行变换 converters={"编号": lambda x: int(x) + 10})
            # EXCEL部分
            sheet_name = kwargs.get('sheet_name', 0), # 读 取EXCEL插页名字 数字按插页索引,字符串按插页名字
            # csv 部分 -S
            sep = kwargs.get('sep', ',\t'),      # 分隔符
            dtype = kwargs.get('dtype', None),   # 指定字段的类型  {'c1':np.float64, 'c2': str})        
            encoding = kwargs.get('encoding', 'gb18030'),   # 字符编码 tab  'utf-16'
            engine = kwargs.get('engine', 'python'), # 解释引擎
            
            # 本类定义
            fm_copy = kwargs.get('fm_copy', 0),  # 复制表
            del_tab = kwargs.get('del_tab', 0),  # 删除 tname  
            )
        
        if self.status == 0:            
            fm_copy = kwargs.get("fm_copy", 0)   # 复制的模板表
            tname = kwargs.get("tname", None)    # 到目标表
            del_tab = kwargs.get("del_tab", 0)   # 删除表， 默认0 不删除
            
            if fm_copy:
                print('\n复制:', fm_copy)
                super().copy_tab(fm_copy, tname, del_tab=1)  # 复制表结构前--先删除表
            
            if del_tab:
                super().del_tab(tname)  # 删除表                 
            super().to_db(**kwargs)     # 写表
         
    def run_sqls(self, run_sql, SQLD=None):        
        ''' 批量执行SQL '''
        if SQLD==None:
            SQLD=self.sqld
        for index, (sql_nm, param) in enumerate(run_sql.items()):
            sql_nm = sql_nm.split('.')  # 取任务名
            print('执行:', sql_nm[0])
            if len(sql_nm) == 1:
                task_nm = sql_nm[0]
            else:
                task_nm = sql_nm[1]
            self.to_pro(task_nm, param=param, sqld=SQLD) # 任务名称, 参数, 主脚本  setdefault(key[,default])

    def to_pro(self, task_nm='任务名空', **kwargs):
        ''' 数据处理 '''
        if self.status == 0:            
            tname = kwargs.get("tname", None)   # 目标表            
            fm_copy = kwargs.get("fm_copy", 0)  # 复制表          
            del_tab = kwargs.get("del_tab", 0)  # 删除表， 默认0 不删除                  
            param = kwargs.get("param", None)   # 到目标表            
            sqld = kwargs.get("sqld", 0)        # 待执行的SQL            
            ren_tab = kwargs.get("ren_tab", 0)  # 重命名表名 

            to_copy = kwargs.get("to_copy", 0) 
            
            if del_tab:
                super().del_tab(tname)  # 删除表                
            if fm_copy:
                super().copy_tab(fm_copy, tname, del_tab=1) # 复制表            
            if sqld:
                sql = sqld[task_nm]

                param.setdefault("s1", '') # select * from 
                param.setdefault("s2", '') # select * from 

                param.setdefault("w1", '') # where1
                param.setdefault("w2", '') # where2
                if(param.get('w2')):
                    param.setdefault("(", '(')
                    param.setdefault(")", ')')
                else:
                    param.setdefault("(",'')
                    param.setdefault(")", '')
                    
                param.setdefault("s", param.get('s1','None')) 
                param.setdefault("w", param.get('w1','None')) # where1 
                param.setdefault("icol", '') # where2 
                param.setdefault("on2", param.get('on','None')) #
                param.setdefault("onMore", '') # select * from 
                             
                sql = sql.format(tname=tname, param=param, p=param)  # 格式化SQL ,3参数过度用
                super().run_sql(sql, task_nm = task_nm)              # 执行SQL

            if ren_tab:
                super().ren_tab(to_copy, ren_tab)           # 修改表名, 用于临时表修改正式表名


    def paste(self, **kwargs):
        ''' SQL 粘贴数据到指定插页单元格'''
        sql = kwargs.get("sql", '')               # sql代码
        param = kwargs.get("param", '')           # sql参数
        excel = kwargs.get("excel", '')           # excel对象
        sheet = kwargs.get("sheet", '')           # 插页名称
        paste_xy = kwargs.get("paste_xy", '')     # 粘贴位置
        header = kwargs.get("header", 0)          # 是否带表头
        split_col = kwargs.get("split_col", None) # 是否要分解字段到多行

        sql = sql.format(param=param, p=param)          
        df1 = self.read_sql(sql)               # data_type="list"
        if split_col is not None:
            df1 = super().split_col(df1,  split_col) 

        excel.set_sheet(sheet)
        excel.paste(df1, paste_xy, header=header)  # 粘贴(数据, 粘贴位置, 是否要表头)


    def __del__(self):
        if self.Beep:    
            winsound.Beep(900, 600) # 提示音(频率, 发生时长毫秒)
    
    
    # ----------------- sqld --------------------------24.10.26
    sqld['更新'] = "UPDATE `{p[t]}` SET {p[set]}"

    sqld['更新JOIN'] = ''' 
    UPDATE `{p[t]}` t1
    LEFT JOIN {p[(]}{p[s2]} `{p[f]}` {p[w2]}{p[)]} t2
    ON t1.`{p[on]}` = t2.`{p[on2]}` {p[onMore]}
    SET {p[set]}
    {p[w1]}
    '''

    sqld['更新join'] = ''' 
    UPDATE `{p[t]}` t1
    LEFT JOIN {p[(]}{p[s2]} `{p[f]}` {p[w2]}{p[)]} t2
    ON {p[on]}
    SET {p[set]}
    {p[w1]}
    '''

    sqld['SELECT建表'] = '''
    DROP TABLE IF EXISTS `{p[t]}`;
    CREATE TABLE `{p[t]}` AS
    SELECT
    {p[s]}
    FROM `{p[f]}` 
    {p[w]};
    '''

    sqld['插入'] = '''
    INSERT INTO `{p[t]}` 
    ({p[icol]})
    SELECT 
    {p[s]}
    FROM `{p[f]}` 
    {p[w]}
    '''
    sqld['创建索引'] = "CREATE INDEX 新索引 ON `{p[t]}` ({p[i]})"
    sqld['删除'] = "DELETE FROM `{p[t]}` WHERE {p[w]} "
    
    sqld['添加字段'] = "ALTER TABLE `{p[t]}` ADD COLUMN {p[col]}"      # {'t':'目标表', 'col':"`实际_商品GMV_自营`"}
    sqld['删除字段'] = "ALTER TABLE `{p[t]}` DROP COLUMN {p[col]}"     # {'t':'目标表', 'col':"`实际_商品GMV_自营` double(18,6) DEFAULT NULL"}
    sqld['修改字段'] = "ALTER TABLE `{p[t]}` CHANGE COLUMN {p[col]}"   # {'t':'目标表', 'col':"`实际_商品GMV_自营` `修改后的名字` double(18,6) DEFAULT NULL"}

    # ----------------- tmpl --------------------------24.11.15
    tmpl['select'] = {'头部':'select', '模板':"{连接2} {符}{前缀}{值}{后缀}{符}",  '连接':','} # ok
    tmpl['col'] = { '模板': "{连接2} {符}{前缀}{值}{后缀}{符}", '连接':','}     # ok     '符s':'检查', '符i':'插入' 
    tmpl['strin'] = {'模板': "{连接2}'{值}'",  '连接':',', '分割':' '} # ok
    tmpl['sum'] = {'模板': "{连接2}{名字}(`{值}`) as '{值}'", '连接':','} # ok
    tmpl['isum'] = { '模板': "{连接2}{符}{值}{符2} ", '连接':',', '符s':'as' ,'符i':'IFNULL(SUM(`' , '符2s':'as' ,'符2i':"`),0) as '{值}'"  }  # ok
    tmpl['max'] = {'模板':"{连接2}{前缀}{名字}(`{值}`){后缀} as '{值}'", '连接':','} # ok
    tmpl['on'] = {'模板': "{连接2} t1.`{值}`= t2.`{值}`",  '连接':' AND '} # ok
    tmpl['onx'] = {'模板': "{连接2} t1.`{值}`= t{计数x2}.`{值}`",  '连接':' AND '} # ok
    tmpl['un'] = {'头部':'SELECT * FROM(', '连接':'UNION ALL', '模板': "{连接2}\n{值}", '尾部':')t ORDER BY 1'}  # ok
    tmpl['un2'] = {'模板': "{连接2}SELECT\n*\nFROM `{前缀}{值}{后缀}`",'连接':'UNION ALL \n', '头部':'SELECT\n*\nFROM(', '尾部':')t1 ORDER BY 1'} #ok
   
    tmpl['删表'] = {'模板':"DROP TABLE IF EXISTS `{值}`;"}
    tmpl['建表'] = {'头部':'CREATE TABLE `{表名}` (', '模板':"{连接2} {符}{前缀}{值}{后缀}{符} {数据类型}" , '连接':',', '尾部':'\n)', '数据类型':'varchar(32) DEFAULT NULL'} #ok
    
    tmpl['增数据'] = {'头部':'INSERT INTO `{表名}` (', '模板': "{连接2} {符}{前缀}{值}{后缀}{符}", '连接':',', '尾部':')'}  # ok
    tmpl['删数据'] = {'模板':'DELETE FROM `{{表名}}` WHERE {值};'}   # ok
    tmpl['改数据'] = {'头部':'UPDATE `{{表名}}` SET ', '模板':"{连接2}{值}", '连接':',', '尾部':';'}
    
    tmpl['alter'] = {'模板':"ALTER TABLE {符}{前缀}{值}{后缀}{符} {字段}; "}    # ok
    tmpl['column'] = {'模板':"{连接2}{指令} COLUMN {符}{前缀}{值}{后缀}{符} {数据类型}", '连接':',', '符s':'`', '符i':'`' }   # ok

    tmpl['增字段'] = {'头部':'ALTER TABLE `{表名}`', '模板':"{连接2}ADD {符}{前缀}{值}{后缀}{符} {数据类型}", '连接':','}   # '模板':"{连接2} ADD `{值[0]}` {值[1]}"
    tmpl['删字段'] = {'头部':'ALTER TABLE `{表名}`', '模板':"{连接2}DROP COLUMN {符}{前缀}{值}{后缀}{符}", '连接':','}
    tmpl['改字段'] = {'头部':'ALTER TABLE `{表名}`', '模板':"{连接2}CHANGE COLUMN {值[0]} {值[1]} {值[2]} ", '连接':','}  # [ ['原字段名', '新字段名', '数据类型'], ]
    tmpl['改类型'] = {'头部':'ALTER TABLE `{表名}`', '模板':"{连接2}MODIFY COLUMN {符}{前缀}{值}{后缀}{符} {数据类型}", '连接':',', '前缀':'', '后缀':'', '符s':'`', '符i':'`' }  # price DECIMAL(6,2)

    tmpl['增索引'] = {'头部':'ALTER TABLE `{表名}`', '模板':"{连接2}ADD INDEX {前缀}{值}{后缀} ({符}{值}{符})", "连接":','}
    tmpl['删索引'] = {'头部':'ALTER TABLE `{表名}`', '模板':"{连接2}DROP INDEX {前缀}{值}{后缀}", "连接":','}    

    tmpl['内连接'] = {'头部':'INNER JOIN `{表名}` t2 ON', '模板':"{连接2} t1.{符}{值}{符}= t{计数x2}.{符}{值}{符}",  '连接':' AND '}
    tmpl['左连接'] = {'头部':'LEFT JOIN  `{表名}` t2 ON', '模板':"{连接2} t1.{符}{值}{符}= t{计数x2}.{符}{值}{符}",  '连接':' AND '}
    tmpl['右连接'] = {'头部':'RIGHT JOIN `{表名}` t2 ON', '模板':"{连接2} t1.{符}{值}{符}= t{计数x2}.{符}{值}{符}",  '连接':' AND '}
    tmpl['全连接'] = {'头部':'RFULL OUTER JOIN `{表名}` t2 ON', '模板':"{连接2} t1.{符}{值}{符}= t{计数x2}.{符}{值}{符}",  '连接':' AND '} 



if __name__ == '__main__':
    X = ProX()
    print(X.timex)

    names1 = ['24年预算_1_7月','24年预算_8月','24年预算_9月','24年预算_10_12月']  # 预算
    names2 = ['23年实际','24年实际_1_4月','24年实际_5月','24年实际_6月','24年实际_7月','24年实际_8月','24年实际_9月','24年实际_10月']  # 实际
    dirNames = names1+names2
    

    字段清单 = '''
    实际_自营_广告-收入
    实际_整体_广告-收入
    '''
    表名清单 = ['abc']

    #--- 多表多字段组合增删改
    def 生成SQL(指令, 字段清单, 表名清单, 数据类型="double(18,6) DEFAULT NULL", 表名前缀="x16_0总部毛利s0_"):
        sql = X.column(字段清单,{'指令':指令, '数据类型':数据类型})           # 步骤1-添加字段  varchar(12) DEFAULT NULL
        sql = X.alter(表名清单,  {'表名前缀':表名前缀, '字段':str(sql)} )     # 步骤2-添加表名  double(18,6) DEFAULT NULL
        return sql
    
    print( 生成SQL('DROP', 字段清单, 表名清单,'') )    # 删除字段
    print( 生成SQL('CHANGE', 字段清单, 表名清单,'') )  # 修改字段名和数据类型
    print( 生成SQL('ADD', 字段清单, 表名清单,'varchar(12) DEFAULT NULL') )    # 增加字段
    print( 生成SQL('MODIFY', 字段清单, 表名清单,'varchar(12) DEFAULT NULL') )  # 改数据类型

    #sql = X.strin('A,B,C')
    #print(sql)
    print(X.sum("A,B,C"))
