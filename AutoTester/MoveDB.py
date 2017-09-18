'''
Created on Aug 18, 2016

@author: eussrh

This is core code for the autotester
'''
import mysql.connector   # @UnresolvedImport
import traceback
import django
import os
import sys
from datetime import datetime

dbHost='localhost'
dbName='testerdb'
dbUser='roboFarmer'
dbPswd='greenThumb'
        
def migrateClippingsDB():
    errorDetected=False
    try:
        from tester.models import TesterFeatureExternal
        testerDB = mysql.connector.connect(host=dbHost, user=dbUser,password=dbPswd,database=dbName)
    except mysql.connector.Error as e:
        try:
            print("Mysql Error connecting to database [%d]: %s" % (e.args[0], e.args[1]))
            errorDetected=True
        except IndexError:
            print("Mysql Error connecting to database2 Error: %s" % str(e))
            errorDetected=True
    if not errorDetected:
        try:
            c = testerDB.cursor(dictionary=True)
#Load tower data (create tower if required)
            sqlStr='SELECT * FROM clippings'
            c.execute(sqlStr)
            cl=c.fetchone()
            while not cl is None:
                name=cl['clippingName']
                description=cl['description']
                ulClipRowOffset=cl['ulClipRowOffset']
                ulClipColOffset=cl['ulClipColOffset']
                lrClipRowOffset=cl['lrClipRowOffset']
                lrClipColOffset=cl['lrClipColOffset']
                learnedWithReferenceDistance=cl['learnedWithReferenceDistance']
                usesRaw=cl['usesRaw']
                centerImage=cl['centerImage']
                useDlib=cl['useDlib']
                roiSideLength=cl['roiSideLength']
                cParmValue=cl['cParmValue']
                upSampling=cl['upSampling']
                positionCoefficientA=cl['positionCoefficientA']
                positionCoefficientB=cl['positionCoefficientB']
                
                feat=TesterFeatureExternal()
                feat.featureName=name
                feat.featureDescription=description
                feat.ulClipRowOffset=ulClipRowOffset
                feat.ulClipColOffset=ulClipColOffset
                feat.lrClipRowOffset=lrClipRowOffset
                feat.lrClipColOffset=lrClipColOffset
                feat.learnedWithReferenceDistance=learnedWithReferenceDistance
                feat.usesRaw=usesRaw
                feat.centerImage=centerImage
                feat.useDlib=useDlib
                feat.roiSideLength=roiSideLength
                feat.cParmValue=cParmValue
                feat.upSampling=upSampling
                feat.positionCoefficientA=positionCoefficientA
                feat.positionCoefficientB=positionCoefficientB
                feat.save()
                print('Saved ' + name)
                
                cl=c.fetchone()
               
#            except mysql.connector.Error as e:
        except:
            traceback.print_exc()
            try:
                print("MySQL Error saving color swatches into database [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print("MySQL Error saving color swatches into database2 %s" % str(e))
    try:
        c.close()
        testerDB.close()
    except:
        pass

def migrateColorSheetDB():
    errorDetected=False
    try:
        from tester.models import ColorSheetExternal
        testerDB = mysql.connector.connect(host=dbHost, user=dbUser,password=dbPswd,database=dbName)
    except mysql.connector.Error as e:
        try:
            print("Mysql Error connecting to database [%d]: %s" % (e.args[0], e.args[1]))
            errorDetected=True
        except IndexError:
            print("Mysql Error connecting to database2 Error: %s" % str(e))
            errorDetected=True
    if not errorDetected:
        try:
            c = testerDB.cursor(dictionary=True)
#Load tower data (create tower if required)
            sqlStr='SELECT * FROM colorSheet'
            c.execute(sqlStr)
            cl=c.fetchone()
            while not cl is None:
                name=cl['colorSheetName']
                description=cl['itemBeingMeasured']
                
                feat=ColorSheetExternal()
                feat.colorSheetName=name
                feat.itemBeingMeasured=description
                feat.save()
                print('Saved ' + name)
                
                cl=c.fetchone()
               
#            except mysql.connector.Error as e:
        except:
            traceback.print_exc()
            try:
                print("MySQL Error saving color swatches into database [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print("MySQL Error saving color swatches into database2 %s" % str(e))
    try:
        c.close()
        testerDB.close()
    except:
        pass

def migrateTestSequenceDB():
    errorDetected=False
    try:
        from tester.models import TestDefinition,ColorSheetExternal,ReagentSetup
        testerDB = mysql.connector.connect(host=dbHost, user=dbUser,password=dbPswd,database=dbName)
    except mysql.connector.Error as e:
        try:
            print("Mysql Error connecting to database [%d]: %s" % (e.args[0], e.args[1]))
            errorDetected=True
        except IndexError:
            print("Mysql Error connecting to database2 Error: %s" % str(e))
            errorDetected=True
    if not errorDetected:
        try:
            c = testerDB.cursor(dictionary=True)
#Load tower data (create tower if required)
            sqlStr='SELECT * FROM testsequence'
            c.execute(sqlStr)
            cl=c.fetchone()
            while not cl is None:
                x=TestDefinition()
                x.testName=cl['testName']
                x.enableTest=True
                x.waterVolInML=cl['waterVolInML']
                if not cl['reagent1'] is None:
                    x.reagent1Slot=ReagentSetup.objects.get(slotName=cl['reagent1'])
                x.reagent1AgitateSecs=cl['reagent1AgitateSecs']
                x.reagent1DropCount=cl['reagent1DropCount']
                if not cl['reagent2'] is None:
                    x.reagent2Slot=ReagentSetup.objects.get(slotName=cl['reagent2'])
                x.reagent2AgitateSecs=cl['reagent2AgitateSecs']
                x.reagent2DropCount=cl['reagent2DropCount']
                if not cl['reagent3'] is None:
                    x.reagent3Slot=ReagentSetup.objects.get(slotName=cl['reagent3'])
                x.reagent3AgitateSecs=cl['reagent3AgitateSecs']
                x.reagent3DropCount=cl['reagent3DropCount']
                x.agitateMixtureSecs=cl['agitateMixtureSecs']
                x.delayBeforeReadingSecs=cl['delayBeforeReadingSecs']
#                print(ColorSheetExternal.objects.get(colorSheetName=cl['colorChartToUse']))
                x.colorChartToUse=ColorSheetExternal.objects.get(colorSheetName=cl['colorChartToUse'])
                x.tooLowAlarmThreshold=cl['tooLowAlarmThreshold']
                x.tooLowWarningThreshold=cl['tooLowWarningThreshold']
                x.tooHighWarningThreshold=cl['tooHighWarningThreshold']
                x.tooHighAlarmThreshold=cl['tooHighAlarmThreshold']
                x.save()
                print('Saved ' + x.testName)
                
                cl=c.fetchone()
               
#            except mysql.connector.Error as e:
        except:
            traceback.print_exc()
            try:
                print("MySQL Error saving color swatches into database [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print("MySQL Error saving color swatches into database2 %s" % str(e))
    try:
        c.close()
        testerDB.close()
    except:
        pass
    
def migrateTestResultsDB():
    errorDetected=False
    try:
        from tester.models import TestResultsExternal
        testerDB = mysql.connector.connect(host=dbHost, user=dbUser,password=dbPswd,database=dbName)
    except mysql.connector.Error as e:
        try:
            print("Mysql Error connecting to database [%d]: %s" % (e.args[0], e.args[1]))
            errorDetected=True
        except IndexError:
            print("Mysql Error connecting to database2 Error: %s" % str(e))
            errorDetected=True
    if not errorDetected:
        try:
            c = testerDB.cursor(dictionary=True)
#Load tower data (create tower if required)
            sqlStr='SELECT * FROM testresults'
            c.execute(sqlStr)
            cl=c.fetchone()
            while not cl is None:
                x=TestResultsExternal()
                x.testPerformed=cl['testPerformed']
                x.results=cl['results']
                x.datetimePerformed=cl['datetimePerformed']
                x.save()
                print('Saved ' + x.testPerformed)
                
                cl=c.fetchone()
               
#            except mysql.connector.Error as e:
        except:
            traceback.print_exc()
            try:
                print("MySQL Error saving color swatches into database [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print("MySQL Error saving color swatches into database2 %s" % str(e))
    try:
        c.close()
        testerDB.close()
    except:
        pass
    
def migrateSwatchesDB():
    errorDetected=False
    try:
        from tester.models import SwatchExternal,ColorSheetExternal,LightingConditionsExternal
        testerDB = mysql.connector.connect(host=dbHost, user=dbUser,password=dbPswd,database=dbName)
    except mysql.connector.Error as e:
        try:
            print("Mysql Error connecting to database [%d]: %s" % (e.args[0], e.args[1]))
            errorDetected=True
        except IndexError:
            print("Mysql Error connecting to database2 Error: %s" % str(e))
            errorDetected=True
    if not errorDetected:
        try:
            c = testerDB.cursor(dictionary=True)
#Load tower data (create tower if required)
            sqlStr='SELECT * FROM swatches'
            c.execute(sqlStr)
            cl=c.fetchone()
            while not cl is None:
                x=SwatchExternal()
                x.colorSheetName=ColorSheetExternal.objects.get(colorSheetName=cl['colorSheetName'])
                x.swatchRow=cl['swatchRow']
                x.valueAtSwatch=cl['valueAtSwatch']
                x.lightingConditions=LightingConditionsExternal.objects.get(lightingConditionName=cl['lightingConditions'])
                x.channel1=cl['channel1']
                x.channel2=cl['channel2']
                x.channel3=cl['channel3']
                x.swatchULRow=cl['swatchULRow']
                x.swatchULCol=cl['swatchULCol']
                x.swatchLRRow=cl['swatchLRRow']
                x.swatchLRCol=cl['swatchLRCol']
                x.enabled=cl['enabled']
                x.save()
                print('Saved ' + str(x.swatchRow) + '/' + str(x.lightingConditions))
                
                cl=c.fetchone()
               
#            except mysql.connector.Error as e:
        except:
            traceback.print_exc()
            try:
                print("MySQL Error saving color swatches into database [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print("MySQL Error saving color swatches into database2 %s" % str(e))
    try:
        c.close()
        testerDB.close()
    except:
        pass
    
def migrateCarouselSlotDB():
    errorDetected=False
    try:
        from tester.models import ReagentSetup
        testerDB = mysql.connector.connect(host=dbHost, user=dbUser,password=dbPswd,database=dbName)
    except mysql.connector.Error as e:
        try:
            print("Mysql Error connecting to database [%d]: %s" % (e.args[0], e.args[1]))
            errorDetected=True
        except IndexError:
            print("Mysql Error connecting to database2 Error: %s" % str(e))
            errorDetected=True
    if not errorDetected:
        try:
            c = testerDB.cursor(dictionary=True)
#Load tower data (create tower if required)
            sqlStr='SELECT * FROM carouselSlot'
            c.execute(sqlStr)
            cl=c.fetchone()
            while not cl is None:
                x=ReagentSetup()
                x.slotName=cl['slotName']
                x.reagentName=cl['reagentName']
                x.used=cl['used']
                x.hasAgitator=cl['hasAgitator']
                x.fluidRemaininginML=cl['fluidRemaininginML']
                x.color=cl['color']
                x.save()
                print('Saved ' + str(x.slotName))
                
                cl=c.fetchone()
               
#            except mysql.connector.Error as e:
        except:
            traceback.print_exc()
            try:
                print("MySQL Error saving color swatches into database [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print("MySQL Error saving color swatches into database2 %s" % str(e))
    try:
        c.close()
        testerDB.close()
    except:
        pass

def removeColorSheetFromDB(colorSheetNameToDelete):
    from tester.models import ColorSheetExternal
#        SwatchExternal.objects.filter(colorSheetName__colorSheetName=colorSheetNameToDelete).delete()
    ColorSheetExternal.objects.filter(colorSheetName=colorSheetNameToDelete).delete()
    print('Deleted')
    
    

def getBasePath():
    programPath=os.path.realpath(__file__)
    programPathForwardSlash=programPath.replace('\\','/')
    programPathList=programPathForwardSlash.split('/')
    numPathSegments=len(programPathList)
    basePath=''
    pathSegment=0
    while pathSegment<numPathSegments-1:
        basePath+=programPathList[pathSegment] + '/'
        pathSegment+=1
#    print(basePath)
    return basePath
            
        
if __name__ == '__main__':
    basePath=getBasePath()
    sys.path.append(os.path.abspath(basePath))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'AutoTesterv2.settings'
    django.setup()
    migrateTestSequenceDB()
#    removeColorSheetFromDB('ph-API')