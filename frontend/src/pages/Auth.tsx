import React, { useState } from 'react';

const API = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

export default function Auth({ onAuth }: { onAuth: (username: string) => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API}/users/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Error');
      onAuth(username);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-sm mx-auto p-8 bg-white rounded shadow mt-10">
      <h2 className="text-2xl font-bold mb-4 text-center">{mode === 'login' ? 'Login' : 'Register'}</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input value={username} onChange={e => setUsername(e.target.value)} className="w-full border rounded px-3 py-2" placeholder="Username" required />
        <input value={password} onChange={e => setPassword(e.target.value)} className="w-full border rounded px-3 py-2" placeholder="Password" type="password" required />
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded" disabled={loading}>{loading ? 'Please wait...' : (mode === 'login' ? 'Login' : 'Register')}</button>
      </form>
      <div className="text-center mt-4">
        {mode === 'login' ? (
          <span>New user? <button className="text-blue-600 underline" onClick={() => setMode('register')}>Register</button></span>
        ) : (
          <span>Already have an account? <button className="text-blue-600 underline" onClick={() => setMode('login')}>Login</button></span>
        )}
      </div>
    </div>
  );
} 