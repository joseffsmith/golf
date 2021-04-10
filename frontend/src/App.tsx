import React, { FunctionComponent, createContext, useContext, useState, ChangeEvent, MouseEventHandler, useEffect } from 'react'
import { observer } from 'mobx-react-lite'
import { makeAutoObservable, runInAction, toJS } from 'mobx'
// import netlifyAuth from './netlifyAuth.js'
// import { User } from 'netlify-identity-widget'
import { configure } from "mobx"


const App: FunctionComponent = () => {
  configure({ isolateGlobalState: true })
  return (
    <StoreContext.Provider value={new Store()}>
      <main>
        <Header />
        <Comps />
      </main>
    </StoreContext.Provider>
  )
}

const Header: FunctionComponent = observer(() => {
  const store = useContext(StoreContext)


  // let [loggedIn, setLoggedIn] = useState(netlifyAuth.isAuthenticated)
  // let [user, setUser] = useState<User>()
  // let login = () => {
  //   netlifyAuth.authenticate((user: any) => {
  //     setLoggedIn(!!user)
  //     setUser(user)
  //     // @ts-ignore
  //     netlifyAuth.closeModal()
  //   })
  // }

  // let logout = () => {
  //   netlifyAuth.signout(() => {
  //     setLoggedIn(false)
  //     setUser(undefined)
  //   })
  // }

  // useEffect(() => {
  //   netlifyAuth.initialize((user: any) => {
  //     setLoggedIn(!!user)
  //   })
  // }, [loggedIn])


  return <header><nav>

    <ul>
      {Object.entries(store.bookings).map(b => <li key={b[0]}>{JSON.stringify(b[1])}</li>)}
    </ul>
  </nav></header>
})

const Comps: FunctionComponent = observer(() => {
  const store = useContext(StoreContext)
  return (<>
    {store!.comps.map((c, idx) => <Competition
      idx={idx}
      key={c.id}
      comp={c}
      players={store!.players}
    />)}
  </>)
})

const Competition: FunctionComponent<{ idx: number, comp: Comp, players: { [id: string]: string } }> = observer(({ idx, comp, players }) => {
  const store = useContext(StoreContext)
  const bookings = store.bookings.filter(b => b.comp.id === comp.id)

  const hours = ['07', '08', '09', '10', '11', '12', '13', '14', '15', '16']
  const minutes = ['00', '10', '20', '30', '40', '50']


  const [tee_times, setTeeTimes] = useState<Array<string>>(['empty'])
  const [partner1, setPartner1] = useState("101:~:Griffith, Rhys ")
  const [partner2, setPartner2] = useState(null)
  const [partner3, setPartner3] = useState(null)
  const [username, changeUsername] = useState("254:~:Smith, Anthony ")
  const [password, changePassword] = useState('')

  const setPassword = (val: string) => {
    changePassword(val)
    store.password_is_legit = false
  }

  const setUsername = (val: string) => {
    setPassword('')
    changeUsername(val)
  }

  const handleSetTeeTime = (e: ChangeEvent<HTMLSelectElement>) => {
    const times = document.querySelectorAll(`#comp-${idx} .tee-time`)
    const ts: string[] = []
    times.forEach((t: any) => {
      if (t.value !== 'empty') {
        ts.push(t.value)
      }
    })
    setTeeTimes(['empty', ...ts])
  }
  const handleSubmitJob = (e: React.MouseEvent) => {
    e.preventDefault()
    store?.book_comp(
      comp.id,
      tee_times.filter(t => t !== 'empty'),
      [partner1, partner2, partner3].filter(Boolean).filter(v => v !== '-1:~:Select Your Name'),
      username,
      password
    )
    setPassword('')
  }

  const testPassword = (e) => {
    e.preventDefault()
    store.test_pass(username, password)
  }

  return (
    <details open={process.env['NODE_ENV'] === 'development'}>
      <summary>
        {formatDateTime(comp.comp_date)}{bookings.length && `, ${bookings[0].booking_times}-${bookings[0].player_ids.map(p_id => players[p_id])}`}
        <p><sub>{comp.html_description}</sub></p>
      </summary>
      <small>Notes: {comp.notes}</small><br />
      <small>Booking opens: {formatDateTime(comp.book_from, true)}</small>

      <form id={`comp-${idx}`}>
        Tee time:<small><br />All of these slots may not be available on the day, set more than one, order matters</small>
        {tee_times.map((t, idx) => {
          return <select className='tee-time' key={t} onChange={handleSetTeeTime}>
            <option value='empty'>No time</option>
            {hours.map(h => minutes.map(m => <option key={`${h}:${m}`} value={`${h}:${m}`}>{`${h}:${m}`}</option>)).flat()}
          </select>
        })}
        {tee_times.length > 1 && <>
          <label>
            Book as:
            <Partner partner={username} setPartner={setUsername} current_players={[username]} />
          </label>
          <label>
            Password
            <input value={password} onChange={e => setPassword(e.target.value)} />
            <button onClick={testPassword}>Test password (Must do before booking)</button>
          </label>
          <label>
            Partners:<small><br />Order matters, for example, with a 2 ball, Rhys is the default, swap him for someone else if necessary</small>
            <Partner partner={partner1} setPartner={setPartner1} current_players={[username, partner1, partner2, partner3]} />
            <Partner partner={partner2} setPartner={setPartner2} current_players={[username, partner1, partner2, partner3]} />
            <Partner partner={partner3} setPartner={setPartner3} current_players={[username, partner1, partner2, partner3]} />
          </label>
          {store.password_is_legit && <button onClick={handleSubmitJob}>Book</button>}
        </>}
      </form>
    </details >
  )
})

const Partner = ({ current_players, partner, setPartner }) => {
  const store = useContext(StoreContext)
  const players = store.players!
  return (
    <select className='partners' onChange={e => setPartner(e.target.value)}>
      <option key={'selected'} value={partner}>{players[partner]}</option>
      <PlayerOptions current_players={current_players} players={players} />
    </select >
  )
}

const PlayerOptions = ({ current_players, players }) => {
  const preferred_players = [
    "254:~:Smith, Anthony ",
    "101:~:Griffith, Rhys ",
    "61:~:Davies, Jeff ",
    "26:~:Brown, Tony Paul ",
    "141:~:Jenkins, Andrew ",
    "1401:~:Griffith, Steffan ",
  ]
  return (<>
    {Object.entries(players).filter(v => {
      const [key, val] = v
      if (current_players.includes(key)) {
        return false
      }
      return true
    }).sort((a, b) => {
      const [keya, vala] = a
      const [keyb, valb] = b
      if (preferred_players.includes(keya)) { return -1 }
      if (preferred_players.includes(keyb)) { return 1 }
      if (vala < valb) { return -1 }
      if (vala > valb) { return 1 }
      return 0
    }).map(v => {
      const [key, val] = v
      return <option key={`${key}-${val}`} value={key}>{val}</option>
    })}
  </>)
}

const formatDateTime = (time: number | null, include_time = false): string => {
  if (!time) {
    return ''
  }
  const dt = new Date(time * 1000)
  return include_time ?
    dt.toDateString() + ' - ' + dt.toLocaleTimeString()
    : dt.toDateString()
}

class API {
  headers: Headers
  url: string
  constructor() {
    this.headers = new Headers()
    const API_SECRET = process.env['REACT_APP_API_SECRET']
    const API_URL = process.env['REACT_APP_API_URL']
    if (!API_SECRET) { throw Error('No access to API') }
    if (!API_URL) { throw Error('No API url set') }
    this.headers.set('X-MS-JS-API-KEY', API_SECRET)
    this.headers.set('Content-Type', 'application/json')
    this.url = API_URL
  }

  async get(url: string) {
    const response = await fetch(`${this.url}${url}`, { headers: this.headers })
    if (!(response.ok && response.status === 200)) {
      console.error(`error retrieving ${url}`)
      return []
    }
    return await response.json()
  }
  async post(url: string) {
    const response = await fetch(`${this.url}${url}`, {
      headers: this.headers,
      method: 'POST',
    })
    if (!(response.ok && response.status === 200)) {
      console.error(`error retrieving ${url}`)
      return []
    }
    return await response.json()
  }

  async test_pass(username: string, password: string) {
    return fetch(`${this.url}/test_pass/`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ username, password })
    })
      .then(response => {
        if (!response.ok) {
          return false
        }
        return true
      })
  }

  book_comp(comp_id: string, booking_times: string[], player_ids: string[], username, password) {
    return fetch(`${this.url}/scheduler/booking/`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ comp_id, booking_times, player_ids, username, password })
    })
      .then(response => {
        if (!response.ok) {
          console.error('Error booking comp')
          alert('Error booking comp, get in touch with joe, take a screenshot if you can')
        }
        return response
      })
      .then(d => {
        return d.json()
      })
  }
}

type Comp = {
  id: string,
  comp_date: number,
  gender: string,
  notes: string,
  action: string,
  html_description: string,
  book_from: number | null,
  bookings_close_by: number | null
}

type Booking = {
  comp: Comp,
  booking_times: string[],
  player_ids: string[],
  booked: boolean
}

class Store {
  comps: Comp[] = []
  bookings: Booking[] = []
  players: { [id: string]: string } = {}
  password_is_legit: Boolean = false

  api: API
  constructor() {
    makeAutoObservable(this)
    this.api = new API()
    this.set_comps()
    this.set_bookings()
    this.set_players()
  }

  async test_pass(username: string, pass: string) {
    const data = await this.api.test_pass(username, pass)
    runInAction(() => {
      this.password_is_legit = data
    })
  }

  async scrape_comps() {
    const data = await this.api.post('/scrape_comps/')
    runInAction(() => {
      this.comps = data.comps
    })
  }
  async set_comps() {
    const data = await this.api.get('/curr_comps/')
    runInAction(() => {
      this.comps = data.comps
    })
  }
  async book_comp(comp_id: string, booking_times: string[], player_ids: string[], username, password) {
    const data = await this.api.book_comp(comp_id, booking_times, player_ids, username, password)
    runInAction(() => {
      this.bookings = data.bookings
    })
  }
  async set_bookings() {
    const data = await this.api.get('/curr_bookings/')
    runInAction(() => {
      this.bookings = data.bookings
    })
  }
  async set_players() {
    const data = await this.api.get('/curr_players/')
    runInAction(() => {
      this.players = data.players
    })
  }
}
const StoreContext = createContext<Store | null>(null)
export default App
