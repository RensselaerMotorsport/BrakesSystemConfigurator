from flask import Flask, render_template, request, url_for
from inputs import getTheConfigs
from waitress import serve
from dotenv import load_dotenv

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
    brakeBias = 0 #TBD
    frontMasterCylinder = request.form['frontMasterCylinder']
    rearMasterCylinder = request.form['rearMasterCylinder']
    frontCaliper = request.form['frontCaliper']
    frontPad = request.form['frontCaliper']
    rearCaliper = request.form['rearCaliper']
    rearPad = request.form['rearPad']
    frontRotorOuter = request.form['frontRotorOuter']
    rearRotorOuter = request.form['rearRotorOuter']
    # user prefrence inputs
    factorOfSafety = request.form['factorOfSafety']
    priority = request.form['priority']

    result = getTheConfigs(vehicleWeight, frontTireDiameter, rearTireDiameter, wheelbase, forwardWeightDistribution, centerOfGravityHeight, brakePedalRatio, brakeBias, frontMasterCylinder, rearMasterCylinder, frontCaliper, frontPad, rearCaliper, rearPad, frontRotorOuter, rearRotorOuter, factorOfSafety, priority)

    return render_template('output.html', prediction_text=str(result))

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)