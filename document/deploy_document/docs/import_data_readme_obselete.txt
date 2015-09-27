数据导入注意事项：

A：中油油站数据

1.all.txt 包含card.txt数据，但是缺少卡号那一列，可以导入all.txt之后再用card.txt更新卡号

2.数据意义

all.txt

410134,2013-07-30 22:17:10,300061,1,20,97号 车用汽油(Ⅲ),2.58,7.74,7.74,公升 20℃,5
交易号，时间，条形码，数量[非油品有效]，金额[油品有效]，商品名，体积[油品有效]，商品单价，金额[非油品有效]，商品单位，油枪号[油品有效]

card.txt

560038,9130200000140705,2014-05-21 09:42:12,70060719,4,18,康师傅 香菇炖鸡桶面 104G,1,4.5,18,桶,0
交易号，卡号，时间，条形码，数量[非油品有效]，金额[油品有效]，商品名，体积[油品有效]，商品单价，金额[非油品有效]，商品单位，油枪号[油品有效]


B:延长壳牌

1.数据意义
0,08,"2014-05-01 00:04:04",1,2518841,1,1,2,"03 - 93#汽油",7.5800,26.3900,200.0000,29.0600,"3",1,2354619,,,,
？，消息类型（08为交易消息），时间，？，交易编号，子消息编号，子消息类型[1为商品信息，0为结算信息]，消息对象类型[2为油品，14为非油品，16为交易总金额，7为交易方式]，消息对象名，单价，数量，金额，？，油枪号或条形码，？，？，？，？，？，？
0,08,"2014-05-01 00:04:04",1,2518841,2,1,2,"08 - 93#汽油",7.5800,26.3900,200.0000,29.0600,"8",1,2354618,,,,
？，消息类型（08为交易消息），时间，？，交易编号，子消息编号，子消息类型[1为商品信息，0为结算信息]，消息对象类型[2为油品，14为非油品，16为交易总金额，7为交易方式]，消息对象名，单价，数量，金额，？，油枪号或条形码，？，？，？，？，？，？
0,08,"2014-05-01 00:04:04",1,2518841,3,0,16,"销售总计",0.0000,0.0000,400.0000,0.0000,"0",,,,,,
？，消息类型（08为交易消息），时间，？，交易编号，子消息编号，子消息类型[1为商品信息，0为结算信息]，消息对象类型[2为油品，14为非油品，16为交易总金额，7为交易方式]，消息对象名，单价，数量，金额，？，油枪号或条形码，？，？，？，？，？，？
0,08,"2014-05-01 00:04:04",1,2518841,4,0,7,"现金",400.0000,1.0000,400.0000,0.0000,"1",,,,,,
？，消息类型（08为交易消息），时间，？，交易编号，子消息编号，子消息类型[1为商品信息，0为结算信息]，消息对象类型[2为油品，14为非油品，16为交易总金额，7为交易方式]，消息对象名，单价，数量，金额，？，油枪号或条形码，？，？，？，？，？，？

2.缺失的数据项
    1.unitname 商品单位==>将使用'unknow'代替
    2.barcode 为油品时条形码缺失==>将使用油枪号+商品名得出的字符串抽取出的数字拼接
    3.cardnum 刷卡卡号缺失，无法分析客户忠诚度

C:深圳胡腾达
1.数据意义
	交易号	油枪代码	商品代码	商品名	单价	startPumpNum	总量	金额	endPumpNum	交易时间	TeamCode	OilsupplierCode	Dealing_ID	ROAcc_ID	isReverse	InputType	upload	StartTime
1	1184320	23	60090935	393	7.4	119123.6	13.51	100	119137.1	06/30/13 09:55 PM	2013070101	[NULL]	[NULL]	[NULL]	0	1	2	06/30/13 09:55 PM

2.缺失的数据项
交易方式将使用现金类型，商品单位使用公升，因为所有的都是油品数据

d:SP集团
提供的xlsx文件,一个xlsx文件包含两个sheet:用户卡和员工卡,自带列名
1.数据意义
用户卡:
商品名,数量,单价,总价,时间,油枪号,操作员编号,账户时间?,卡号[会员卡],交易类型
content,         litter, price,  amount, opetime,        macno,openo,accountdate,    cardno,             paymode
93号汽油（Ⅳ）自助	49.86	7.65	381.43	6/1/2014 8:03	019	  13	6/2/2014 9:07	1000113500001800443	IC卡
员工卡:
同上,只是交易类型仅包含现金和银行卡

2.无效数据
检查发现有一批无效数据,特征如下:
litter=0
amount=0
直接丢掉?

3.缺失数据
交易号,这个可以根据excel数据编号自动生成
条形码,这个可以根据商品名自动hash生成
商品单位,自动填入公升,因为全是油品数据

RVL:
1.数据意义
油品：
时间，交易时间(没有作用，计算得到)，交易编号，(油枪号+商品名),单价，交易数量，金额，交易类型
非油品：
时间，交易编号，(油枪号+商品名),单价，交易数量，金额，交易类型
2.缺失数据：
条形码,这个可以根据商品名自动hash生成
商品单位,油品自动填入公升,非油品填入未知
没有卡号，这个必须要有的（****）

森美数据:
1.数据意义
油品
  站名  ,交易时间,  日结时间  ,交易类型 , 卡号 ,支付类型 ,'',卡余额 , 油枪  , 油品  , 单价 , 升数 , 金额  , '元', 总累 ,PSAM 序列号,日结时间  ,员工号 ,''
nodetag,opetime,accountdate,tracode,cardno,paymode,'',balance,macno,content,price,litter,amount,'元',pumpno,psam_ttc,accountdate,openo,''
'福州本部五一加油站','2013-11-1 00:06:04','2013-11-1 08:27:17','00','1000413500000035828','00',' ',29141046.78,'007','93号汽油（Ⅳ）',7.4,13.92,103.01,'元',7570887.56,104704,'2013-11-1 08:27:17','  02',' '
非油品
  报表时间    组织         组织名称         商品编码     商品名称                 条形码      数量  含税售价 含税进价 毛利 毛利率
2013-11-01	35010902	¸£ÖÝ³¤Í¡¼ÓÓÍÕ¾	000002	Óæ·òÖ®±¦ÌØÇ¿ÈóºíÌÇ±¡ºÉÎ¶25g	50357536	1	18	11.8	6.2	34.4444

2.缺失数据
油品:
交易编号(和PSAM 序列号有关系吗?)
交易方式,可以通过卡号算
条形码,这个可以根据商品名自动hash生成
商品单位,油品自动填入公升
这个表里有站名,上传时候和选择的站名不一致的话,是不是以表里的为准呢?
非油品:
没有卡号
条形码,给的数据超出了范围,所以取了后9位
交易方式
交易编号
商品单位
时间只有报表日期,跟据报表日期生成时间,另外报表日期只有年月日,所以十分秒是随机生成的

3.导入过程
a.数据预处理
由于一个文件包含了多个油站的数据,所以进行了数据预处理,将油站数据分开并滤除没用数据
文件共包含了六个油站的数据,分别是五一,六一,北门,连潘,泉塘,长汀
例如:
python manage.py deal_with_senmei_data --file='/home/yulongxue/员工卡1.txt' --save_path='/home/yulongxue'
--file为原文见  --save_path为整理后的数据保存的文件目录
预处理后应该在保存目录下存在了上述六个油站的txt文件,为整理后的数据文件
b.数据导入
例如:
python manage.py submit_senmei_task --file='/home/work/develop/gilbarco/trunk/data/连潘.txt' --site='FZ_LF' --site_desc='FZ_LF' --location_name='BJ_CN' --location_desc='北京' --user='tao'


B.中石化数据导入
a.数据预处理
windows下,安装sybase9，到dbisql目录下，执行python sinopec_trans_db.py,运行前先到sinopec_trans_db_setting.py
下进行目录设置
b.导入数据：
gearman_worker_import_sinopec_data
例如python manage.py submit_sinopec_task --user tao --site SXJFLSP --site_desc 山西晋府路站 --location_name SX_CN --location_desc 山西 --file /home/work/save.txt



=====================

导入的具体过程如下：

1.使用脚本导入原始交易数据到Trans表格中
cnpc    单个站使用import_cnpc_text_data.py   大批量[!!!请修改]使用import_cnpc_res.py
ycshell 单个站使用import_ycshell_text_data.py   大批量[!!!请修改]使用import_ycshell_res.py
sp集团   单个站使用import_sp_excel_data.py   批量使用import_sp_res.py

然后手动更新代码中的如下全局变量：

stations/reports.py:
        LOCATION
        LOCATION_SITE_NUM    select count(distinct(site)) from fact_trans where location=3;
        FuelType    select barcode, min("desc") from fact_trans where location=3 and pump_id>0 group by barcode;

stations/models.py
        G   select site, count(distinct(pump_id)) from fact_trans where location=3 and pump_id>0 group by site;


common/models.py
        Stations   select site from fact_trans where location=3 group by site;


2.生成card表
使用init_card_items.py

3.生成item表
使用init_item_items.py

4.相关性分析
使用compute_item_assoc.py
