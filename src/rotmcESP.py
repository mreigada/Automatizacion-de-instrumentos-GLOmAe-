import pyvisa
import numpy as np
import time


class RotmcESP(object):
    '''Class for handling Newport motion controller of the ESP series using PyVISA interface'''

    def __init__(self, resource):
        self._resource = resource
        self._axis = 2
        self._vel = 5
        self._direction = '+'
        self._setOrigin = False


    def __call__(self, reference='ABS', rotAngle:float=0):

        self.initComm()
        self.setVelocity(self._axis, self._vel)

        if self._setOrigin == True:
            self._motorCont.write("{0}DH".format(self._axis))
            self._setOrigin = False
                    
        if reference == 'ABS':
            self.moveToAbsPosition(self._axis, rotAngle)

        elif reference == 'REL':
            self.moveToRelPosition(self._axis, rotAngle)

        currPos = self.getPosition(self._axis)    
            
        self.closeComm()

        return currPos


    def config(self, axis:int, vel:float, direction:str, setOrigin:bool):
        self._axis = axis
        self._vel = vel
        self._direction = direction
        self._setOrigin = setOrigin


    def initComm(self):
        self._motorCont = pyvisa.ResourceManager().open_resource(self._resource)
        self._motorCont.baud_rate = 19200
        self._motorCont.read_termination = '\r'
        self._motorCont.write_termination = '\r'


    def closeComm(self):
        self._motorCont.close()      

    
    def getID(self):
        return self._motorCont.query("*IDN?").replace("\n", "")
    

    def setOrigin(self, axis):
        self._motorCont.write("{0}DH".format(axis))


    def getPosition(self, axis):
        return self._motorCont.query("{0}TP".format(axis)).replace("\n", "")


    def setVelocity(self, axis, vel):
        self._motorCont.write("{0}VA{1}".format(axis,vel))


    def getVelocity(self, axis):
        return self._motorCont.query("{0}VA?".format(axis)).replace("\n", "")


    def setAcceleration(self, axis, acc):
        self._motorCont.write("{0}AC{1}".format(axis,acc))


    def getAcceleration(self, axis):
        return self._motorCont.query("{0}AC?".format(axis)).replace("\n", "")
    

    def enableAxis(self, axis):
        self._motorCont.write("{0}MO".format(axis))


    def disableAxis(self, axis):
        self._motorCont.write("{0}MF".format(axis))

    
    def moveToAbsPosition(self, axis, aPos):
        self.enableAxis(axis)
        self._motorCont.write("{0}PA{1}".format(axis,aPos))

        while(not bool(int(self._motorCont.query("{0}MD?".format(axis))))):
          time.sleep(0.01)
          #print("Axis {0} still moving".format(axis))

        self.disableAxis(axis)


    def moveToRelPosition(self, axis, rPos):
        self.enableAxis(axis)
        self._motorCont.write("{0}PR{1}".format(axis,rPos))

        while(not bool(int(self._motorCont.query("{0}MD?".format(axis))))):
          time.sleep(0.01)
          #print("Axis {0} still moving".format(axis))

        self.disableAxis(axis)


    def moveIndefinitely(self, axis, direction):
        self.enableAxis(axis)
        self._motorCont.write("{0}MV{1}".format(axis,direction))  #direction could be "+" or "-" 


    def stopMotion(self, axis):
        self._motorCont.write("{0}ST".format(axis))
        self.disableAxis(axis)