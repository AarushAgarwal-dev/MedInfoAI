import React, { useState, useEffect } from 'react';
import { MapContainer } from 'react-leaflet/MapContainer';
import { TileLayer } from 'react-leaflet/TileLayer';
import { Marker } from 'react-leaflet/Marker';
import { Popup } from 'react-leaflet/Popup';
import 'leaflet/dist/leaflet.css';

const API = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

export default function Tools({ user }: { user: string }) {
  // Medicine Search
  const [search, setSearch] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);

  // Generic Finder
  const [generic, setGeneric] = useState('');
  const [genericResult, setGenericResult] = useState<any | null>(null);
  const [genericLoading, setGenericLoading] = useState(false);

  // Save for Future Purchase
  const [saved, setSaved] = useState<any[]>([]);
  const [saveLoading, setSaveLoading] = useState(false);
  const [saveError, setSaveError] = useState('');

  // Daily Essentials
  const [essentials, setEssentials] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [categoryMeds, setCategoryMeds] = useState<any[]>([]);
  const [essentialsLoading, setEssentialsLoading] = useState(false);

  // Kendra Finder
  const [kendras, setKendras] = useState<any[]>([]);
  const [kendraLoading, setKendraLoading] = useState(false);
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null);

  // AI Assistant
  const [aiMessages, setAiMessages] = useState<{role: string, content: string}[]>([]);
  const [aiInput, setAiInput] = useState('');
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    fetch(`${API}/users/saved/${user}`)
      .then(res => res.json())
      .then(data => setSaved(data.saved || []));
  }, [user]);

  useEffect(() => {
    fetch(`${API}/essentials/`)
      .then(res => res.json())
      .then(data => setEssentials(data.categories || []));
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setSearchLoading(true);
    setSearchResults([]);
    try {
      const res = await fetch(`${API}/medicines/search?q=${encodeURIComponent(search)}`);
      const data = await res.json();
      setSearchResults(data.results || []);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleGeneric = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenericLoading(true);
    setGenericResult(null);
    try {
      const res = await fetch(`${API}/medicines/generic?name=${encodeURIComponent(generic)}`);
      const data = await res.json();
      setGenericResult(data);
    } finally {
      setGenericLoading(false);
    }
  };

  const handleSave = async (medicineId: number) => {
    setSaveLoading(true);
    setSaveError('');
    try {
      const res = await fetch(`${API}/users/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user, medicine_id: medicineId })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Error');
      // Refresh saved list
      const savedRes = await fetch(`${API}/users/saved/${user}`);
      const savedData = await savedRes.json();
      setSaved(savedData.saved || []);
    } catch (err: any) {
      setSaveError(err.message);
    } finally {
      setSaveLoading(false);
    }
  };

  const handleCategory = async (cat: string) => {
    setSelectedCategory(cat);
    setEssentialsLoading(true);
    setCategoryMeds([]);
    try {
      const res = await fetch(`${API}/essentials/${cat}`);
      const data = await res.json();
      setCategoryMeds(data.medicines || []);
    } finally {
      setEssentialsLoading(false);
    }
  };

  const handleFindKendras = async () => {
    setKendraLoading(true);
    setKendras([]);
    if (!userLocation) {
      navigator.geolocation.getCurrentPosition(
        pos => {
          setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        },
        () => {
          setUserLocation({ lat: 28.6139, lng: 77.2090 }); // Default to Delhi
        }
      );
      setKendraLoading(false);
      return;
    }
    try {
      const res = await fetch(`${API}/kendra/nearby?lat=${userLocation.lat}&lng=${userLocation.lng}`);
      const data = await res.json();
      setKendras(data.kendras || []);
    } finally {
      setKendraLoading(false);
    }
  };

  const handleAiSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiInput.trim()) return;
    setAiLoading(true);
    setAiMessages(msgs => [...msgs, { role: 'user', content: aiInput }]);
    try {
      const res = await fetch(`${API}/assistant/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: aiInput })
      });
      const data = await res.json();
      setAiMessages(msgs => [...msgs, { role: 'assistant', content: data.response }]);
      setAiInput('');
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-16">
      <section className="bg-white rounded-2xl shadow-md p-8 mb-8 border border-blue-100">
        <h2 className="text-2xl font-extrabold mb-6 text-gray-900 border-b border-blue-200 pb-3">1. Search for <span className='text-blue-700'>Medicine</span></h2>
        <form onSubmit={handleSearch} className="flex gap-2 mb-2">
          <input value={search} onChange={e => setSearch(e.target.value)} className="border rounded px-2 py-1 flex-1" placeholder="Enter medicine name..." />
          <button type="submit" className="bg-blue-600 text-white px-4 py-1 rounded">Search</button>
        </form>
        {searchLoading && <div>Loading...</div>}
        {searchResults.length > 0 && (
          <ul className="border rounded p-2 bg-white">
            {searchResults.map(m => (
              <li key={m.id} className="py-1 border-b last:border-b-0 flex justify-between items-center">
                <span><b>{m.name}</b> <span className="text-gray-500">({m.generic})</span> <span className="text-sm text-gray-400">{m.company}</span> <span className="text-green-700 font-semibold">₹{m.price}</span></span>
                <button onClick={() => handleSave(m.id)} className="ml-4 bg-green-600 text-white px-2 py-1 rounded text-sm" disabled={saveLoading}>Save</button>
              </li>
            ))}
          </ul>
        )}
        {saveError && <div className="text-red-600 text-sm mt-2">{saveError}</div>}
      </section>

      <section className="bg-white rounded-2xl shadow-md p-8 mb-8 border border-purple-100">
        <h2 className="text-2xl font-extrabold mb-6 text-gray-900 border-b border-purple-200 pb-3">2. Find <span className='text-purple-700'>Generic Name</span> &amp; <span className='text-pink-700'>Compare Prices</span></h2>
        <form onSubmit={handleGeneric} className="flex gap-2 mb-2">
          <input value={generic} onChange={e => setGeneric(e.target.value)} className="border rounded px-2 py-1 flex-1" placeholder="Enter brand or medicine name..." />
          <button type="submit" className="bg-blue-600 text-white px-4 py-1 rounded">Find</button>
        </form>
        {genericLoading && <div>Loading...</div>}
        {genericResult && genericResult.generic && (
          <div className="bg-white border rounded p-2">
            <div><b>Generic Name:</b> {genericResult.generic}</div>
            <div className="mt-2"><b>Brands & Prices:</b></div>
            <ul>
              {genericResult.brands.map((b: any) => (
                <li key={b.id} className="py-1 border-b last:border-b-0">
                  <b>{b.name}</b> <span className="text-gray-500">{b.company}</span> <span className="text-green-700 font-semibold">₹{b.price}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {genericResult && genericResult.error && (
          <div className="text-red-600">{genericResult.error}</div>
        )}
      </section>

      <section className="bg-white rounded-2xl shadow-md p-8 mb-8 border border-green-100">
        <h2 className="text-2xl font-extrabold mb-6 text-gray-900 border-b border-green-200 pb-3">3. <span className='text-green-700'>Saved Medicines</span> for Future Purchase</h2>
        {saveLoading && <div>Updating saved list...</div>}
        {saved.length === 0 ? <div className="text-gray-500">No medicines saved yet.</div> : (
          <ul className="border rounded p-2 bg-white">
            {saved.map(m => (
              <li key={m.id} className="py-1 border-b last:border-b-0">
                <b>{m.name}</b> <span className="text-gray-500">({m.generic})</span> <span className="text-sm text-gray-400">{m.company}</span> <span className="text-green-700 font-semibold">₹{m.price}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="bg-white rounded-2xl shadow-md p-8 mb-8 border border-yellow-100">
        <h2 className="text-2xl font-extrabold mb-6 text-gray-900 border-b border-yellow-200 pb-3">4. <span className='text-yellow-600'>Daily Essentials</span></h2>
        <div className="flex flex-wrap gap-2 mb-2">
          {essentials.map(cat => (
            <button key={cat} onClick={() => handleCategory(cat)} className={`px-3 py-1 rounded border ${selectedCategory === cat ? 'bg-blue-600 text-white' : 'bg-white'}`}>{cat}</button>
          ))}
        </div>
        {essentialsLoading && <div>Loading...</div>}
        {selectedCategory && (
          <div>
            <div className="font-semibold mb-1">{selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)} Medicines:</div>
            {categoryMeds.length === 0 ? <div className="text-gray-500">No medicines found.</div> : (
              <ul className="border rounded p-2 bg-white">
                {categoryMeds.map(m => (
                  <li key={m.id} className="py-1 border-b last:border-b-0">
                    <b>{m.name}</b> <span className="text-gray-500">({m.generic})</span> <span className="text-sm text-gray-400">{m.company}</span> <span className="text-green-700 font-semibold">₹{m.price}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </section>

      <section className="bg-white rounded-2xl shadow-md p-8 mb-8 border border-blue-100">
        <h2 className="text-2xl font-extrabold mb-6 text-gray-900 border-b border-blue-200 pb-3">5. <span className='text-blue-700'>Nearest Jan Aushadi Kendra Finder</span></h2>
        <button onClick={handleFindKendras} className="bg-blue-600 text-white px-4 py-1 rounded mb-2">Find Kendras Near Me</button>
        <div className="w-full h-64 rounded border mb-2">
          {(userLocation || kendras.length > 0) && (
            <MapContainer center={[userLocation?.lat || 28.6139, userLocation?.lng || 77.2090]} zoom={11} style={{ height: '100%', width: '100%' }}>
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {userLocation && (
                <Marker position={[userLocation.lat, userLocation.lng]}>
                  <Popup>You are here</Popup>
                </Marker>
              )}
              {kendras.map(k => (
                <Marker key={k.id} position={[k.lat, k.lng]}>
                  <Popup>{k.name}</Popup>
                </Marker>
              ))}
            </MapContainer>
          )}
        </div>
        {kendraLoading && <div>Loading map and Kendras...</div>}
        {kendras.length > 0 && (
          <ul className="border rounded p-2 bg-white">
            {kendras.map(k => (
              <li key={k.id} className="py-1 border-b last:border-b-0">
                <b>{k.name}</b> <span className="text-gray-500">({k.lat}, {k.lng})</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="bg-white rounded-2xl shadow-md p-8 mb-8 border border-pink-100">
        <h2 className="text-2xl font-extrabold mb-6 text-gray-900 border-b border-pink-200 pb-3">6. <span className='text-pink-700'>Guided AI Assistant</span></h2>
        <div className="bg-white border rounded p-4 max-w-xl mx-auto">
          <div className="h-40 overflow-y-auto mb-2 flex flex-col gap-2">
            {aiMessages.length === 0 && <div className="text-gray-400">Ask any health or medicine-related question!</div>}
            {aiMessages.map((msg, i) => (
              <div key={i} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
                <span className={msg.role === 'user' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'} style={{ borderRadius: 8, padding: '4px 8px', display: 'inline-block' }}>{msg.content}</span>
              </div>
            ))}
          </div>
          <form onSubmit={handleAiSend} className="flex gap-2">
            <input value={aiInput} onChange={e => setAiInput(e.target.value)} className="border rounded px-2 py-1 flex-1" placeholder="Type your question..." />
            <button type="submit" className="bg-blue-600 text-white px-4 py-1 rounded" disabled={aiLoading || !aiInput.trim()}>Send</button>
          </form>
        </div>
      </section>
    </div>
  );
} 