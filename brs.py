import requests
import bs4
from pprint import pprint




def login():
    session = requests.Session()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
    session.headers = {'User-Agent': user_agent}
    resp = session.get('https://members.brsgolf.com/thevalehotelspa/login')

    b = bs4.BeautifulSoup(resp.content, features='html.parser')

    token = b.find(attrs={'id':'login_form__token'}).get('value')

    print('token: ', token)
    
    resp = session.post('https://members.brsgolf.com/thevalehotelspa/login', data={
        'login_form[username]': USERNAME,
        'login_form[password]': PASSWORD,
        'login_form[login]': '',
        'login_form[_token]': token
    })

    
    resp = session.get('https://members.brsgolf.com/thevalehotelspa/tee-sheet/data/1/2022/11/04')
    print(resp)
    print(resp.headers)
    pprint(resp.json())




if __name__ == '__main__':
    login()
