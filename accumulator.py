import numpy as np
import matplotlib.pyplot as plt
import math

#MOTOR VARIABLES: Emrax 228 HV 
motor_cooling = "liquid"
I_max_motor = 250 #A
I_Continuous_motor = 125 #A
if motor_cooling == "air":
    P_continuous_motor = 55 #kW
    T_continuous_motor = 96 #Nm
elif motor_cooling == "liquid":
    P_continuous_motor = 64 #kW
    T_continuous_motor = 112 #Nm
elif motor_cooling == "combined":
    P_continuous_motor = 75 #kW
    T_continuous_motor = 130 #Nm
P_max_motor = 124 #kW @ 5500 RPM

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
cellMass = np.asanyarray(cellDatabase[:, [14]], dtype = float) #g

V_cell = np.asanyarray(cellDatabase[:, [12]], dtype = float) #V
I_cell = np.asanyarray(cellDatabase[:, [10]], dtype = float) #A
C_cell = np.asanyarray(cellDatabase[:, [9]], dtype = float)  #mAh

#bulk discount data
range1Min = np.asanyarray(cellDatabase[:, [16]], dtype = float) #min number of cells for discount
range1Max = np.asanyarray(cellDatabase[:, [17]], dtype = float) #max number of cells for discount
range1Cost = np.asanyarray(cellDatabase[:, [18]], dtype = float) #discount for range 1 (USD)
range2Min = np.asanyarray(cellDatabase[:, [19]], dtype = float) #min number of cells for discount
range2Max = np.asanyarray(cellDatabase[:, [20]], dtype = float) #max number of cells for discount
range2Cost = np.asanyarray(cellDatabase[:, [21]], dtype = float) #discount for range 2 (USD)
range3Min = np.asanyarray(cellDatabase[:, [22]], dtype = float) #min number of cells for discount
range3Max = np.asanyarray(cellDatabase[:, [23]], dtype = float) #max number of cells for discount
range3Cost = np.asanyarray(cellDatabase[:, [24]], dtype = float) #discount for range 3 (USD)
range4Min = np.asanyarray(cellDatabase[:, [25]], dtype = float) #min number of cells for discount
range4Max = np.asanyarray(cellDatabase[:, [26]], dtype = float) #max number of cells for discount
range4Cost = np.asanyarray(cellDatabase[:, [27]], dtype = float) #discount for range 4 (USD)
range5Min = np.asanyarray(cellDatabase[:, [28]], dtype = float) #min number of cells for discount
range5Max = np.asanyarray(cellDatabase[:, [29]], dtype = float) #max number of cells for discount
range5Cost = np.asanyarray(cellDatabase[:, [30]], dtype = float) #discount for range 5 (USD)
range6Min = np.asanyarray(cellDatabase[:, [31]], dtype = float) #min number of cells for discount
range6Max = np.asanyarray(cellDatabase[:, [32]], dtype = float) #max number of cells for discount
range6Cost = np.asanyarray(cellDatabase[:, [33]], dtype = float) #discount for range 6 (USD)

#convert units
C_cell = C_cell/1000 #Ah
cellMass = cellMass/1000 #kg

#ACCUMULATOR VARIABLES
E_accumulator = np.zeros(len(cellBrand)) #kWh
V_accumulator = np.zeros(len(cellBrand)) #V
I_accumulator = np.zeros(len(cellBrand)) #A
I_Continuous_accumulator = np.zeros(len(cellBrand)) #A
P_accumulator = np.zeros(len(cellBrand)) #kW
C_accumulator = np.zeros(len(cellBrand)) #Ah
dischargeTime_accumulator = np.zeros(len(cellBrand)) #hours

accumulator_cost = np.zeros(len(cellBrand)) #USD
accumulator_mass = np.zeros(len(cellBrand)) #kg

percentDifference_E = np.zeros(len(cellBrand)) #kwH
percentDifference_V = np.zeros(len(cellBrand)) #V
percentDifference_I = np.zeros(len(cellBrand)) #A
percentDifference_P = np.zeros(len(cellBrand)) #kW
percentDifference_dischargeTime = np.zeros(len(cellBrand)) #hours
percentDifferenceAverage = np.zeros(len(cellBrand)) #percent difference between actual and target values

s = np.zeros(len(cellBrand)) #number of cells in series to reach target voltage
p = np.zeros(len(cellBrand)) #number of cells in parallel to reach target current

#TARGET ACCUMULATOR VALUES
E_target_accumulator = 8 #kWh
V_target_accumulator = V_max_ESC #V
I_target_max_accumulator = min(I_max_ESC , I_max_motor) #A
I_target_accumulator = min(I_continuous_ESC, I_Continuous_motor) #A
P_target_accumulator = min(P_max_ESC, P_max_motor)
dischargeTime_target_accumulator = 0.08 #hours

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
    print("The accumulator has a voltage of", round(V_accumulator[cellIndex] , 4), "V")
    print("The accumulator has a current of", round(I_accumulator[cellIndex] , 4), "A")
    print("The accumulator has a power of", round(P_accumulator[cellIndex] , 4), "kW")
    print("The accumulator has a capacity of", round(C_accumulator[cellIndex] , 4), "Ah")
    print("The accumulator has a discharge time of", round(dischargeTime_accumulator[cellIndex] , 5), "hours")
    print("The accumulator has an energy of", round(E_accumulator[cellIndex] , 3), "kWh")
    print("The accumulator has a cost of $",round(accumulator_cost[cellIndex] , 6), "USD")
    print("The accumulator has a mass of", round(accumulator_mass[cellIndex] , 4), "kg")
    print("")

#CALCULATE ACCUMULATOR VALUES
#calculate accumulator values for each cell
for i in range(len(cellBrand)):
    #get closest integer number of cells in series to reach target voltage
    s[i] = math.floor(V_target_accumulator / V_cell[i]) #V
    #get closest integer number of cells in parallel to reach target current
    p[i] = math.floor(I_target_max_accumulator / I_cell[i]) #A

    V_accumulator[i] = s[i] * V_cell[i] #V
    I_accumulator[i] = p[i] * I_cell[i] #A
    P_accumulator[i] = V_accumulator[i] * I_accumulator[i] / 1000 #kW
    E_accumulator[i] = p[i] * s[i] * C_cell[i] * V_cell[i] / 1000 #kwH 
    C_accumulator[i] = C_cell[i] * p[i] #Ah
    dischargeTime_accumulator[i] = C_accumulator[i] / I_accumulator[i] #hours

#calculate percent difference between actual and target values
for i in range(len(cellBrand)):
    percentDifference_E[i] = abs(E_accumulator[i] - E_target_accumulator) / E_target_accumulator * 100 
    percentDifference_V[i] = abs(V_accumulator[i] - V_target_accumulator) / V_target_accumulator * 100
    percentDifference_I[i] = abs(I_accumulator[i] - I_target_accumulator) / I_target_accumulator * 100 
    percentDifference_P[i] = abs(P_accumulator[i] - P_target_accumulator) / P_target_accumulator * 100 
    percentDifference_dischargeTime[i] = abs(dischargeTime_accumulator[i] - dischargeTime_target_accumulator) / dischargeTime_target_accumulator * 100 #hours

    #calculate the percent difference
    percentDifferenceAverage[i] = (percentDifference_E[i] + percentDifference_V[i] + percentDifference_I[i] + percentDifference_P[i] + percentDifference_dischargeTime[i]) / 5

#calculate the cost and mass of the accumulator
for i in range(len(cellBrand)):
    #account for sale price if applicable
    if (cellCostSale[i] != -1):
        accumulator_cost[i] = p[i] * s[i] * cellCostSale[i] #USD
    #account for bulk discount if applicable
    elif (p[i] * s[i] >= range6Min[i] and p[i] * s[i] <= range6Max[i]):
        accumulator_cost[i] = p[i] * s[i] * range6Cost[i] #USD
    elif (p[i] * s[i] >= range5Min[i] and p[i] * s[i] <= range5Max[i]):
        accumulator_cost[i] = p[i] * s[i] * range5Cost[i] #USD
    elif (p[i] * s[i] >= range4Min[i] and p[i] * s[i] <= range4Max[i]):
        accumulator_cost[i] = p[i] * s[i] * range4Cost[i] #USD
    elif (p[i] * s[i] >= range3Min[i] and p[i] * s[i] <= range3Max[i]):
        accumulator_cost[i] = p[i] * s[i] * range3Cost[i] #USD
    elif (p[i] * s[i] >= range2Min[i] and p[i] * s[i] <= range2Max[i]):
        accumulator_cost[i] = p[i] * s[i] * range2Cost[i] #USD
    elif (p[i] * s[i] >= range1Min[i] and p[i] * s[i] <= range1Max[i]):
        accumulator_cost[i] = p[i] * s[i] * range1Cost[i] #USD
    #otherwise, no discount
    else: 
        accumulator_cost[i] = p[i] * s[i] * cellCost[i] #USD

    accumulator_mass[i] = p[i] * s[i] * cellMass[i] #kg

#find the cell with the lowest average percent difference, lowest cost, and lowest weight
minDiffCellIndex = np.argmin(percentDifferenceAverage)
minCostCellIndex = np.argmin(accumulator_cost)
minMassCellIndex = np.argmin(accumulator_mass)


#OUTPUT RESULTS
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