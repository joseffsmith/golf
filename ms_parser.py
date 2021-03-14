import bs4
from datetime import datetime


class Parser:
    def __init__(self):
        pass

    def parse(self, content):
        b = bs4.BeautifulSoup(content)
        rows = b.find_all('tr')[1:]  # skip first row it's a header
        return {'comps': [self.parse_row(row) for row in rows]}

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

    def select_slot_page(self, content):
        b = bs4.BeautifulSoup(content.decode('utf-8'))
        form_data = {i['name']: i['value']
                     for i in b.find_all('input')}
        return form_data

    def select_partner_page(self, content):
        b = bs4.BeautifulSoup(content.decode('utf-8'))
        form_data = {i['name']: i['value']
                     for i in b.find_all('input')}
        num_partners = len(b.find_all('select'))
        return form_data, num_partners

    def partner_ids(self, content):
        b = bs4.BeautifulSoup(content.decode('utf-8'))
        id_to_name_map = {o['value']: o.text for o in b.find_all('option')}
        return id_to_name_map
