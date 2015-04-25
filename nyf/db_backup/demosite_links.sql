-- MySQL dump 10.13  Distrib 5.5.41, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: demosite
-- ------------------------------------------------------
-- Server version	5.5.41-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `demosite_links`
--

LOCK TABLES `demosite_links` WRITE;
/*!40000 ALTER TABLE `demosite_links` DISABLE KEYS */;
INSERT INTO `demosite_links` VALUES (1,'sqlalchemy   ','http://www.cnblogs.com/bjdxy/archive/2012/11/24/2785654.html  ','2015-03-26'),(2,'DjangoAndSQLAlchemy    ','http://blog.liuts.com/post/93/','2015-03-26'),(3,'mysqlDataStructure','http://blog.chinaunix.net/uid-26330274-id-3249083.html','2015-03-26'),(4,'Django model list',' http://www.cnblogs.com/lhj588/archive/2012/05/24/2516040.html ','2015-03-26'),(5,'SQLAlchemy create table','http://www.2cto.com/kf/201108/101549.html ','2015-03-26'),(6,'SQLAlchemy book','http://www.zouyesheng.com/sqlalchemy.html   ','2015-03-26'),(7,'PostgreSQL','http://www.yiibai.com/html/postgresql/2013/080116.html','2015-03-26'),(8,'postgresql learning ','http://www.ruanyifeng.com/blog/2013/12/getting_started_with_postgresql.html','2015-03-26'),(9,'postgresbackup ','http://www.open-open.com/lib/view/open1385448336182.html    ','2015-03-26'),(10,'postgresbackup','http://www.cnblogs.com/wangbin/archive/2009/06/23/1509537.html','2015-03-26'),(11,'sqlalchemy',' http://gashero.yeax.com/?p=6#id14    ','2015-03-26'),(13,'PYTHON后台开发小结','http://blog.csdn.net/wengchzh/article/details/8523287','2015-03-26'),(14,'django DateTimeField和DateField和TimeField，auto_now=False和auto_now_add=False','http://www.douban.com/note/299260890/?type=like','2015-03-26'),(15,'django中文文档','http://django-chinese-docs.readthedocs.org/en/latest/','2015-03-26'),(16,' Django documentation','https://docs.djangoproject.com/en/1.7/','2015-03-26'),(17,'emacs配置','http://blog.chinaunix.net/uid-20592351-id-1620596.html','2015-03-27'),(18,'svn代码回滚命令','http://www.cnblogs.com/jndream/archive/2012/03/20/2407955.html','2015-03-29'),(19,'解决ubuntu中sublime text 2输入中文方法','http://jingyan.baidu.com/article/9225544687fe61851748f453.html','2015-03-30'),(20,'Ubuntu系统下Sublime Text 2中fcitx中文输入法的解决方法','http://www.linuxidc.com/Linux/2014-06/103855.htm','2015-03-30'),(21,'Ubuntu12.04安装并配置Sublime Text 2','http://www.cnblogs.com/fanyong/p/3462023.html','2015-03-30'),(22,' python中列表，元组，字符串如何互相转换','http://blog.csdn.net/sruru/article/details/7803208','2015-04-02'),(23,'python json格式字符串转换为python对象','http://outofmemory.cn/code-snippet/10876/python-convert-string-to-json-object','2015-04-02'),(24,'在线的项目管理和bug管理平台','http://project.tmlsystem.com:3000/','2015-04-06'),(25,'The Django Book 2.0--中文版','http://docs.30c.org/djangobook2/','2015-04-06'),(26,'python下的MySQLdb使用','http://drizzlewalk.blog.51cto.com/2203401/448874/','2015-04-06'),(27,'The Python Tutorial','https://docs.python.org/2/tutorial/','2015-04-06'),(28,'The Python interpreter and the extensive standard library','https://www.python.org/','2015-04-06'),(29,'Spark安装与学习','http://www.cnblogs.com/jerrylead/archive/2012/08/13/2636115.html','2015-04-07'),(30,'Scala Downloads: Index of /files/archive/','http://www.scala-lang.org/files/archive/','2015-04-07'),(31,'Spark 学习入门教程','http://blog.csdn.net/wankunde/article/details/41675079','2015-04-07'),(32,'Spark 简易入门教程（Java的微型Web框架）','http://www.oschina.net/question/5189_20641','2015-04-07'),(33,'Spark 学习入门教程','http://blog.csdn.net/wankunde/article/details/41675079','2015-04-07'),(34,'Android开发入门学习路线图','http://mobile.51cto.com/abased-377230.htm','2015-04-07'),(35,'欢迎来到 Flask 的世界','http://dormousehole.readthedocs.org/en/latest/','2015-04-07'),(36,'模拟GET/POST请求的工具','http://www.jingwentian.com/t-517','2015-04-08'),(37,'svn 命令行下常用的几个命令','http://blog.csdn.net/yangzhongxuan/article/details/7018168','2015-04-09'),(38,'SVN命令使用详解 ','http://blog.sina.com.cn/s/blog_963453200101eiuq.html','2015-04-09'),(39,'Python:数据库操作模块SQLAlchemy ','http://blog.sina.com.cn/s/blog_4ddef8f80101g6cl.html','2015-04-14');
/*!40000 ALTER TABLE `demosite_links` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-04-15 22:14:15
