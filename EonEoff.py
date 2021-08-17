import math
import pandas as pd
import numpy as np
import csv
import os
import glob
import matplotlib.pyplot as plt


global T1
T1 = 0.00005
global T2
T2 = 0.00025
global T3
T3= 0.00045

global Dlen
Dlen = 0

global SW1Index
SW1pt = [0,0]
global SW2Index
SW2pt = [0,0]

global MOSFET 
MOSFET = [0,0,0,0]#Eon,Eoff,Conduction,index

global BodyDiode
BodyDiode = [0,0,0]#Eon,Eoff,Conduction,index

global k
k = 3

def getFileList():
    path = "./"
    file_list = os.listdir(path)
    file_list_txt = [file for file in file_list if file.endswith(".txt")]
    #print(file_list_txt)
    
    FL = file_list_txt
    FL.sort()
    
    FL.remove('cases.txt')
    
    return FL

def getDataCol(data, index):
    dfile = pd.read_csv(data,delimiter = '\t')
    column_data = dfile.loc[:,dfile.columns[index]]
    return column_data

def getRefPt(data, value, option = 1):
    flag = 0
    length = data.__len__()
    #print(len(data))
    for i in range(0,len(data)):
        if (data[i] > value) & (option == 1):
            return i
        if (data[i] > value) & (option == 0):
            return i-1

##Using differentiation to get slope and intercept of each time sector
#getTrend returns A,B value which represent slope and intercept of trend equation(y = Ax+B)

def getTrend(trefpt, data, time,  ptnum = 3):
    
    slope=[]
    intercept=[]
    error = []
    
    A = 0
    B = 0

    datalen = ptnum*2+1
    
    for i in range(trefpt-ptnum, trefpt+ptnum):
        slope.append((data[i]-data[i-1])/(time[i]-time[i-1]))
    A = sum(slope)/len(slope)
    
    for i in range(trefpt-ptnum, trefpt+ptnum):
        intercept.append(data[i] - time[i]*A)        
    B = sum(intercept)/len(intercept)
    
    for i in range(trefpt-ptnum, trefpt+ptnum):
        error.append(abs(data[i] - (A*time[i]+B)))
    
    ERROR = sum(error)/len(error)
    return [A, B, ERROR]

#Using average error ratio. coeff means multiple of k 
def getSwitchPt1(trefpt1, trefpt2, trend, data, time, mark, coeff = k):
    for i in range(trefpt1, trefpt2):
        error = abs(data[i]-(trend[0]*time[i]+trend[1]))
        #print(error/trend[2])
        #print(trend[2])
        #print(error)
        #print(i)
        #print("")
        if ((error/trend[2]) < coeff) & (mark == 0):
            return i
        elif ((error/trend[2]) > coeff) & (mark == 1):
            return i
        
#Using difference ratio. coeff means difference percentage       
def getSwitchPt2(trefpt1, trefpt2, trend, data, time, mark, coeff = k):
    for i in range(trefpt1, trefpt2):
        ratio = 100 - abs(data[i]/(trend[0]*time[i]+trend[1])*100)
        #print((data[i]/(trend[0]*time[i]+trend[1])*100))
        #print(ratio)
        #print("")
        if (ratio < coeff) & (mark == 0):
            return i
        elif (ratio > coeff) & (mark == 1):
            return i

#Using differenciation to get slope. coeff means difference percentage       
def getSwitchPt3(trefpt1, trefpt2, trend, data, time, mark, coeff = k):
    for i in range(trefpt1, trefpt2):
        slope = (data[i]-data[i+1])/(time[i]-time[i+1])
        #print(slope)
        #print(trend[0])
        #print(100-(abs((slope/trend[0])*100)))
        #print("")
        if ((abs(100-abs((slope/trend[0])*100)) < coeff) & (mark == 0)):
            return i
        elif ((abs(100-abs((slope/trend[0])*100)) > coeff) & (mark == 1)):
            return i        

def getTestCnd(file):
    sub = "_data.txt"
    #row = len(filelist[0])-9
    #col = len(filelist)-1
    
    fileSub = []
    FILE = []
    
    #fileTitles = np.zeros((col,row))
    

    fileSub = ( [x for x in file if x not in sub] )
    
    temperature = float(fileSub[1])*100 + float(fileSub[2])*10+float(fileSub[3])
    voltage = float(fileSub[5])*100 + float(fileSub[6])*10+float(fileSub[7])
    current = float(fileSub[9])*100 + float(fileSub[10])*10+float(fileSub[11])
        
    FILE.append(temperature)
    FILE.append(voltage)
    FILE.append(current)
    
    return FILE

fileList = getFileList()
fileNum = len(fileList)


tempcnd = []
currcnd = []
voltcnd = []

TEMP = []
CURRENT = [] 
VOLTAGE = []

onRow1 = []
onRow2 = []
onRow3 = []
onRow4 = []

    
offRow1 = []
offRow2 = []
offRow3 = []
offRow4 = []
    
    

    


for i in range(0,fileNum-1):
    testcnd = getTestCnd(fileList[i])
    
    tempcnd.append(testcnd[0])
    voltcnd.append(testcnd[1])
    currcnd.append(testcnd[2])

for i in tempcnd:
    if i not in TEMP:
        TEMP.append(i)
        
for i in currcnd:
    if i not in CURRENT:
        CURRENT.append(i)
        
for i in voltcnd:
    if i not in VOLTAGE:
        VOLTAGE.append(i)
    
tempNUM = len(TEMP)
currNUM = len(CURRENT)*2 - 1
voltNUM = len(VOLTAGE) -1
                   
                   
for i in range(1,currNUM*2):
    onRow1.append(0)
    onRow2.append(0)
    onRow3.append(0)
    onRow4.append(0)
    
    
for i in range(1,currNUM*2):
    offRow1.append(0)
    offRow2.append(0)
    offRow3.append(0)
    offRow4.append(0)
                   
                   


for i in range(0,int((fileNum/2))):
    TimeRef = []
    
    TIME = getDataCol(fileList[i],0)
    V1 = getDataCol(fileList[i],1)
    I1 = getDataCol(fileList[i],2)
    P1 = getDataCol(fileList[i],3)
    E1 = getDataCol(fileList[i],4)
    V2 = getDataCol(fileList[i],5)
    I2 = getDataCol(fileList[i],6)
    P2 = getDataCol(fileList[i],7)
    E2 = getDataCol(fileList[i],8)
    
    TimeRef.append(getRefPt(TIME,T1))
    TimeRef.append(getRefPt(TIME,T2))
    TimeRef.append(getRefPt(TIME,T3))
    
    TC = getTestCnd(fileList[i])
    
    E1trendT1 = getTrend(TimeRef[0], E1, TIME, 5)     
    E1trendT2 = getTrend(TimeRef[1], E1, TIME, 5)
    E1trendT3 = getTrend(TimeRef[2], E1, TIME, 5) 

    E2trendT1 = getTrend(TimeRef[0], E2, TIME, 5)     
    E2trendT2 = getTrend(TimeRef[1], E2, TIME, 5)
    E2trendT3 = getTrend(TimeRef[2], E2, TIME, 5)

    V2trendT1 = getTrend(TimeRef[0], V2, TIME, 5)
    
    SW1pt[0] = getSwitchPt1(TimeRef[0], TimeRef[1], E1trendT1, E1, TIME,1)        
    SW1pt[1] = getSwitchPt2(TimeRef[0], TimeRef[1], E1trendT2, E1, TIME,0)       
    SW2pt[0] = getSwitchPt1(TimeRef[1], TimeRef[2], E1trendT2, E1, TIME,1)
    SW2pt[1] = getSwitchPt1(SW2pt[0], TimeRef[2], E1trendT3, E1, TIME,0)
    Q2pt = getSwitchPt3(TimeRef[0], TimeRef[1], E2trendT1, E2, TIME, 1, 6 )
    
    Q1Eon = E1[SW1pt[1]] - E1[SW1pt[0]]
    Q1Eoff = E1[SW2pt[1]] - E1[SW2pt[0]]
    
    Q2Eoff = E2[SW1pt[1]] - E2[SW1pt[0]]
    Q2Eon = E2[SW2pt[1]] - E2[SW2pt[0]]
    
    testcnd = getTestCnd(fileList[i])

    if testcnd[0] == TEMP[0]:
        if testcnd[1] == VOLTAGE[0]:
            if testcnd[2] == CURRENT[0]:
                onRow1[len(CURRENT)] = Q1Eon
                offRow1[len(CURRENT)-1] = Q2Eoff
                onRow1[len(CURRENT)-1] = Q2Eon
                offRow1[len(CURRENT)] = Q1Eoff
            elif testcnd[2] == CURRENT[1]:
                onRow1[len(CURRENT)+1] = Q1Eon
                offRow1[len(CURRENT)-2] = Q2Eoff
                onRow1[len(CURRENT)-2] = Q2Eon
                offRow1[len(CURRENT)+1] = Q1Eoff
            elif testcnd[2] == CURRENT[2]:
                onRow1[len(CURRENT)+2] = Q1Eon
                offRow1[len(CURRENT)-3] = Q2Eoff
                onRow1[len(CURRENT)-3] = Q2Eon
                offRow1[len(CURRENT)+2] = Q1Eoff
            elif testcnd[2] == CURRENT[3]:
                onRow1[len(CURRENT)+3] = Q1Eon
                offRow1[len(CURRENT)-4] = Q2Eoff
                onRow1[len(CURRENT)-4] = Q2Eon
                offRow1[len(CURRENT)+3] = Q1Eoff
            elif testcnd[2] == CURRENT[4]:
                onRow1[len(CURRENT)+4] = Q1Eon
                offRow1[len(CURRENT)-5] = Q2Eoff
                onRow1[len(CURRENT)-5] = Q2Eon
                offRow1[len(CURRENT)+4] = Q1Eoff
        
        if testcnd[1] == VOLTAGE[1]:
            if testcnd[2] == CURRENT[0]:
                onRow2[len(CURRENT)] = Q1Eon
                offRow2[len(CURRENT)-1] = Q2Eoff
                onRow2[len(CURRENT)-1] = Q2Eon
                offRow2[len(CURRENT)] = Q1Eoff
            elif testcnd[2] == CURRENT[1]:
                onRow2[len(CURRENT)+1] = Q1Eon
                offRow2[len(CURRENT)-2] = Q2Eoff
                onRow2[len(CURRENT)-2] = Q2Eon
                offRow2[len(CURRENT)+1] = Q1Eoff
            elif testcnd[2] == CURRENT[2]:
                onRow2[len(CURRENT)+2] = Q1Eon
                offRow2[len(CURRENT)-3] = Q2Eoff
                onRow2[len(CURRENT)-3] = Q2Eon
                offRow2[len(CURRENT)+2] = Q1Eoff
            elif testcnd[2] == CURRENT[3]:
                onRow2[len(CURRENT)+3] = Q1Eon
                offRow2[len(CURRENT)-4] = Q2Eoff
                onRow2[len(CURRENT)-4] = Q2Eon
                offRow2[len(CURRENT)+3] = Q1Eoff
            elif testcnd[2] == CURRENT[4]:
                onRow2[len(CURRENT)+4] = Q1Eon
                offRow2[len(CURRENT)-5] = Q2Eoff
                onRow2[len(CURRENT)-5] = Q2Eon
                offRow2[len(CURRENT)+4] = Q1Eoff
                          
    
        if testcnd[1] == VOLTAGE[2]:
            if testcnd[2] == CURRENT[0]:
                onRow3[len(CURRENT)] = Q1Eon
                offRow3[len(CURRENT)-1] = Q2Eoff
                onRow3[len(CURRENT)-1] = Q2Eon
                offRow3[len(CURRENT)] = Q1Eoff
            elif testcnd[2] == CURRENT[1]:
                onRow3[len(CURRENT)+1] = Q1Eon
                offRow3[len(CURRENT)-2] = Q2Eoff
                onRow3[len(CURRENT)-2] = Q2Eon
                offRow3[len(CURRENT)+1] = Q1Eoff
            elif testcnd[2] == CURRENT[2]:
                onRow3[len(CURRENT)+2] = Q1Eon
                offRow3[len(CURRENT)-3] = Q2Eoff
                onRow3[len(CURRENT)-3] = Q2Eon
                offRow3[len(CURRENT)+2] = Q1Eoff
            elif testcnd[2] == CURRENT[3]:
                onRow3[len(CURRENT)+3] = Q1Eon
                offRow3[len(CURRENT)-4] = Q2Eoff
                onRow3[len(CURRENT)-4] = Q2Eon
                offRow3[len(CURRENT)+3] = Q1Eoff
            elif testcnd[2] == CURRENT[4]:
                onRow3[len(CURRENT)+4] = Q1Eon
                offRow3[len(CURRENT)-5] = Q2Eoff
                onRow3[len(CURRENT)-5] = Q2Eon
                offRow3[len(CURRENT)+4] = Q1Eoff
        

                       
f = open('result_temp1.csv', 'w', encoding='utf-8', newline='')
wr = csv.writer(f)

wr.writerow(['On Losses', int(CURRENT[4]*-1), float(CURRENT[3]*-1),float(CURRENT[2]*-1),float(CURRENT[1]*-1), float(CURRENT[0]*-1),0.0, CURRENT[0], CURRENT[1], CURRENT[2], CURRENT[3], CURRENT[4]])
wr.writerow([VOLTAGE[0],onRow1[0], onRow1[1], onRow1[2], onRow1[3], onRow1[4],'0.0', onRow1[5], onRow1[6], onRow1[7], onRow1[8], onRow1[9]])
wr.writerow([VOLTAGE[1],onRow2[0], onRow2[1], onRow2[2], onRow2[3], onRow2[4],'0.0', onRow2[5], onRow2[6], onRow2[7], onRow2[8], onRow2[9]])
wr.writerow([VOLTAGE[2],onRow3[0], onRow3[1], onRow3[2], onRow3[3], onRow3[4],'0.0', onRow3[5], onRow3[6], onRow3[7], onRow3[8], onRow3[9]])

wr.writerow(['Off Losses', int(CURRENT[4]*-1), float(CURRENT[3]*-1),float(CURRENT[2]*-1),float(CURRENT[1]*-1), float(CURRENT[0]*-1),0.0, CURRENT[0], CURRENT[1], CURRENT[2], CURRENT[3], CURRENT[4]])
wr.writerow([VOLTAGE[0],offRow1[0], offRow1[1], offRow1[2], offRow1[3], offRow1[4], '0.0', offRow1[5], offRow1[6], offRow1[7], offRow1[8], offRow1[9]])
wr.writerow([VOLTAGE[1],offRow2[0], offRow2[1], offRow2[2], offRow2[3], offRow2[4], '0.0', offRow2[5], offRow2[6], offRow2[7], offRow2[8], offRow2[9]])
wr.writerow([VOLTAGE[2],offRow3[0], offRow3[1], offRow3[2], offRow3[3], offRow3[4], '0.0', offRow3[5], offRow3[6], offRow3[7], offRow3[8], offRow3[9]])

                   
f.close()

onRow1 = []
onRow2 = []
onRow3 = []
onRow4 = []

    
offRow1 = []
offRow2 = []
offRow3 = []
offRow4 = []


for i in range(1,currNUM*2):
    onRow1.append(0)
    onRow2.append(0)
    onRow3.append(0)
    onRow4.append(0)
    
    
for i in range(1,currNUM*2):
    offRow1.append(0)
    offRow2.append(0)
    offRow3.append(0)
    offRow4.append(0)

                   
for i in range(int(fileNum/2),fileNum):
    TimeRef = []
    
    TIME = getDataCol(fileList[i],0)
    V1 = getDataCol(fileList[i],1)
    I1 = getDataCol(fileList[i],2)
    P1 = getDataCol(fileList[i],3)
    E1 = getDataCol(fileList[i],4)
    V2 = getDataCol(fileList[i],5)
    I2 = getDataCol(fileList[i],6)
    P2 = getDataCol(fileList[i],7)
    E2 = getDataCol(fileList[i],8)
    
    TimeRef.append(getRefPt(TIME,T1))
    TimeRef.append(getRefPt(TIME,T2))
    TimeRef.append(getRefPt(TIME,T3))
    
    TC = getTestCnd(fileList[i])
    
    E1trendT1 = getTrend(TimeRef[0], E1, TIME, 5)     
    E1trendT2 = getTrend(TimeRef[1], E1, TIME, 5)
    E1trendT3 = getTrend(TimeRef[2], E1, TIME, 5) 

    E2trendT1 = getTrend(TimeRef[0], E2, TIME, 5)     
    E2trendT2 = getTrend(TimeRef[1], E2, TIME, 5)
    E2trendT3 = getTrend(TimeRef[2], E2, TIME, 5)

    V2trendT1 = getTrend(TimeRef[0], V2, TIME, 5)
    
    SW1pt[0] = getSwitchPt1(TimeRef[0], TimeRef[1], E1trendT1, E1, TIME,1)        
    SW1pt[1] = getSwitchPt2(TimeRef[0], TimeRef[1], E1trendT2, E1, TIME,0)       
    SW2pt[0] = getSwitchPt1(TimeRef[1], TimeRef[2], E1trendT2, E1, TIME,1)
    SW2pt[1] = getSwitchPt1(SW2pt[0], TimeRef[2], E1trendT3, E1, TIME,0)
    Q2pt = getSwitchPt3(TimeRef[0], TimeRef[1], E2trendT1, E2, TIME, 1, 6 )
    

    
    Q1Eon = E1[SW1pt[1]] - E1[SW1pt[0]]
    Q1Eoff = E1[SW2pt[1]] - E1[SW2pt[0]]
    
    Q2Eoff = E2[SW1pt[1]] - E2[SW1pt[0]]
    Q2Eon = E2[SW2pt[1]] - E2[SW2pt[0]]
    

    
    testcnd = getTestCnd(fileList[i])

    
    if testcnd[0] == TEMP[1]:
        if testcnd[1] == VOLTAGE[0]:
            if testcnd[2] == CURRENT[0]:
                onRow1[len(CURRENT)] = Q1Eon
                offRow1[len(CURRENT)-1] = Q2Eoff
                onRow1[len(CURRENT)-1] = Q2Eon
                offRow1[len(CURRENT)] = Q1Eoff
            elif testcnd[2] == CURRENT[1]:
                onRow1[len(CURRENT)+1] = Q1Eon
                offRow1[len(CURRENT)-2] = Q2Eoff
                onRow1[len(CURRENT)-2] = Q2Eon
                offRow1[len(CURRENT)+1] = Q1Eoff
            elif testcnd[2] == CURRENT[2]:
                onRow1[len(CURRENT)+2] = Q1Eon
                offRow1[len(CURRENT)-3] = Q2Eoff
                onRow1[len(CURRENT)-3] = Q2Eon
                offRow1[len(CURRENT)+2] = Q1Eoff
            elif testcnd[2] == CURRENT[3]:
                onRow1[len(CURRENT)+3] = Q1Eon
                offRow1[len(CURRENT)-4] = Q2Eoff
                onRow1[len(CURRENT)-4] = Q2Eon
                offRow1[len(CURRENT)+3] = Q1Eoff
            elif testcnd[2] == CURRENT[4]:
                onRow1[len(CURRENT)+4] = Q1Eon
                offRow1[len(CURRENT)-5] = Q2Eoff
                onRow1[len(CURRENT)-5] = Q2Eon
                offRow1[len(CURRENT)+4] = Q1Eoff
        
        if testcnd[1] == VOLTAGE[1]:
            if testcnd[2] == CURRENT[0]:
                onRow2[len(CURRENT)] = Q1Eon
                offRow2[len(CURRENT)-1] = Q2Eoff
                onRow2[len(CURRENT)-1] = Q2Eon
                offRow2[len(CURRENT)] = Q1Eoff
            elif testcnd[2] == CURRENT[1]:
                onRow2[len(CURRENT)+1] = Q1Eon
                offRow2[len(CURRENT)-2] = Q2Eoff
                onRow2[len(CURRENT)-2] = Q2Eon
                offRow2[len(CURRENT)+1] = Q1Eoff
            elif testcnd[2] == CURRENT[2]:
                onRow2[len(CURRENT)+2] = Q1Eon
                offRow2[len(CURRENT)-3] = Q2Eoff
                onRow2[len(CURRENT)-3] = Q2Eon
                offRow2[len(CURRENT)+2] = Q1Eoff
            elif testcnd[2] == CURRENT[3]:
                onRow2[len(CURRENT)+3] = Q1Eon
                offRow2[len(CURRENT)-4] = Q2Eoff
                onRow2[len(CURRENT)-4] = Q2Eon
                offRow2[len(CURRENT)+3] = Q1Eoff
            elif testcnd[2] == CURRENT[4]:
                onRow2[len(CURRENT)+4] = Q1Eon
                offRow2[len(CURRENT)-5] = Q2Eoff
                onRow2[len(CURRENT)-5] = Q2Eon
                offRow2[len(CURRENT)+4] = Q1Eoff
                          
    
        if testcnd[1] == VOLTAGE[2]:
            if testcnd[2] == CURRENT[0]:
                onRow3[len(CURRENT)] = Q1Eon
                offRow3[len(CURRENT)-1] = Q2Eoff
                onRow3[len(CURRENT)-1] = Q2Eon
                offRow3[len(CURRENT)] = Q1Eoff
            elif testcnd[2] == CURRENT[1]:
                onRow3[len(CURRENT)+1] = Q1Eon
                offRow3[len(CURRENT)-2] = Q2Eoff
                onRow3[len(CURRENT)-2] = Q2Eon
                offRow3[len(CURRENT)+1] = Q1Eoff
            elif testcnd[2] == CURRENT[2]:
                onRow3[len(CURRENT)+2] = Q1Eon
                offRow3[len(CURRENT)-3] = Q2Eoff
                onRow3[len(CURRENT)-3] = Q2Eon
                offRow3[len(CURRENT)+2] = Q1Eoff
            elif testcnd[2] == CURRENT[3]:
                onRow3[len(CURRENT)+3] = Q1Eon
                offRow3[len(CURRENT)-4] = Q2Eoff
                onRow3[len(CURRENT)-4] = Q2Eon
                offRow3[len(CURRENT)+3] = Q1Eoff
            elif testcnd[2] == CURRENT[4]:
                onRow3[len(CURRENT)+4] = Q1Eon
                offRow3[len(CURRENT)-5] = Q2Eoff
                onRow3[len(CURRENT)-5] = Q2Eon
                offRow3[len(CURRENT)+4] = Q1Eoff
        

                       
f = open('result_temp2.csv', 'w', encoding='utf-8', newline='')
wr = csv.writer(f)

wr.writerow(['On Losses', int(CURRENT[4]*-1), float(CURRENT[3]*-1),float(CURRENT[2]*-1),float(CURRENT[1]*-1), float(CURRENT[0]*-1),0.0, CURRENT[0], CURRENT[1], CURRENT[2], CURRENT[3], CURRENT[4]])
wr.writerow([VOLTAGE[0],onRow1[0], onRow1[1], onRow1[2], onRow1[3], onRow1[4],'0.0', onRow1[5], onRow1[6], onRow1[7], onRow1[8], onRow1[9]])
wr.writerow([VOLTAGE[1],onRow2[0], onRow2[1], onRow2[2], onRow2[3], onRow2[4],'0.0', onRow2[5], onRow2[6], onRow2[7], onRow2[8], onRow2[9]])
wr.writerow([VOLTAGE[2],onRow3[0], onRow3[1], onRow3[2], onRow3[3], onRow3[4],'0.0', onRow3[5], onRow3[6], onRow3[7], onRow3[8], onRow3[9]])

wr.writerow(['Off Losses', int(CURRENT[4]*-1), float(CURRENT[3]*-1),float(CURRENT[2]*-1),float(CURRENT[1]*-1), float(CURRENT[0]*-1),0.0, CURRENT[0], CURRENT[1], CURRENT[2], CURRENT[3], CURRENT[4]])
wr.writerow([VOLTAGE[0],offRow1[0], offRow1[1], offRow1[2], offRow1[3], offRow1[4], '0.0', offRow1[5], offRow1[6], offRow1[7], offRow1[8], offRow1[9]])
wr.writerow([VOLTAGE[1],offRow2[0], offRow2[1], offRow2[2], offRow2[3], offRow2[4], '0.0', offRow2[5], offRow2[6], offRow2[7], offRow2[8], offRow2[9]])
wr.writerow([VOLTAGE[2],offRow3[0], offRow3[1], offRow3[2], offRow3[3], offRow3[4], '0.0', offRow3[5], offRow3[6], offRow3[7], offRow3[8], offRow3[9]])



                   
f.close()
print('END PROCESSING')   