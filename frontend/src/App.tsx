// import { useState } from 'react'
import './App.css'

function App() {

  return (
    <>
      <header className="text-4xl pb-4">Anime Similarity Searcher</header>
      <main>
        <form className="m-2">
          <label className="text-xl mx-2">Search</label>
          <input type="text" placeholder="Anime name" className="border p-2" /><br /><br />
          <input type="submit" value="Submit" className="py-1 px-4 m-2 border" />
        </form>
        <div>
          
        </div>
      </main>
    </>
  )
}

export default App
