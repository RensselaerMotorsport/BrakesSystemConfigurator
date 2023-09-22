import numpy as np
import matplotlib.pyplot as plt
import math as Math
from scipy.optimize import fsolve

debug = True

#MOTOR VARIABLES: Emrax 228 HV 
motor_cooling = "combined"
I_max_motor = 250 #A
#I_Continuous_motor = 125 #A
if motor_cooling == "air":
    P_continuous_motor = 55 #kW
    T_continuous_motor = 96 #Nm
elif motor_cooling == "liquid":
    P_continuous_motor = 64 #kW
    T_continuous_motor = 112 #Nm
elif motor_cooling == "combined":
    P_continuous_motor = 62 #kW
    T_continuous_motor = 130 #Nm
P_max_motor = 124 #kW @ 5500 RPM
I_Continuous_motor = P_continuous_motor*1000/399


#ESC VARIABLES: Rinehart PM100DX 
V_max_ESC = 400 #V
I_max_ESC = 300 #A
I_continuous_ESC = 350 #A
P_max_ESC = 100 #kW

#CELL VARIABLES
#import values from database
cellDatabase = np.loadtxt(open("18650 cell database.csv", "rb"), delimiter=",", skiprows=2, dtype=str)

cellBrand = np.asanyarray(cellDatabase[:, [3]], dtype = str)
cellModel = np.asanyarray(cellDatabase[:, [4]], dtype = str) 
cellCost = np.asanyarray(cellDatabase[:, [5]], dtype = float) #USD
cellCostSale = np.asanyarray(cellDatabase[:, [6]], dtype = float) #USD
cellMass = np.asanyarray(cellDatabase[:, [15]], dtype = float) #g
cellResistance = np.asanyarray(cellDatabase[:, [11]], dtype = float) #mOhm
cellChemistry = np.asanyarray(cellDatabase[:, [7]], dtype = str) #NCA, NMC, LFP, etc.

V_cell = np.asanyarray(cellDatabase[:, [13]], dtype = float) #V
I_cell = np.asanyarray(cellDatabase[:, [10]], dtype = float) #A
C_cell = np.asanyarray(cellDatabase[:, [9]], dtype = float)  #mAh


#bulk discount data
range1Min = np.asanyarray(cellDatabase[:, [17]], dtype = float) #min number of cells for discount
range1Max = np.asanyarray(cellDatabase[:, [18]], dtype = float) #max number of cells for discount
range1Cost = np.asanyarray(cellDatabase[:, [19]], dtype = float) #discount for range 1 (USD)
range2Min = np.asanyarray(cellDatabase[:, [20]], dtype = float) #min number of cells for discount
range2Max = np.asanyarray(cellDatabase[:, [21]], dtype = float) #max number of cells for discount
range2Cost = np.asanyarray(cellDatabase[:, [22]], dtype = float) #discount for range 2 (USD)
range3Min = np.asanyarray(cellDatabase[:, [23]], dtype = float) #min number of cells for discount
range3Max = np.asanyarray(cellDatabase[:, [24]], dtype = float) #max number of cells for discount
range3Cost = np.asanyarray(cellDatabase[:, [25]], dtype = float) #discount for range 3 (USD)
range4Min = np.asanyarray(cellDatabase[:, [26]], dtype = float) #min number of cells for discount
range4Max = np.asanyarray(cellDatabase[:, [27]], dtype = float) #max number of cells for discount
range4Cost = np.asanyarray(cellDatabase[:, [28]], dtype = float) #discount for range 4 (USD)
range5Min = np.asanyarray(cellDatabase[:, [29]], dtype = float) #min number of cells for discount
range5Max = np.asanyarray(cellDatabase[:, [30]], dtype = float) #max number of cells for discount
range5Cost = np.asanyarray(cellDatabase[:, [31]], dtype = float) #discount for range 5 (USD)
range6Min = np.asanyarray(cellDatabase[:, [32]], dtype = float) #min number of cells for discount
range6Max = np.asanyarray(cellDatabase[:, [33]], dtype = float) #max number of cells for discount
range6Cost = np.asanyarray(cellDatabase[:, [34]], dtype = float) #discount for range 6 (USD)

#convert units
C_cell = C_cell/1000 #Ah
cellMass = cellMass/1000 #kg

#ACCUMULATOR VARIABLES
E_accumulator = np.zeros((len(cellBrand),15,15)) #kWh
V_accumulator = np.zeros((len(cellBrand),15)) #V
I_accumulator = np.zeros((len(cellBrand),15,15)) #A
P_accumulator = np.zeros((len(cellBrand),15,15)) #kW
C_accumulator = np.zeros((len(cellBrand),15,15)) #Ah
dischargeTime_accumulator = np.zeros((len(cellBrand),15,15)) #hours
segmentEnergy = np.zeros((len(cellBrand),15,15)) #J
segmentVoltage = np.zeros((len(cellBrand),15,15)) #V

V_accumulator_max = 0
V_accumulator_min = 0

accumulator_cost = np.zeros((len(cellBrand),15,15,15)) #USD
accumulator_mass = np.zeros((len(cellBrand),15,15,15)) #kg

percentDifference_E = np.zeros(len(cellBrand)) #kwH
percentDifference_V = np.zeros(len(cellBrand)) #V
percentDifference_I = np.zeros(len(cellBrand)) #A
percentDifference_P = np.zeros(len(cellBrand)) #kW
percentDifference_dischargeTime = np.zeros(len(cellBrand)) #hours
percentDifferenceAverage = np.zeros(len(cellBrand)) #percent difference between actual and target values

s = np.zeros((len(cellBrand),15)) #number of cells in series to reach target voltage
p = np.zeros((len(cellBrand),15,15)) #number of cells in parallel to reach target current

I_mainFuse = np.zeros((len(cellBrand),15,15))

segments = np.zeros((len(cellBrand),15,15,15)) #number of segments
p_segment = np.zeros((len(cellBrand),15,15,15)) #number of cells in parallel per segment
s_segment = np.zeros((len(cellBrand),15,15,15)) #number of cells in series per segment
V_segment = np.zeros((len(cellBrand),15,15,15)) #V
I_segment = np.zeros((len(cellBrand),15,15,15)) #A
E_segment = np.zeros((len(cellBrand),15,15,15)) #J
I_fuse_cell = np.zeros((len(cellBrand),15,15,15)) #A


#TARGET ACCUMULATOR VALUES
E_target_accumulator = 8 #kWh
V_target_accumulator = V_max_ESC #V
I_target_max_accumulator = min(I_max_ESC , I_max_motor) #A
I_target_accumulator = min(I_continuous_ESC, I_Continuous_motor) #A
P_target_accumulator = min(P_max_ESC, P_max_motor)
dischargeTime_target_accumulator = 0.08 #hours

#FUSING VARIABLES
#material constants for strip / wire fusing material
specificResistance_nickel = 6.99e-8 #Ohm*m
specificResistance_copper = 1.68e-8 #Ohm*m
specificResistance_aluminum = 2.82e-8 #Ohm*m
specificResistance_steel = 1.43e-7 #Ohm*m

density_nickel = 8908 #kg/m^3
density_copper = 8960 #kg/m^3
density_aluminum = 2700 #kg/m^3
density_steel = 7850 #kg/m^3

resistivity = np.zeros(len(cellBrand))
resistivity_nickel = 7*10**(-8) #Ohm*m @20C
resistivity_copper = 1.68*10**(-8) #Ohm*m @20C
resistivity_aluminum = 2.82*10**(-8) #Ohm*m @20C
resistivity_steel = 1.43*10**(-7) #Ohm*m @20C

tempCoeficentOfResistance = np.zeros(len(cellBrand))
tempCoeficentOfResistance_nickel = 0.006 #1/K
tempCoeficentOfResistance_copper = 0.00393 #1/K
tempCoeficentOfResistance_aluminum = 0.0043 #1/K
tempCoeficentOfResistance_steel = 0.0066 #1/K

heatCapacity_nickel = 440 #J/kg*K
heatCapacity_copper = 385 #J/kg*K
heatCapacity_aluminum = 900 #J/kg*K
heatCapacity_steel = 490 #J/kg*K

#cell chemistry constants, specific heat capacity (J/kg*K) is usually between 800-1200 J/kg*K for lithium ion batteries
heatCapacity_NCA = 830 #J/kg*K LiNiCoAlO2, Lithium Nickel Cobalt Aluminum Oxide	
heatCapacity_NMC = 1040 #J/kg*K (NMC and INR are the same) LiNiMnCoO2, Lithium Manganese Nickel	
heatCapacity_LFP = 1130 #J/kg*K (LFP and IFR are the same) LiFePO4, Lithium Iron Phosphate		

#web strip fusing variables
thickness = np.zeros(len(cellBrand)) #mm (0.15mm is standard for amazon plated fusing)
webWidth = np.zeros(len(cellBrand)) #mm (7mm is standard for amazon plated fusing)
cellSpacing = np.zeros(len(cellBrand)) #mm (20.2mm is standard)
areaBetweenGroups = np.zeros(len(cellBrand)) #mm^2
resistanceBetweenGroups = np.zeros(len(cellBrand)) #mOhm


#ampacity = np.zeros(len(cellBrand),4) #A  the maximum current that a conductor can carry continuously under expected operating conditions without exceeding its temperature rating
wr = np.zeros(len(cellBrand)) #W heat dissipated by radiation
wc = np.zeros(len(cellBrand)) #W heat dissipated by natural convection
wfc = np.zeros(len(cellBrand)) #W heat dissipated by forced convection
R_fuse = np.zeros(len(cellBrand)) #mOhm resistance of the fusing material at operating temperature

#cooling variables
operatingTemperature = 60 #C

#FUNCTION: calculate strip fusing 
def calculateStripFusing(cellIndex):
    areaBetweenGroups = (webWidth[cellIndex]**2) * cellSpacing[cellIndex] #mm^2
    resistanceBetweenGroups = (cellSpacing[cellIndex] * 1/(thickness[cellIndex]*areaBetweenGroups[cellIndex]))/100 #mOhm

    #assign heat capacity based on cell chemistry
    if (cellChemistry[cellIndex] == "NCA"):
        heatCapacity = heatCapacity_NCA #J/kg*K
    elif (cellChemistry[cellIndex] == "NMC" or cellChemistry[cellIndex] == "INR"): #INR and NMC are the same
        heatCapacity = heatCapacity_NMC #J/kg*K
    elif (cellChemistry[cellIndex] == "LFP" or cellChemistry[cellIndex] == "IFR"): #IFR and LFP are the same
        heatCapacity = heatCapacity_LFP #J/kg*K

    #iterate through possible fuse materials 
    for i in range(4):
        R_fuse[i] = (resistivity[i] + operatingTemperature * tempCoeficentOfResistance[i])
        wc = 1 / ()
        #ampacity[cellIndex] = ((wr+wc)/R_fuse)**(0.5)

    

#FUNCTION: print accumulator values for a given cell
def printAccumulatorValues(cellIndex,description):
    """
    Prints the accumulator values for a given cell
    INPUTS:
        cellIndex: index of the cell in the database
    OUTPUTS:
        none
    """
    print("The cell that", description, cellBrand[cellIndex], cellModel[cellIndex], "cell")
    print("Number of cells in series:", s[cellIndex], "cells")
    print("Number of cells in parallel:", p[cellIndex], "cells")
    print("The accumulator has a voltage of", round(V_accumulator[cellIndex] , 4), "V")
    print("The accumulator has a current of", round(I_accumulator[cellIndex] , 4), "A")
    print("The accumulator has a power of", round(P_accumulator[cellIndex] , 4), "kW")
    print("The accumulator has a capacity of", round(C_accumulator[cellIndex] , 4), "Ah")
    print("The accumulator has a discharge time of", round(dischargeTime_accumulator[cellIndex] , 5), "hours")
    print("The accumulator has an energy of", round(E_accumulator[cellIndex] , 3), "kWh")
    print("The accumulator has a cost of $",round(accumulator_cost[cellIndex] , 6), "USD")
    print("The accumulator has a mass of", round(accumulator_mass[cellIndex] , 4), "kg")
    print("")

    #print all possible segment configurations for this accumulator
    print("The following segment configurations are possible for this accumulator:")
    for i in range(len(segments[cellIndex])):
        if (segments[cellIndex,i] != 0):
            print("Segment", i+1, "has", p_segment[cellIndex,i], "cells in parallel and", s_segment[cellIndex,i], "cells in series")
            print("Segment", i+1, "has a voltage of", V_segment[cellIndex,i], "V")
            print("Segment", i+1, "has a current of", I_segment[cellIndex,i], "A")
            print("Segment", i+1, "has an energy of", E_segment[cellIndex,i], "J")
            print("Segment", i+1, "has a fuse current of", I_fuse_cell[cellIndex,i], "A")
            print("")

#CALCULATE ACCUMULATOR VALUES
#calculate accumulator values for each cell
for i in range(len(cellBrand)):
    #create accumulator voltage targets: +-0.75% of target voltage
    V_accumulator_max = (V_target_accumulator * 1.0075) #V
    V_accumulator_min = V_target_accumulator * 0.9925 #V
    
    
    s_max = Math.floor(V_accumulator_max / V_cell[i]) #V
    s_min = Math.floor(V_accumulator_min / V_cell[i]) #V

    #create array of intgers between s_max and s_min
    s_accumulator_range = np.arange(s_min, s_max+1, 1)
    
    print("S_accumulator_range",s_accumulator_range)

    #loop through possible number of cells in series
    for j in range(len(s_accumulator_range)):
        #get closest integer number of cells in series to reach target voltage
        s[i,j] = s_accumulator_range[j]

        #calculate accumulator voltage
        V_accumulator[i,j] = s[i,j] * V_cell[i] #V

        #get closest integer number of cells in parallel to reach target current
        p_max = Math.floor(I_Continuous_motor / I_cell[i]) #A
        p_min = Math.floor((I_Continuous_motor-50) / I_cell[i]) #A
        
        

        #create array of integers between p_max and p_min
        p_accumulator_range = np.arange(p_min, p_max+1, 1)


        #loop through possible number of cells in parallel
        for k in range(len(p_accumulator_range)):
            #get closest integer number of cells in parallel to reach target current
            p[i,j,k] = p_accumulator_range[k] #A

            V_accumulator[i,j] = s[i,j] * V_cell[i] #V
            I_accumulator[i,j,k] = p[i,j,k] * I_cell[i] #A
            P_accumulator[i,j,k] = V_accumulator[i,j] * I_accumulator[i,j,k] / 1000 #kW
            E_accumulator[i,j,k] = p[i,j,k] * s[i,j] * C_cell[i] * V_cell[i] / 1000 #kwH 
            C_accumulator[i,j,k] = C_cell[i] * p[i,j,k] #Ah
            dischargeTime_accumulator[i,j,k] = C_accumulator[i,j,k] / I_accumulator[i,j,k] #hours


            #fuse max value is I_Continuous_motor (DC)
            #standard fuse sizes are 80,90,100,150,180,200
            #https://www.digikey.com/en/products/filter/electrical-specialty-fuses/155?s=N4IgjCBcoGw1oDGUBmBDANgZwKYBoQB7KAbRACYAOAdgAYBWSkA8gTlceuZBkvttrdq1co26UAzNUqCCfeq3gFWAFnoSl4AbTBMCYBsIncwptSpNgVKibPAra5chAC6BAA4AXKCADKngCcASwA7AHMQAF8WKwtoEGRIdGx8IlIQahhyWhUuAkzs%2BjyMrIZ6IVL6C3zK8grCiBrCuwKc1nqcpjcQLx9-YPCoggBaOvjEwIBXVOJIMnKXSKWgA
            #set fuse size to closest standard fuse size that is less than I_Continuous_motor
            if (I_accumulator[i,j,k] < 90):
                I_mainFuse[i,j,k] = 80
            elif (I_accumulator[i,j,k] < 100):
                I_mainFuse[i,j,k] = 90
            elif (I_accumulator[i,j,k] < 150):
                I_mainFuse[i,j,k] = 100
            elif (I_accumulator[i,j,k] < 180):
                I_mainFuse[i,j,k] = 150
            elif (I_accumulator[i,j,k] < 200):
                I_mainFuse[i,j,k] = 180


            #loop through possible number of segments
            for n in range(1, 15):
                #check if whole number of segments
                if (s[i,j] % n != 0):
                    #set segment value to zero
                    s_segment[i,j,k,n] = 0
                else:

                    #calculate segment values
                    s_segment[i,j,k,n] = (s[i,j]/n)
                    p_segment[i,j,k,n] = p[i,j,k]
                    V_segment[i,j,k,n] = s_segment[i,j,k,n] * V_cell[i] #V
                    I_segment[i,j,k,n] = p_segment[i,j,k,n] * I_cell[i] #A
                    E_segment[i,j,k,n] = p_segment[i,j,k,n] * s_segment[i,j,k,n] * C_cell[i] * V_cell[i] #J
                    
                    

                    I_fuse_cell[i,j,k,n] = I_mainFuse[i,j,k] * 3 / p_segment[i,k,k,n] #A
                
                    #check if rules legal
                    #check if segment voltage is more than 120V
                    if (V_segment[i,j,k,n] > 120):
                        #set segment value to zero
                        segments[i,j,k,n] = 0
                        if (debug==True):
                            print("rejected because segment voltage is more than 120V")        
                    #check if segment energy is more than 6 MJ
                    elif (E_segment[i,j,k,n] > 6000000):
                        #set segment value to zero
                        segments[i,j,k,n] = 0
                        if (debug==True):
                            print("rejected because segment energy is more than 6MJ")
                    #calculate cell-level fuse continuous current
                    #reject combination of cells in segment if the continuous current of the fuse is more than 55A (max we can test) or more than 2*discharge current of the cell (ESF requirement)
                    elif (I_fuse_cell[i,j,k,n] > 55 or I_fuse_cell[i,j,k,n] > 2*I_cell[i]):
                        #set segment value to zero
                        segments[i,j,k,n] = 0
                        if (debug==True):
                            print("rejected because fuse current is more than 55A or more than 2*cell discharge current")
                
                    segments[i,j,k,n] = n

"""
#calculate percent difference between actual and target values
for i in range(len(cellBrand)):
    percentDifference_E[i] = abs(E_accumulator[i] - E_target_accumulator) / E_target_accumulator * 100 
    percentDifference_V[i] = abs(V_accumulator[i] - V_target_accumulator) / V_target_accumulator * 100
    percentDifference_I[i] = abs(I_accumulator[i] - I_target_accumulator) / I_target_accumulator * 100 
    percentDifference_P[i] = abs(P_accumulator[i] - P_target_accumulator) / P_target_accumulator * 100 
    percentDifference_dischargeTime[i] = abs(dischargeTime_accumulator[i] - dischargeTime_target_accumulator) / dischargeTime_target_accumulator * 100 #hours

    #calculate the percent difference
    percentDifferenceAverage[i] = (percentDifference_E[i] + percentDifference_V[i] + percentDifference_I[i] + percentDifference_P[i] + percentDifference_dischargeTime[i]) / 5



#find the cell with the lowest average percent difference, lowest cost, and lowest weight
minDiffCellIndex = np.argmin(percentDifferenceAverage)
minCostCellIndex = np.argmin(accumulator_cost)
minMassCellIndex = np.argmin(accumulator_mass)


#OUTPUT RESULTS
#output cells that create the best accumulators, as measured by percent difference to goal, cost, or weight
#if cell with lowest average percent difference is the same as the cell with the lowest cost and lowest mass
if (minDiffCellIndex == minCostCellIndex and minDiffCellIndex == minMassCellIndex):
    #output accumulator values for the cell with the lowest average percent difference and lowest cost and lowest mass
    printAccumulatorValues(minDiffCellIndex, "has the lowest average percent difference, lowest cost, and lowest weight is: ")
#if cell with lowest average percent difference is the same as the cell with the lowest cost
elif (minDiffCellIndex == minCostCellIndex):
    #output accumulator values for the cell with the lowest average percent difference and lowest cost
    printAccumulatorValues(minDiffCellIndex, "has the lowest average percent difference and lowest cost is: ")
    #output accumulator values for the cell with the lowest mass
    printAccumulatorValues(minMassCellIndex, "has the lowest mass is: ")
#if cell with lowest average percent difference is the same as the cell with the lowest mass
elif (minDiffCellIndex == minMassCellIndex):
    #output accumulator values for the cell with the lowest average percent difference and lowest mass
    printAccumulatorValues(minDiffCellIndex, "has the lowest average percent difference and lowest weight is: ")
    #output accumulator values for the cell with the lowest cost
    printAccumulatorValues(minCostCellIndex, "has the lowest cost is: ")
#if cell with lowest cost is the same as the cell with the lowest mass
elif (minCostCellIndex == minMassCellIndex):
    #output accumulator values for the cell with the lowest cost
    printAccumulatorValues(minCostCellIndex, "has the lowest cost and lowest weight is: ")
    #output accumulator values for the cell with the lowest average percent difference
    printAccumulatorValues(minDiffCellIndex, "has the lowest average percent difference is: ")
else:
    #output accumulator values for the cell with the lowest average percent difference
    printAccumulatorValues(minDiffCellIndex, "has the lowest average percent difference is: ")
    #output accumulator values for the cell with the lowest cost
    printAccumulatorValues(minCostCellIndex, "has the lowest cost is: ")
    #output accumulator values for the cell with the lowest mass
    printAccumulatorValues(minMassCellIndex, "has the lowest mass is: ")

#create a ranking 


#TBD, limit by rules requirements for segment energy and voltage 
"""

#calculate the cost and mass of the accumulator
for i in range(len(cellBrand)):
    for j in range(len(s_accumulator_range)):
        for k in range(len(p_accumulator_range)):
            for n in range(len(segments)):
                #if segment value is not zero
                if (segments[i,j,k,n] != 0):
                    #calculate segment mass
                    accumulator_mass[i,j,k,n] = p[i,j,k] * s[i,j] * cellMass[i] #kg

                    #calculate accumulator price
                    #account for sale price if applicable
                    if (cellCostSale[i] != -1):
                        accumulator_cost[i,j,k,n] = p[i,j,k] * s[i,j] * cellCostSale[i]
                    #account for bulk discount if applicable
                    elif (p[i,j,k] * s[i,j] >= range6Min[i] and p[i,j,k] * s[i,j] <= range6Max[i]):
                        accumulator_cost[i,j,k,n] = p[i,j,k] * s[i,j] * range6Cost[i]
                    elif (p[i,j,k] * s[i,j] >= range5Min[i] and p[i,j,k] * s[i,j] <= range5Max[i]):
                        accumulator_cost[i,j,k,n] = p[i,j,k] * s[i,j] * range5Cost[i]
                    elif (p[i,j,k] * s[i,j] >= range4Min[i] and p[i,j,k] * s[i,j] <= range4Max[i]):
                        accumulator_cost[i,j,k,n] = p[i,j,k] * s[i,j] * range4Cost[i]
                    elif (p[i,j,k] * s[i,j] >= range3Min[i] and p[i,j,k] * s[i,j] <= range3Max[i]):
                        accumulator_cost[i,j,k,n] = p[i,j,k] * s[i,j] * range3Cost[i]
                    elif (p[i,j,k] * s[i,j] >= range2Min[i] and p[i,j,k] * s[i,j] <= range2Max[i]):
                        accumulator_cost[i,j,k,n] = p[i,j,k] * s[i,j] * range2Cost[i]
                    elif (p[i,j,k] * s[i,j] >= range1Min[i] and p[i,j,k] * s[i,j] <= range1Max[i]):
                        accumulator_cost[i,j,k,n] = p[i,j,k] * s[i,j] * range1Cost[i]
                    #otherwise, no discount
                    else:
                        accumulator_cost[i,j,k,n] = p[i,j,k] * s[i,j] * cellCost[i]
#OUTPUT RESULTS



#output accumulator values for each cell
for i in range(len(cellBrand)):

    #output cell brand
    print("Cell:", cellBrand[i], cellModel[i])
    print("")
    #output accumulator values each voltage combination
    for j in range(len(s_accumulator_range)):

        #output accumulator values each current combination
        for k in range(len(p_accumulator_range)):
            
            #output accumulator values for each segment combination
            for n in range(len(segments)):

                #if segment value is not zero
                if (segments[i,j,k,n] != 0):

                    #output accumulator values
                    print("Number of cells in parallel:", p[i,j,k], "cells")
                    print("Number of cells in series:", s[i,j], "cells")
                    print("Voltage:", V_accumulator[i,j], "V")
                    print("Current:", I_accumulator[i,j,k], "A")
                    print("Energy:", E_accumulator[i,j,k], "J")
                    print("Fuse current:", I_mainFuse[i,j,k], "A")
                    print("Cell-level fuse current:", I_fuse_cell[i,j,k,n], "A")
                    print("")

                    print("Segment:", segments[i,j,k,n])
                    print("Number of cells in parallel (segment):", p_segment[i,j,k,n], "cells")
                    print("Number of cells in series (segment):", s_segment[i,j,k,n], "cells")
                    print("Voltage:", V_segment[i,j,k,n], "V")
                    print("Current:", I_segment[i,j,k,n], "A")
                    print("Energy:", E_segment[i,j,k,n], "J")
                    print("")

                    print("Cost:", accumulator_cost[i,j,k,n], "USD")
                    print("Mass:", accumulator_mass[i,j,k,n], "kg")
                    print("")

    print("------------------------------")



