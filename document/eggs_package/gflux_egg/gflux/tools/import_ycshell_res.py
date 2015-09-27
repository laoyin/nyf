# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os,pdb

search_dir_start=os.path.abspath(os.path.dirname(__file__))+'/data/RVL'
work_path=os.path.abspath(os.path.dirname(__file__))

def checkDirFiles(dir_path):
    if not os.path.isdir(dir_path):
        print dir_path+':not a dir path'
        return
        
    for p,d,f in os.walk(dir_path):
        #check currect dir
        #从小到大排
        f.sort()
        for d_f in f:
            res=os.path.join(p,d_f)
            if not os.path.isfile(res):
                continue
                
            #check
            if not d_f.endswith('.SAV'):
                continue
                
            old_work_dir=os.getcwd()
            os.chdir(work_path)
            cmd='python manage.py import_trans_ycshell_text_data --file=%s --location=3 --site=YCSHELL_XA >import_log/%s.out'%(res,d_f)
            ret=os.system(cmd)
            os.chdir(old_work_dir)
            if ret==0:
                print 'finish import res '+res
            else:
                print 'error when import res '+res
            
if __name__=='__main__':
    print 'strart'
    checkDirFiles(search_dir_start)
    print 'end'