# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from bs4 import BeautifulSoup
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


def getWeather(city='Barcelona', date='today'):
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

        print("\nTracker: ")
        print(tracker.sender_id)
        print(tracker.slots)
        print(tracker.latest_message)
        print(tracker.events)
        print(tracker.active_loop)
        print(tracker.latest_action_name)
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

        print("\nTracker: ")
        print(tracker.sender_id)
        print(tracker.slots)
        print(tracker.latest_message)
        print(tracker.events)
        print(tracker.active_loop)
        print(tracker.latest_action_name)
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


def webScrapAnswer(question):
    headers = {
        'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
    }

    params = {
        'hl': 'en',
        'gl': 'us',
        'lr': 'lang_en'
    }

    html = requests.get('https://www.google.com/search?q=' + question + '&hl=en', headers=headers, params=params).text

    soup = BeautifulSoup(html, 'lxml')

    answer = soup.select_one('.Z0LcW.XcVN5d')
    # if the box contains a upper link to de thing you are looking (USA / President)
    # dates Z0LcW XcVN5d, people to but they might be in a link (<a>)
    # for more info yxAsKe kZ91ed
    more = soup.select_one('.yxAsKe.kZ91ed')
    if answer is None:
        # when info is inside divs '.zCubwf'
        answera = soup.select_one('.zCubwf')
        print(answera.text)
        return answera.text
    else:
        print(answer.text)
        print(more.text)
        return answer.text + ',' + more.text

    # when response is alone .IZ6rdc
    # to get response from text which is in bold .hgKElc , b
    # responses with a graph .KBXm4e


class ActionSearchAnswer(Action):

    def name(self) -> Text:
        return "action_search_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        question = tracker.latest_message['entities'].get('search')
        if question is None:
            question = tracker.latest_message.text
        answer = webScrapAnswer(question)

        dispatcher.utter_message(text=answer)

        return []
