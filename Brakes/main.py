from flask import Flask, render_template, request
from inputs import getConfigs
from waitress import serve
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()


@app.route('/')
@app.route('/index')
def index():
    return("Hello World!")
    return render_template('index.html')




@app.route('/inputs')
def getConfigs():
    FOS = request.args.get('FOS')

    # Check for empty strings or string with only spaces
    if not bool(FOS.strip()):
        # You could render "City Not Found" instead like we do below
        FOS = 2

    config_outputs = getConfigs(FOS)


    return render_template(
        "index.html",
        title=config_outputs["name"],
    )


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)