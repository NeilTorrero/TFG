# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import datetime
import requests
import pytz


def searchInform(entities):
    for entity in entities:
        print(entity)


def getTime(city='Barcelona'):
    # check for ip lookup timezone https://ipapi.com / https://apilayer.com/#products
    # country_codes = {country: code for code, country in pytz.country_names.items()}
    # print(pytz.country_timezones[country_codes['Germany']])
    # tz = pytz.timezone('Europe/London')
    now = datetime.datetime.now()  # tz)
    date = now.strftime("%A %dth of %B")
    time = now.strftime("%H:%M")
    print(date + " - " + time)
    return date, time


def getWeather(city='Barcelona'):
    # check for ip lookup city https://ipapi.com
    API_KEY = "2e40656c78ebe1ec22f4f6a82540f208"
    WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?"

    url = WEATHER_URL + "q=" + city + "&appid=" + API_KEY + "&units=metric"

    response = requests.get(url)
    json_r = response.json()
    if json_r['cod'] != '404':
        info = json_r['main']
        temperature = info['temp']
        pressure = info['pressure']
        humidity = info['humidity']
        weather_description = json_r['weather'][0]['description']
        print(temperature, pressure, humidity, weather_description)
        return [temperature, pressure, humidity, weather_description]
    else:
        print("City not found")
        return []


class ActionAskTime(Action):

    def name(self) -> Text:
        return "action_ask_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("\nDispacher: ")
        print(dispatcher)
        print("\nTracker: ")
        print(tracker)
        print("\nDomain: ")
        print(domain)
        date, time = getTime()
        print(date, time)
        dispatcher.utter_message(text="Date: " + date + " and Time: " + time)

        return []


class ActionAskWeather(Action):

    def name(self) -> Text:
        return "action_ask_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("\nDispacher: ")
        print(dispatcher)
        print("\nTracker: ")
        print(tracker)
        print("\nDomain: ")
        print(domain)
        weather = getWeather()
        if weather:
            dispatcher.utter_message(
                text="It's " + str(weather[3]) + ", with a temperature of " + str(weather[0]) + "ºC and with a humidity of a " + str(weather[2]) + "%.")
        else:
            dispatcher.utter_message(text="Sorry, couldn't find the weather for this city.")

        return []


class ActionFood(Action):

    def name(self) -> Text:
        return "action_food"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(dispatcher, tracker, domain)
        dispatcher.utter_message(text="I'd need some more data. If you lick the monitor perhaps I can evaluate your taste buds.")
        dispatcher.utter_message(text="I'm sorry, I can't recommend you a restaurant as I usually cook at home.")

        return []


class ActionMusic(Action):

    def name(self) -> Text:
        return "action_music"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(dispatcher, tracker, domain)

        dispatcher.utter_message(text="Playing music.")

        return []
