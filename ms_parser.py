import bs4
from dateutil import parser

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Parser:
    def __init__(self):
        pass

    def parse_comps(self, content):
        b = bs4.BeautifulSoup(content)
        rows = b.find_all('tr')[1:]  # skip first row it's a header
        comps = []
        for row in rows:
            try:
                r = self.parse_row(row)
                comps.append(r)
            except Exception as e:
                logger.exception('Could not parse row')
                continue

        return comps

    def parse_row(self, row):
        # TODO check day of month is zero padded

        cells = row.find_all('td')
        if len(cells) == 1:
            raise Exception('Header column')
        if len(cells) != 4:
            raise Exception('Unable to parse row, cells not equal to 4')

        raw_gender, raw_date, raw_html_description, raw_notes = cells

        form = raw_notes.find('form')
        action = None
        if form:
            action = raw_notes.find('form', action=True)['action']

        comp_date = None
        try:
            comp_date = parser.parse(raw_date.text).timestamp()
        except Exception as e:
            logger.exception(f"Failed to parse datetime {raw_date.text}")

        notes = raw_notes.text

        bkb = 'Bookings close by '
        bookings_close_by = None
        if bkb in notes:
            index = notes.find(bkb)
            bkb_date = notes[index:].replace(bkb, '')
            try:
                bookings_close_by = parser.parse(bkb_date).timestamp()
            except Exception as e:
                logger.exception(
                    f'Could not parse Booking close by date {bkb_date}')

        bf = 'Book from '
        book_from = None
        if bf in notes:
            bf_date = notes.replace(bf, '')
            try:
                book_from = parser.parse(bf_date).timestamp()
            except Exception as e:
                logger.exception(
                    f'Could not parse Book from date {bf_date}')

        return {
            'id': f'{comp_date}-{raw_html_description.text}',
            'gender': raw_gender.find('img', alt=True)['alt'],
            'comp_date': comp_date,
            'html_description': raw_html_description.text,
            'action': action,
            'notes': notes,
            'bookings_close_by': bookings_close_by,
            'book_from': book_from
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
