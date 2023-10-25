# from dotenv import load_dotenv
# from flask import Flask, render_template, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import json



from pprint import pprint
import requests
import os

#load_dotenv()

def getTheConfigs(vehicleWeight, frontTireDiameter, rearTireDiameter, wheelbase, forwardWeightDistribution, centerOfGravityHeight, brakePedalRatio, brakeBias):
    
    # vehicle data inputs
    vehicleWeight = float(vehicleWeight)
    frontTireDiameter = float(frontTireDiameter)
    rearTireDiameter = float(rearTireDiameter)
    wheelbase = float(wheelbase)
    forwardWeightDistribution = float(forwardWeightDistribution)
    centerOfGravityHeight = float(centerOfGravityHeight)
    # brake data inputs
    brakePedalRatio = float(brakePedalRatio)
    brakeBias = float(brakeBias)
    frontMasterCylinder = float(frontMasterCylinder)
    rearMasterCylinder = float(rearMasterCylinder)
    frontCaliper = float(frontCaliper)
    rearCaliper = float(rearCaliper)
    frontRotorOuter = float(frontRotorOuter)
    rearRotorOuter = float(rearRotorOuter)
    # user prefrence inputs
    factorOfSafety = float(factorOfSafety)
    priority = float(priority)
    

    result = vehicleWeight*frontTireDiameter*rearTireDiameter*wheelbase*forwardWeightDistribution*centerOfGravityHeight*brakePedalRatio*brakeBias
    return result

    #    <input type="text" name="vehicleWeight" placeholder="vehicle weight with driver [lbs]" required="required" /> <br>
    #     <input type="text" name="frontTireDiameter" placeholder="front tire diameter [in]" required="required" /> <br>
    #     <input type="text" name="rearTireDiameter" placeholder="rear tire diameter [in]" required="required" /> <br>
    #     <input type="text" name="wheelbase" placeholder="wheelbase length [in]" required="required" /> <br>
    #     <input type="text" name="forwardWeightDistribution" placeholder="forward weight distribution [%]" required="required" /> <br>
    #     <input type="text" name="centerOfGravityHeight" placeholder="center of gravity height [in]" required="required" /> <br>

    #     <h2>Brake Data Inputs</h2>
    #     <input type="text" name="brakePedalRatio" placeholder="brake pedal ratio"/> <br>
    #     <input type="text" name="brakeBias" placeholder="brake bias"/> <br>
    #     <input type="text" name="frontMasterCylinder" placeholder="front master cylinder size [in]"/> <br>
    #     <input type="text" name="rearMasterCylinder" placeholder="rear master cylinder size [in]"/> <br>
    #     <input type="text" name="frontCaliper" placeholder="front caliper piston area [in^2]"/> <br>
    #     <input type="text" name="rearCaliper" placeholder="rear caliper piston area [in^2]"/> <br>
    #     <input type="text" name="frontRotorOuter" placeholder="front rotor outer radius [in]"/> <br>
    #     <input type="text" name="rearRotorOuter" placeholder="rear rotor outer radius [in]"/> <br>
        
    #     <h2>User Prefrence Inputs</h2>
    #     <input type="text" name="factorOfSafety" placeholder="factor of safety"/> <br>
    #     <input type="text" name="priority" placeholder="priority"/> <br>