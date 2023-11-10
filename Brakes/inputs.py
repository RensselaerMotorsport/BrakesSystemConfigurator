# from dotenv import load_dotenv
# from flask import Flask, render_template, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import json

from brakeCalcs import BrakeSystem


from pprint import pprint
import requests
import os

#load_dotenv()

def getTheConfigs(vehicleWeight, frontTireDiameter, rearTireDiameter, wheelbase, forwardWeightDistribution, centerOfGravityHeight, brakePedalRatio, brakeBias, frontMasterCylinder, rearMasterCylinder, frontCaliper, frontPad, rearCaliper, rearPad, frontRotorOuter, rearRotorOuter, factorOfSafety, priority):
    
    # vehicle data inputs
    vehicleWeight = float(vehicleWeight)  
    frontTireDiameter = float(frontTireDiameter)
    rearTireDiameter = float(rearTireDiameter)
    wheelbase = float(wheelbase)
    forwardWeightDistribution = float(forwardWeightDistribution)
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
    result = BrakeSystem(700, 8, 8, 10, 10, 60.5, 0.49, 13, 5.25, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1.3, 2)

    # #convert result array to string
    result = str(result)
    
    result = "test"

    return result