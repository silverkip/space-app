import requests
import json

from bs4 import BeautifulSoup


key = "AIzaSyAUkNMzDo7KUo2TrCYYF9ENig32N7RJYg4"

def getLaunches(past=False):
    ''' Returns a dict containing info about future launches '''

    url = "http://www.spaceflightinsider.com/launch-schedule/"
    if past:
        url += "?past=1"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    launches = []

    for tag in soup.select("table.launchcalendar"):

        result = {}
        details = tag.find(class_="launchdetails").find_all("tr")

        for detail in details:
            result[detail.th.string.lower()] = detail.td.get_text()

        style = tag.find(class_='vehicle').div['style']
        index = style.index("http")
        result['image'] = style[index:-3]
        result['mission'] = tag.find(colspan='2').get_text()
        result['description'] = tag.find(class_='description').p.get_text()
        launches.append(result)

    return launches


def geocode(address):
    ''' converts address string to lat-long coordinates '''
    address = address.replace(' ', '+')
    url = f"https://maps.googleapis.com/maps/api/geocode/json?key={key}&address={address}"
    response = requests.get(url).json()
    coordinates = response['results'][0]['geometry']['location']
    return coordinates


if __name__ == '__main__':
    from pprint import pprint
    pprint(getLaunches())


# result = requests.get("https://launchlibrary.net/1.4/launch?name=falcon")
# with open("launches.json", "w") as file:
#     json.dump(result.json(), file)

