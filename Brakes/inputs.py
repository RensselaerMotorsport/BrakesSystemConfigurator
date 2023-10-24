# from dotenv import load_dotenv
# from flask import Flask, render_template, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import json



from pprint import pprint
import requests
import os

#load_dotenv()

def getTheConfigs(a,b):
    if (a.isnumeric() & b.isnumeric()):
        a=float(a)
        b=float(b)
    result = a*b
    return result

# def getTheConfigs(fos=1):
#     #fos = requests.get().json()

#     fos = request.args.get['fos']

#     print("HI")
#     print(fos)
#     print("Hi2")

#     force = 2 * fos
#     return str(force)

# if __name__ == "__main__":
#     fos = input("\nPlease enter a factor of safety: ")

#     # Check for empty strings or string with only spaces
#     # This step is not required here
#     # if not bool(city.strip()):
#     #     city = "Kansas City"

#     config_outputs = getTheConfigs(fos)

#     print("\n")
#     pprint(config_outputs)    