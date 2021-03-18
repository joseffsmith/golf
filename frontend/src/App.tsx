import React, { FunctionComponent, createContext, useContext, useState, ChangeEvent } from 'react'
import { observer } from 'mobx-react-lite'
import { makeAutoObservable, runInAction } from 'mobx'

const App: FunctionComponent = () => {
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
  return <header><nav>Logged in as A.Smith</nav></header>
})

const Comps: FunctionComponent = observer(() => {
  const store = useContext(StoreContext)
  return (<>
    {store!.comps.map(c => <Competition key={c.id} comp={c} booking={store?.bookings.find(b => b.comp.id === c.id)} players={store!.players} />)}
  </>)
})

const Competition: FunctionComponent<{ comp: Comp, booking: Booking | undefined, players: { [id: string]: string } }> = ({ comp, booking, players }) => {
  const hours = ['07', '08', '09', '10', '11', '12', '13', '14', '15', '16']
  const minutes = ['00', '10', '20', '30', '40', '50']

  const preferred_partners = ["101:~:Griffith, Rhys ", "61:~:Davies, Jeff ", "26:~:Brown, Tony Paul "]
  const [tee_times, setTeeTimes] = useState<Array<string>>(['empty'])
  const [partners, setPartners] = useState<Array<string>>(preferred_partners)
  const handleSetTeeTime = (e: ChangeEvent<HTMLSelectElement>) => {
    const fieldset = e.target.form![0]
    // const all_tees = tee_times.filter(e => e !== 'empty')
    // console.log(new_val, all_tees)
    // const set_tees = new Set(all_tees)

    // if (new_val !== 'empty') {
    //   set_tees.add(new_val)
    // }
    // setTeeTimes(['empty', ...Array.from(set_tees)])
  }
  const handleSetPartner = (e: ChangeEvent<HTMLSelectElement>) => {
  }
  return <details open={true}>
    <summary>
      {formatDateTime(comp.comp_date)}{booking && `, ${booking.booking_time}-${booking.player_ids.map(p_id => players[p_id])}`}
      <p><sub>{comp.html_description}</sub></p>
    </summary>
    <small>Notes: {comp.notes}</small><br />
    <small>Booking opens: {formatDateTime(comp.book_from, true)}</small>

    <form id={comp.id}>
      <fieldset>
        Tee time:<small><br />All of these slots may not be available on the day, set more than one, order matters</small>
        {tee_times.map(t => {
          return <select className='tee-time' key={t} onChange={handleSetTeeTime}>
            <option value='empty'>No time</option>
            {hours.map(h => minutes.map(m => <option value={h + ':' + m}>{h + ':' + m}</option>)).flat()}
          </select>
        })}
      </fieldset>
      <label>
        Partners:<small><br />Order matters, for example, with a 2 ball, Rhys is the default, swap him for someone else if necessary</small>
        {partners.map(p => {
          return <select key={p} onChange={handleSetPartner}>
            <option value={p}>{players[p]}</option>
            {Object.entries(players).map(v => {
              const [key, val] = v
              return <option key={`${key}-${val}`} value={key}>{val}</option>
            })}
          </select>
        })}
      </label>
      <button type='submit'>Book</button>
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

  book_comp(comp_id: string, booking_time: string, player_ids: number[]) {
    return fetch(`${this.url}scheduler/booking/`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ comp_id, booking_time, player_ids })
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
  player_ids: number[],
  booked: boolean
}

class Store {
  comps: Comp[] = []
  bookings: Booking[] = []
  players: { [id: string]: string } = {}
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
