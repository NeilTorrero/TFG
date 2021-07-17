# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from backendCalls import getTime, getWeather


class ActionAskTime(Action):

    def name(self) -> Text:
        return "action_ask_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print(dispatcher, tracker, domain)
        date, time = getTime()
        print(date, time)
        dispatcher.utter_message(text="Date: " + date + "and Time: " + time)

        return []

class ActionAskWeather(Action):

    def name(self) -> Text:
        return "action_ask_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print(dispatcher, tracker, domain)
        weather = getWeather()
        if weather:
            dispatcher.utter_message(text="It's " + weather[3] + ", with a temperature of " + weather[0] + " and with a humidity of a " + weather[2] + "%.")
        else:
            dispatcher.utter_message(text="Sorry, couldn't find the weather for this city.")

        return []
