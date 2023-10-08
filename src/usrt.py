import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm
from IPython.display import clear_output


###############################################################################
def createImagegrid2D(nx,dx):
    N = int(nx*nx)
    x = np.linspace(-nx*dx/2,nx*dx/2,nx)
    y = np.linspace(-nx*dx/2,nx*dx/2,nx)
    xv, yv = np.meshgrid(x,y,indexing='xy')
    rj = np.zeros((2,N)) # pixel position [rj]=(2,N))
    rj[0,:] = xv.ravel()
    rj[1,:] = yv.ravel()
    rj = rj.astype(np.float32)
    return rj

###############################################################################
def plotResults(F, nx, dx):
    img = np.reshape(F,(nx,nx))
    fig, ax = plt.subplots(1, 3, figsize=(26, 5.5), gridspec_kw={"width_ratios": [1,1,1]})

    mainPlt = ax[0].imshow(img)
    fig.colorbar(mainPlt, ax=ax[0])
    ax[0].set_xlabel('x [pixel]')
    ax[0].set_ylabel('y [pixel]')

    ax[1].plot(np.arange(-nx//2,nx//2)*dx*1e3,img[nx//2,:])
    ax[1].grid()
    ax[1].set_xlabel('x [mm]')
    ax[1].set_ylabel('Amplitude (a.u.)')

    img2 = np.copy(img)
    img2[img2<0]=0
    mm=nx//2*dx*1e3
    secPlt = ax[2].imshow(img2, extent=(-mm, mm, -mm, mm), cmap="gray")
    fig.colorbar(secPlt, ax=ax[2])
    ax[2].set_xlabel('x [mm]')
    ax[2].set_ylabel('y [mm]')
    ax[2].grid()
    clear_output(wait=True)
    plt.show()

###############################################################################
def usrt(sino,pt,t,Snoise,hfrec,vs,nx,dx,Rs,arc, plot):
    """
    pt: transducer time singnal
    sino: sinograma  [Na, Nt]
    t: time axis [Nt,]
    Snoise: std of measured noise
    hfrec: value of the frequency of the ideal filter response, Hz
    vs: speed of sound of the medium, m/s
    nx = number of pixels per side of the image grid
    dx = size of the pixel, m
    Rs: distance between the transducer and the rotation axis of the sample
    arc: circunference arc [°]
    plot: plot results? True or False
    """

    t = t.astype(np.float32)
    pt = pt.astype(np.float32)
    sino = sino.astype(np.float32)

    Na, Nt = sino.shape
    dt = (t[1]-t[0])                          # s
    Fs = 1/dt                                 #[Hz]
    frec = np.arange(Nt)/Nt*Fs                # Hz [Nt, ]
    f = frec-Fs/2                             # Hz [Nt, ]
    w = 2*np.pi*f                             # 1/s [Nt, ]
    tita = np.linspace(0,arc*np.pi/180,Na+1)  # rad [Na, ]
    tita = tita[0:-1]
    dtita = (arc/Na)*np.pi/180                # rad
    N = nx*nx                                 # total number of pixels

    tita = tita.astype(np.float32)
    frec = frec.astype(np.float32)
    f = f.astype(np.float32)
    w = w.astype(np.float32)

    Ptf = np.fft.fftshift(np.fft.fft(pt)/Nt)  # [Nt,]

    Hw = np.abs(w) # [Nt,]
    Hw = np.where(Hw > 2*np.pi*hfrec, Hw*0, Hw*1) # [Nt,]
    #Hw = Hw*np.hamming(Nt)

    rj = createImagegrid2D(nx,dx)             # [2,N]
    rj = rj.astype(np.float32)
    F = np.zeros(rj.shape[1])                 # [2,N]
    F = F.astype(np.float32)
    for i2 in tqdm(range(0,Na)):
        Prf = np.fft.fftshift(np.fft.fft(sino[i2,:])/Nt)
        Sw = Prf*np.conjugate(Ptf)/(np.abs(Ptf)**2 + Snoise**2)
        Psi = Hw * Sw
        psi = 4/vs**2*np.fft.ifft(np.fft.ifftshift(Psi))
        rsx = Rs*np.cos(tita[i2]); rsy = Rs*np.sin(tita[i2])
        for i1 in range(0,N):
            ta = 2/vs*((rsx-rj[0,i1])*np.cos(tita[i2])+(rsy-rj[1,i1])*np.sin(tita[i2]))
            F[i1] = F[i1] + np.interp(ta, t, np.real(psi)) * dtita
        if plot:
          plotResults(F, nx, dx)

    return np.reshape(F,(nx,nx))