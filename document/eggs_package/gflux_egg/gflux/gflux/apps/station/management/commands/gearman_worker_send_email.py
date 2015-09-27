# coding=utf-8
from django.conf import settings
import smtplib,hashlib, pdb, json, logging, datetime
import django_gearman_commands
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart

#set logger
gearmanLogger=logging.getLogger('gearman')

class Command(django_gearman_commands.GearmanWorkerBaseCommand):
    """Gearman worker performing 'send_email' job."""

    @property
    def task_name(self):
      return 'send_email'

    def do_job(self, job_data):
        args=json.loads(job_data)
        try :
            email = args["to"]
            if type(email)!=type([]):
                MSG_TO=[email]
            else:
                MSG_TO=email

            msg = MIMEMultipart()

            #正文内容
            content = args["content"]

            #设置字符编码
            body = MIMEText(content,'html','utf8')
            msg.attach(body)

            #主题
            msg['subject'] = args["subject"]

            #抄送人地址 多个地址不起作用
            msg['Cc']=''

            try:
                smtp = smtplib.SMTP()

                # smtp设置
                smtp.connect(settings.SMTP_HOST)

                #登录
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

                #发送
                smtp.sendmail(settings.SMTP_MSG_FROM, MSG_TO, msg.as_string())

                smtp.close()

                gearmanLogger.info("succeed to send the email %s!" % str(MSG_TO))

            except Exception,e:
                gearmanLogger.info("fail to send the email %s!" % str(e))

        except Exception,e:
            gearmanLogger.info("handle task fail %s!" % str(e))
