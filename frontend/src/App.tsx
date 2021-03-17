import React, { FunctionComponent, createContext, useContext } from 'react'
import { observer } from 'mobx-react-lite'
import { makeAutoObservable, runInAction, toJS } from 'mobx'

const App: FunctionComponent = () => {
  return (
    <StoreContext.Provider value={new Store()}>
      <List />
    </StoreContext.Provider>
  )
}

const List: FunctionComponent = observer(() => {
  const store = useContext(StoreContext)
  console.log(toJS(store!.players))
  return (
    <table>
      <tbody>
        <tr>
          <th>Gender</th>
          <th>Comp date</th>
          <th>Booking opens</th>
          <th>Booking closes</th>
          <th>Notes</th>
          <th>Description</th>
        </tr>
        {store!.comps.map(c => <Competition key={c.id} comp={c} />)}
      </tbody>
    </table>
  )
})

const Competition: FunctionComponent<{ comp: Comp }> = ({ comp }) => {
  return <tr>
    <td>{comp.gender}</td>
    <td>{formatDateTime(comp.comp_date)}</td>
    <td>{formatDateTime(comp.book_from, true)}</td>
    <td>{formatDateTime(comp.bookings_close_by, true)}</td>
    <td>{comp.notes}</td>
    <td>{comp.html_description}</td>

  </tr>
}

const formatDateTime = (time: number | null, include_time = false): string => {
  if (!time) {
    return ''
  }
  const t = new Date(time * 1000).toLocaleTimeString()
  const d = new Date(time * 1000).toLocaleDateString()
  return include_time ?
    `${t}-${d}`
    : d
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
    return fetch(`${this.url}scheduler/booking/`, { headers: this.headers })
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
