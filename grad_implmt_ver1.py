# -*- coding: utf-8 -*-
#! /usr/bin/env python2

"""
This implementation at first experiment by pyqtgraph.examples 
graphics item - ImageItem - video.

Examples from Zencode.com about PyQt4 Widget help me a lot.
"""

#from PyQt4 import QtCore, QtGui
from pyqtgraph.Qt import QtCore, QtGui
#from PyQt4.QtGui import *
import numpy as np
import pyqtgraph as pg
import pyqtgraph.ptime as ptime
#import sys
import copy

#QtGui.QApplication.setGraphicsSystem ("opengl") #it seems get slower...
qt_app = QtGui.QApplication([])
#qt_app = QApplication(sys.argv)

## Create image item
img = pg.ImageItem(border='w')

# Initiate globally the population of env and life objects
envdata1ct = 0
prod1ct = 0
consu1ct = 0
decom1ct = 0

class WidgetMore(QtGui.QWidget):
    def __init__(self):
        #QtGui.QWidget.__init__(self)
        super(WidgetMore,self).__init__()
        self.initUI()
        self.timer = QtCore.QTimer()
        self.bool1 = True
        #
        self.envdata1ctL = QtGui.QLabel(self)
        self.envdata1ctL.move(AWID*4+10, 70)
        self.prod1ctL = QtGui.QLabel(self)
        self.prod1ctL.move(AWID*4+10, 120)
        self.consu1ctL = QtGui.QLabel(self)
        self.consu1ctL.move(AWID*4+10, 170)
        self.decom1ctL = QtGui.QLabel(self)
        self.decom1ctL.move(AWID*4+10, 220)
        self.envdata1ctL.setText('Env energy count:\n%d' %envdata1ct) #if here it's not initiated first, below the update will look weird.
        self.prod1ctL.setText('Producer1 count:\n%d' %prod1ct)
        self.consu1ctL.setText('Consumer1 count:\n%d' %consu1ct)
        self.decom1ctL.setText('Decomposer1 count:\n%d' %decom1ct)
        #consu1ctV = QtCore.QString('%d' %consu1ct)


    def initUI(self):
        self.setWindowTitle('Raw World')
        self.setMinimumSize(AWID*5,ALEN*4)
        self.INTERVAL = 10
        #
        button1 = QtGui.QPushButton('pause/resume',self)
        button1.setMinimumWidth(145)
        button1.move(AWID*4+10, 0)
        button1.clicked.connect(self.buttonClicked)
        #
        slider1L = QtGui.QLabel('Time Interval:', self)
        slider1L.move(AWID*4+10, 30)
        global slider1 #define as self.slider1 may be another way
        slider1 = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        slider1.setMinimum(1)
        slider1.setMaximum(1000)
        slider1.setMinimumWidth(145)
        slider1.setValue(self.INTERVAL)
        slider1.sliderMoved.connect(self.sliderMove)
        #slider1.valueChanged.connect(self.INTERVAL)
        slider1.move(AWID*4+10, 50)
        #
        World = pg.GraphicsLayoutWidget(self)
        World.setMinimumSize(AWID*4,ALEN*4)
        World.move(5,5)
        view = World.addViewBox()
        ## lock the aspect ratio so pixels are always square
        view.setAspectLocked(True)
        ## Set initial view bounds
        view.setRange(QtCore.QRectF(0, 0, LEN, WID))
        view.addItem(img)

    def buttonClicked(self):
        if self.bool1:
            self.timer.stop()
            self.bool1 = False
        else:
            self.timer.start()
            self.bool1 = True

    def sliderMove(self):
        self.timer.stop()
        #self.bool1 = False
        self.INTERVAL = slider1.value()
        self.timer.setInterval(self.INTERVAL)
        self.timer.start()

    def run(self):
        self.show()
        #timer = QtCore.QTimer()
        #self.timer.timeout.connect(envFood)
        self.timer.timeout.connect(update)
        self.timer.setInterval(self.INTERVAL)
        self.timer.start()
        qt_app.exec_()

ALEN = 100
AWID = 200 #ALEN and AWID decide the frame size of the windows, with LEN and WID we can zone in and zone out the size of a cell
LEN = int(AWID*1.0) #LEN*WID is the absolute amount of cells.
WID = int(ALEN*1.0)
LIGHTBIT = [255,255,255,20]
PRODBIT = [0,255,0,20]
CONSUBIT = [255,0,0,20]
DECOMBIT = [0,0,255,60] #the amount of decomposer is constant, and it doesn't have lifespan.
PMATURE = 100 #mature threshold of producer
CMATURE = 180
PLIFESPAN = 160 #lifespan threshold of producer
CLIFESPAN = 240

updatect = 0 #for testing speed

class EnvAndLife(object):
    def __init__(self):
        #Generate Environment Light Bits
        r = np.random.random((LEN,WID))
        self.envdata1 = copy.copy(LIGHTBIT)* \
                np.random.randint(2,size=(LEN,WID,1)) #for colorizing image
        for i in range(LEN):
            for j in range(WID):
                if r[i][j] < 0.7:
                    self.envdata1[i][j][3] = 0
        self.mixenv = copy.deepcopy(self.envdata1)

        #Generate Producers from Light Bits
        r = np.random.random((LEN,WID))
        #prod1tp = np.random.randint(2,size=(LEN,WID,1))*PRODBIT #producer assigns to green cell.
        self.prod1 = {} #use dictionary reduce interation time as there are many 0 values.
        for i in range(LEN):
            for j in range(WID):
                if r[i][j] > 0.8 and self.envdata1[i][j][3] > 0: #It can be considered as producer generated from env energy, it's also beneficial to display data as that producer won't stay in the same cell with env energy.
                    self.prod1[(i,j)] = copy.copy(PRODBIT)
                    self.envdata1[i][j][3] = 0
                    self.mixenv[i][j] = copy.copy(PRODBIT)
        #print(self.prod1) ##tft
        #Generate Consumers from Producers
        r = np.random.random((LEN,WID))
        self.consu1 = {}
        for i in self.prod1.keys():
            if r[i[0]][i[1]] > 0.8:
                self.consu1[i] = copy.copy(CONSUBIT)
                del(self.prod1[i])
                self.mixenv[i[0]][i[1]] = copy.copy(CONSUBIT)

        #Generate Decomposers from Environment Light Bits Left, the code is the same structure as the producer generator.
        r = np.random.random((LEN,WID))
        self.decom1 = {}
        for i in range(LEN):
            for j in range(WID):
                if r[i][j] > 0.9 and self.envdata1[i][j][3] > 0:
                    self.decom1[(i,j)] = copy.copy(DECOMBIT)
                    self.envdata1[i][j][3] = 0
                    self.mixenv[i][j] = copy.copy(DECOMBIT)

    def envEnergy(self): #This function trys to simulate light energy.
        #global img
        ## Display the data
        #print(self.envdata1) ##tft
        #img.setImage(self.envdata1)
        #datatp = np.zeros((LEN,WID,1)) #empty is faster than zeros, but here is better with a zeros matrix
        datatp = np.ones((LEN,WID,1))*[255,255,255,0]
        #datatp = copy.deepcopy(data4)
        for i in range(LEN):
            for j in range(WID):
                while self.envdata1[i][j][3] > 0:
                #if self.envdata1[i][j][3] > 0: #Can't use while loop because when showing the img the value of self.envdata1 can't be changed, or the picture keeps blank.
                    #tp = self.envdata1[i][j][3]
                    #while tp > 0:
                    rnmove = np.random.randint(4) #four direction, may add another as the object may not move
                    if rnmove in (0,2):
                        datatp[i][(j+rnmove-1)%WID][3] += LIGHTBIT[3]
                        self.envdata1[i][j][3] -= LIGHTBIT[3]
                    else:
                        datatp[(i+rnmove-2)%LEN][j][3] += LIGHTBIT[3]
                        self.envdata1[i][j][3] -= LIGHTBIT[3]
        #print('Successfully jump out loop') ##tft
        #print(datatp) ##tft
        self.envdata1 = copy.deepcopy(datatp) #if the alpha value is more than 255, the color will look weird, but the fact that light bit won't intefere each other stays true.
        #self.mixenv = copy.deepcopy(datatp)

    def envExist(self, position): #position is in form of (x,y)
        if self.envdata1[position[0]][position[1]][3] > 0:
            #print(self.envdata1[position[0]][position[1]][3]) ##tft
            return True
        else:
            return False

    def prodExist(self, position):
        if position in self.prod1.keys():
            return True
        else:
            return False

    def envDataTransf(self, position):
        return self.envdata1[position[0]][position[1]]

    def prodTransf(self, position):
        return self.prod1[position]

    def lifeMove(self, prod1tp, prod1, isConsu=False): #Assignment Name is from producer.
        for i in prod1.keys():
            rnmove = np.random.randint(4)
            if rnmove in (0,2):
                if isConsu:
                    positp = (i[1] + rnmove*2 - 2)%WID #(-2,2)
                    #print ('mix: ', self.mixenv[i[0]][positp][0:3]) ##tft
                    #if list(self.mixenv[i[0]][positp][0:3]) == DECOMBIT[0:3]:
                    if (i[0], positp) in self.decom1.keys(): #escape from decomposer and bigger comsumer if it's in 2 cell front
                        movetp = (i[1]-rnmove+1)%WID
                    else:
                        movetp = (i[1]+rnmove-1)%WID
                else:
                    movetp = (i[1]+rnmove-1)%WID
                pkeytp = (i[0], movetp)
                if pkeytp not in prod1tp:
                    prod1tp[pkeytp] = copy.copy(prod1[i])
                else: #if producer counters each other, they merge.
                    prod1tp[pkeytp][3] += prod1[i][3]
            else: #may use function to merge with the first part.
                if isConsu:
                    positp = (i[0] + rnmove*2 - 4)%LEN
                    #if list(self.mixenv[positp][i[1]][0:3]) == DECOMBIT[0:3]:
                    if (positp, i[1]) in self.decom1.keys():
                        movetp = (i[0]-rnmove+2)%LEN
                    else:
                        movetp = (i[0]+rnmove-2)%LEN
                else:
                    movetp = (i[0]+rnmove-2)%LEN
                pkeytp = (movetp,i[1])
                if pkeytp not in prod1tp:
                    prod1tp[pkeytp] = copy.copy(prod1[i])
                else:
                    prod1tp[pkeytp][3] += prod1[i][3]

    def growAndGiveBirth(self, prod1tp2, prod1tp, PMATURE, PRODBIT, \
            envExist, envDataTransf):
        for i in prod1tp.keys():
            if envExist(i): #absorb light bit if it exists.
                #prod1tp[i][3] += envdata1[i[0]][i[1]][3] ##tft
                #envdata1[i[0]][i[1]][3] = 0 ##tft
                if prod1tp[i][3] < PMATURE:
                    prod1tp[i][3] += envDataTransf(i)[3]
                    envDataTransf(i)[3] = 0
                else: #give birth in random nearby, the baby never merge with its mother XD
                    rnmove = np.random.randint(4)
                    if rnmove in (0,2):
                        birthtp = (i[1]+rnmove-1)%WID
                        positp = (i[0], birthtp)
                        if positp not in prod1tp2:
                            prod1tp2[positp] = copy.copy(PRODBIT)
                            prod1tp2[positp][3] = PRODBIT[3] #the baby birth with only 20 alpha value.
                            prod1tp[i][3] += envDataTransf(i)[3] - PRODBIT[3]
                        else:
                            prod1tp2[positp][3] += PRODBIT[3]
                            prod1tp[i][3] += envDataTransf(i)[3] - PRODBIT[3]
                        envDataTransf(i)[3] = 0 #may be a condition clause of which whether the envlight is larger than 20 is better.
                        if envExist(positp): #the baby will absort the light bit.
                            prod1tp2[positp][3] += envDataTransf(positp)[3]
                            envDataTransf(positp)[3] = 0
                    else:
                        birthtp = (i[0]+rnmove-2)%LEN
                        positp = (birthtp, i[1])
                        if positp not in prod1tp2:
                            prod1tp2[positp] = copy.copy(PRODBIT)
                            prod1tp2[positp][3] = PRODBIT[3]
                            prod1tp[i][3] += envDataTransf(i)[3] - PRODBIT[3]
                        else:
                            prod1tp2[positp][3] += PRODBIT[3]
                            prod1tp[i][3] += envDataTransf(i)[3] - PRODBIT[3]
                        envDataTransf(i)[3] = 0
                        if envExist(positp):
                            prod1tp2[positp][3] += envDataTransf(positp)[3]
                            envDataTransf(positp)[3] = 0
        for i in prod1tp2.keys(): #the babies merge into the existent producers
            if i in prod1tp.keys():
                prod1tp[i][3] += prod1tp2[i][3]
            else:
                prod1tp[i] = copy.copy(prod1tp2[i])

    # producer consumer decomposer
    def Producer(self):
        #global img
        prod1tp = {}
        self.lifeMove(prod1tp, self.prod1) #in the definiont part the attributes can't contain "self.".
            #self.envExist(i) ##tft
        #print(prod1tp) ##tft

        prod1tp2 = {} #this is for temptly storing the babies.
        self.growAndGiveBirth(prod1tp2, prod1tp, PMATURE, PRODBIT, \
                self.envExist, self.envDataTransf)

        #self.mixenv = copy.deepcopy(self.envdata1)
        for i in prod1tp.keys(): #clean the death.
            if prod1tp[i][3] > PLIFESPAN:
                self.envdata1[i[0]][i[1]][3] = prod1tp[i][3]
                #self.mixenv[i[0]][i[1]][3] = prod1tp[i][3]
                del(prod1tp[i])
            #else:
                #self.mixenv[i[0]][i[1]] = copy.copy(prod1tp[i])
        self.prod1 = copy.deepcopy(prod1tp)


    def Consumer(self):
        consu1tp = {}
        self.lifeMove(consu1tp, self.consu1, isConsu = True)

        consu1tp2 = {}
        self.growAndGiveBirth(consu1tp2, consu1tp, CMATURE, CONSUBIT, \
                self.prodExist, self.prodTransf)

        for i in consu1tp.keys():
            if consu1tp[i][3] > CLIFESPAN:
                self.envdata1[i[0]][i[1]][3] = consu1tp[i][3]
                #self.mixenv[i[0]][i[1]] = copy.copy(self.envdata1[i[0]][i[1]])
                del(consu1tp[i])
            #else:
                #self.mixenv[i[0]][i[1]] = copy.copy(consu1tp[i])
        self.consu1 = copy.deepcopy(consu1tp)

    def decomposeLife(self, decom1tp2, decom1tp, splittp1, splittp2, i):
        for j in (splittp1, splittp2):
            #print('tp: ', j) ##tft
            if j not in decom1tp2.keys():
                decom1tp2[j] = copy.copy(DECOMBIT)
                if decom1tp[i][3] > DECOMBIT[3]:
                    decom1tp2[j][3] = decom1tp[i][3] - DECOMBIT[3]
                    decom1tp[i][3] = DECOMBIT[3]
                #else:
                    #decom1tp2[j][3] = DECOMBIT[3]
            else: #decomposer can also merge each other.
                if decom1tp[i][3] > DECOMBIT[3]:
                    decom1tp2[j][3] += decom1tp[i][3] - DECOMBIT[3]
                    decom1tp[i][3] = DECOMBIT[3]
                else:
                    decom1tp2[j][3] += DECOMBIT[3]
            if j in self.prod1.keys():
                self.envdata1[j[0]][j[1]][3] = self.prod1[j][3]
                del(self.prod1[j])
            if j in self.consu1.keys():
                self.envdata1[j[0]][j[1]][3] = self.consu1[j][3]
                del(self.consu1[j])
        #print('interval') ##tft

    def decomSplit(self, decom1tp2, decom1tp, i):
        if decom1tp[i][3] > DECOMBIT[3]: #commomly splits only when decomposes some lives.
            rnmove = np.random.randint(4)
            if rnmove in (0, 2):
                splittp1 = (i[0], (i[1]+rnmove-1)%WID)
                splittp2 = (i[0], (i[1]-rnmove+1)%WID)
                self.decomposeLife(decom1tp2, decom1tp, splittp1, splittp2, i)
            if rnmove in (1, 3):
                splittp1 = ((i[0]+rnmove-2)%LEN, i[1])
                splittp2 = ((i[0]-rnmove+2)%LEN, i[1])
                self.decomposeLife(decom1tp2, decom1tp, splittp1, splittp2, i)
        else: #I missed this condition and can't find it in damn long time X(
            if i not in decom1tp2.keys():
                decom1tp2[i] = copy.copy(decom1tp[i])
            else:
                decom1tp2[i][3] += decom1tp[i][3]

    def Decomposer(self):
        decom1tp = {}
        self.lifeMove(decom1tp, self.decom1)
        decom1tp2 = {}
        for i in decom1tp.keys():
            if i in self.prod1.keys(): #decompose producor into light bit
                self.envdata1[i[0]][i[1]][3] = self.prod1[i][3]
                del(self.prod1[i])
                self.decomSplit(decom1tp2, decom1tp, i)
            elif i in self.consu1.keys():
                self.envdata1[i[0]][i[1]][3] += self.consu1[i][3]
                del(self.consu1[i])
                self.decomSplit(decom1tp2, decom1tp, i)
            elif decom1tp[i][3] >= 240: #decomposer also splits if it's too big.
                self.decomSplit(decom1tp2, decom1tp, i)
            else:
                if i not in decom1tp2.keys():
                    decom1tp2[i] = copy.copy(decom1tp[i]) #all decomposers merge into decom1tp2
                else:
                    decom1tp2[i][3] += decom1tp[i][3]
        self.decom1 = copy.deepcopy(decom1tp2)
        #self.decom1 = copy.deepcopy(decom1tp) ##tft
        #print ('decom1: ', self.decom1) ##tft

    def mergeData(self):
        self.mixenv = copy.deepcopy(self.envdata1)
        for i in self.prod1.keys():
            self.mixenv[i[0]][i[1]] = copy.copy(self.prod1[i])
        for i in self.consu1.keys():
            self.mixenv[i[0]][i[1]] = copy.copy(self.consu1[i])
        for i in self.decom1.keys(): #decomposer and consumer can cover light bit.
            self.mixenv[i[0]][i[1]] = copy.copy(self.decom1[i])

    def updatePopulation(self):
        envdata1ct = 0
        for i in self.envdata1:
            for j in i:
                if j[3] > 0:
                    envdata1ct += 1
        prod1ct = len(self.prod1.keys())
        consu1ct = len(self.consu1.keys())
        decom1ct = len(self.decom1.keys())

        app.envdata1ctL.setText('Env energy count:\n%d' %envdata1ct)
        app.prod1ctL.setText('Producer1 count:\n%d' %prod1ct)
        app.consu1ctL.setText('Consumer1 count:\n%d' %consu1ct)
        app.decom1ctL.setText('Decompsr1 count:\n%d' %decom1ct)


    def updateData(self):
        #self.envEnergy()
        self.Producer()
        self.Consumer()
        self.Decomposer()
        #self.envEnergy()
        self.envEnergy() # add more envEnergy() to diffuse the energy the dead life left
        self.mergeData()
        self.updatePopulation()
        #img.setImage(self.envdata1)
        ##tft
        for i in self.mixenv:
            for j in i:
                if j[3] > 255:
                    print('orz: ', j)
                    print('PRODBIT: ',PRODBIT)
        #print(self.mixenv) ##tft
        img.setImage(self.mixenv)
        #for testing the speed of the program
        global updatect
        updatect += 1
        if updatect > 100:
            now = ptime.time()
            print('Run time: ', now - updatetime)
            app.timer.stop()




## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        updatetime = ptime.time()
        app = WidgetMore()
        envlife = EnvAndLife()
        update = envlife.updateData
        #print(type(update)) ##tft
        app.run()
        #QtGui.QApplication.instance().exec_()
        #qt_app.exec_()

