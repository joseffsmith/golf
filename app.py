from typing import Dict
from dotenv import load_dotenv
import logging

from MasterScoreboard import MasterScoreboard
from Parser import Parser
from Library import Library, DB
from datetime import datetime

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# TODO add all needed classes to session variable
# set up logging with papertrail, email on exceptions
# handle comps already open/ check for spaces available

load_dotenv()


def scrape_and_save_comps(parsed_test_comps=None):
    lib = Library()
    current_comps = {c['id']: c for c in lib.read('curr_comps', default=[])}
    parsed_comps = parsed_test_comps
    if not parsed_test_comps:
        ms = MasterScoreboard()
        ms.auth()
        content = ms.list_comps()
        parsed_comps = {p['id']: p for p in Parser().parse_comps(content)}
        logger.info(f'{len(parsed_comps)} fresh comps')

    if len(current_comps) == 0:
        logger.info(
            f"No current comps, saving {len(parsed_comps)} parsed comps as current")
        lib.write('curr_comps', list(parsed_comps.values()))
        return parsed_comps

    skipped = []
    saving = []
    removed = []
    for id, pc in parsed_comps.items():
        if id not in current_comps:
            # new comp we haven't seen before
            # or the id has changed since we last viewed it
            if 'Book from' not in pc['notes']:
                logger.exception(
                    f"New Comp without 'book from', don't like it - {id}, skipping")
                skipped.append(pc)
                continue

            logger.info(
                f"New comp with book from, adding to list - {pc['html_description']}")
            saving.append(pc)
            continue

        cc = current_comps[id]

        if cc == pc:
            logger.info(
                f"No change in comp, saving as normal - {pc['html_description']}")
            saving.append(pc)
            continue

        logger.info(
            f"Change detected in comp, patching current comp with new data - {pc['html_description']}")
        for key, value in pc.items():
            if not value:
                continue
            if key == 'book_from' and value is None:
                continue
            if cc[key] == value:
                continue
            logger.info(
                f"Key - {key}, Newval - {pc[key]}, Oldval - {cc[key]}")
            cc[key] = value
        saving.append(cc)

    removed = [c for c in current_comps.values() if c not in saving]

    bookings: Dict = lib.read('bookings')
    keep_bookings = {b_id: booking for b_id, booking in bookings.items(
    ) if booking['comp']['id'] in parsed_comps.keys()}
    lib.write('bookings', keep_bookings)
    logger.info(f'Removed bookings: {bookings.keys() - keep_bookings.keys()}')

    logger.info(
        f"Finished with comps, parsed: {len(parsed_comps)} saving: {len(saving)}, skipped: {len(skipped)}, removed: {len(removed)}")

    lib.write('curr_comps', saving)
    return saving


def scrape_and_save_comps_db():
    db = DB()
    db_comps = db.client.golf.comps
    current_comps = {c['id']: c for c in list(db_comps.find())}

    ms = MasterScoreboard()
    ms.auth()
    content = ms.list_comps()
    parsed_comps = {p['id']: p for p in Parser().parse_comps(content)}
    logger.info(f'{len(parsed_comps)} parsed comps')

    if db.client.golf.comps.count_documents({}) == 0:
        logger.info(
            f"No current comps, saving {len(parsed_comps)} parsed comps as current")
        db_comps.insert_many(list(parsed_comps.values()))
        return parsed_comps

    skipped = []
    saving = []
    removed = []
    for id, pc in parsed_comps.items():
        if id not in current_comps:
            # new comp we haven't seen before
            # or the id has changed since we last viewed it
            if 'Book from' not in pc['notes']:
                logger.exception(
                    f"New Comp without 'book from', don't like it - {id}, skipping")
                skipped.append(pc)
                continue

            logger.info(
                f"New comp with book from, adding to list - {pc['html_description']}")
            saving.append(pc)
            continue

        cc = current_comps[id]

        del cc['_id']

        if cc == pc:
            logger.info(
                f"No change in comp, saving as normal - {pc['html_description']}")
            saving.append(pc)
            continue

        logger.info(
            f"Change detected in comp, patching current comp with new data - {pc['html_description']}")
        for key, value in pc.items():
            if not value:
                continue
            if key == 'book_from':
                continue
            if cc[key] == value:
                continue
            logger.info(
                f"Key - {key}, Newval - {pc[key]}, Oldval - {cc[key]}")
            cc[key] = value
        saving.append(cc)

    removed = [c for c in current_comps.values() if c not in saving]

    for comp in saving:
        saved = db.client.golf.comps.replace_one(
            {'id': comp['id']}, comp, upsert=True)

    for comp in removed:
        deleted = db.client.golf.comps.delete_one({'id': comp['id']})
        bookings_removed = db.client.golf.bookings.delete_many(
            {'comp': {'id': comp['id']}})

    return saved


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
            time.sleep(.1)
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
            time = v.split(' ')[0]
            if time == t and slot_page_data.get(f"BlockNumAvailable_{k.split('_')[1]}") >= str(len(partner_ids)):
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
