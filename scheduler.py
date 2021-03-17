
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
