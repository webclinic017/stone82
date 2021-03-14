from pywinauto import application
import time
import os

EXEC_PATH='C:\CREON\STARTER\coStarter.exe'
ID='JEELLATO'
PWD='kjs2896@'
PWDCERT='wnffprtk123@'


os.system('taskkill /IM coStarter* /F /T')
os.system('taskkill /IM CpStart* /F /T')
os.system('wmic process where "name like \'%coStarter%\'" call terminate')
os.system('wmic process where "name like \'%CpStart%\'" call terminate')
time.sleep(5)        

app = application.Application()
#app.start('C:\CREON\STARTER\coStarter.exe /prj:cp /id:JEELLATO /pwd:kjs2896@ /pwdcert:wnffprtk123@ /autostart')
app.start('{} /prj:cp /id:{} /pwd:{} /pwdcert:{} /autostart'.format(EXEC_PATH,ID,PWD,PWDCERT))
time.sleep(60)
