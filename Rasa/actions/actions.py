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
from pymongo import MongoClient
from pymongo.database import Database
from rasa_sdk.events import ReminderScheduled, SessionStarted, SlotSet, ActionExecuted, EventType, BotUttered, \
    ReminderCancelled
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher

import datetime
import requests
import pytz

logger = logging.getLogger(__name__)


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
            if entity['entity'] == 'location' or entity['entity'] == 'GPE':
                location = entity['value']

        date, time = getTime(location)
        print(date, time)
        dispatcher.utter_message(text="Date: " + date + " and Time: " + time)

        return []


def getWeather(city, date, date_grain):
    # check for ip lookup city https://ipapi.com
    API_KEY = "2e40656c78ebe1ec22f4f6a82540f208"

    if city is None:
        city = 'Barcelona'

    # check if forecast can be done
    # date format 2021-07-27T15:41:49.000+02:00 -> datetime.fromisoformat('2011-11-04T00:05:23+04:00')
    # minute for 1 hour, hourly for 48 hours and daily for 7 days
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
            print(temperature, pressure, humidity, weather_description)
            return [temperature, pressure, humidity, weather_description]
        else:
            print("City not found")
            return []
    else:
        diff = (datetime.datetime.fromisoformat(date) - datetime.datetime.now(datetime.datetime.fromisoformat(date).tzinfo))
        if not 7 >= diff.days >= 0:
            print("I don't have the forecast for the date you are asking.")
            return []

        FORECAST_URL = "https://api.openweathermap.org/data/2.5/onecall?"
        response = requests.get("https://geocode.xyz/" + city + "?json=1")
        json_city = response.json()
        if json_city['code'] != '018':
            print('City not found')
            return []
        # Forecast -> https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={API key}&units=metric
        url = FORECAST_URL + "lat=" + json_city['latt'] + "&lon=" + json_city['longt'] + "&appid=" + API_KEY + "&units=metric"

        response = requests.get(url)
        json_r = response.json()
        if json_r['cod'] != '404':
            if date_grain == 'seconds' or date_grain == 'second' or date_grain == 'minutes' or date_grain == 'minute' or date_grain == 'hours' or date_grain == 'hour':
                if diff.seconds / 60 / 60 <= 48:
                    print('Check next 48 hours')
                    info = json_r['hourly'][int(diff.seconds/60/60)]
                    temperature = info['temp']
                    pressure = info['pressure']
                    humidity = info['humidity']
                    weather_description = json_r['weather'][0]['description']
                    print(temperature, pressure, humidity, weather_description)
                    return [temperature, pressure, humidity, weather_description]
                else:
                    print('Check next 7 days')
                    info = json_r['daily'][int(diff.days)]
                    temperature = info['temp']
                    pressure = info['pressure']
                    humidity = info['humidity']
                    weather_description = json_r['weather'][0]['description']
                    print(temperature, pressure, humidity, weather_description)
                    return [temperature, pressure, humidity, weather_description]
            elif date_grain == 'days' or date_grain == 'day':
                print('Check next 7 days')
                info = json_r['daily'][int(diff.days)]
                temperature = info['temp']
                pressure = info['pressure']
                humidity = info['humidity']
                weather_description = json_r['weather'][0]['description']
                print(temperature, pressure, humidity, weather_description)
                return [temperature, pressure, humidity, weather_description]
        else:
            print("There's no forecast for this date.")
            return[]


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
        date_grain = None
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'location' or entity['entity'] == 'GPE':
                location = entity['value']
            if entity['entity'] == 'time':
                date = datetime.datetime.fromisoformat(str(entity['value']))
                date_grain = entity['additional_info']['grain']
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

        weather = getWeather(location, date, date_grain)
        if weather:
            dispatcher.utter_message(
                text="It's " + str(weather[3]) + ", with a temperature of " + str(
                    weather[0]) + "ºC and with a humidity of a " + str(weather[2]) + "%.")
        else:
            dispatcher.utter_message(text="Sorry, couldn't find the weather for this city or there wasn't forecast for it.")

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
        # TODO: search for restaurants or food related business nearby
        
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


class ActionTimer(Action):
    def name(self) -> Text:
        return "action_timer"

    async def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        date = None
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
            "utter_end_timer",
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

        date = None
        task = None
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
        reminders.append(task + date)

        reminder = ReminderScheduled(
            "utter_remind",
            trigger_date_time=date,
            entities=entities,
            name="reminder_" + task,
            kill_on_user_message=False,
        )

        return [reminder, SlotSet('reminders', reminders)]


class ActionCancelReminder(Action):
    """Cancels reminder."""

    def name(self) -> Text:
        return "action_cancel_reminder"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        task = None
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

        slots = setUserDBConversation(slot_value, tracker)
        dispatcher.utter_message("User registered.")
        slots['user_db_name'] = slot_value
        return slots  # {"user_db_name": slot_value}


def setUserDBConversation(user_db_name, tracker: Tracker):
    print(os.path.abspath(os.getcwd()))
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
            "conversations": tracker.sender_id
        }
        colec.insert_one(userDocument)
        return None
    else:
        print('User found')
        found = colec.find_one_and_update({"name": user_db_name}, {"$addToSet": {"conversations": tracker.sender_id}})
        # load slots that have been saved
        slots = {}
        for key in found.keys():
            if key != 'conversations':
                # slot = SlotSet(key, found[key])
                # slots.append(slot)
                slots[key] = found[key]
        return slots


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
