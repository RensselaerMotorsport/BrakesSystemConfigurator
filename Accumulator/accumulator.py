import numpy as np
import matplotlib.pyplot as plt
import math as Math
import csv

#TO-DO:
#figure out touch safe segment voltage math
#set constants as all caps
#calculate optimal packaging
#figure out what variables are not being used
#fix units for accumulator & segment energy
#fix motor variable info
#filter for rules required voltage
#add segment contributions to weight (and cost?)

debug = True

#MOTOR VARIABLES: Emrax 228 HV 
MOTOR_COOLING = "combined"
I_MAX_MOTOR = 240 #A for a max of 2 minutes if cooled properlly
#I_Continuous_motor = 125 #A
if MOTOR_COOLING == "air":
    P_continuous_motor = 55 #kW
    T_continuous_motor = 96 #Nm
elif MOTOR_COOLING == "liquid":
    P_continuous_motor = 64 #kW
    T_continuous_motor = 112 #Nm
elif MOTOR_COOLING == "combined":
    P_continuous_motor = 62 #kW
    T_continuous_motor = 130 #Nm
P_MAX_MOTOR = 124 #kW @ 5500 RPM

#SIZING VARIABLES 

cellSpacingMin = 0.005 #m 
cellSpacingMax = 0.0075 #m
I_cellSpacingSlope = 0.017 #A/m
I_cellSpacingIntercept = 3.3 #A

horizontalSpacing = 0.0 #m (center to center distance between cells), was 15mm last year
verticalSpacing = 0.03 #m (center to center distance between cells)

#cell dimensions (assuming 18650)
cellDiameter = 0.018 #m
cellHeight = 0.065 #m


#ESC VARIABLES: Rinehart PM100DX 
V_MAX_ESC = 400 #V
I_MAX_ESC = 300 #A
I_CON_ESC = 350 #A
P_MAX_ESC = 100 #kW

#CELL VARIABLES
#import values from database
cellDatabase = np.loadtxt(open("18650 cell database.csv", "rb"), delimiter=",", skiprows=1, dtype=str)

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
combinations = np.zeros((len(cellBrand)*15*15*15,20))

#TARGET ACCUMULATOR VALUES
#EV.4.1.2 The maximum permitted voltage that may occur between any two points must not exceed 600 V DC
V_target_accumulator = min(V_MAX_ESC, 600) #V
I_target_max_accumulator = min(I_MAX_ESC , I_MAX_MOTOR) #A
P_target_accumulator = min(P_MAX_ESC, P_MAX_MOTOR)
dischargeTime_target_accumulator = 0.08 #hours

#FUNCTION: calculate the best packaging for the accumulator
def accumulatorPackaging(series,parallel,segments,I_accumulator):
    """
    Calculates the best packaging for the accumulator
    INPUTS:
        series: number of cells in series
        parallel: number of cells in parallel
        segments: number of segments
    OUTPUTS:
        length: length of accumulator
        width: width of accumulator
        height: height of accumulator
    """
    #this is not correct yet, ignore for now

    #calculate cell spacing based on accumulator amperage
    cellSpacing = I_cellSpacingSlope * I_accumulator + I_cellSpacingIntercept #m
    verticalSpacing = (((horizontalSpacing)**2) + (cellSpacing)**2) ** 0.5


    #calculate length, width, and height of segment
    segmentLength = series * horizontalSpacing + (2*0.015) #m
    segmentWidth = parallel * verticalSpacing + (2*0.0023) #m

    #calculate length, width, and height of accumulator
    accumulatorHeight = cellHeight * segments + (segments+1)*0.012#m 
    accumulatorLength = segmentLength + 0.160 #m, accounting for component spacing

#FUNCTION: calculate the cost and mass of the accumulator
def accumulatorCost(brand,series,parallel):
    """
    Calculates the cost and mass of the accumulator
    INPUTS:
        none
    OUTPUTS:
        none
    """
    #calculate accumulator price
    #account for sale price if applicable
    numCells = series * parallel
    if (cellCostSale[brand] != -1 and cellCostSale[brand] != 0):
        cost = numCells * cellCostSale[brand]
    #account for bulk discount if applicable
    elif (numCells >= range6Min[brand] and numCells <= range6Max[brand] and range6Cost[brand] != 0 and range6Cost[brand] != -1):
        cost = numCells * range6Cost[brand]
    elif (numCells >= range5Min[brand] and numCells <= range5Max[brand] and range5Cost[brand] != 0 and range5Cost[brand] != -1):
        cost = numCells * range5Cost[brand]
    elif (numCells >= range4Min[brand] and numCells <= range4Max[brand] and range4Cost[brand] != 0 and range4Cost[brand] != -1):
        cost = numCells * range4Cost[brand]
    elif (numCells >= range3Min[brand] and numCells <= range3Max[brand] and range3Cost[brand] != 0 and range3Cost[brand] != -1):
        cost = numCells * range3Cost[brand]
    elif (numCells >= range2Min[brand] and numCells <= range2Max[brand] and range2Cost[brand] != 0 and range2Cost[brand] != -1):
        cost = numCells * range2Cost[brand]
    elif (numCells >= range1Min[brand] and numCells <= range1Max[brand] and range1Cost[brand] != 0 and range1Cost[brand] != -1):
        cost = numCells * range1Cost[brand]
    #otherwise, no discount
    else:
        cost = numCells * cellCost[brand]
    
    return cost


#FUNCTION: calculate all possible accumulator configurations
def calculateAccumulatorConfigurations():
    """
    Calculates all possible accumulator configurations
    INPUTS:
        none
    OUTPUTS:
        combinations 
    """

    #initalize counter for number of possible combinations
    o = 0
    combinations = np.zeros((len(cellBrand)*15*15*15,20))


    #loop through possible cells
    for i in range(len(cellBrand)):

        #initalize accumulator values
        s = 0 #number of cells in series
        p = 0 #number of cells in parallel
        V_accumulator = 0 #V
        I_accumulator = 0 #A
        E_accumulator = 0 #J
        C_accumulator = 0 #Ah
        P_accumulator = 0 #kW
        dischargeTime_accumulator = 0 #hours

        #initalize segment values
        n = 0 #number of segments
        s_segment = 0 #number of cells in series per segment
        p_segment = 0 #number of cells in parallel per segment
        V_segment = 0 #V
        I_segment = 0 #A
        E_segment = 0 #J

        #initalize fuse values
        I_mainFuse = 0 #A
        I_fuse_cell = 0 #A

        #get closest integer number of cells in parallel to reach target current
        p_max = Math.floor(I_MAX_MOTOR / I_cell[i]) #A
        p_min = Math.floor((100) / I_cell[i]) #A
        
        #create array of integers between p_max and p_min
        p_accumulator_range = np.arange(p_min, p_max+1, 1)
        
        #loop through possible number of cells in parallel
        for k in range(len(p_accumulator_range)):

            #get closest integer number of cells in parallel to reach target current
            p = p_accumulator_range[k] #A

            #calculate accumulator current
            I_accumulator = p * I_cell[i] #A

            #if 2*cell discharge current is more than 55A (max we can test) set cell fuse to 55A
            if (2*I_cell[i] > 55):
                I_fuse_cell = 55
            #otherwise, set cell fuse to 2*cell discharge current (minus 1 for wiggle room)
            else:
                I_fuse_cell = 2*I_cell[i] - 1

            #calculate main fuse max using third sum rule
            I_mainFuse_max = (p * I_fuse_cell)/3

            #calculate accumulator main fuse
            #standard fuse sizes are 50,60,70,80,90,100,150,180,200,225,250,275
            #https://www.digikey.com/en/products/filter/electrical-specialty-fuses/155?s=N4IgjCBcoGw1oDGUBmBDANgZwKYBoQB7KAbRACYAOAdgAYBWSkA8gTlceuZBkvttrcwA2mCYEwYACxSAzIIlTa5chEWUp1eBPq8ZQmFVrbwlVcpABdAgAcALlBABlOwCcAlgDsA5iAC%2BLNJSCCDIkOjY%2BESkIFrktJrccQxcBMn09EmGDMFp2fTkWfH0arH5CmXxUqxFCUzWIPaOLh4%2B-gQAtIXQoVBuAK5RxJBkmZZ%2BE0A
            #set fuse size to closest standard fuse size that is less than I_accumulator
            
            #if I_accumulator is less than 50, return error
            if (I_mainFuse_max < 50):
                print("ERROR: max fuse current is less than 50A")
                I_mainFuse = 0
            elif (I_mainFuse_max < 60):
                I_mainFuse = 50
            elif (I_mainFuse_max < 70):
                I_mainFuse = 60
            elif (I_mainFuse_max < 80):
                I_mainFuse = 70
            elif(I_mainFuse_max < 90):
                I_mainFuse = 80
            elif (I_mainFuse_max < 100):
                I_mainFuse = 90
            elif (I_mainFuse_max < 150):
                I_mainFuse = 100
            elif (I_mainFuse_max < 180):
                I_mainFuse = 150
            elif (I_mainFuse_max < 200):
                I_mainFuse = 180
            elif (I_mainFuse_max < 225):
                I_mainFuse = 200
            elif (I_mainFuse_max < 250):
                I_mainFuse = 225
            elif (I_mainFuse_max < 275):
                I_mainFuse = 250
            else:
                I_mainFuse = 275

            #loop through possible number of segments
            for n in range(1, 8):
    
                #calculate max and min accumulator voltage (+= 1.25% of target voltage)
                V_accumulator_max = V_target_accumulator * 1.0125 #V
                V_accumulator_min = V_target_accumulator * 0.9875 #V   
                    
                #calculate max & min number of series cells per segments
                s_seg_max = Math.floor(V_accumulator_max / (V_cell[i]*n))
                s_seg_min = Math.ceil(V_accumulator_min / (V_cell[i]*n))
                
    
                #create array of integers between s_seg_max and s_seg_min
                s_seg_range = np.arange(s_seg_min, s_seg_max+1, 1)
    
                #loop through possible number of cells in series per segment
                for j in range(len(s_seg_range)):
    
                    #calculate segment values
                    s_segment = s_seg_range[j] #number of cells in series per segment
                    p_segment = p #number of cells in parallel per segment
                    V_segment = s_segment * V_cell[i] #V
                    I_segment = p_segment * I_cell[i] #A
                    E_segment = p_segment * s_segment * C_cell[i] * V_cell[i] #J
        
                    #calculate accumulator values
                    s = s_segment * n #number of cells in series
                    V_accumulator = s * V_cell[i] #V
                    P_accumulator = V_accumulator * I_accumulator / 1000 #kW
                    E_accumulator = p * s * C_cell[i] * V_cell[i] / 1000 #kwH 
                    C_accumulator = C_cell[i] * p #Ah
                    dischargeTime_accumulator = C_accumulator / I_accumulator #hours

                    #calculate segment weight
                    segmentWeight = p_segment * s_segment * cellMass[i] #kg
    
    
                    #check if combination is rules legal
                    #make sure segment weight is less than 12kg (F.10.3.2.b.)
                    if (segmentWeight > 12):
                        if (debug==True and i==1):
                            print("rejected because segment weight is more than 12kg")
                    #check if segment voltage is more than 120V
                    elif (V_segment> 120):
                        if (debug==True and i==1):
                            print("rejected because segment voltage is more than 120V")        
                    #check if segment energy is more than 6 MJ
                    elif (E_segment > 6000000):
                        if (debug==True and i==1):
                            print("rejected because segment energy is more than 6MJ")
                    #elif (V_segment > 60):
                        #if (debug==True):
                            #print("rejected because not touch safe (voltage >60V)")
                    #check if energy is less than 5 kWh
                    elif (E_accumulator < 5.5):
                        if (debug==True and i==1):
                            print("rejected because accumulator energy is more than 5kWh")
                    #check that power is less than 80kW
                    elif (P_accumulator > 80):
                        if (debug==True and i==1):
                            print("rejected because accumulator power is more than 80kW")
                    else:
                        #record combination
    
                        combinations[o,0] =  o #combination number
                        combinations [o,1] = i #cell index
    
                        #record accumulator values
                        combinations [o,2] = s #number of cells in series
                        combinations [o,3] = p #number of cells in parallel
                        combinations [o,4] = V_accumulator #V
                        combinations [o,5] = I_accumulator #A
                        combinations [o,6] = E_accumulator #J
                        combinations [o,7] = C_accumulator #Ah                            
                        combinations [o,8] = P_accumulator #kW
                        combinations [o,9] = dischargeTime_accumulator #hours
    
                        #record segment values
                        combinations [o,10] = n #number of segments
                        combinations [o,11] = s_segment #number of cells in series per segment
                        combinations [o,12] = p_segment #number of cells in parallel per segment
                        combinations [o,13] = V_segment #V
                        combinations [o,14] = I_segment #A
                        combinations [o,15] = E_segment #J
        
                        #record fuse values
                        combinations [o,16] = I_fuse_cell #A
                        combinations [o,17] = I_mainFuse #A
    
                        #record cost and mass
                        combinations [o,18] = accumulatorCost(i,s,p) #USD
                        combinations [o,19] = p * s * cellMass[i] #kg

                        #record dimensions
                        #combinations[i,20] = #segment length
                        #combinations[i,21] = #segment width
                        #combinations[i,22] = #accumulator length
                        #combinations[i,23] = #accumulator width
                        #combinations[i,24] = #accumulator height
                            
                        #increment counter
                        o += 1


    #delete duplicate entries and zeros
    combinations = np.unique(combinations, axis=0)    

    #return array of possible combinations
    return combinations, o

#FUNCTION: print all possible accumulator configurations
def printAccumulatorConfigurations(combinations,o):
    """
    Prints all possible accumulator configurations
    INPUTS:
        combinations: array of possible accumulator configurations
    OUTPUTS:
        none
    """

    #delete combinations where main fuse is 0
    combinations = combinations[combinations[:,17] != 0]

    #sort combinations by cost
    #combinations = combinations[combinations[:,18].argsort()]
    #reverse combinations so that lowest cost is first
    #combinations = combinations[::-1]

    #sort combinations by mass
    combinations = combinations[combinations[:,19].argsort()]
    #reverse combinations so that lowest mass is first
    combinations = combinations[::-1]

    
    #loop through combinations
    for i in range(len(combinations)):
        #print accumulator values
            print("Combination #", combinations[i,0])
            print("Cell Brand:", cellBrand[int(combinations[i,1])], "Cell Model",cellModel[int(combinations[i,1])])
            print("Number of cells in series:", combinations[i,2], "cells")
            print("Number of cells in parallel:", combinations[i,3], "cells")
            print("The accumulator has a voltage of", combinations[i,4], "V")
            print("The accumulator has a current of", combinations[i,5], "A")
            print("The accumulator has a power of", combinations[i,8], "kW")
            print("The accumulator has a capacity of", combinations[i,7], "Ah")
            print("The accumulator has a discharge time of", combinations[i,9], "hours")
            print("The accumulator has an energy of", combinations[i,6], "kWh")
            print("The accumulator has a cost of $",combinations[i,18], "USD")
            print("The accumulator has a mass of", round(combinations[i,19] , 4), "kg")
            print("Segment Values:")
            print("Number of segments:", combinations[i,10])
            print("Number of cells in series per segment:", combinations[i,11])
            print("Number of cells in parallel per segment:", combinations[i,12])
            print("Segment voltage:", combinations[i,13], "V")
            print("Segment current:", combinations[i,14], "A")
            print("Segment energy:", combinations[i,15], "J")
            print("Fuse Values:")
            print("Fuse current:", combinations[i,16], "A")
            print("Main fuse current:", combinations[i,17], "A")
            print("Sizing: (tbd)")
            print("")
    #print number of possible combinations
    print("There are", o, "possible accumulator configurations")

#FUNCTION: print all possible accumulator configurations for input into spreadsheet
def printAccumulatorConfigurationsSpreadsheet(combinations,o):       
    #delete combinations where main fuse is 0
    combinations = combinations[combinations[:,17] != 0]

    #delete duplicate entries and zeros
    combinations = np.unique(combinations, axis=0)

    #loop through combinations
    for i in range(len(combinations)):
        #print accumulator values
        print(combinations[i,0] , "," , cellBrand[int(combinations[i,1])] , "," , cellModel[int(combinations[i,1])] , "," , combinations[i,2] , "," , combinations[i,3] , "," , combinations[i,4] , "," , combinations[i,5] , "," , combinations[i,8] , "," , combinations[i,7] , "," , combinations[i,9] , "," , combinations[i,6] , "," , combinations[i,18] , "," , combinations[i,19] , "," , combinations[i,10] , "," , combinations[i,11] , "," , combinations[i,12] , "," , combinations[i,13] , "," , combinations[i,14] , "," , combinations[i,15] , "," , combinations[i,16] , "," , combinations[i,17])

    
    #print row headers
    print("Combination #" , "," , "Cell Brand" , "," , "Cell Model" , "," , "Number of cells in series" , "," , "Number of cells in parallel" , "," , "The accumulator has a voltage" , "," , "The accumulator has a current" , "," , "The accumulator has a power" , "," , "The accumulator has a capacity" , "," , "The accumulator has a discharge time" , "," , "The accumulator has an energy" , "," , "The accumulator has a cost" , "," , "The accumulator has a mass" , "," , "Number of segments" , "," , "Number of cells in series per segment" , "," , "Number of cells in parallel per segment" , "," , "Segment voltage" , "," , "Segment current" , "," , "Segment energy" , "," , "Fuse current" , "," , "Main fuse current")
    print("")

    #print number of possible combinations
    print("There are", o, "possible accumulator configurations")






configs, index = calculateAccumulatorConfigurations()
printAccumulatorConfigurationsSpreadsheet(configs,index)


