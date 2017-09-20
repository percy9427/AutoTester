tester=None

class Tester:
    def __init__(self):
        self.basePath = "/home/pi"
        self.virtualEnvironmentName='cv'
        self.webPort=8000
    

def generateWebLaunchFile(tester,name):
    launchFile=tester.basePath + "/launchWebServer.sh"
    launchText="#!/bin/bash\nexport WORKON_HOME=$HOME/.virtualenvs\nexport VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3\nsource /usr/local/bin/virtualenvwrapper.sh\nworkon "
    launchText = launchText + tester.virtualEnvironmentName + "\n"
#    launchText=launchText + tester.basePath + '/manage.py runserver 0.0.0.0:' + str(tester.webPort) + '\n'
    launchText=launchText + 'python'
    f=open(launchFile,"w+")
    f.write(launchText)
    f.close()

if __name__ == '__main__':
    tester=Tester()
    generateWebLaunchFile(tester,"Joe")
    name="Joe"
    from subprocess import call
    call(["screen","-d","-m","-S",name,"bash", "launchWebServer.sh" ])   
