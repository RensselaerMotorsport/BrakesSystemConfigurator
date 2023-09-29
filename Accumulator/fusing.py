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
