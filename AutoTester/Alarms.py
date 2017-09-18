'''
Created on Aug 9, 2017

@author: eussrh
'''
"""Handle sending API requests to the IFTTT Webhooks Channel"""

import requests    # @UnresolvedImport

def send_event(api_key, event, value1=None, value2=None, value3=None):
    """Send an event to the IFTTT maker channel
    Parameters:
    -----------
    api_key : string
        Your IFTTT API key
    event : string
        The name of the IFTTT event to trigger
    value1 :
        Optional: Extra data sent with the event (default: None)
    value2 :
        Optional: Extra data sent with the event (default: None)
    value3 :
        Optional: Extra data sent with the event (default: None)
    """

    url = 'https://maker.ifttt.com/trigger/{e}/with/key/{k}/'.format(e=event,k=api_key)
    payload = {'value1': value1, 'value2': value2, 'value3': value3}
    return requests.post(url, data=payload)

def sendMeasurementReport(tester,testRun,result):
    print('Measurement Report sent with value1= ' + tester.testerName + ', value2= ' + testRun + ', value3= %.2f' % result)
    send_event(tester.iftttSecretKey, "measure", value1=tester.testerName, value2=testRun, value3=str(result),)

def sendTestMeasurementReport(tester,testRun,testKey):
    print('Test Measurement Report sent with value1= ' + tester.testerName + ', value2= ' + testRun + ', value3=This Was a Test')
    send_event(testKey, "measure", value1=tester.testerName, value2=testRun, value3='This Was a Test')

def sendAlarm(tester,reason,info):
    print('Alarm sent with value1= ' + tester.testerName + ', value2= ' + reason + ', value3= ' + info)
    send_event(tester.iftttSecretKey, "alarm", value1=tester.testerName, value2=reason, value3=info)

def sendWarning(tester,reason,info):
    print('Alarm sent with value1= ' + tester.testerName + ', value2= ' + reason + ', value3= ' + info)
    send_event(tester.iftttSecretKey, "warning", value1=tester.testerName, value2=reason, value3=info)

def sendReagentAlarm(tester,reagent,remainingML):
    sendAlarm(tester,'Reagent in Slot ' + reagent + ' Low','Remaining ML: '+ str(remainingML)) 
    
def sendFillAlarm(tester,testBeingRun):
    sendAlarm(tester,'Error filling Mixing Cylinder',testBeingRun)   
    
def sendDispenseAlarm(tester,reagent,remainingML):
    sendAlarm(tester,'Unable to Dispense Drops for Slot ' + reagent ,'Remaining ML: '+ str(remainingML)) 

def sendEvaluateAlarm(tester,sequenceName,lightingConditions):
    sendAlarm(tester,'Unable to Evaluate Samples for Test ' + sequenceName,'Lighting Conditions: '+ lightingConditions) 

def sendUnableToRotateAlarm(tester,slot,testName):
    sendAlarm(tester,'Unable to Rotate Carousel to Slot ' + slot,'Test: '+ testName) 

def sendCannotOpenStoppersAlarm(tester,testName):
    sendAlarm(tester,'Cannot Open Stoppers', 'Test: '+ testName) 

def sendCannotParkAlarm(tester,testConcern):
    sendAlarm(tester,'Parking Failure', testConcern) 
    
def sendOutOfLimitsAlarm(tester,testName,results):
    sendAlarm(tester,'Out of Limits',testName + ' results: ' + str(results)) 

def sendOutOfLimitsWarning(tester,testName,results):
    sendWarning(tester,'Out of Limits',testName + ' results: ' + str(results)) 

    