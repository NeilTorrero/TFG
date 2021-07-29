import datetime
import requests
import pytz
import urllib.parse

from bs4 import BeautifulSoup

def searchInform(question):
    """
    - if the box contains a upper link to de thing you are looking (USA / President)
      dates Z0LcW XcVN5d, people to but they might be in a link (<a>)
      for more info yxAsKe kZ91ed
    - when info is inside divs (when is mothers day) '.zCubwf' or #EtGB6d div (for hole box)
    - when response is alone .IZ6rdc
    - to get response from text which is in bold .hgKElc , b
    - responses with a graph .KBXm4e
    - money converter .gzfeS
    - response inside little boxes as a list .FozYP (bread ingredients)/(pokemon types "what type is rayquaza")
    - calculator response .XSNERd
    - Translate .Y2IQFc
    - Dictionary definition .sY7ric span
    - response conversion #NotFQb .vXQmIe (result) and .bjhkR (formula)
    - when response is a snippet(wikipedia or other pages extracted) .iKJnec
    + list of ranking .Crs1tb
    + location .XCwAFc
    """
    """
    https://stackoverflow.com/questions/49268359/scraping-googles-quick-answer-box-in-python
    https://stackoverflow.com/questions/42808534/how-to-get-googles-fast-answer-box-text
    https://stackoverflow.com/questions/42792503/web-scrape-from-google-quick-answer-box
    https://dev.to/dimitryzub/how-to-scrape-google-knowledge-graph-with-python-2ilp
    https://stackoverflow.com/questions/31798009/is-there-an-api-for-the-google-answer-boxes
    https://practicaldatascience.co.uk/data-science/how-to-scrape-google-search-results-using-python

    question = "president of usa"
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

    # if the box contains a upper link to de thing you are looking (USA / President)
    # dates Z0LcW XcVN5d, people to but they might be in a link (<a>)
    answer = soup.select_one('.Z0LcW.XcVN5d')
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



def getTime(city):
    # https://geocode.xyz/<city>?json=1 -> to get info of the place (long and lat)
    # check for ip lookup timezone https://ipapi.com / https://apilayer.com/#products
    # http://www.geonames.org/export/web-services.html#timezone

    # https://api.ipgeolocation.io/timezone?apiKey=API_KEY&location=London,%20UK
    API_KEY = "58e075c842754f2891afa358af81cf39"
    LOC_URL = "https://api.ipgeolocation.io/timezone?apiKey="
    url = LOC_URL + API_KEY + "&location=" + city

    response = requests.get(url)
    json_r = response.json()
    date_time = json_r['date_time_txt'][:-3]
    splited = date_time.rpartition(' ')
    print(splited[0] + " - " + splited[2])
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


if __name__ == '__main__':
    getTime("california")
