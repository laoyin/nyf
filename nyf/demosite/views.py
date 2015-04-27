#coding=utf-8 
from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from django import forms
from demosite.models import *
import pdb,sys
from django.template import Template,RequestContext
from django.template.loader import get_template
import json
from django.core.files.base import ContentFile 
from django.conf import settings
#文件名
variable={}
DEMOSITE = "demosite/"
#登录页面
def loginpage(request):
    return render_to_response('%slogin_page.html'%DEMOSITE)

#登录验证
def logincheck(request):
    rsdic={}
    username=request.POST['username']
    password=request.POST['password']
    try:
        account=customer.objects.filter(name=username)
        if len(account)==0:
            rsdic['ret']='1103'
            rsdic['info']='user no exist!'
        if account[0].password != password :
            rsdic={'ret':'1104','info':'password is wrong!'}
        else:
            rsdic={'ret':'1101','info':'ok','username':username}
    except:
        rsdic={'ret':'1105','info':'user no exist!'}
    finally:
        return HttpResponse(json.dumps(rsdic))
    
#加载首页 
def indexload(request):
        link_list=Links.objects.all()
        return render_to_response('%sdemosite_admin.html'%DEMOSITE,{'link_list':link_list})

#注册页面
def registerload(request):
    return render_to_response('%sregisterpage.html'%DEMOSITE)

#注册处理
def register(request):
    rsdic={'ret':'1101','info':'注册成功！'}
    name_t = request.GET['name']
    password_t=request.GET['password']
    sex_t = request.GET['sex']
    age_t = request.GET['age']
    tel_t = request.GET['tel']
    address_t = request.GET['address']
    city_t = request.GET['city']
    existname=customer.objects.filter(name=name_t)
    print "name: %s,password:%s" %(name_t,password_t)
    if len(existname)==0:  
        customers=customer.objects.create    (name=name_t,sex=sex_t,age=age_t,tel=tel_t,address=address_t,city=city_t,password=password_t,authority='customer')
        return HttpResponse(json.dumps(rsdic))
    else:
        rsdic={'ret':'1102','info':'用户名已存在！'}
        return HttpResponse(json.dumps(rsdic))

#加载博文页面
def articlelistload(request,order):
	articlesList=File.objects.filter(file_type=0).all()
	return render_to_response('%sarticellist.html'%DEMOSITE,{'order':order,'articles':articlesList,'pagetitle':'ArticlesList'})

#获取文章名
def get_filename(request):
	rsdic={}
	variable['filename']=request.POST['filename']
	if variable['filename'] :
		rsdic={'message':'ok'}
	return HttpResponse(json.dumps(rsdic))

#查看文章
def show_file(request):
        rsdic={}
        if variable['filename'] :
            temp_file=File.objects.filter(title=variable['filename'],file_type=0)
        if not len(temp_file):
            rsdic={'message':'文件不存在!'}
        filename=temp_file[0].title
        time=temp_file[0].time
        filesrc=temp_file[0].filesrc
        #读取文件数据
        f1=open(filesrc+filename,'r')
        data=f1.read()
        str(data)
        f1.close()
        rsdic={'article_title':filename,'time':time,'data':data}
        return render_to_response('%sarticlePage.html'%DEMOSITE,rsdic)

#加载上传文件页面
def uploadFilePage(request):
        images = File.objects.filter(file_type=1).all()
        for image in images :
            image.filesrc = "/static/images/"+image.title
        return render_to_response("%sdemosite_image.html"%DEMOSITE,{"images":images})
#上传文件
def uploadFile(request):
        htmlTemplate = None
        rsdic={'ret':'1101','info':'上传成功'}
        if request.GET['type'] == "image" :
                htmlTemplate = '%sdemosite_image.html'%DEMOSITE
                if not request.FILES :
                    rsdic={'ret':'1103','info':'请选择上传文件!'}
                    return render_to_response('%sdemosite_image.html'%DEMOSITE,{'message':rsdic['info']})
                filename=request.FILES['file']._name
                if filename.endswith(".png") or filename.endswith(".jpg") :
                    file_type = 1
                    src=settings.BASE_DIR + '/demosite/static/images/'
                    rsdic['info']=u'成功保存图片到'+src
                else :
                    rsdic={'ret':'1103','info':'请选择图片格式文件!'}
                    return render_to_response('%sdemosite_image.html'%DEMOSITE,{'message':rsdic['info']})
        elif request.GET['type'] == "article" : 
                htmlTemplate ='%sarticellist.html'%DEMOSITE
                if not request.FILES :
                    rsdic={'ret':'1103','info':'请选择上传文件!'}
                    return render_to_response('%sarticellist.html'%DEMOSITE,{'message':rsdic['info']})
                filename=request.FILES['file']._name
                file_type = 0
                src=settings.BASE_DIR + '/demosite/static/articles/'
                rsdic['info']=u'成功保存文章到'+src
        file_title=File.objects.filter(title=filename)
        if len(file_title):
            if file_type == 1 :
                rsdic={'ret':'1102','info':'存在同名图片，上传失败'}
            elif file_type == 0 :
                rsdic={'ret':'1102','info':'存在同名文章，上传失败'}
            return render_to_response(htmlTemplate,{'message':rsdic['info']})
        size=request.FILES['file']._size
        if size > 1024*1024  :
            rsdic={'ret':'1102','info':'上传文件太大'}
            return render_to_response(htmlTemplate,{'message':rsdic['info']})
        file_data=request.FILES['file'].file.read()
        File.objects.create(title=filename,time=datetime.date.today(),filesrc=src,file_type=file_type)
        #写文件到服务器指定路径
        f1=open(src+filename,'w')
        f1.write(file_data)
        f1.close()
        return render_to_response(htmlTemplate,{'message':rsdic['info']})

#上传链接页面
def linkPage(request):
	return render_to_response('%slink.html'%DEMOSITE)	

#上传链接
def add_link(request):
	rsdic={}
	temp_title=request.POST['title']
	temp_url=request.POST['url']
	if temp_title and temp_url :
		link_list=Links.objects.filter(url=temp_url)
		if len(link_list):
			rsdic={'message':"存在同名链接,上传失败"}
		else :
			Links.objects.create(title=temp_title,url=temp_url)
			rsdic={'message':"上传成功"}
	return HttpResponse(json.dumps(rsdic))
		
#请求链接数据
def request_link_data(request):
	rsdic={}
	rsdic['link_href']=[]
	link_list=Links.objects.all()
	for link in link_list:
		rsdic['link_href'].append(link.url)
	return HttpResponse(json.dumps(rsdic))

#插入博客链接
def insert_link_url(request):
	rsdic={'ret':1,'message':'success'}
	try:
		blog_name=request.POST['blog_name']
		blog_url=request.POST['blog_url']
		link=Links(title=blog_name,url=blog_url)
		link.save()
	except Exception , e :
		rsdic={'ret':0,'message':'error'}
	return  HttpResponse(json.dumps(rsdic))	


#search_articles
def search_articles(request,order):
    search_str = request.GET['search_str']
    if search_str == "" :
        articlelist = File.objects.filter(file_type=0).all()
        return render_to_response('%sarticellist.html'%DEMOSITE,{'order':order,'articles':articlelist,'pagetitle':'ArticlesList'})
    else :
        objs = File.objects.filter(file_type=0).all()
        articlelist = []
        for obj in objs :
            temp = obj.title
            if temp.find(search_str) != -1 :
                articlelist.append(obj)
    return render_to_response('%sarticellist.html'%DEMOSITE,{'order':order,'articles':articlelist,'pagetitle':'ArticlesList'})

def search_blog(request):
    search_str = request.GET['search_str']
    link_list=Links.objects.all()
    if search_str == "" :
        return render_to_response('%sdemosite_admin.html'%DEMOSITE,{'link_list':link_list})
    else :
        links = []
        for link in link_list :
            temp = link.title
            if temp.find(search_str) != -1 :
                links.append(link)
        return render_to_response('%sdemosite_admin.html'%DEMOSITE,{'link_list':links})
#加载知识树页面
def knowledge_tree(request):
	return render_to_response('%sknowledgeTree.html'%DEMOSITE)
    
# upload question
def  newques(request):
    if request.method == "POST":
        uf = UserForm1(request.POST,request.FILES)
        if uf.is_valid():
            #获取表单信息
            question = uf.cleaned_data['question']
            answer =uf.cleaned_data['answer']
            now=datetime.datetime.now()
            #写入数据库
            ques=Ques()
            ques.question=question
            ques.answer=answer
            ques.date=now
            ques.save()
            return HttpResponse(' 上传成功 !')
    else:
        uf = UserForm1()
    return render_to_response('question_upload_page.html',{'uf':uf})

def  queslist(request):
    list1 = Ques.objects.all()
    return render_to_response('question_list.html',{'posts':list1})




