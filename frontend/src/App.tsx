import React, { FunctionComponent, createContext, useContext } from 'react'
import { observer } from 'mobx-react-lite'
import { makeAutoObservable, runInAction } from 'mobx'

const App: FunctionComponent = () => {
  return (
    <StoreContext.Provider value={new Store()}>
      <List />
    </StoreContext.Provider>
  )
}

const List: FunctionComponent = observer(() => {
  const store = useContext(StoreContext)
  console.log(store!.comps)
  return (
    <table>
      <tbody>
        <tr><th>Gender</th><th>Comp date</th><th>Description</th><th>Notes</th></tr>
        {store!.comps.map(c => <Competition comp={c} />)}
      </tbody>
    </table>
  )
})

const Competition: FunctionComponent<{ comp: Comp }> = ({ comp }) => {
  return <tr>
    <td>{comp.gender}</td>
    <td>{new Date(comp.date * 1000).toLocaleDateString()}</td>
    <td>{comp.html_description}</td>
    <td>{comp.notes}</td>
  </tr>
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

  async comps() {
    const response = await fetch(`${this.url}comps/`, { headers: this.headers })
    if (!(response.ok && response.status === 200)) {
      console.log('error retrieving comps')
      return []
    }
    const { comps } = await response.json()
    return comps
  }
}

type Comp = {
  date: number,
  gender: string,
  notes: string,
  action: string,
  html_description: string
}
class Store {
  comps: Comp[] = []
  api: API
  constructor() {
    makeAutoObservable(this)
    this.api = new API()
    this.set_comps()
  }

  async set_comps() {
    const data = await this.api.comps()
    runInAction(() => {
      this.comps = data.comps
    })
  }
}
const StoreContext = createContext<Store | null>(null)
export default App
