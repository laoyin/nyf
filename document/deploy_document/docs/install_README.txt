注意此项目要求django 1.6
我们所开发的项目使用的1.5,使用virtualenv来进行虚拟环境的创建，在虚拟环境中使用pip或easy_install安装django 1.6来进一步开发该项目
注意运行pip或easy_install 时不要使用sudo，那样就跳出虚拟环境了
virtualenv的使用参考：http://mengzhuo.org/blog/virtualenv%E5%92%8Cpip%E5%B0%8F%E6%8E%A2.html

1.install postgresql and psycopg2==2.5.2, 方法见requirements_common.txt

2.configure postgresql

postresql操作见下面的文档:
http://blog.sina.com.cn/s/blog_6af33caa0100ypck.html

在ubuntu上以postgres账号启动命令行
sudo -u postgres psql
postgres=#  ALTER USER postgres WITH PASSWORD 'pku123';

在macos上安装Postgres的安装文件，之后点击图形界面的右下角的psql按钮起动类似psql

3.create user tao in postgres
postgres=# create user tao with password 'pku123'; #密码设置为local_settings.py配置的值

4.make tao to be superuser
postgres=# alter role tao with superuser;

5.create database 我们用一个数据库存储主控信息，第二个数据库以上存储数据，数据库名称账号密码与local_settings.py中相对应
create database gflux1;
create database gflux2;

在ubuntu或者centos的postgres网络服务模式下需要配置如下:
sudo vi /etc/postgresql/9.*/main/pg_hba.conf
modify peer to md5 from local
sudo service postgresql restart

6.import sql data
psql -U tao -f gflux.sql -d gflux 此命令已经作废
请阅读README中倒入数据的方法

7.configure django setting

请编辑local_settings.py中的数据库列表。

8.end

//=============新增库
django-localeurl


//===tips
查看当前命令
SELECT pg_stat_get_backend_pid(S.backendid) AS procpid,pg_stat_get_backend_activity(S.backendid) AS current_query FROM (SELECT pg_stat_get_backend_idset() AS backendid) AS S;

后台修改
nohup psql -d gflux -c 'update fact_trans set payment_type=3 where cardnum>=4000000000000000 and cardnum<6000000000000000;' &
