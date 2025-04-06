import { useState } from 'react'
import './App.css'
import axios from 'axios'

function App() {
  // State to hold the input value
  const [animeName, setAnimeName] = useState('');

  // State to hold the fetched data
  const [data, setData] = useState<any[]>([]);

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
            className="flex border p-2 rounded-lg"
            value={animeName}
            onChange={handleInputChange}
          />
          <button type="submit" value="SUBMIT" className="flex ml-2 py-2 px-4 border rounded-lg active:bg-white">GO</button>
        </form>
        <div className="p-4">
          {data && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-6">
              {data.map((item: any) => (
                <a
                  key={item.anime_id}
                  href={item.site_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex flex-col items-center hover:opacity-80 transition"
                >
                  <img
                    src={item.image_url}
                    alt={item.anime_name}
                    className="w-full h-auto rounded-lg shadow-md"
                  />
                  <span className="mt-2 text-center text-sm font-medium">
                    {item.anime_name}
                  </span>
                  <span className="mt-1 text-center text-xs text-gray-500">
                    {"Similarity: " + item.similarity}
                  </span>
                </a>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  )
}

export default App
