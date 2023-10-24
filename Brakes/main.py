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

    a = request.form['a']
    b = request.form['b']

    result = getTheConfigs(a,b)

    return render_template('index.html', prediction_text=str(result))



# # INPUTS PAGE   
# @app.route('/inputs')
# def inputs():
#     form = getTheConfigs('/inputs')
#     return render_template('output.html', form=form)
#     # fos = request.args.get('fos')
#     # # Check for empty strings or string with only spaces
#     # if not bool(fos.strip()):
#     #     # You could render "City Not Found" instead like we do below
#     #     fos = 2
#     # print("WTF")
#     # print(fos)
#     # print("WTF2")    
#     # config_outputs = getTheConfigs(fos)
#     # print("here!")
#     # return render_template(
#     #     "output.html",
#     #     status=config_outputs[0],
#     # )


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)