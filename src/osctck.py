import pyvisa
import numpy as np
import time


class Osctck(object):
    '''Class for handling Tektronix oscilloscopes of the TDS series using PyVISA interface'''    

    def __init__(self, resource:str):
        self._resource = resource
        self._channels = (1,)
        self._triggerSource = 'EXT'                 
        self._triggerLevel = 0
        self._triggerSlope = 'FALL'
        self._triggerMode = 'NORM'
        self._triggerCoup = 'AC'
        self._acquisition = 1
        self._vAutoScale = False
        

    def __call__(self):
        self.initComm()
        self.setEdgeTrigger(self._triggerSource, self._triggerSlope, self._triggerMode, self._triggerCoup, self._triggerLevel)
        
        if self._vAutoScale == True:
            for chNum in self._channels:
                self.useAlternativeAutorange(chNum)
        
        self.setAcquisition(acqMode = 1)
        if self._acquisition !=1:
            self.setAcquisition(self._acquisition)
        
        self.stop()
        values = self.getHorValues(self._channels[0])
        for chNum in self._channels:
            values = np.vstack((values, self.getVertValues(chNum)))            
        self.run()        
        
        self.closeComm()        
        return values

           
    def initComm(self):
        self._osci = pyvisa.ResourceManager().open_resource(self._resource)
        #Setting of the curves to acquire
        self._osci.write('DAT:ENC RPB')   #Data Format: Positive Binary. 
        self._osci.write('DAT:WID 1')     #Number of bytes per data point: 1 byte.
        self._osci.write("DAT:STAR 1")    #The curve to be transferred starts at the first data on the screen.
        self._osci.write("DAT:STOP 2500") #The curve to be transferred ends at the last data on the screen.

    
    def closeComm(self):
        self._osci.close()       #Closing the communication session with the oscilloscope.
   

    def config(self, channels:tuple, triggerSource:str, triggerLevel:float, triggerSlope:str, triggerMode:str, triggerCoup:str, acquisition:int, vAutoScale:bool):
        self._channels = channels
        self._triggerSource = triggerSource                 
        self._triggerLevel = triggerLevel
        self._triggerSlope = triggerSlope
        self._triggerCoup = triggerCoup
        self._acquisition = acquisition
        self._vAutoScale = vAutoScale
        self._triggerMode = triggerMode


    def setVertScale(self, channel, vScale):
        self._osci.write("CH{0}:SCA {1}".format(channel,vScale))
        
        
    def getVertScale(self, channel):
        return float(self._osci.query("CH{0}:SCALE?".format(channel))) #Returns the current vertical scale of the channel.


    def setHScale(self, horizontalScale, zero=0):
        self._osci.write("HOR:SCA {0}".format(horizontalScale))
        self._osci.write("HOR:POS {0}".format(zero))	


    def run(self):
        self._osci.write("ACQ:STATE RUN")


    def stop(self):
        self._osci.write("ACQ:STATE STOP")   


    def setAcquisition(self, acqMode):
        if acqMode == 1:
            self.setSampAcquisition()

        elif acqMode == 4:
            self.setAvgAcquisition(nAvg = 4)
 
        elif acqMode == 16:
            self.setAvgAcquisition(nAvg = 16)
 
        elif acqMode == 64:
            self.setAvgAcquisition(nAvg = 64)

        elif acqMode == 128:
            self.setAvgAcquisition(nAvg = 128)


    def setAvgAcquisition(self, nAvg):
        self._osci.write("ACQ:MOD AVE")
        self._osci.write("ACQ:NUMAV {0}".format(nAvg))
        time.sleep(float(nAvg)/self.getTriggerFreq()) 
       

    def setSampAcquisition(self):
        self._osci.write("ACQ:MOD SAMP")  #acquisitionMode can be SAMple, PEAKdetect or AVErage
        time.sleep(2)


    def setEdgeTrigger(self, source="CH1", slope="FALL", mode="NORM", coupling="AC", level=0):
        self._osci.write("TRIG:MAI:TYP EDGE")
        self._osci.write("TRIG:MAI:EDGE:SOU {0}".format(source))    #source can be CH1, CH2, EXT, EXT5, LINE
        self._osci.write("TRIG:MAI:EDGE:SLO {0}".format(slope))     #slope can be FALL or RISe
        self._osci.write("TRIG:MAI:MOD {0}".format(mode))           #mode can be AUTO or NORMal
        self._osci.write("TRIG:MAI:EDGE:COUP {0}".format(coupling)) #coupling can be AC or DC
        self._osci.write("TRIG:MAI:LEV {0}".format(level))          #level must be between -1.4 and 1.6 
     

    def useAlternativeAutorange(self, channel):        
        self.run()
        self.setAcquisition(1)

        vScale = self.getVertScale(channel)
        maxValue = np.max(np.absolute(self.getVertValues(channel)))
        
        while 4*vScale <= maxValue:
            vScale = 4*vScale
            self.setVertScale(channel,vScale)
            maxValue = np.max(np.absolute(self.getVertValues(channel)))            
        
        vScale = maxValue/3.7
        self.setVertScale(channel,vScale)
            

    def getVertValues(self, channel):
        self._osci.write("SEL:CH{0} ON".format(channel))
        self._osci.write("DAT:SOU CH{0}".format(channel)) #The channel from which to read the data is selected.  
        yze, ymu, yoff = self._osci.query_ascii_values('WFMP:YZE?;YMU?;YOFF?;', separator=';') 
        dataY = (self._osci.query_binary_values('CURV?', datatype='B', container=np.array) - yoff) * ymu + yze
        return np.array(dataY)


    def getHorValues(self, channel):
        self._osci.write("SEL:CH{0} ON".format(channel))
        self._osci.write("DAT:SOU CH{0}".format(channel)) #The channel from which to read the data is selected.
        xze, xin = self._osci.query_ascii_values('WFMP:XZE?;XIN?;', separator=';')   
        dataX = xze + np.arange(len(self.getVertValues(channel))) * xin
        return np.array(dataX)
    

    def getTriggerFreq(self):
        return float(self._osci.query("TRIGger:MAIn:FREQuency?"))


    def getID(self):
        return self._osci.query("*IDN?")
        

    def setupDefault(self):
        self._osci.write("RECALL:SETUP FACTORY")


    def setChannel(self, channel, zero=0, coupling='AC', bwLimit='OFF', probeFactor=1, invert='OFF'):
        #self._osci.write("CH{0}:SCA {1}".format(channel, vScale))
        self._osci.write("CH{0}:POS {1}".format(channel,zero))
        self._osci.write("CH{0}:COUP {1}".format(channel,coupling)) #coupling can be AC, DC or GND
        self._osci.write("CH{0}:BANDWIDTH {1}".format(channel,bwLimit)) #bwLimit can be ON or OFF
        self._osci.write("CH{0}:PROBE {1}".format(channel,probeFactor)) #probeFactor can be 1, 10, 20, 50, 100, 500 or 1000
        self._osci.write("CH{0}:INV {1}".format(channel,invert)) #invert can be ON or OFF


    def getHScale(self):
        return self._osci.query("HOR?") #Returns the current horizontal configuration of the scope.
    

    def invertChannel(self, channel, state='OFF'):
        self._osci.write("CH{0}:INV {1}".format(channel,state))
        

    def useAutorange(self, setting):
        self._osci.write("AUTOR:SETT {0}".format(setting)) #setting can be HORizontal, VERTical or BOTH
        self._osci.write("AUTOR:STATE ON")


    def executeAutoSet(self):
        self._osci.write("AUTOS EXEC")


    def showChannel(self, channel):
        self._osci.write("SEL:CH{0} ON".format(channel))


    def hideChannel(self, channel):
        self._osci.write("SEL:CH{0} OFF".format(channel))


    def setFFTMode(self, channel, window = 'HANNING'):
        self._osci.write('MATH:DEFINE "FFT (CH{0}, {1})"'.format(channel, window))  #window can be HANNING, FLATtop or RECTangular