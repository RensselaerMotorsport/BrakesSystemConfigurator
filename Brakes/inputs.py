# from dotenv import load_dotenv
# from flask import Flask, render_template, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import json

from brakeCalcs import BrakeSystem

import numpy as np

from pprint import pprint
import requests
import os

#load_dotenv()

"""Brake Constants"""
#imports caliper data from csv files into numpy arrays

#Brake Caliper Constants
caliperData = np.loadtxt(open("database - calipers.csv", "rb"), delimiter=",", skiprows=1, dtype=str)
caliperBrands = caliperData[:, [0]]
caliperModel = caliperData[:, [1]]
caliperPartNumber = caliperData[:, [2]]
caliperPistonArea = np.asarray(caliperData[:, [3]], dtype = float)
caliperNumberOfPistons = np.asarray(caliperData[:, [4]], dtype = float)
caliperWeight = np.asarray(caliperData[:, [5]], dtype = float)
caliperPrice = np.asarray(caliperData[:, [6]], dtype = float)
caliperMinRotorDiameter = np.asanyarray(caliperData[:, [7]], dtype = float)
caliperMaxRotorDiameter = np.asanyarray(caliperData[:, [8]], dtype = float)
caliperMinRotorThickness = np.asanyarray(caliperData[:, [9]], dtype = float)
caliperMaxRotorThickness = np.asanyarray(caliperData[:, [10]], dtype = float)
caliperPadType = caliperData[:, [11]]

#Brake Pad Constants
padData = np.loadtxt(open("database - pads.csv", "rb"), delimiter=",", skiprows=1, dtype=str)
padBrand = padData[:, [0]]
padModel = padData[:, [1]]
padPartNumber = padData[:, [3]]
padType = padData[:, [2]]
padArea = np.asarray(padData[:, [4]], dtype = float)
padCoefficientOfFrictionMin = np.asarray(padData[:, [5]], dtype = float)
padCoefficientOfFrictionMax = np.asarray(padData[:, [6]], dtype = float)
padIdealTemperature = padData[:, [7]]
padPricePer = np.asarray(padData[:, [8]], dtype = float)
padCompatableMaterial = padData[:, [9]]

def getTheConfigs(vehicleWeight, frontTireDiameter, rearTireDiameter, wheelbase, forwardWeightDistribution, centerOfGravityHeight, brakePedalRatio, brakeBias, frontMasterCylinder, rearMasterCylinder, frontCaliper, frontPad, rearCaliper, rearPad, frontRotorOuter, rearRotorOuter, factorOfSafety, priority):
    
    # vehicle data inputs
    if not bool(vehicleWeight.strip()):
        vehicleWeight = 600 #lbs
    vehicleWeight = float(vehicleWeight)  
    if not bool(frontTireDiameter.strip()):
        frontTireDiameter = 8 #inches
    frontTireDiameter = float(frontTireDiameter)
    if not bool(rearTireDiameter.strip()):
        rearTireDiameter = 8 #inches
    rearTireDiameter = float(rearTireDiameter)
    if not bool(wheelbase.strip()):
        wheelbase = 60.5
    wheelbase = float(wheelbase)
    if not bool(forwardWeightDistribution.strip()):
        forwardWeightDistribution = 0.49
    forwardWeightDistribution = float(forwardWeightDistribution)
    if not bool(centerOfGravityHeight.strip()):
        centerOfGravityHeight = 13
    centerOfGravityHeight = float(centerOfGravityHeight)
    
    # brake data inputs
    if not bool(brakePedalRatio.strip()):
        brakePedalRatio = -1
    brakePedalRatio = float(brakePedalRatio)
    if not bool(frontMasterCylinder.strip()):
        frontMasterCylinder = -1
    frontMasterCylinder = float(frontMasterCylinder)
    if not bool(rearMasterCylinder.strip()):
        rearMasterCylinder = -1
    rearMasterCylinder = float(rearMasterCylinder)
    if not bool(frontCaliper.strip()):
        frontCaliper = -1
    frontCaliper = float(frontCaliper)
    if not bool(frontPad.strip()):
        frontPad = -1
    frontPad = float(frontPad)
    if not bool(rearCaliper.strip()):
        rearCaliper = -1
    rearCaliper = float(rearCaliper)
    if not bool(rearPad.strip()):
        rearPad = -1
    rearPad = float(rearPad)
    if not bool(frontRotorOuter.strip()):
        frontRotorOuter = -1
    frontRotorOuter = float(frontRotorOuter)
    if not bool(rearRotorOuter.strip()):
        rearRotorOuter = -1
    rearRotorOuter = float(rearRotorOuter)
    
    # user prefrence inputs
    if not bool(factorOfSafety.strip()):
        factorOfSafety = 2
    factorOfSafety = float(factorOfSafety)
    if not bool(priority.strip()):
        priority = 1
    priority = float(priority)

    frontWheelShellDiameter = 0
    rearWheelShellDiameter = 0
    brakeBias = 0
    

    #result = BrakeSystem(vehicleWeight, frontTireDiameter, rearTireDiameter, frontWheelShellDiameter, rearWheelShellDiameter, wheelbase, forwardWeightDistribution, centerOfGravityHeight, brakePedalRatio, brakeBias, frontMasterCylinder, rearMasterCylinder, frontCaliper, rearCaliper, frontPad, rearPad, frontRotorOuter, rearRotorOuter, factorOfSafety, priority)
    #result = BrakeSystem(700, 8, 8, 10, 10, 60.5, 0.49, 13, 5.25, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1.3, 2)
    result = BrakeSystem(600, 8, 8, 10, 10, 60.5, 0.49, 13, 5.25, -1, -1, -1 , 2, -1, -1, -1, 8/2, 7.5/2, 1.0, 1)


    # #convert result array to string
    
    print(result)

    frontCaliper = caliperBrands[int(result[0,5])]
    rearCaliper = caliperBrands[int(result[0,6])]
    result3 = "c"


    return frontCaliper, rearCaliper, result3

    # return result