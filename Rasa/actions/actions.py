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


def getTime(city):
    # https://geocode.xyz/<city>?json=1 -> to get info of the place (long and lat)
    # check for ip lookup timezone https://ipapi.com / https://apilayer.com/#products

    # https://api.ipgeolocation.io/timezone?apiKey=API_KEY&location=London,%20UK
    if city is None:
        # tz = pytz.timezone('Europe/London')
        now = datetime.datetime.now()  # tz)
        date = now.strftime("%A %dth of %B")
        time = now.strftime("%H:%M")
        print(date + " - " + time)
        return date, time
    else:
        API_KEY = "58e075c842754f2891afa358af81cf39"
        LOC_URL = "https://api.ipgeolocation.io/timezone?apiKey="
        url = LOC_URL + API_KEY + "&location=" + city

        response = requests.get(url)
        json_r = response.json()
        date_time = json_r['date_time_txt'][:-3]
        splited = date_time.rpartition(' ')
        date = splited[0]
        time = splited[2]
        print(date + " - " + time)
        return date, time


class ActionAskTime(Action):

    def name(self) -> Text:
        return "action_ask_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("\nTracker: ")
        # print(tracker.sender_id)
        print(tracker.latest_message)
        # print(tracker.events)
        # print(tracker.active_loop)
        # print(tracker.latest_action_name)
        print("\nSlots: ")
        # print(tracker.slots)

        location = None
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'location':
                location = entity['value']

        date, time = getTime(location)
        print(date, time)
        dispatcher.utter_message(text="Date: " + date + " and Time: " + time)

        return []


def getWeather(city, date):
    # check for ip lookup city https://ipapi.com
    API_KEY = "2e40656c78ebe1ec22f4f6a82540f208"
    WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?"
    # Forecast minute for 1 hour, hourly for 48 hours and daily for 7 days -> https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}&units=metric

    if city is None:
        city = 'Barcelona'
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


class ActionAskWeather(Action):

    def name(self) -> Text:
        return "action_ask_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("\nTracker: ")
        # print(tracker.sender_id)
        print(tracker.latest_message)
        # print(tracker.events)
        # print(tracker.active_loop)
        # print(tracker.latest_action_name)
        print("\nSlots: ")
        # print(tracker.slots)

        location = None
        date = None
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'location':
                location = entity['value']
            if entity['entity'] == 'time':
                date = entity['value']

        weather = getWeather(location, date)
        if weather:
            dispatcher.utter_message(
                text="It's " + str(weather[3]) + ", with a temperature of " + str(
                    weather[0]) + "ºC and with a humidity of a " + str(weather[2]) + "%.")
        else:
            dispatcher.utter_message(text="Sorry, couldn't find the weather for this city.")

        return []


class ActionFood(Action):

    def name(self) -> Text:
        return "action_food"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("\nTracker: ")
        # print(tracker.sender_id)
        print(tracker.latest_message)
        # print(tracker.events)
        # print(tracker.active_loop)
        # print(tracker.latest_action_name)
        print("\nSlots: ")
        # print(tracker.slots)
        dispatcher.utter_message(
            text="I'd need some more data. If you lick the monitor perhaps I can evaluate your taste buds.")
        dispatcher.utter_message(text="I'm sorry, I can't recommend you a restaurant as I usually cook at home.")

        return []


class ActionMusic(Action):

    def name(self) -> Text:
        return "action_music"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("\nTracker: ")
        # print(tracker.sender_id)
        print(tracker.latest_message)
        # print(tracker.events)
        # print(tracker.active_loop)
        # print(tracker.latest_action_name)
        print("\nSlots: ")
        # print(tracker.slots)

        dispatcher.utter_message(text="Playing music. Well yes but actually no.")

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

    # if the box contains a upper link to de thing you are looking (USA / President)
    # dates Z0LcW XcVN5d, people to but they might be in a link (<a>)
    answer = soup.select_one('.Z0LcW.XcVN5d')
    try:
        if answer is not None:
            # for more info yxAsKe kZ91ed
            more = soup.select_one('.yxAsKe.kZ91ed')
            print(answer.text)
            if more is None:
                return answer.text
            else:
                print(more.text)
                return answer.text + ',' + more.text
        else:
            # when info is inside divs (when is mothers day) '.zCubwf' or #EtGB6d div (for hole box)
            answer = soup.select_one('.zCubwf')
            if answer is not None:
                print(answer.text)
                return answer.text

        # when response is alone .IZ6rdc
        answer = soup.select_one('.IZ6rdc')
        if answer is not None:
            print(answer.text)
            return answer.text
        else:
            # to get response from text which is in bold .hgKElc , b
            answer = soup.select_one('.hgKElc b')
            if answer is not None:
                print(answer.text)
                return answer.text

        # responses with a graph .KBXm4e
        answer = soup.select_one('.KBXm4e')
        if answer is not None:
            print(answer.text)
            return answer.text
        else:
            # money converter .gzfeS
            answer = soup.select_one('.gzfeS')
            if answer is not None:
                print(answer.text)
                return answer.text

        # response inside little boxes as a list .FozYP (bread ingredients)/(pokemon types "what type is rayquaza")
        answer = soup.select_one('.FozYP')
        if answer is not None:
            print(answer.text)
            return answer.text
        else:
            # calculator response .XSNERd
            answer = soup.select_one('.XSNERd')
            if answer is not None:
                print(answer.text)
                return answer.text

        # Translate .Y2IQFc
        answer = soup.select_one('.Y2IQFc')
        if answer is not None:
            print(answer.text)
            return answer.text
        else:
            # Dictionary definition .sY7ric span
            answer = soup.select_one('.sY7ric span')
            if answer is not None:
                print(answer.text)
                return answer.text

        # response conversion #NotFQb .vXQmIe (result) and .bjhkR (formula)
        answer = soup.select_one('#NotFQb .vXQmIe')
        if answer is not None:
            # for the formula .bjhkR
            more = soup.select_one('.bjhkR')
            print(answer.text)
            if more is None:
                return answer.text
            else:
                print(more.text)
                return answer.text + ',' + more.text
        else:
            # when response is a snippet(wikipedia or other pages extracted) .iKJnec
            answer = soup.select_one('.iKJnec')
            if answer is not None:
                print(answer.text)
                return answer.text
    except:
        print(answer)
        return "Something went wrong while looking for the answer, I will have this check and be solved as soon as possible."
    return "I didn't find anything for what you asked."


class ActionSearchAnswer(Action):

    def name(self) -> Text:
        return "action_search_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        question = ''
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'search':
                question += entity['value']
        if question == '':
            question = tracker.latest_message.text
        answer = webScrapAnswer(question)

        dispatcher.utter_message(text=answer)

        return []
