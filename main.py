
import locale
locale.setlocale(locale.LC_ALL, 'en_US') #as we need to deal with NAMES of monthes later on.
import ssl
import time

from ship_dict import ship_names
from ships import Ship

NAMES = list(ship_names.keys())

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


IMOS = []
while True:
    print_ships()
    num = int(input('Pick a ship (0 to stop): '))
    if num == 0:
        if len(IMOS) == 0:
            quit()
        else:
            break
    else:
        IMOS.append(ship_names[NAMES[num-1]])
while True:
    ships = []
    for IMO in IMOS:
        ships.append(Ship(IMO))
        
    for i in ships:
        print(i)
    time.sleep(5*60)

