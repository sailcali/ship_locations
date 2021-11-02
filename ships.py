import urllib.request
from bs4 import BeautifulSoup
import re
from datetime import datetime
import geopy.distance
from locations import locations

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', 
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 
       'Accept-Encoding': 'none', 
       'Accept-Language': 'en-US,en;q=0.8', 
       'Connection': 'keep-alive'}

class Ship:
    """Attributes of Ship are: IMO, name, lat, lng, loc_time"""
    def __init__(self, IMO):
        self.IMO = IMO
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
                        coords = item[item.find('coordinates') + 12:item.find('coordinates')+39]
                        if 'E)' in coords:
                            coords = coords[:coords.find('E)')+1]
                        else:
                            coords = coords[:coords.find('W)')+1]
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
                            self.name = aux[1].string
                        if aux[0].string == "Position received":
                            loc_time = datetime.strptime(aux[1].get("data-title"), '%b %d, %Y %H:%M %Z')
                            self.loc_time = loc_time.strftime('%Y-%m-%d %H:%M-%S')
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
        self.lat = parse_dms(coordsSplit[0])
        self.lng = parse_dms(coordsSplit[1])
        
    
    def closest_port(self):
        my_coords = (self.lat, self.lng)
        location_names = list(locations.keys())
        self.closest_to = {'location': '',
                      'distance': 500000}
        for loc in location_names:
            their_coords = (locations[loc]['lat'], locations[loc]['lng'])
            dist = geopy.distance.great_circle(my_coords, their_coords).miles
            if self.closest_to['distance'] > dist:
                self.closest_to['distance'] = dist
                self.closest_to['location'] = loc

    def __str__(self):
        self.closest_port()
        current_time = datetime.utcnow()
        diff = current_time - datetime.strptime(self.loc_time,'%Y-%m-%d %H:%M-%S')
        diff = diff.total_seconds() / 60
        if diff < 100:
            return f'{self.name} was in position {self.lat} {self.lng} at {self.loc_time} GMT ({round(diff,1)} minutes ago).\n'\
            f'Ship was closest to {self.closest_to["location"]} at {round(self.closest_to["distance"],2)} miles away.'
        elif diff < 1440:
            diff = diff/60
            return f'{self.name} was in position {self.lat} {self.lng} at {self.loc_time} GMT ({round(diff, 1)} hrs ago).\n'\
            f'Ship was closest to {self.closest_to["location"]} at {round(self.closest_to["distance"],2)} miles away.'
        else:
            diff = (diff/60)/24
            return f'{self.name} was in position {self.lat} {self.lng} at {self.loc_time} GMT ({round(diff, 1)} days ago).\n'\
            f'Ship was closest to {self.closest_to["location"]} at {round(self.closest_to["distance"],2)} miles away.'