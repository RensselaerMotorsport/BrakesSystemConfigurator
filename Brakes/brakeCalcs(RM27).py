from math import pi
import matplotlib.pyplot as plt
import numpy as np

"""Definining Constants"""
wd= 0.49 # front weight distribution: guestimate from Michael
a = 1.1 #acceleration during braking: taken from RM25 brake test data (G)
Pf = 1165 #max line pressure front: from RM25 data (PSI)
Pr = 787 #max line pressure rear: from RM25 data (PSI)
RR = 3.223 #rotor radius: effective, for 8" rotor (in)
R = 8 #tire radius (in)
h = 13.0 #CG height: Jasper & Michael's guestimate (in)
WB = 60.5 #wheelbase length, in, Michael & Jasper's Guestimate
A_22_049 = (((0.984252/2)**2)*pi) #ISR 22-049 piston area (in^2)
A_GP200 = 1.23  #Wilwood GP200 piston area (in^2)
u_22_049 = 0.7 #coeficent of friction between ISR 22-059 pad & rotor: obtained from ISR
u_GP200 = 0.5 #coeficent of friction between Wilwood GP200 pad & rotor: obtained from Wilwood
u_TG = 1.1 #coeficent of friction between tire and ground, g, stolen shamelessly from Zips' design report



def stop_at_weight(min,max):
    """calculates if there is enough force to stopping at a range of vehicle weights"""
    
    n = max - min
    WT = np.zeros(n) #weight transfer (lb)
    NLF = np.zeros(n) #normal load front (lb)
    NLR  = np.zeros(n) #normal load rear (lb)
    TF = np.zeros(n) #required torque front (lb*in)
    TR = np.zeros(n) #required torque rear (lb*in)
    w = np.zeros(n) # weight (lb)
    
    # calculate at range of weights
    for i in range(0,n,1):
        w[i] = i + min + 1
        WT[i] = ((h*(w[i])*a)/WB) #weight transfer, lbs
        NLF[i] = ((((w[i])*wd)+WT[i])/2) #normal load front, per wheel, after weight transfer
        NLR[i] = (w[i]-(2*NLF[i]))/2 #normal load rear, per wheel, after weight transfer
        TF[i] = R*NLF[i]*u_TG*1.5 #required torque front, per wheel, (to stop car), in lbs
        TR[i] = R*NLR[i]*u_TG*1.5 #required torque front, per wheel (to stop car), in lbs
    
    # calculate max torque calipers can generate
    #mtf_Wilwood = 2 *u_GP200*RR*A_GP200*Pf #max torque front, Wilwood 
    mtf_Wilwood = 2 *u_22_049*RR*A_22_049*Pf #max torque front, Wilwood 
    mtr_ISR = 2*u_22_049*RR*A_22_049*Pr #max torque front, ISR
     
    #plot Weight VS Stopping Torque (note, if dotted line below solid line, thats good)
    plt.title("RM26 Weight vs Stopping Torque", fontsize=14)

    plt.figure(1, figsize=(6, 4))
    plt.xlabel("weight, lbs", fontsize=12)
    plt.ylabel("torque, in-lbs", fontsize=12)
    plt.plot(w, TF, linestyle="--",color='r', label='required torque front')
    plt.axhline(y=mtf_Wilwood, c='r', label='max torque front, (GP200)')
    plt.plot(w, TR, linestyle="--",color='b', label='required torque rear')
    plt.axhline(y=mtr_ISR, c='b', label='max torque rear (ISR)')

    plt.fill_between(w, TR, mtr_ISR)
    plt.fill_between(w, TF, mtf_Wilwood)
    
    plt.legend()
    plt.show()

   
stop_at_weight(700,900)    



    
    
    
    
    
    