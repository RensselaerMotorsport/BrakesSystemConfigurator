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

    # column 1: vehicle data inputs
    vehicleWeight = request.form['vehicleWeight']
    frontTireDiameter = request.form['frontTireDiameter']
    rearTireDiameter = request.form['rearTireDiameter']
    wheelbase = request.form['wheelbase']
    forwardWeightDistribution = request.form['forwardWeightDistribution']
    centerOfGravityHeight = request.form['centerOfGravityHeight']
    # column 2: brake data inputs
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
    # column 3: user prefrence inputs
    factorOfSafety = request.form['factorOfSafety']
    priority = request.form['priority']

    frontCaliper, rearCaliper, result3 = getTheConfigs(vehicleWeight, frontTireDiameter, rearTireDiameter, wheelbase, forwardWeightDistribution, centerOfGravityHeight, brakePedalRatio, brakeBias, frontMasterCylinder, rearMasterCylinder, frontCaliper, frontPad, rearCaliper, rearPad, frontRotorOuter, rearRotorOuter, factorOfSafety, priority)

    # return  '{} {} {}'.format(result1, result2, result3)

    return render_template('index.html', prediction_text1=str(frontCaliper), prediction_text2=str(rearCaliper), prediction_text3=str(result3))

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)