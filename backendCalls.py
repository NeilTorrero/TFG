import datetime
import requests
import pytz
import urllib.parse

from bs4 import BeautifulSoup
from requests_html import HTML
from requests_html import HTMLSession


def searchInform(question):
    """question = "president of usa"
    query = urllib.parse.quote_plus(question)

    session = HTMLSession()
    response = session.get("https://www.google.co.uk/search?q=" + query)

    css_identifier_header = ".kp-header"#".ULSxyf"
    css_identifier_result = ".tF2Cxc"
    css_identifier_title = "h3"
    css_identifier_link = ".yuRUbf a"
    css_identifier_text = ".IsZvec"

    header = response.html.find(css_identifier_header)
    for result in header:
        print(result.find(".FLP8od"))

    results = response.html.find(css_identifier_result)

    output = []

    for result in results:
        item = {
            'title': result.find(css_identifier_title, first=True).text,
            'link': result.find(css_identifier_link, first=True).attrs['href'],
            'text': result.find(css_identifier_text, first=True).text
        }

        output.append(item)

    print(output)"""

    headers = {
        'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
    }

    params = {
        'hl': 'en',
        'gl': 'us',
        'lr': 'lang_en'
    }

    question = 'when was keanu reeves born'

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
    else:
        print(answer.text)
        print(more.text)

    # when response is alone .IZ6rdc
    # to get response from text which is in bold .hgKElc , b
    # responses with a graph .KBXm4e



def getTime(city):
    # check for ip lookup timezone https://ipapi.com / https://apilayer.com/#products
    # country_codes = {country: code for code, country in pytz.country_names.items()}
    # print(pytz.country_timezones[country_codes['Germany']])
    # tz = pytz.timezone('Europe/London')
    now = datetime.datetime.now()  # tz)
    date = now.strftime("%A %dth of %B")
    time = now.strftime("%H:%M")
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


if __name__ == '__main__':
    searchInform("hello")
