import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import './mvp.css'
import App from './App'
import netlifyIdentity from 'netlify-identity-widget'
import { configure } from "mobx"

configure({ isolateGlobalState: true })

netlifyIdentity.init({ // defaults to document.body
  locale: 'en' // defaults to 'en'
})

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
)

