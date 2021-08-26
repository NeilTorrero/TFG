# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import logging
import json
import os
from typing import Any, Text, Dict, List

from bs4 import BeautifulSoup
import bson
from pymongo import MongoClient
from pymongo.database import Database
from rasa_sdk.events import ReminderScheduled, SessionStarted, SlotSet, ActionExecuted, EventType, BotUttered, \
    ReminderCancelled
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher

import datetime
import requests
import pytz
from spellchecker import SpellChecker

logger = logging.getLogger(__name__)


def spellCheck(entity):
    spell = SpellChecker()
    words = spell.unknown(spell.split_words(entity))
    corrected_entity = ''
    for word in words:
        corrected = spell.correction(word)
        print(word + " has been corrected to " + corrected)
        if corrected_entity != '':
            corrected_entity += ' '
        corrected_entity += corrected
    return corrected_entity


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
        # print("\nTracker: ")
        # print(tracker.sender_id)
        # print(tracker.latest_message)
        # print(tracker.events)
        # print(tracker.active_loop)
        # print(tracker.latest_action_name)
        # print("\nSlots: ")
        # print(tracker.slots)

        location = tracker.get_slot('location')
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'location' or entity['entity'] == 'GPE':
                location = entity['value']

        # Location Spell check
        if location is not None:
            location = spellCheck(location)
        # API/library call
        date, time = getTime(location)  # TODO: slot where user lives
        print(date, time)
        dispatcher.utter_message(text="Date: " + date + " and Time: " + time)

        return []


def getWeather(city, date, date_grain):
    # check for ip lookup city https://ipapi.com
    API_KEY = "2e40656c78ebe1ec22f4f6a82540f208"

    if city is None: # TODO: slot of where the user lives
        city = 'Barcelona'

    # check if forecast can be done
    # date format 2021-07-27T15:41:49.000+02:00 -> datetime.fromisoformat('2011-11-04T00:05:23+04:00')
    # minute for 1 hour, hourly for 48 hours and daily for 7 days
    # check for asked weather condition https://openweathermap.org/weather-conditions
    if date is None:
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
            condition_code = json_r['weather'][0]['id']
            print(temperature, pressure, humidity, weather_description)
            return ['OK', temperature, pressure, humidity, weather_description, condition_code]
        else:
            print("City not found")
            return ['KO', "City not found"]
    else:
        diff = (datetime.datetime.fromisoformat(str(date)) - datetime.datetime.now(datetime.datetime.fromisoformat(str(date)).tzinfo))
        if not 7 >= diff.days >= 0:
            if diff.seconds >= 86400:
                print("I don't have the forecast for the date you are asking.")
                return ['KO', "I don't have the forecast for the date you are asking."]

        FORECAST_URL = "https://api.openweathermap.org/data/2.5/onecall?"
        response = requests.get("https://geocode.xyz/" + city + "?json=1")
        json_city = response.json()
        if 'error' in json_city:
            if json_city['code'] == '018':
                print('City not found')
                return ['KO', 'City not found']
        # Forecast -> https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={API key}&units=metric
        url = FORECAST_URL + "lat=" + json_city['latt'] + "&lon=" + json_city['longt'] + "&appid=" + API_KEY + "&units=metric"

        response = requests.get(url)
        json_r = response.json()
        if 'cod' not in json_r: #and json_r['cod'] != '404':
            if date_grain == 'seconds' or date_grain == 'second' or date_grain == 'minutes' or date_grain == 'minute' or date_grain == 'hours' or date_grain == 'hour':
                if diff.seconds / 60 / 60 <= 48:
                    print('Check next 48 hours')
                    info = json_r['hourly'][int(diff.seconds/60/60)]
                    temperature = info['temp']
                    pressure = info['pressure']
                    humidity = info['humidity']
                    weather_description = info['weather'][0]['description']
                    condition_code = info['weather'][0]['id']
                    print(temperature, pressure, humidity, weather_description)
                    return ['OK', temperature, pressure, humidity, weather_description, condition_code]
                else:
                    print('Check next 7 days')
                    info = json_r['daily'][int(diff.days)]
                    temperature = 'a maximum of ' + str(info['temp']['max']) + 'ºC and a minimum of ' + str(info['temp']['min'])
                    pressure = info['pressure']
                    humidity = info['humidity']
                    weather_description = info['weather'][0]['description']
                    condition_code = info['weather'][0]['id']
                    print(temperature, pressure, humidity, weather_description)
                    return ['OK', temperature, pressure, humidity, weather_description, condition_code]
            elif date_grain == 'days' or date_grain == 'day':
                print('Check next 7 days')
                info = json_r['daily'][int(diff.days)]
                temperature = 'a maximum of ' + str(info['temp']['max']) + 'ºC and a minimum of ' + str(info['temp']['min'])
                pressure = info['pressure']
                humidity = info['humidity']
                weather_description = info['weather'][0]['description']
                condition_code = info['weather'][0]['id']
                print(temperature, pressure, humidity, weather_description)
                return ['OK', temperature, pressure, humidity, weather_description, condition_code]
        else:
            print("There's no forecast for this date.")
            return['KO', "There's no forecast for this date."]
    return['KO', "Sorry I couldn't get you the weather."]


class ActionAskWeather(Action):
    def name(self) -> Text:
        return "action_ask_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # print("\nTracker: ")
        # print(tracker.sender_id)
        # print(tracker.latest_message)
        # print(tracker.events)
        # print(tracker.active_loop)
        # print(tracker.latest_action_name)
        # print("\nSlots: ")
        # print(tracker.slots)

        location = tracker.get_slot('location')
        date = tracker.get_slot('time')
        date_grain = None
        weather_condition = None
        date_text = None
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'location' or entity['entity'] == 'GPE':
                location = entity['value']
            if entity['entity'] == 'weather_condition':
                weather_condition = entity['value']
            if entity['entity'] == 'time':
                date = datetime.datetime.fromisoformat(str(entity['value']))
                date_grain = entity['additional_info']['grain']
                date_text = entity['text']
            if entity['entity'] == 'duration':
                date_grain = entity['additional_info']['unit']
                if date_grain == 'day' or date_grain == 'days':
                    date = datetime.datetime.now() + datetime.timedelta(days=entity['value'])
                elif date_grain == 'hour':
                    date = datetime.datetime.now() + datetime.timedelta(hours=entity['value'])
                elif date_grain == 'minute':
                    date = datetime.datetime.now() + datetime.timedelta(minutes=entity['value'])
                elif date_grain == 'second':
                    date = datetime.datetime.now() + datetime.timedelta(seconds=entity['value'])
                elif date_grain == 'week':
                    date = datetime.datetime.now() + datetime.timedelta(weeks=entity['value'])
                elif date_grain == 'month':
                    date = datetime.datetime.now() + datetime.timedelta(days=entity['value']*30)
                elif date_grain == 'year':
                    date = datetime.datetime.now() + datetime.timedelta(days=entity['value']*365)

        # Location Spell check
        if location is not None:
            location = spellCheck(location)
        # API calls
        weather = getWeather(location, date, date_grain)
        if weather[0] == 'OK':
            answer = "It's " + str(weather[4]) + ("" if date is None else " " + date_text) + ", with a temperature of " + str(weather[1]) + "ºC and with a humidity of a " + str(weather[3]) + "%."
            if weather_condition is not None:
                # https://openweathermap.org/weather-conditions
                if weather_condition == 'rain':
                    if 200 <= weather[5] < 600:
                        answer = "It seems is " + ("" + str(weather[4]) if date is None else "going to " + str(weather[4]) + " " + date_text) + "."
                    else:
                        answer = "It doesn't like is " + ("raining, the weather is " + str(weather[4]) if date is None else "going to rain. it's going to " + str(weather[4]) + " " + date_text) + "."
                elif weather_condition == 'snow':
                    if 600 <= weather[5] < 700:
                        answer = "It seems is " + ("" + str(weather[4]) if date is None else "going to " + str(weather[4]) + " " + date_text) + "."
                    else:
                        answer = "It doesn't like is " + ("snowing, the weather is " + str(weather[4]) if date is None else "going to snow. it's going to " + str(weather[4]) + " " + date_text) + "."
                elif weather_condition == 'clear':
                    if weather[5] == 800:
                        answer = "It seems there's " + ("" + str(weather[4]) if date is None else "going to be a " + str(weather[4]) + " " + date_text) + "."
                    else:
                        answer = "It doesn't like is " + ("sunny, the weather is " + str(weather[4]) if date is None else "going to be a clear sky. it's going to " + str(weather[4]) + " " + date_text) + "."
                elif weather_condition == 'cloud':
                    if 800 < weather[5] < 810:
                        answer = "It seems is " + ("" + str(weather[4]) if date is None else "going to " + str(weather[4]) + " " + date_text) + "."
                    else:
                        answer = "It doesn't like is " + ("cloudy, the weather is " + str(weather[4]) if date is None else "going to be cloudy. it's going to " + str(weather[4]) + " " + date_text) + "."
                elif weather_condition == 'temperature':  # TODO: other parameters like humidity
                    answer = "The temperature " + ("is of " + str(weather[4]) if date is None else "going to be" + str(weather[1]) + "ºC" + " " + date_text) + "."
            dispatcher.utter_message(text=answer)
        else:
            dispatcher.utter_message(text=weather[1])  # "Sorry, couldn't find the weather for this city or there wasn't forecast for it."

        return []


class ActionFood(Action):
    def name(self) -> Text:
        return "action_food"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # print("\nTracker: ")
        # print(tracker.sender_id)
        # print(tracker.latest_message)
        # print(tracker.events)
        # print(tracker.active_loop)
        # print(tracker.latest_action_name)
        # print("\nSlots: ")
        # print(tracker.slots)
        dispatcher.utter_message(
            text="I'd need some more data. If you lick the monitor perhaps I can evaluate your taste buds.")
        dispatcher.utter_message(text="I'm sorry, I can't recommend you a restaurant as I usually cook at home.")
        # TODO: search for restaurants or food related business nearby
        
        return []


class ActionMusic(Action):
    def name(self) -> Text:
        return "action_music"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # print("\nTracker: ")
        # print(tracker.sender_id)
        # print(tracker.latest_message)
        # print(tracker.events)
        # print(tracker.active_loop)
        # print(tracker.latest_action_name)
        # print("\nSlots: ")
        # print(tracker.slots)

        dispatcher.utter_message(text="Playing music. Well yes but actually no.")
        # music entityes -> music_mode, song_name, playlist_name, WORK_OF_ART
        # TODO: connect with spotify and do action requested

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

        # simple response .XcVN5d
        answer = soup.select_one('.XcVN5d')
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
            else:
                # response from info paragraph .hgKElc
                answer = soup.select_one('.hgKElc')
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

        # calculator operation #cwos
        answer = soup.select_one('.TIGsTb div span')
        if answer is not None:
            result = soup.select_one('#cwos')
            print(answer.text + " " + result.text)
            return answer.text + " " + result.text
        else:
            # conversions #NotFQb .vXQmIe
            answer = soup.select_one('#NotFQb .vXQmIe')
            if answer is not None:
                formula = soup.select_one('.bjhkR')
                if formula is not None:
                    print(answer.text + ", the formula to do this conversion is " + formula.text)
                    return answer.text + ", the formula to do this conversion is " + formula.text
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

        # Suggestion .FLP8od
        answer = soup.select_one('.FLP8od')
        if answer is not None:
            print(answer.text)
            return answer.text
        else:
            # Translate .Y2IQFc
            answer = soup.select_one('.Y2IQFc')
            if answer is not None:
                print(answer.text)
                return answer.text

        # Suggestion .UTvhje
        answer = soup.select_one('.UTvhje')
        if answer is not None:
            print(answer.text)
            return answer.text
        else:
            # information (like covid) .AupITe
            answer = soup.select_one('.AupITe')
            if answer is not None:
                answers = ''
                for (idx, entry) in list(enumerate(answer)):
                    answers += '- ' + entry.text + '\n'
                print(answers)
                return answers

        # wikipedia definition .kno-rdesc span
        answer = soup.select_one('.kno-rdesc span')
        if answer is not None:
            print('According to Wikipedia: ' + answer.text)
            return 'According to Wikipedia: ' + answer.text
        else:
            # Dictionary definition .sY7ric span
            answer = soup.select('.sY7ric span')
            if answer is not None:
                if len(list(answer)) > 1:
                    answers = 'Dictionary definition: \n'
                    for (idx, entry) in list(enumerate(answer))[1:]:
                        print(idx + " - " + entry.text)
                        if answer[idx - 1].text.isnumeric():
                            answers += '- ' + entry.text + '\n'
                    print(answers)
                    return answers

        # recomendations .TrT0Xe
        answer = soup.select('.sY7ric span')
        if answer is not None:
            if len(list(answer)) > 0:
                for (idx, entry) in list(enumerate(answer)):
                    print(idx + " - " + entry.text)
                    if answer[idx - 1].text.isnumeric():
                        answers += '- ' + entry.text + '\n'
                print(answers)
                return answers

        # box for b response .LGOjhe
        answer = soup.select_one('.LGOjhe')
        if answer is not None:
            # extracted from web b
            answer = soup.select_one('b')
            if answer is not None:
                print(answer.text)
                return answer.text

    except Exception as e:
        print(answer)
        LOG_FILENAME = 'Rasa/logs/actions.log'
        logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
        logging.exception("Exception = " + str(e) + "\n\n Question = " + question + "\n Answer = " + str(answer))
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
        # maybe adding a secondary search for the whole msg in case this one fails or the ner is not correct

        dispatcher.utter_message(text=answer)

        return []


class ActionTimer(Action):
    def name(self) -> Text:
        return "action_timer"

    async def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        date = tracker.get_slot('time')
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'time':
                date = datetime.datetime.fromisoformat(entity['value'])
            if entity['entity'] == 'duration':
                date_grain = entity['additional_info']['unit']
                if date_grain == 'day':
                    date = datetime.datetime.now() + datetime.timedelta(days=entity['value'])
                elif date_grain == 'hour':
                    date = datetime.datetime.now() + datetime.timedelta(hours=entity['value'])
                elif date_grain == 'minute':
                    date = datetime.datetime.now() + datetime.timedelta(minutes=entity['value'])
                elif date_grain == 'second':
                    date = datetime.datetime.now() + datetime.timedelta(seconds=entity['value'])
                elif date_grain == 'week':
                    date = datetime.datetime.now() + datetime.timedelta(weeks=entity['value'])
                elif date_grain == 'month':
                    date = datetime.datetime.now() + datetime.timedelta(days=entity['value']*30)
                elif date_grain == 'year':
                    date = datetime.datetime.now() + datetime.timedelta(days=entity['value']*365)

        dispatcher.utter_message("Setting the timer.")

        reminder = ReminderScheduled(
            "end_timer",
            trigger_date_time=date,
            name="timer",
            kill_on_user_message=True,
        )

        return [reminder]


class ActionCancelTimer(Action):
    """Cancels timer."""

    def name(self) -> Text:
        return "action_cancel_timer"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(f"Okay, I'll cancel your timer.")

        # Cancel timer
        return [ReminderCancelled("timer")]


class ActionReminder(Action):
    def name(self) -> Text:
        return "action_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        date = tracker.get_slot('time')
        task = tracker.get_slot('task')
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'task':
                task = entity['value']
            if entity['entity'] == 'time':
                date = datetime.datetime.fromisoformat(entity['value'])
            if entity['entity'] == 'duration':
                date_grain = entity['additional_info']['unit']
                if date_grain == 'day':
                    date = datetime.datetime.now() + datetime.timedelta(days=entity['value'])
                elif date_grain == 'hour':
                    date = datetime.datetime.now() + datetime.timedelta(hours=entity['value'])
                elif date_grain == 'minute':
                    date = datetime.datetime.now() + datetime.timedelta(minutes=entity['value'])
                elif date_grain == 'second':
                    date = datetime.datetime.now() + datetime.timedelta(seconds=entity['value'])
                elif date_grain == 'week':
                    date = datetime.datetime.now() + datetime.timedelta(weeks=entity['value'])
                elif date_grain == 'month':
                    date = datetime.datetime.now() + datetime.timedelta(days=entity['value']*30)
                elif date_grain == 'year':
                    date = datetime.datetime.now() + datetime.timedelta(days=entity['value']*365)

        if date is None:
            date = datetime.datetime.now() + datetime.timedelta(minutes=5)
            dispatcher.utter_message("I will remind you of that in 5 minutes.")
        else:
            dispatcher.utter_message("I will remind you of that.")

        entities = tracker.latest_message.get("entities")

        # Add reminder to slot
        reminders = tracker.get_slot('reminders')
        if reminders is None:
            reminders = []
        reminders.append(task + '_' + str(date))

        reminder = ReminderScheduled(
            "check_reminder",
            trigger_date_time=date,
            entities=entities,
            name="reminder_" + task,
            kill_on_user_message=False,
        )

        return [reminder, SlotSet('reminders', reminders)]


class ActionRemind(Action):

    def name(self) -> Text:
        return "action_remind"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        task = tracker.get_slot('task')
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'task':
                task = entity['value']
        dispatcher.utter_message(text="Remember to " + task)

        return [SlotSet("task", None), SlotSet("time", None)]


class ActionCancelReminder(Action):
    """Cancels reminder."""

    def name(self) -> Text:
        return "action_cancel_reminder"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        task = tracker.get_slot('task')
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'task':
                task = entity['value']

        dispatcher.utter_message(f"Okay, I'll cancel your reminder.")

        # Cancel reminder
        return [ReminderCancelled("reminder_" + task)]


class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_name_form"

    def validate_user_db_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        print(slot_value)
        if slot_value is None:
            slot_value = tracker.get_slot('name')
            if slot_value is None:
                slot_value = tracker.get_slot('PERSON')
                if slot_value is None:
                    dispatcher.utter_message("I didn't understand that, please introduce the your name.")
                    return {"user_db_name": None}
        return {"user_db_name": slot_value}


class ActionSubmitRegister(Action):
    def name(self) -> Text:
        return "action_submit_register"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        user = tracker.get_slot('user_db_name')
        slots = setUserDBConversation(user, tracker)
        dispatcher.utter_message("User registered as " + user + ".")
        return slots


def setUserDBConversation(user_db_name, tracker: Tracker):
    # print(os.path.abspath(os.getcwd()))
    path = os.path.abspath('actions/credentials.json')
    with open(path, 'r') as f:
        data = json.load(f)
    client = MongoClient(host=data['host'], username=data['username'], password=data['password'], authSource='admin', connect=False)
    database = Database(client, data['db'])
    colec = database['users']

    existsDocument = colec.find_one({"name": user_db_name})
    if existsDocument is None:
        print('User created')
        userDocument = {
            "name": user_db_name,
            "conversations": [{
                "id": tracker.sender_id,
                "added_time": datetime.datetime.fromtimestamp(tracker.current_state()['latest_event_time'], None)
            }]
        }
        colec.insert_one(userDocument)
        return None
    else:
        print('User found')
        isodate = datetime.datetime.fromtimestamp(tracker.current_state()['latest_event_time'], None)
        found = colec.find_one_and_update({"name": user_db_name}, {"$addToSet": {"conversations": {"id": tracker.sender_id, "added_time": isodate}}})
        # load slots that have been saved
        slots = []
        # slots = {}
        for key in found.keys():
            if key != 'conversations':
                slot = SlotSet(key, found[key])
                slots.append(slot)
                #slots[key] = found[key]
        return slots


def getNews(interests, date):
    # https://newsapi.org/v2/everything?q=bitcoin&apiKey=d7e327b9213748bd9c274abed9bfc5d7
    API_KEY = 'd7e327b9213748bd9c274abed9bfc5d7'
    NEWS_URL = "https://newsapi.org/v2/everything?"
    url = NEWS_URL + "q=" + interests  + "&language=en&sortBy=popularity" + "&apiKey=" + API_KEY + ("" if date is None else ("&to=" + date))

    response = requests.get(url)
    json_r = response.json()

    if json_r['status'] == 'ok':
        article = json_r['articles'][0]
        title = article['title']
        description = article['description']
        link = article['url']
        return 'I found this article!\n Title: ' + title + "\n  " + description + "\n  Link: " + link
    else:
        # TODO: check for different errors with error code
        return "Didn't find any news for what you asked."


class ActionNews(Action):
    def name(self) -> Text:
        return "action_news"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        interests = None
        date = tracker.get_slot('time')
        # ORG, PERSON, GPE, NORP
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'date':
                date = entity['value']
            if entity['entity'] == 'ORG':
                if interests is None:
                    interests = entity['value']
                else:
                    interests += "AND " + entity['value']
            if entity['entity'] == 'PERSON':
                if interests is None:
                    interests = entity['value']
                else:
                    interests += "AND " + entity['value']
            if entity['entity'] == 'GPE':
                if interests is None:
                    interests = entity['value']
                else:
                    interests += "AND " + entity['value']
            if entity['entity'] == 'NORP':
                if interests is None:
                    interests = entity['value']
                else:
                    interests += "AND " + entity['value']

        response = getNews(interests, date)
        dispatcher.utter_message(text=response)
        return []


class ActionMemory(Action):
    def name(self) -> Text:
        return "action_memory"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        date = tracker.get_slot('time')
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'time':
                date = datetime.datetime.fromisoformat(entity['value'])


        intent = tracker.latest_message['response_selector']['memory']['response']['intent_response_key']
        dispatcher.utter_message(text="Database search and retrieval WIP (intent= " + intent + ')')

        if intent == 'memory/retrieve_question':
            # asking for the task
            print()

        else:
            # redo the task
            print()

        return []


"""
class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    @staticmethod
    def fetch_slots(tracker: Tracker) -> List[EventType]:
        # Collect slots that contain the user's name and phone number.

        slots = []
        for key in ("name", "phone_number"):
            value = tracker.get_slot(key)
            if value is not None:
                slots.append(SlotSet(key=key, value=value))
        return slots

    async def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # the session should begin with a `session_started` event
        events = [SessionStarted()]

        # any slots that should be carried over should come after the
        # `session_started` event
        events.extend(self.fetch_slots(tracker))

        # an `action_listen` should be added at the end as a user message follows
        events.append(ActionExecuted("action_listen"))

        return events
"""
