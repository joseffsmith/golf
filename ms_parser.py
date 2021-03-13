import bs4
from datetime import datetime, timedelta
import json

class Parser:
    def __init__(self, content=None):
        if not content:
            self.load_content()


    def load_content(self):
        with open('comps_list.txt', 'r') as f:
            self.content = f.read()

    def parse(self):
        b = bs4.BeautifulSoup(self.content)
        rows = b.find_all('tr')[1:] # skip first row it's a header
        return json.dumps({'comps': [self.parse_row(row) for row in rows]})

    
    def parse_row(self, row):
        # TODO check day of month is zero padded

        cells = row.find_all('td')
        if len(cells) != 4:
            raise Exception('Unable to parse row, cells not equal to 4')

        gender, date, html_description, notes = cells

        form = notes.find('form')
        action = None
        if form:
            action = notes.find('form', action=True)['action']

        return {
            'gender': gender.find('img', alt=True)['alt'],
            'date': datetime.strptime(date.text, '%a %d %b %y').timestamp(),
            'html_description': html_description.text,
            'action': action,
            'notes': notes.text
        }
        