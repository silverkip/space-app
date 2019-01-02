import json
import requests
from bs4 import BeautifulSoup

def updatePlaces(key):
    '''Puts the launch places (address and coords) in a json'''
    link = "http://www.spaceflightinsider.com/launch-schedule/"
    places = {}
    for url in [link, link+"?past=1"]:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'lxml')

        for tag in soup.select("table.launchcalendar"):
            result = {}
            details = tag.find(class_="launchdetails").find_all("tr")

            for detail in details:
                result[detail.th.string.lower()] = detail.td.get_text()

            place = result['location'].split(' ')
            result['location'] = ' '.join(place[:-1])
            coordinates = places.get(result['location'], geocode(result['location'], key))
            places[result['location']] = coordinates

        with open('places.txt', 'w') as fout:
            json.dump(places, fout)

    return places

def getLaunches(past=False):
    ''' Returns a dict containing info about future launches '''
    url = "http://www.spaceflightinsider.com/launch-schedule/"
    if past:
        url += "?past=1"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    launches = []
    places = {}
    with open('places.txt') as fin:
        places = json.load(fin)

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
        place = result['location'].split(' ')
        result['location'] = ' '.join(place[:-1])
        result['pad'] = place[-1]
        coordinates = places.get(result['location'], None)
        if coordinates:
            result['long'] = coordinates.get('lng', None)
            result['lat'] = coordinates.get('lat', None)
        launches.append(result)

    return launches

def geocode(address, key):
    ''' converts address string to lat-long coordinates '''
    address = address.replace(' ', '+')
    url = f"https://maps.googleapis.com/maps/api/geocode/json?key={key}&address={address}"
    response = requests.get(url).json()
    if not response['results']:
        print('oopsy')
        return {}
    coordinates = response['results'][0]['geometry']['location']
    for k, v in coordinates.items():
        coordinates[k] = round(v, 7)
    return coordinates

if __name__ == '__main__':
    from pprint import pprint
    #print('Please enter your Google API key:')
    #key = input()
    #updatePlaces(key)
    launches = getLaunches()
    for l in launches:
        pprint(l['mission'])
        pprint(l['location'])
        pprint(l['lat'])
        print()
