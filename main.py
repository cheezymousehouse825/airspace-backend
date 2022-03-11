#!/usr/bin/python3
import json
from datetime import datetime
from pytz import timezone
import requests
from time import sleep

def getPollution(key):
    response = requests.get("https://api.waqi.info/feed/toronto/?token=" + key)

    return response.json()

def getCovid(key):
    response = requests.get("https://api.apify.com/v2/key-value-stores/" + key + "/records/LATEST?disableRedirect=true")

    return response.json()

def getWeather(key):
    response = requests.get("http://api.weatherapi.com/v1/current.json?key=" + key + "&q=Toronto&aqi=no")

    return response.json()

def getTimeEST():
    tz = timezone("EST")
    time = datetime.now(tz)

    return time

def getSettings():
    try:
        with open("settings.json", "r") as openfile:
            settings = json.load(openfile)
    except FileNotFoundError:
        waqi = input("waqi api key: ")
        apify = input("apify api key: ")
        weatherapi = input("weatherapi api key: ")
        output = input("/path/to/data.json: ")

        settings = {
            "waqi": waqi,
            "apify": apify,
            "weatherapi": weatherapi,
            "output": output
        }

        json_object = json.dumps(settings, indent=4)
        with open("settings.json", "w") as outfile:
            outfile.write(json_object)

    return settings

def main():
    backendSettings = getSettings()

    while True:
        timeData = getTimeEST()
        pollutionData = getPollution(backendSettings["waqi"])
        covidData = getCovid(backendSettings["apify"])
        weatherData = getWeather(backendSettings["weatherapi"])

        data = {
            "time": str(timeData).split(".", 1)[0],
            "pollution": pollutionData["data"]["aqi"],
            "covid": {
                "infectedCount": covidData["infectedByRegion"][6]["infectedCount"],
                "deceasedCount": covidData["infectedByRegion"][6]["deceasedCount"]
            },
            "weather": {
                "temp": weatherData["current"]["temp_c"],
                "cloud": weatherData["current"]["cloud"],
                "wind_kph": weatherData["current"]["wind_kph"],
                "humidity": weatherData["current"]["humidity"],
                "feelslike": weatherData["current"]["feelslike_c"],
                "condition": weatherData["current"]["condition"]["text"]
            }
        }

        json_object = json.dumps(data, indent=4)
        with open(backendSettings["output"], "w") as outfile:
            outfile.write(json_object)

        sleep(3600)

if __name__ == "__main__":
    main()

