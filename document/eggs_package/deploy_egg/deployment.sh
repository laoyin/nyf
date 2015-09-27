#!/bin/sh

#拷贝dash到/usr/local/lib/python2.7/dist-packages/
cd dash 
sudo python setup.py install 
cd ../
sudo cp -r dash /usr/local/lib/python2.7/dist-packages

#安装gflux到/usr/local/lib/python2.7/dist-packages/
sudo python setup.py install  
sudo rm -rf /usr/local/lib/python2.7/dist-packages/dash

#打包相关文件并解压到/usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/gflux
# gflux-0.1.0-py2.7.egg 其中的0.1.0为setup.py中设置的version
cd gflux
tar -cvf deployment.tar config lib live_auto_generate_static locale logs scripts tools collectstatic.sh collectstatic_manage.py crontab.conf dash debug_manage.py install.sh local_settings.py manage.py score_settings.py  
cd ../
sudo mv gflux/deployment.tar /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/
sudo tar -xvf  /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/deployment.tar  -C /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/
sudo rm /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/deployment.tar

#编译py文件为pyc 删除所有的py文件
python -c "import compileall; import re; compileall.compile_dir('/usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg', rx=re.compile(r'[/\\][.]svn'), force=True)"
# sudo rm -rfv  /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/*.py 
sudo rm -rfv  /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/*/*.py 
sudo rm -rfv  /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/*/*/*.py 
sudo rm -rfv  /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/*/*/*/*.py 
sudo rm -rfv  /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/*/*/*/*/*.py 
sudo rm -rfv  /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/*/*/*/*/*/*.py
sudo rm -rfv  /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/*/*/*/*/*/*/*.py

#拷贝启动脚本manage.py到/usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/gflux/
sudo cp gflux/manage.py /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/
sudo cp gflux/local_settings.py /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/
sudo cp gflux/gcustomer/server_rsa_private_key.pem /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/gcustomer/
sudo cp gflux/gcustomer/server_rsa_public_key.pem /usr/local/lib/python2.7/dist-packages/gflux-0.1.0-py2.7.egg/gcustomer/




