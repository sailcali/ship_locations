import urllib.request
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US') #as we need to deal with NAMES of monthes later on.
import os
import ssl
import time
import webbrowser
from ship_dict import ships

NAMES = list(ships.keys())


def print_ships():
    print('----------------------------------------')
    
    for i in range(len(NAMES)):
        print(f'{i+1}. {NAMES[i]}')
    print('----------------------------------------')

try:
   _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', 
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 
       'Accept-Encoding': 'none', 
       'Accept-Language': 'en-US,en;q=0.8', 
       'Connection': 'keep-alive'}
IMOS = []
while True:
    print_ships()
    num = int(input('Pick a ship: '))
    if num == 0:
        if len(IMOS) == 0:
            quit()
        else:
            break
    else:
        IMOS.append(ships[NAMES[num-1]])

while True:
    items = []
    for IMO in IMOS:
        url = r'https://www.vesselfinder.com/en/vessels/VOS-TRAVELLER-IMO-' + str(IMO)
        req = urllib.request.Request(url, None, hdr)
        with urllib.request.urlopen(req) as response:
            the_page = response.read()
        parsed_html = BeautifulSoup(the_page, 'html.parser')
        tables = parsed_html.findAll("table")
        paras = parsed_html.findAll("p")
        for para in paras:
            for item in para.children:
                if '(coordinates' in item:
                    try:
                        coords = item[item.find('coordinates') + 12:item.find('coordinates')+35]
                    except TypeError as error:
                        print('no location')
        
        for table in tables:
            if table.findParent("table") is None:
                for row in table.findAll('tr'):
                    aux = row.findAll('td')
                    try:
                        if aux[0].string == "Coordinates":
                            coords = aux[1].string
                        if aux[0].string == "Vessel Name":
                            name = aux[1].string
                        if aux[0].string == "Position received":
                            loc_time = datetime.strptime(aux[1].get("data-title"), '%b %d, %Y %H:%M %Z')
                    except: 
                        pass
        coordsSplit = coords.split("/")
        coordsSplit[0] = coordsSplit[0][:-1]
        coordsSplit[1] = coordsSplit[1][1:]
        def dms2dd(degrees,direction):
            dd = float(degrees) ;
            if direction == 'S' or direction == 'W':
                dd *= -1
            return dd
        def parse_dms(dms):
            parts = re.split(' ', dms)
            lat = dms2dd(parts[0], parts[1])
            return lat
        lat = parse_dms(coordsSplit[0])
        lng = parse_dms(coordsSplit[1])
        items.append((lat, lng, name, loc_time.strftime('%Y-%m-%d %H:%M-%S')))
        
    for item in items:
        print(item)
    time.sleep(5*60)
