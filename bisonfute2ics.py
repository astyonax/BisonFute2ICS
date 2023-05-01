# author: G.SAGGIORATO May - 2023
# manual conversion of Bison Fute calendar to ICS 

from ics import Calendar, Event
from pandas import to_datetime, date_range

class EndOfData(Exception):
    pass

# a guess
BF_pdf_url = "https://www.bison-fute.gouv.fr/IMG/pdf/Calendrier_{year}_Bison_Fute_A3_impression.pdf" 

def make_event(date, *, 
               zones:int=0, 
               basecolor:str='G', 
               color:str='G', 
               direction='',
               description=''):
    ZONES = [0,1,2,3,4,5,6]
    assert basecolor in 'BROG' # Black, Red, Orange, Green
    assert color in 'BROG' # Black, Red, Orange, Green
    assert isinstance(zones, (str,int))
    try:
        assert (int(zones) in ZONES)
    except ValueError:
        pass
    if isinstance(zones,str) and '-' in zones:
        assert all(int(z) in ZONES for z in zones.split('-'))

    if zones == 0:
        assert color == '' or color == basecolor
        color=basecolor

    longcolor = {'B':'Black',
                 'R':'Red',
                 'O':'Orange',
                 'G':'Green'}

    begin = to_datetime(date).strftime('%Y-%m-%d 00:00:00')

    if color != basecolor:
        name = f'{longcolor[color]} in zone {zones} else {longcolor[basecolor]}'
    else:
        name = f'{longcolor[basecolor]} everywhere'
    if direction:
        name  = f'{direction} {name}'
    e = Event(name=name, begin=begin, description=description)
    e.make_all_day()
    return e

def make_calendar(year, direction):
    c = Calendar()
    
    if direction.lower() == 'depart':
        dd='->'
    else:
        dd='<-'

    pdf_url = BF_pdf_url.replace('{year}', str(year))

    try: 
        import pickle
        with open(f'{direction}-{year}.pkl', 'rb') as fin:
            data = pickle.load(fin)
    except (IOError, EOFError):
        data = []
    
    if len(data):
        print('replaying..')
    for row in data:
        print(row)
        c.events.add(make_event(**row, direction=dd, description=pdf_url))
    

    try:
        while True:
            date = input(f'date - {year}-MM-DD: ')
            if date=='X':
                raise EndOfData
            date = f'{year}-{date}'
            basecolor = input(f'{date} - basecolor: ')
            color = input(f'{date} - color: ')
            if not (color==basecolor or color==''):
                zones = input(f'{date} - zones: ')
            else:
                zones = 0 
            record = dict(date=date, zones=zones, 
                          basecolor=basecolor, color=color)
            
            c.events.add(make_event(**record, direction=dd, description=pdf_url))
            data += record,
    except EndOfData:
        pass
    finally:
        print('saving..')
        with open(f'{direction}-{year}.ics', 'w') as f:
            f.writelines(c)
        with open(f'{direction}-{year}.pkl', 'wb') as fin:
            pickle.dump(data,fin)


if __name__=='__main__':
    make_calendar(input('Year (YYYY)'), input('Direction '))