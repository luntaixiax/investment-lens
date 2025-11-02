import './App.css'
import { useEffect, useState } from 'react'

import axios from 'axios'

function App() {

  const [welcome, setWelcome] = useState('')

  useEffect(() => {
    axios.get('/api/').then((res) => {
      setWelcome(res.data)
    })
  }, [])

  return (
    <>
      <h1>{welcome}</h1>
    </>
  )
}

export default App
