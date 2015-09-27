# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os,pdb

search_dir_start=os.path.abspath(os.path.dirname(__file__))+'/data/YN-CN-1-19'
work_path=os.path.abspath(os.path.dirname(__file__))

def checkDirFiles(dir_path):
    if not os.path.isdir(dir_path):
        print dir_path+':not a dir path'
        return
        
    for p,d,f in os.walk(dir_path):
        #check currect dir
        #从小到大排
        f.sort()
        
        #构造sitename
        dir_names=p.split('/')
        site='YN-%s'%dir_names[len(dir_names)-1]
        
        all_file_path=None
        card_file_path=None
        
        for d_f in f:
            res=os.path.join(p,d_f)
            if not os.path.isfile(res):
                continue
                
            #check
            d_f=d_f.lower()
            
            if d_f.startswith('all')==False and d_f.startswith('card')==False:
                continue
                
            elif d_f.startswith('all'):
                all_file_path=res
                
            elif d_f.startswith('card'):
                card_file_path=res
            
        if all_file_path!=None and card_file_path!=None:
            old_work_dir=os.getcwd()
            os.chdir(work_path)
            cmd='python manage.py import_trans_cnpc_text_data --all_file=%s --card_file=%s --location=5 --site=%s >import_log/%s.out'%(all_file_path,card_file_path,site,site)
            ret=os.system(cmd)
            os.chdir(old_work_dir)
            if ret==0:
                print 'finish import res site name:'+site
            else:
                print 'error when import res site name:'+site
            
if __name__=='__main__':
    print 'strart'
    checkDirFiles(search_dir_start)
    print 'end'