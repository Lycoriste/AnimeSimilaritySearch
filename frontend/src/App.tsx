import { useState } from 'react'
import './App.css'
import axios from 'axios'

function App() {
  // State to hold the input value
  const [animeName, setAnimeName] = useState('');

  // State to hold the fetched data
  const [data, setData] = useState(null);

  // Handle input change
  const handleInputChange = (e: any) => {
    setAnimeName(e.target.value);
  };

  // Handle form submission
  const handleSubmit = async (e: any) => {
    e.preventDefault(); // Prevent page reload
    try {
      const response = await axios.get(`http://localhost:8080/api/search?anime=${animeName}`);
      setData(response.data); // Update state with fetched data
      console.log(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <>
      <header className="flex text-4xl pb-4 justify-center">ANIME SIMILARITY SEARCH</header>
      <main>
        <form className="flex m-2 justify-center" onSubmit={handleSubmit}>
          <label className="flex items-center text-xl mx-2">SEARCH</label>
          <input 
            type="text" 
            placeholder="ANIME NAME" 
            className="flex border p-2"
            value={animeName}
            onChange={handleInputChange}
          />
          <input type="submit" value="SUBMIT" className="flex ml-2 py-2 px-4 border"/>
        </form>
        <div>
          {/* Render fetched data */}
          {data && (
            <div>
              <h2>Search Results:</h2>
              <pre>{JSON.stringify(data, null, 2)}</pre>
            </div>
          )}
        </div>
      </main>
    </>
  )
}

export default App
