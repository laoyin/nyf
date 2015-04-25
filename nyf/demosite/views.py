#coding=utf-8 
from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from demosite import models
from django import forms
from demosite.models import *
import pdb,sys
from django.template import Template,RequestContext
from django.template.loader import get_template
import json
from django.core.files.base import ContentFile 
#文件名
variable={}

#登录页面
def loginpage(request):
    return render_to_response('login_page.html')

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
	return render_to_response('index.html',{'link_list':link_list})

#注册页面
def registerload(request):
    return render_to_response('registerpage.html')

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
	articlesList=articles.objects.all()
	return render_to_response('articellist.html',{'order':order,'articles':articlesList,'pagetitle':'ArticlesList'})

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
		temp_file=articles.objects.filter(title=variable['filename'])
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
	return render_to_response('articlePage.html',rsdic)

#加载上传文件页面
def uploadFilePage(request):
	return render_to_response("uploadfile.html")
#上传文件
def uploadFile(request):
        if not request.FILES :
                rsdic={'ret':'1103','info':'请选择上传文件!'}
                return render_to_response('uploadfile.html',{'message':rsdic['info']})
        src=r'/home/nyf/youfa/nyf/demosite/static/articles/'
        filename=request.FILES['file']._name
        size=request.FILES['file']._size
        file_data=request.FILES['file'].file.read()
        rsdic={'ret':'1101','info':'ok'}
        try:
                file_title=articles.objects.filter(title=filename)
                if len(file_title):
                        rsdic={'ret':'1102','info':'存在同名文件，上传失败'}
                        return render_to_response('uploadfile.html',{'message':rsdic['info']})
        except:
                articles.objects.create(title=filename,time=datetime.date.today(),filesrc=src)
                return render_to_response('uploadfile.html',{'message':rsdic['info']})
        articles.objects.create(title=filename,time=datetime.date.today(),filesrc=src)
        #写文件到服务器指定路径
        f1=open(src+filename,'w')
        f1.write(file_data)
        f1.close()
        src_file=src
        rsdic['info']=u'成功保存文件到'+src_file
        return render_to_response('uploadfile.html',{'message':rsdic['info']})

#上传链接页面
def linkPage(request):
	return render_to_response('link.html')	

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


#加载知识树页面
def knowledge_tree(request):
	return render_to_response('knowledgeTree.html')


def registerlist(request):
    customers=customer.objects.all()
    t=get_template("customerlist.html")
    c=Context({'customers':customers})
    p=t.render(c)
    return HttpResponse(p)


def registerpage(request,url):
    if url=='registerPage_form1':
        return render_to_response('htmlregister.html',{'register':url})
    elif url=='registerPage_form2':
        return render_to_response('htmlregister1.html',{'register':url})
    elif url=='registerPage_form3':
        return render_to_response('htmlregister2.html',{'register':url})
    else:
        return HttpResponse('error')
    
def fileloadpage(request):
    return render_to_response('uploadfile.html')



def upload(request):
	return render_to_response('upload.html')


def get(request):
    filename = request.FILES['file'].name
    f=open('/home/nyf/%s'%(filename),'wb')
    f.write(request.FILES['file'].read())
    return HttpResponse('upload OK!')

def population_view(request):
    return render_to_response('population.html')
    

'''#表单上传文件
def fileload(request):
	src=r'logindemo/templates/'
	filename=request.POST['name']
	lastModifiedDate=request.POST['lastModifiedDate']
	size=request.POST['size']
	file_data=request.POST['binary_data']
	filetype=request.POST['type']
	rsdic={'ret':'1101','info':'ok'}
	try:
		file_title=articles.objects.filter(title=filename)
		if len(file_title):
			rsdic={'ret':'1102','info':'存在同名文件，上传失败'}
			return HttpResponse(json.dumps(rsdic))
	except:
		articles.objects.create(title=filename,time=lastModifiedDate,filesrc=src) 
		return HttpResponse(json.dumps(rsdic)) 
	articles.objects.create(title=filename,time=lastModifiedDate,filesrc=src)    
	#写数据到服务器指定目录
	reload(sys)
	sys.setdefaultencoding('utf-8')
	f1= open(src+filename,"w")
	f1.write(file_data)
	f1.close()
	src_file=r'/home/nyf/study/codedemo/demosite/'+src+filename
	rsdic={'ret':'1101','info':'name','name':filename,'lastModifiedDate':lastModifiedDate,'size':size,'file_text':file_data,'filetype':filetype,'src':src_file}
	return HttpResponse(json.dumps(rsdic))
'''


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




