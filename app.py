from typing import Dict
import bs4
from dotenv import load_dotenv
import logging
import time

# from Parser import Parser
# from Library import Library, DB
from datetime import datetime
import os
from supabase import create_client, Client
from urllib.parse import parse_qs, urlparse
from dateutil.parser import parse

from intelligent import login

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO add all needed classes to session variable
# set up logging with papertrail, email on exceptions
# handle comps already open/ check for spaces available

load_dotenv()


def scrape_and_save_comps_db():
    PASSWORD = os.getenv('INT_PASSWORD')
    BASE_URL = os.getenv('INT_BASE_URL')
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    session = login(PASSWORD)
    resp = session.get(BASE_URL + '/competition.php?time=future')
    b = bs4.BeautifulSoup(resp.content, features='html.parser')
    rows = b.find_all('tr')
    to_upsert = {}
    for row in rows[1:]:
        fav, comp, comp_date, comp_in, booking_opts, cal = row.find_all(
            'td')
        gender = 'Ladies' if comp.text.startswith('Ladies') else 'Male'
        gender = 'Junior' if comp.text.startswith('Junior') else gender
        params = comp.find('a').attrs['href']
        compDate = parse(comp_date.text)
        if compDate < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            raise Exception('Cannot have comp in the past')

        data = {
            'comp_id': parse_qs((urlparse(params).query))['compid'][0],
            'gender': gender,
            'comp_date': compDate.isoformat(),
            'html_description': comp.text,
        }
        # if there's an action we can book straight away
        clickable = booking_opts.find('a')
        if clickable:
            data['action'] = clickable.attrs['href']

        if 'Signup Closes' in booking_opts.text:
            # comp open, fill in bookings_close_by
            data['bookings_close_by'] = parse(booking_opts.text.split(
                'Signup Closes')[-1].strip().split('at')[-1].strip().rstrip(')')).isoformat()

        if 'Signup Opens' in booking_opts.text:
            data['book_from'] = parse(booking_opts.text.split(
                'Signup Opens')[-1].strip().split('at')[-1].strip().rstrip(')')).isoformat()

        to_upsert[data['comp_id']] = data

    resp = supabase.table('comps').select('comp_id').execute()
    comp_ids = [c['comp_id'] for c in resp.data]

    to_update = []
    to_insert = []

    for comp_id, data in to_upsert.items():
        if comp_id in comp_ids:
            to_update.append(data)
        else:
            to_insert.append(data)

    ins_resp = supabase.table('comps').insert(to_insert).execute()
    print(ins_resp)

    upd_resp = supabase.table('comps').update(to_update).execute()
    print(upd_resp)

    return


def scrape_and_save_players(parsed_test_players=None):
    lib = Library()
    parsed_players = parsed_test_players
    if not parsed_test_players:
        parser = Parser()
        ms = MasterScoreboard()
        content = ms.get_partners()
        parsed_players = parser.partner_ids(content)

    lib.write('players', parsed_players)
    logger.info(f'players: ${len(parsed_players)}')
    return parsed_players


def book_job(comp, preferred_times, partner_ids=[], username=None, password=None, wait=None):
    # assumes that the comp is live
    # time in 16:00 format, 10 min incs
    # need correct id_number of partners

    ms = MasterScoreboard(username=username, password=password)
    ms.auth()
    parser = Parser()
    lib = Library()

    if wait:
        logger.info(f'Checking for wait')
        while datetime.now() < wait:
            time.sleep(.01)
            logger.info(f'Waiting...')
            continue

    # all the time booking slots
    action = comp.get('action')
    if not action:
        comps = {c['id']: c for c in scrape_and_save_comps()}
        action = comps[comp['id']]['action']

    raw_slots_available = ms.select_comp(action)

    logger.info('Finding slots available for comp')
    slot_page_data = parser.select_slot_page(raw_slots_available)
    block_id_pair = {}
    for t in preferred_times:
        if block_id_pair:
            continue
        for k, v in slot_page_data.items():
            tim = v.split(' ')[0]
            if tim == t and slot_page_data.get(f"BlockNumAvailable_{k.split('_')[1]}") >= str(len(partner_ids)):
                block_id_pair[k] = v

    if not block_id_pair:
        raise Exception('No slots for times found')

    logger.info('block-id-pair: ', block_id_pair)

    if (len(block_id_pair.keys()) == 0):
        raise Exception('No slots available')

    logger.info(f'slots: {len(block_id_pair.keys())}')
    raw_partner_choosing = ms.select_slot(block_id_pair, slot_page_data)
    partner_page_data, num_partners = parser.select_partner_page(
        raw_partner_choosing)

    logger.info('Number of partners = ' + str(num_partners))
    logger.info('Selecting partners')

    new_ids = partner_ids[:num_partners]
    while len(new_ids) < 4:  # always send 4 partner ids
        new_ids.append('0')

    ms.select_partners(new_ids, partner_page_data)

    logger.info('BOOKED!!!')
    bookings = lib.read('bookings')
    booking = bookings.get(f"{username}-{comp['id']}")
    if booking:
        booking['booked'] = True
        bookings[f"{username}-{comp['id']}"] = booking
        lib.write('bookings', bookings)
    return
