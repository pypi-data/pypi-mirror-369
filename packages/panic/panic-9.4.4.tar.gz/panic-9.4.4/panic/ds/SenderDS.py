import fandango, traceback
from fandango.functional import *
import collections
from panic.ds.PyAlarm import PyAlarm, PyAlarmClass

class Sender(PyAlarm, fandango.log.Logger):
    
    def __init__(self):
                 #mail_method = 'smtp:smtp.cells.es:25',
                 #from_address = 'oncall-noreply@cells.es'):
        fandango.log.Logger.__init__(self)
        self.info = self.debug = self.warning = self.error = print
        self.init_from_properties()
        #self.MailMethod = mail_method
        #self.FromAddress = from_address
        self.SentEmails = fandango.defaultdict(int)
        self.SMS_Sent = collections.deque()
        self.Alarms =  {}
        self.lock = fandango.threads.RLock()
    
    def init_from_properties(self):
        for p,v in PyAlarmClass.class_property_list.items():
            w = fandango.tango.get_class_property('PyAlarm',p)
            w = w or fandango.first(v[-1],'')
            print(p,w)
            setattr(self,p,w)
        for p,v in PyAlarmClass.device_property_list.items():
            if not getattr(self,p,None):
                w = fandango.first(v[-1],'')
                print(p,w)
                setattr(self,p,w)
                
    def __del__(self):
        pass

    #def SendMail(self, argin):
        #"""
        #Arguments: message, subject, receivers
        #"""
        #self.info('SendMail({},{})'.format(self.MailMethod, argin))

        #def format4sendmail(report):
            #out = report.replace('\r', '\n').replace('\n\n', '\n')
            #out = out.replace('\n', '\\n').replace('"', "'")  # .replace("'",'')
            #return out

        #try:
            #if self.MailMethod.startswith('smtp'):
                #import smtplib
                #from email.mime.text import MIMEText
                #text = argin[0]
                #msg = MIMEText(text)
                #msg['Subject'] = argin[1]
                #msg['From'] = self.FromAddress
                #receivers = argin[2] if isSequence(argin[2]) \
                    #else str(argin[2]).split(',')
                #msg['To'] = receivers[0]
                #s = smtplib.SMTP()
                #args = self.FromAddress, receivers, msg.as_string()
                #self.info('Launching {} command: '.format(self.MailMethod
                                                            #+ shortstr(str(args))))
                #s.connect(*(self.MailMethod.split(':')[1:]))
                #s.sendmail(*args)

            #elif self.MailMethod == 'mail':
                #command = 'echo -e "' + format4sendmail(argin[0]) + '" '
                #command += '| mail -s "{}" '.format(argin[1])
                #if len(self.MailDashRoption) > 0:
                    #command += '-r {} '.format(self.FromAddress)
                #else:
                    ## Legacy sendmail for old Linux
                    #command += '-S from={} '.format(self.FromAddress)
                    ## Add Receivers
                #command += ' -- ' + (argin[2] if isString(argin[2])
                                        #else ','.join(argin[2]))
                #self.info('Launching mail command: ' + shortstr(command, 512))
                ## & needed in Debian to avoid timeouts
                #os.system(command + ' &')

                #for m in argin[2].split(','):
                    #self.SentEmails[m.lower()] += 1

            #return 'DONE'
        
        #except Exception:
            #self.info('Exception in PyAlarm.SendMail(): \n{}'.format(traceback.format_exc()))
        #return 'FAILED'
