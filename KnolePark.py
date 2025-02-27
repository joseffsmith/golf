import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Literal
from urllib.parse import parse_qs

import bs4
import dateutil.parser as dateutils
import pytz
import requests
from dotenv import load_dotenv

from IntelligentGolf import getSystems, intLogin
from redis_helpers import get_redis_conn

bst = pytz.timezone('Europe/London')

load_dotenv()

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def bookJob(username, password, date, teeTime, wait_until):
    if wait_until:
        logger.info(f'Checking for wait')
        while pytz.UTC.localize(datetime.utcnow()) < wait_until:
            time.sleep(.01)
            logger.info(f'Waiting...')
            continue
    
    session = intLogin(username, password, "knole")
    
    teeTimes = getHtmlTeeTimes(username, password, date, session=session)
    
    try: 
        [formData] = [t for t in teeTimes if 'book' in t and t['book'] == teeTime]
    except ValueError:
        logger.error(f"Time {teeTime} not found in tee times")
        return
    
    bookSlot(username, password, formData, 1, session=session)



type FormData = Dict[Literal[
        "numslots", 
        "date", 
        "course", 
        "group", 
        "book",
        "2928a5c9ee030452e356c86636ac3a62c91a0cc1dc3dc7c32d0856d6cdac0e17"
        ], str]

def getHtmlTeeTimes(username, password, dateStr, session=None):
    """
    date fmt: 01-03-2025
    """
    if not session:
        logger.info("No session provided, logging in...")
        session = intLogin(username, password, "knole")
    
    logger.info("Getting tee times...")
    urls = getSystems()
    resp = session.get(urls['knole'] + "memberbooking/", params={
        "date": dateStr,
        "course": 1,
        "group": 1,
    })

    resp.raise_for_status()
    logger.info(f"Response: {resp.status_code}")
    content = resp.content
    
    soup = bs4.BeautifulSoup(content, 'html.parser')
    
    forms = soup.find_all("form")
    all_form_data: List[FormData] = []

    for form in forms:
        form_fields = {}
        
        # Process all input fields in the form
        for input_tag in form.find_all("input"):
            name = input_tag.get("name")
            if not name:
                continue  # skip inputs without a name
            
            input_type = input_tag.get("type", "text").lower()
            value = input_tag.get("value", "")
            
            # For radio buttons, only capture the checked one.
            if input_type == "radio":
                if input_tag.has_attr("checked"):
                    form_fields[name] = value
                # Optionally, you could store all options if needed.
            else:
                form_fields[name] = value

        all_form_data.append(form_fields)

    # Output the data in JSON format
    logger.info(f"Found {len(all_form_data)} forms for date {dateStr}")
    logger.info(f"times: {[f['book'] for f in all_form_data if 'book' in f]}")
    return all_form_data
    



def bookSlot(username: str, password: str, formData: FormData, numPlayers: int, session=None):
    # numslots: 2
    # date: 01-03-2025
    # course: 1
    # group: 1
    # book: 14:08:00
    # 2928a5c9ee030452e356c86636ac3a62c91a0cc1dc3dc7c32d0856d6cdac0e17: 114295d6506596e65212d45119b05938af6477618e4b7f6791f0709fbbf0d94d
    
    if not session:
        session = intLogin(username, password, "knole")
        
    urls = getSystems()
    logger.info(f"Booking slot: {formData['date']} {formData['book']} for {numPlayers} players")
    
    formData["numslots"] = str(numPlayers)
    
    resp = session.get(urls['knole'] + "memberbooking/", params=formData, allow_redirects=True)    
    resp.raise_for_status()
    
    
    