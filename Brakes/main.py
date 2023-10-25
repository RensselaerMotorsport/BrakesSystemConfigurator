from flask import Flask, render_template, request, url_for
from inputs import getTheConfigs
from waitress import serve
from dotenv import load_dotenv

from inputs import getTheConfigs

app = Flask(__name__)
load_dotenv()


# HOME PAGE
@app.route('/')
@app.route('/index')
def index():
    #return("Hello World!")
    return render_template('index.html')


@app.route('/predict',methods=['POST'])
def predict():

    # vehicle data inputs
    vehicleWeight = request.form['vehicleWeight']
    frontTireDiameter = request.form['frontTireDiameter']
    rearTireDiameter = request.form['rearTireDiameter']
    wheelbase = request.form['wheelbase']
    forwardWeightDistribution = request.form['forwardWeightDistribution']
    centerOfGravityHeight = request.form['centerOfGravityHeight']
    # brake data inputs
    brakePedalRatio = request.form['brakePedalRatio']
    brakeBias = request.form['brakeBias']
    frontMasterCylinder = request.form['frontMasterCylinder']
    rearMasterCylinder = request.form['rearMasterCylinder']
    frontCaliper = request.form['frontCaliper']
    rearCaliper = request.form['rearCaliper']
    frontRotorOuter = request.form['frontRotorOuter']
    rearRotorOuter = request.form['rearRotorOuter']
    # user prefrence inputs
    factorOfSafety = request.form['factorOfSafety']
    priority = request.form['priority']

    

    result = getTheConfigs(vehicleWeight, frontTireDiameter, rearTireDiameter, wheelbase, forwardWeightDistribution, centerOfGravityHeight, brakePedalRatio, brakeBias, frontMasterCylinder, rearMasterCylinder, frontCaliper, rearCaliper, frontRotorOuter, rearRotorOuter, factorOfSafety, priority)

    return render_template('output.html', prediction_text=str(result))

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)

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