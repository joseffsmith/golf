
# def add_job(comp, times, player_ids):
#     lib = Library()
#     current_jobs = lib.read('jobs')
#     for job in current_jobs:
#         if job['comp'] == comp:
#             raise Exception('Booking already made for existing comp')

#     current_jobs.append({
#         'comp': comp,
#         'times': times,
#         'player_ids': player_ids
#     })

#     lib.write('jobs')


# def scrape_players():
#     lib = Library(live=LIVE)
#     parser = Parser()
#     parsed_players = lib.read('players')
#     if LIVE:
#         ms = MasterScoreboard()
#         content = ms.get_partners()
#         parsed_players = parser.partner_ids(content)
#     print('hello')
#     lib.write('players', parsed_players)


# def book_job(comp, preferred_times, partner_ids):
#     # assumes that the comp is live
#     # time in 16:00 format, 10 min incs
#     # need correct id_number of partners

#     ms = MasterScoreboard()
#     ms.auth()
#     parser = Parser()

#     # all the time booking slots
#     raw_slots_available = ms.select_comp(comp['action'])

#     slot_page_data = parser.booking_page(raw_slots_available)
#     block_id_pair = {k: v for k, v in slot_page_data.items() if
#                      v.split(' ')[0] in preferred_times}

#     raw_partner_choosing = ms.select_slot(block_id_pair, slot_page_data)
#     partner_page_data, num_partners = parser.select_partner_page(
#         raw_partner_choosing)

#     if len(partner_ids) != num_partners:
#         raise Exception("Not right amount of players")

#     booked = ms.select_partners(partner_ids, partner_page_data)
#     return booked
