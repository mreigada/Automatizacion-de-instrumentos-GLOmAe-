import matplotlib.pyplot as plt
import os
from datetime import date
import numpy as np
import math as mt


def plotSignalInTxt(path):
    meas = np.loadtxt(path, dtype = float)
    step = meas[1,0] - meas[0,0]
    y = meas[:,1]
    #x = meas[:,0]
    #x = np.arange(0, len(y), 1)
    x = np.arange(0, len(y)*step, step)[0:len(y)]
    plt.plot(x, y, label = path.split("/")[-1].replace(".txt", ""))
    plt.xlim([x[0], x[len(x)-1]])
    #plt.xlabel("Muestras [n]", fontsize=14)
    plt.xlabel("Tiempo [s]", fontsize=14)
    plt.ylabel("Amplitud [V]", fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=12)
    plt.ion()
    #plt.get_current_fig_manager().window.state('zoomed')
    #figManager = plt.get_current_fig_manager()
    #figManager.window.showMaximized()
    
    
def plotSignalNormInTxt(path):
    meas = np.loadtxt(path, dtype = float)
    step = meas[1,0] - meas[0,0]
    y = meas[:,1]
    #x = meas[:,0]
    #x = np.arange(0, len(y), 1)
    x = np.arange(0, len(y)*step, step)[0:len(y)]
    plt.plot(x, y/ np.max(y), label = path.split("/")[-1].replace(".txt", ""))
    plt.xlim([x[0], x[len(x)-1]])
    #plt.xlabel("Muestras [n]", fontsize=14)
    plt.xlabel("Tiempo [s]", fontsize=14)
    plt.ylabel("Amplitud [V]", fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=12)
    plt.ion()
    #plt.get_current_fig_manager().window.state('zoomed')
    #figManager = plt.get_current_fig_manager()
    #figManager.window.showMaximized()


def plotFFTfromTxt(txtpath):
    meas = np.loadtxt(txtpath, dtype = float)
    x = meas[:,0]
    y = meas[:,1]

    N = len(x)
    T = x[1]-x[0]
    y_f = np.fft.fft(y)
    x_f = np.linspace(0, 1/(2*T), N//2)
    
    Y = np.abs(y_f[:N//2])
    Y = Y / np.max(Y[1:])

    plt.semilogx(x_f, Y, label = txtpath.split("/")[-1].replace(".txt", ""))
    plt.xlabel("Frecuencia [Hz]")
    plt.grid(True, which="both", ls="-")
    
    #plt.get_current_fig_manager().window.showMaximized()
    plt.legend(fontsize=12)
    plt.ion()


def plotSignalFFTtxt(txtPath):
    meas = np.loadtxt(txtPath, dtype = float)
    x = meas[:,0]
    y = meas[:,1]    
    N = len(x)
    T = x[1]-x[0]
    y_f = np.fft.fft(y)
    x_f = np.linspace(0, 1/(2*T), N//2)

    plt.figure(txtPath.split("/")[-1].replace(".txt", ""))
    plt.subplot(121)
    plt.plot(x,y,"g-")
    plt.xlim([x[0], x[len(x)-1]])
    plt.title(txtPath.split("/")[-1].replace(".txt", ""), fontsize=14)
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Amplitud [V]")
    plt.grid(True, which="both", ls="--")
    plt.minorticks_on()     
    
    plt.subplot(122)
    plt.semilogx(x_f, 2/N * np.abs(y_f[:N//2]))
    plt.title(txtPath.split("/")[-1].replace(".txt", "") + " (FFT)", fontsize=14)
    plt.xlabel("Frecuencia [Hz]")
    plt.grid(True, which="both", ls="-")
    plt.ion()
    plt.show()
    #plt.get_current_fig_manager().window.showMaximized()
    

def getTxtName():
    txtName = input("\nIngrese el nombre del archivo donde guardar resultados: ")
    return txtName

def getFilePath():
    fileName = input("\nIngrese el nombre del archivo en el que guardar resultados: ")
    return getDirectory() + "/" + fileName



def clearConsole():
    # for windows
    if os.name == 'nt':
        os.system('cls')
 
    # for mac and linux(here, os.name is 'posix')
    else:
        os.system('clear')


def getFilesList():
    folderPaths = os.listdir("Mediciones")
    pathsList = []

    for x in folderPaths:
        listFiles = os.listdir("Mediciones/" + x)
        for y in listFiles:
            pathsList.append("Mediciones/" + x + "/" + y)

    return pathsList 

def printFilesList(filesList):
    i = 1
    for x in filesList:
        print(str(i) + " - " + x.replace("Mediciones/",""))
        i=i+1

        
def getFolderName():
    folderName = input("\nIngrese el nombre de la carpeta donde guardar resultados: ")
    return folderName


def getDirectory():
    directory = "Mediciones/Mediciones " + date.today().strftime("%d-%m-%Y")
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory 


def saveAngleMeas(folderName, angle, meas):
    
    dirPath = getDirectory() + "/" + folderName
    
    if not os.path.exists(dirPath): 
        os.mkdir(dirPath)
        
    txtPath =  dirPath + "/Medicion_en_{0}°".format(angle)
    txtHeader = "[{0}]    [{1}]".format("seg.", "V")
    measArray = np.column_stack((meas[0], meas[1]))      
    np.savetxt(txtPath, measArray, fmt='%.12f', header = txtHeader)
    

def vela9mac(T):
    """
    This function allows you to determine the speed of sound in distilled water.
    as a function of temperature using the 9-term Mackenzie equation:
       
            [va]=vela9mac(T)
           
    where T is the temperature in degrees Celsius.
           
    References:
    K. Mackenzie, Nine-term equation for sound speed in the oceans,
    J. Acousti. Soc. Am. vol. 70, pp. 807-812 (1981).
    """

    a=1448.96
    b=4.591
    c=-5.304e-2
    d=2.374e-4
    e=1.340
    f=-35
    g=1.63e-2
    h=1.675e-7
    i=-1.025e-2
    j=-7.139e-13
    S=0; #(Salinidad del agua en partes por mil)
    D=0.05; #(profundidad en metros)

    va=a+b*T+c*T**2+d*T**3+e*(S+f)+g*D+h*D**2+i*T*(S+f)+j*T*D**3;

    return va


def T_estimate(A, B, R):
    return B/mt.log(R/A) - 273.15


def printTempVel(R:float):
    A = 0.1662
    B = 3969.36
    T = T_estimate(A, B, R)
    V = vela9mac(T)
    print("Temperatura: {0:0.2f} °C".format(T))
    print("Velocidad del sonido: {0:0.2f} m/s".format(V))