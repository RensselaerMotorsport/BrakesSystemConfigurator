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
verticalSpacing = 0.015 #m (center to center distance between cells)

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


#TARGET ACCUMULATOR VALUES
#EV.4.1.2 The maximum permitted voltage that may occur between any two points must not exceed 600 V DC
V_target_accumulator = min(V_MAX_ESC, 600) #V
I_target_max_accumulator = min(I_MAX_ESC , I_MAX_MOTOR) #A
P_target_accumulator = min(P_MAX_ESC, P_MAX_MOTOR)
dischargeTime_target_accumulator = 0.08 #hours

#FUNCTION: calculate the best packaging for the accumulator
def accumulatorPackaging(series,parallel,segments,I_accumulator):
    """
    Calculates the best packaging for the accumulator (without mounting tabs)
    INPUTS:
        series: number of cells in series
        parallel: number of cells in parallel
        segments: number of segments
    OUTPUTS:
        length: length of accumulator
        width: width of accumulator
        height: height of accumulator
    """
    
    #calculate cell spacing based on accumulator amperage
    cellSpacing = (I_cellSpacingSlope * I_accumulator + I_cellSpacingIntercept)/1000 #m
    horizontalSpacing = (((cellSpacing+cellDiameter)**2-(verticalSpacing)**2)) ** 0.5

    #calculate length, width, and height of segment
    segmentLength = series * horizontalSpacing #m
    accumulatorLength = segmentLength #m, 
    segmentWidth = parallel * verticalSpacing + (2*0.0023) #m
    segmentHeight = 0.08

    #calculate length, width, and height of accumulator
    accumulatorWidth = segmentHeight * segments +0.03
    accumulatorHeight = segmentWidth #m 
    
    #make sure segment isnt longer than 

    #make sure smallest dimension is height
    #if length is less than height, swap length and height
    if (accumulatorLength < accumulatorHeight):
        accumulatorLength, accumulatorHeight = accumulatorHeight, accumulatorLength
    #if width is less than height, swap width and height
    if (accumulatorWidth < accumulatorHeight):
        accumulatorWidth, accumulatorHeight = accumulatorHeight, accumulatorWidth

    #if length + spacing is more than last year +5mm (0.63m)
    if ((accumulatorLength+0.21 > 0.63) and (accumulatorWidth < accumulatorLength)):
        #swap width and length
        accumulatorLength, accumulatorWidth = accumulatorWidth, accumulatorLength
    
    #then account for component spacing in length
    accumulatorLength += 0.210 #m, accounting for component spacing

    #account for cooling spacing in height 
    accumulatorHeight += 0.161

    print("L",accumulatorLength)
    print("H",accumulatorHeight)
    print("W",accumulatorWidth)
    #last year's values (max)
    #horizontal cell spacing = 29.6mm 
    #W = 17 in = 0.43 m
    #L = 23 in = 0.58 m
    #H = 10.5 in = 0.27 m

    #return zero dimensions if accumulator is too big (1mm bigger than last year's accumulator, calculation error)
    if (accumulatorLength > 0.59 or accumulatorWidth > 0.44 or accumulatorHeight > 0.28):
        accumulatorLength, accumulatorWidth, accumulatorHeight = 0, 0, 0




    #filter for values that will not fit (size of last year's accumulator)
    return accumulatorLength, accumulatorWidth, accumulatorHeight

def accumulatorPackagingV2(series,parallel,segments,I_accumulator):
    """
    Calculates the best packaging for the accumulator (without mounting tabs)
    INPUTS:
        series: number of cells in series
        parallel: number of cells in parallel
        segments: number of segments
    OUTPUTS:
        length: length of accumulator
        width: width of accumulator
        height: height of accumulator
    """
    
    #calculate cell spacing based on accumulator amperage
    cellSpacing = (I_cellSpacingSlope * I_accumulator + I_cellSpacingIntercept)/1000 #m
    horizontalSpacing = (((cellSpacing+cellDiameter)**2-(verticalSpacing)**2)) ** 0.5

    #calculate length, width, and height of segment
    segmentLength = series * horizontalSpacing #m
    
    segmentWidth = parallel * verticalSpacing + (2*0.0023) #m
    segmentHeight = 0.08


    #if segment width is larger than segment length, swap them
    if (segmentWidth > segmentLength):
        segmentWidth, segmentLength = segmentLength, segmentWidth
    
    CGH = 0

    #1 segment deep configurations
    #prefrence 1: E or G (narrow MRH, behind MRH)
    #if <= 4 segments, and width <= 11", and length <= 15" use G
    if segments <= 4 and  segmentWidth <= 0.279 and segmentLength <= 0.381:
         configs = 1
         CGH = segmentLength/2
    #2 deg deep
    elif segments <= 8 and segmentWidth <= 0.2792 and segmentLength <= 0.381/2:
        configs=1.5
        CGH = segmentWidth/2
    #if <= 3 segments, and width <= 12", and length <= 16" use E
    elif segments <= 3 and segmentWidth <= 0.304 and segmentLength <= 0.406:
        configs = 2
        CGH = segmentLength/2
    #2 seg deep
    elif segments <= 6 and segmentLength <= 0.304 and segmentWidth <= 0.406/2:
        configs = 2.5
        CGH = segmentLength/2
    #prefrence 2: A or C (wider MRH, in cockpit)
    #if <= 5 segments, and width <=11, and length <= 16" use C
    elif segments <= 5 and segmentWidth <= 0.279 and segmentLength <= 0.406:
        configs = 3
        CGH=segmentLength/2
    elif segments <= 10 and segmentLength <= 0.2792 and segmentWidth <= 0.406/2:
        configs = 3.5
        CGH=segmentLength/2
    #if <= 3 segments, and width <= 16", and length <= 16" use A
    elif segments <= 3 and segmentWidth <= 0.406 and segmentLength <= 0.406:
        configs = 4
        CGH = min(segmentWidth,segmentLength)/2 
    #2 seg deep
    elif segments <= 6 and segmentWidth <= 0.406/2 and segmentLength <= 0.406:
        configs = 4.5
        CGH = segmentLength/2 
    #prefrence 3: F or H (narrow MRH, in cockpit)
    #if segments = 7, and segment width <4", segment length <12" use F
    elif segments == 7 and segmentLength <= 0.304 and segmentWidth <= 0.1016:
        configs = 5.0
        CGH = segmentWidth / 2
    #if segments = 6, and segment width <7", segment length <12" use F
    elif segments == 6 and segmentLength <= 0.304 and segmentWidth <= 0.1778:
        configs = 5.1
        CGH = segmentWidth / 2
    #if segments = 5 and segment width < 10.5", segment length <12 use F
    elif segments == 5 and segmentLength <= 0.304 and segmentWidth <= 0.3048:
        configs = 5.2
        CGH = segmentWidth / 2
    #if segments = 4, and segment length < 13.5, segment width <12 " use F
    elif segments == 4 and segmentLength <= 0.3429 and segmentWidth <= 0.3048:
        configs = 5.3
        CGH = segmentWidth / 2
    #if segments = 3, and segment length < 16, segment width <12 " use F
    elif segments == 3 and segmentLength <= 0.4064 and segmentWidth <= 0.3048:
        configs = 5.4
        CGH = segmentWidth / 2
    elif segments <= 4 and ((27-segmentWidth < segmentLength)or(27-segmentLength<segmentWidth)):
        configs = 6
        CGH = max(segmentWidth,segmentLength) / 2

    
    #prefrence 4: B or D (wide MRH, in cockpit)
    #if segments = 7, and segment width <4", segment length <16" use B
    elif segments == 7 and segmentLength <= 0.406 and segmentWidth <= 0.1016:
        configs = 5.5
        CGH = segmentWidth / 2

    #if segments = 6, and segment width <7", segment length <16" use B
    elif segments == 6 and segmentLength <= 0.406 and segmentWidth <= 0.1778:
        configs = 5.6
        CGH = segmentWidth / 2

    #if segments = 5 and segment width < 10.5", segment length <16 use B
    elif segments == 5 and segmentLength <= 0.406 and segmentWidth <= 0.2667:
        configs = 5.7
        CGH = segmentWidth / 2


    #if segments = 4, and segment width < 13.5, segment length <16 " use B
    elif segments == 4 and segmentLength <=0.406 and segmentWidth <= 0.3429:
        configs = 5.8
        CGH = segmentWidth / 2


    #if segments = 3, and segment length < 16, segment width <16 " use B
    elif segments == 3 and segmentLength <= 0.406 and segmentWidth <= 0.4064:
        configs = 5.9
        CGH = max(segmentWidth,segmentLength) / 2


    #if segments <=5, use D
    elif segments <= 5 and ((27-segments < segmentWidth)or(27*segments<segmentHeight)):   
        configs = 8
        CGH = max(segmentWidth,segmentLength) / 2

    else:
        configs = 0
        CGH = 0



    
    return configs, CGH

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
    combinations = np.zeros((len(cellBrand)*15*15*15,25))


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
        p_max = Math.floor(300 / I_cell[i]) #A
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
            #standard fuse sizes are 35,40,45,50,60,70,80,90,100,150,180,200,225,250,275
            #https://www.digikey.com/en/products/filter/electrical-specialty-fuses/155?s=N4IgjCBcoGw1oDGUBmBDANgZwKYBoQB7KAbRACYAOAdgAYBWSkA8gTlceuZBkvttrcwA2mCYEwYACxSAzIIlTa5chEWUp1eBPq8ZQmFVrbwlVcpABdAgAcALlBABlOwCcAlgDsA5iAC%2BLNJSCCDIkOjY%2BESkIFrktJrccQxcBMn09EmGDMFp2fTkWfH0arH5CmXxUqxFCUzWIPaOLh4%2B-gQAtIXQoVBuAK5RxJBkmZZ%2BE0A
            #set fuse size to closest standard fuse size that is less than I_accumulator
            
            #if I_accumulator is less than 35, return error
            if (I_mainFuse_max < 35):
                print("ERROR: max fuse current is less than 35A")
                I_mainFuse = 0
            elif (I_mainFuse_max < 40):
                I_mainFuse = 35
            elif (I_mainFuse_max < 45):
                I_mainFuse = 40
            elif (I_mainFuse_max < 50):
                I_mainFuse = 45
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
            for n in range(8, 12):
    
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
                        if (debug==True):
                            print("rejected because segment weight is more than 12kg")
                    #check if segment voltage is more than 120V
                    elif (V_segment> 120):
                        if (debug==True):
                            print("rejected because segment voltage is more than 120V")    
                    #check if segment energy is more than 6 MJ
                    elif (E_segment > 6000000):
                        if (debug==True):
                            print("rejected because segment energy is more than 6MJ")
                    #elif (V_segment > 60):
                        #if (debug==True):
                            #print("rejected because not touch safe (voltage >60V)")
                    #check if energy is less than 5 kWh
                    elif (E_accumulator < 5.5):
                        if (debug==True):
                            print("rejected because accumulator energy is more than 5.5kWh")
                    #check that power is less than 80kW
                    elif (V_accumulator*I_mainFuse_max/1000 > 80):
                        if (debug==True):
                            print("rejected because accumulator power is more than 80kW")

                    else:
                        #record combination
                        print("meep")
    
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
                        combinations [o,9] = dischargeTime_accumulator*60 #min
    
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
                        #combinations[o,20], combinations[o,21], combinations[o,22] = accumulatorPackaging(s_segment,p,n,I_accumulator)
                        combinations[o,23],combinations[o,24] = accumulatorPackagingV2(s_segment,p,n,I_accumulator)
 
                        if(s_seg_range[j] == 16 and i==1 and p==6):
                            print("meep")
                            print(n)    
                            print(combinations[o,23],combinations[o,24])
                        #increment counter
                        o += 1

    #delete duplicate entries and zeros
    combinations = np.unique(combinations, axis=0)    
    
    #delete combinations where main fuse is 0
    combinations = combinations[combinations[:,17] != 0]

    #delete combinations where accumulator packaging is 0
    combinations = combinations[combinations[:,23] != 0]

    #delete combinations where accumulator length is 0
    #combinations = combinations[combinations[:,20] != 0]
    

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
            print("The accumulator has a discharge time of", combinations[i,9], "min")
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
            #print("Length:", combinations[i,20], "m")
            #print("Width:", combinations[i,21], "m")
            #print("Height:", combinations[i,22], "m")
            print("Configuration:", combinations[i,23])
            print("CH height:", combinations[i,24])
            print("")
    #print number of possible combinations
    print("There are", o, "possible accumulator configurations")

#FUNCTION: print all possible accumulator configurations for input into spreadsheet
def printAccumulatorConfigurationsSpreadsheet(combinations,o):       
    #print row headers
    #print("Combination #" , "," , "Cell Brand" , "," , "Cell Model" , "," , "Series" , "," , "Parallell" , "," , "Voltage" , "," , "Current" , "," , "Power" , "," , "Capacity" , "," , "Discharge Time" , "," , "Energy" , "," , "Cost" , "," , "Mass" , "," , "Segments" , "," , "Series per Segment" , "," , "Parallel Per Segment" , "," , "Segment Voltage" , "," , "Segment Current" , "," , "Segment Energy" , "," , "Cell Fuse Current" , "," , "Main Fuse Current", ","  , "Length" , "," , "Width" , "," , "Height")
    print("Combination #" , "," , "Cell Brand" , "," , "Cell Model" , "," , "Series" , "," , "Parallell" , "," , "Voltage" , "," , "Current" , "," , "Power" , "," , "Capacity" , "," , "Discharge Time" , "," , "Energy" , "," , "Cost" , "," , "Mass" , "," , "Segments" , "," , "Series per Segment" , "," , "Parallel Per Segment" , "," , "Segment Voltage" , "," , "Segment Current" , "," , "Segment Energy" , "," , "Cell Fuse Current" , "," , "Main Fuse Current", ","  , "Configuration", "CG Height")


    #loop through combinations
    for i in range(len(combinations)):
        #print accumulator values
        #print(combinations[i ,0] , "," , cellBrand[int(combinations[i,1])] , "," , cellModel[int(combinations[i,1])] , "," , combinations[i,2] , "," , combinations[i,3] , "," , combinations[i,4] , "," , combinations[i,5] , "," , combinations[i,8] , "," , combinations[i,7] , "," , combinations[i,9] , "," , combinations[i,6] , "," , combinations[i,18] , "," , combinations[i,19] , "," , combinations[i,10] , "," , combinations[i,11] , "," , combinations[i,12] , "," , combinations[i,13] , "," , combinations[i,14] , "," , combinations[i,15] , "," , combinations[i,16] , "," , combinations[i,17], "," , combinations[i,20],",",combinations[i,21],",",combinations[i,22])
        print(combinations[i ,0] , "," , cellBrand[int(combinations[i,1])] , "," , cellModel[int(combinations[i,1])] , "," , combinations[i,2] , "," , combinations[i,3] , "," , combinations[i,4] , "," , combinations[i,5] , "," , combinations[i,8] , "," , combinations[i,7] , "," , combinations[i,9] , "," , combinations[i,6] , "," , combinations[i,18] , "," , combinations[i,19] , "," , combinations[i,10] , "," , combinations[i,11] , "," , combinations[i,12] , "," , combinations[i,13] , "," , combinations[i,14] , "," , combinations[i,15] , "," , combinations[i,16] , "," , combinations[i,17], "," , combinations[i,23], "," , combinations[i,24])


 

    print("")

    #print number of possible combinations
    print("There are", o, "possible accumulator configurations")


#FUNCTION calculate decision matrix for accumulator
def decisionMatrix(combinations):
    """ calculates a decision matrix for the accumulator, based on weighted values
    INPUTS:
        combinations: array of possible accumulator configurations
    OUTPUTS:
        compositeScore
    """
    #initialize decision matrix
    matrix = np.zeros((len(combinations),20))

    #normalize amperage between 0 and 1
    amperage = combinations[:,5]
    amperage = amperage/amperage.max()

    #normalize discharge time between 0 and 1
    dischargeTime = combinations[:,9]
    dischargeTime = dischargeTime/dischargeTime.max()

    #normalize capacity between 0 and 1
    capacity = combinations[:,7]
    capacity = capacity/capacity.max()

    #normalize cell level fusing between 0 and 1
    cellFuse = combinations[:,16]
    cellFuse = cellFuse/cellFuse.max()

    #normalize mass between 0 and 1
    mass = combinations[:,19]
    mass = mass/mass.max()

    #normalize cost between 0 and 1
    cost = combinations[:,18]
    cost = cost/cost.max()

    #normalize CG height between 0 and 1
    CGH = combinations[:,24]
    CGH = CGH/CGH.max()

    #print matrix headers
    print("Combination #, Amperage, Discharge Time, Capacity, Cell Fuse, Mass, Cost, Touch Safe, Even Segments, Configuration")

    
    for i in range(len(combinations)):
        #set values for each criteria between 0 and 1

        matrix[i,0] = amperage[i]
        matrix[i,1] = dischargeTime[i]
        matrix[i,2] = capacity[i]
        matrix[i,3] = cellFuse[i]
        matrix[i,4] = mass[i]
        matrix[i,5] = cost[i]
        #if less than 60V per segment, set to 1
        if (combinations[i,13] < 60):
            matrix[i,6] = 1
        #if more than 60V per segment, set to 0
        else:
            matrix[i,6] = 0
        #if even number of segments, set to 1
        if (combinations[i,10] % 2 == 0):
            matrix[i,7] = 1
        #if odd number of segments, set to 0
        else:
            matrix[i,7] = 0
        #if config is e or g, set to 1 (between 1 and 2.9)
        if (combinations[i,23] >= 1 and combinations[i,23] <= 2.9):
            matrix[i,8] = 1
        #if config is a or c, set to 0.8 (between 3 and 4.9)
        elif (combinations[i,23] >= 3 and combinations[i,23] <= 4.9):
            matrix[i,8] = 0.8
        #if config is f or h, set to 0.5 (between 5 and 6.9)
        elif (combinations[i,23] >= 5 and combinations[i,23] <= 6.9):
            matrix[i,8] = 0.5
        #if config is b or d, set to 0.3 (between 7 and 8.9)
        elif (combinations[i,23] >= 7 and combinations[i,23] <= 8.9):
            matrix[i,8] = 0.3
        matrix[i,9] = CGH[i]

       


        #print matrix in CSV form
        print(i,",",matrix[i,0],",",matrix[i,1],",",matrix[i,2],",",matrix[i,3],",",matrix[i,4],",",matrix[i,5],",",matrix[i,6],",",matrix[i,7],",",matrix[i,8],",",matrix[i,9])
        





    




configs, index = calculateAccumulatorConfigurations()

#outputs accumulator values in CSV form
#printAccumulatorConfigurationsSpreadsheet(configs,index)

#outouts accumulator values in easily readable form
printAccumulatorConfigurations(configs,index)

#outputs decison matrix in csv form
#decisionMatrix(configs)



