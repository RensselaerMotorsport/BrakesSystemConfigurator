from dotenv import load_dotenv


from pprint import pprint
import requests
import os

load_dotenv()

def getConfigs(FOS="2"):

    return "test"

if __name__ == "__main__":
    FOS = input("\nPlease enter a factor of safety: ")

    # Check for empty strings or string with only spaces
    # This step is not required here
    # if not bool(city.strip()):
    #     city = "Kansas City"

    config_outputs = getConfigs(FOS)

    print("\n")
    pprint(config_outputs)    