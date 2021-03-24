import React, { FunctionComponent, createContext, useContext, useState, ChangeEvent, MouseEventHandler, useEffect } from 'react'
import { observer } from 'mobx-react-lite'
import { makeAutoObservable, runInAction } from 'mobx'
import netlifyAuth from './netlifyAuth.js'
import { User } from 'netlify-identity-widget'
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

  let [loggedIn, setLoggedIn] = useState(netlifyAuth.isAuthenticated)
  let [user, setUser] = useState<User>()
  let login = () => {
    netlifyAuth.authenticate((user: any) => {
      setLoggedIn(!!user)
      setUser(user)
      // @ts-ignore
      netlifyAuth.closeModal()
    })
  }

  let logout = () => {
    netlifyAuth.signout(() => {
      setLoggedIn(false)
      setUser(undefined)
    })
  }

  useEffect(() => {
    netlifyAuth.initialize((user: any) => {
      setLoggedIn(!!user)
    })
  }, [loggedIn])

  return <header><nav>
    <div id='netlify-modal' data-netlify-identity-menu></div>
    {user}
    {loggedIn}
  </nav></header>
})

const Comps: FunctionComponent = observer(() => {
  const store = useContext(StoreContext)
  return (<>
    {store!.comps.map((c, idx) => <Competition idx={idx} key={c.id} comp={c} booking={store?.bookings.find(b => b.comp.id === c.id)} players={store!.players} />)}
  </>)
})

const Competition: FunctionComponent<{ idx: number, comp: Comp, booking: Booking | undefined, players: { [id: string]: string } }> = ({ idx, comp, booking, players }) => {
  const store = useContext(StoreContext)
  const hours = ['07', '08', '09', '10', '11', '12', '13', '14', '15', '16']
  const minutes = ['00', '10', '20', '30', '40', '50']

  const [tee_times, setTeeTimes] = useState<Array<string>>(['empty'])
  const [partners, setPartners] = useState<Array<string>>(["101:~:Griffith, Rhys "])
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
  const handleSetPartner = (e: ChangeEvent<HTMLSelectElement>) => {
    const partners = document.querySelectorAll(`#comp-${idx} .partners`)
    const ps: string[] = []
    partners.forEach((p: any) => {
      ps.push(p.value)
    })
    setPartners(ps)
  }
  const handelSubmitJob = (e: React.MouseEvent) => {
    e.preventDefault()
    store?.api.book_comp(comp.id, tee_times.filter(t => t !== 'empty'), partners)

  }

  return <details open={process.env['NODE_ENV'] === 'development'}>
    <summary>
      {formatDateTime(comp.comp_date)}{booking && `, ${booking.booking_time}-${booking.player_ids.map(p_id => players[p_id])}`}
      <p><sub>{comp.html_description}</sub></p>
    </summary>
    <small>Notes: {comp.notes}</small><br />
    <small>Booking opens: {formatDateTime(comp.book_from, true)}</small>

    <form id={`comp-${idx}`}>
      Tee time:<small><br />All of these slots may not be available on the day, set more than one, order matters</small>
      {tee_times.map((t, idx) => {
        return <select className='tee-time' key={idx} onChange={handleSetTeeTime}>
          <option value='empty'>No time</option>
          {hours.map(h => minutes.map(m => <option value={h + ':' + m}>{h + ':' + m}</option>)).flat()}
        </select>
      })}
      <label>
        Partners:<small><br />Order matters, for example, with a 2 ball, Rhys is the default, swap him for someone else if necessary</small>
        {partners.map(p => {
          return <select className='partners' key={p} onChange={handleSetPartner}>
            {Object.entries(store?.preferred_players!).sort((a, b) => {
              const [keya, vala] = a
              const [keyb, valb] = b
              if (vala < valb) {
                return -1
              }
              if (vala > valb) {
                return 1
              }
              return 0
            }).map(v => {
              const [key, val] = v
              return <option key={`${key}-${val}`} value={key}>{val}</option>
            })}
            {Object.entries(players).filter(v => {
              const [key, val] = v
              if (store?.preferred_players.hasOwnProperty(key)) {
                return false
              }
              return true
            }).sort((a, b) => {
              const [keya, vala] = a
              const [keyb, valb] = b
              if (vala < valb) {
                return -1
              }
              if (vala > valb) {
                return 1
              }
              return 0
            }).map(v => {
              const [key, val] = v
              return <option key={`${key}-${val}`} value={key}>{val}</option>
            })}
          </select>
        })}
      </label>
      <button onClick={handelSubmitJob}>Book</button>
    </form>
  </details>
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
    this.headers.set('X_MS_JS_API_KEY', API_SECRET)
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

  book_comp(comp_id: string, booking_times: string[], player_ids: string[]) {
    return fetch(`${this.url}scheduler/booking/`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ comp_id, booking_times, player_ids })
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
  booking_time: string,
  player_ids: string[],
  booked: boolean
}

class Store {
  comps: Comp[] = []
  bookings: Booking[] = []
  players: { [id: string]: string } = {}
  preferred_players = {
    "101:~:Griffith, Rhys ": 'Rhys',
    "61:~:Davies, Jeff ": 'Jeff',
    "26:~:Brown, Tony Paul ": 'Tony',
    "141:~:Jenkins, Andrew ": 'Andy Jenkins',
  }
  api: API
  constructor() {
    makeAutoObservable(this)
    this.api = new API()
    this.set_comps()
    this.set_bookings()
    this.set_players()
  }

  async set_comps() {
    const data = await this.api.get('curr_comps/')
    runInAction(() => {
      this.comps = data.comps
    })
  }
  async set_bookings() {
    const data = await this.api.get('curr_bookings/')
    runInAction(() => {
      this.bookings = data.bookings
    })
  }
  async set_players() {
    const data = await this.api.get('curr_players/')
    runInAction(() => {
      this.players = data.players
    })
  }
}
const StoreContext = createContext<Store | null>(null)
export default App
