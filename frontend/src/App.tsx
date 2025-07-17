import { Routes, Route, Link } from 'react-router-dom';
import Tools from './pages/Tools';
import Auth from './pages/Auth';
import { useState } from 'react';
import Blog from './pages/Blog';
import logo from './assets/logo_white_bg.png';

function Home() {
  return <div className="p-8">
    <h1 className="text-4xl font-extrabold mb-4 text-gray-900 drop-shadow-lg">Medicine Web App</h1>
    <p className="text-lg text-gray-700">Welcome to your <span className="text-blue-600 font-semibold">one-stop solution</span> for <span className="text-purple-600 font-semibold">medicine search</span>, <span className="text-pink-600 font-semibold">price comparison</span>, <span className="text-green-600 font-semibold">daily essentials</span>, <span className="text-yellow-600 font-semibold">Jan Aushadi Kendra finder</span>, <span className="text-indigo-600 font-semibold">AI assistant</span>, and <span className="text-red-600 font-semibold">awareness blog</span>.</p>
  </div>;
}
function About() {
  return <div className="p-8">
    <h2 className="text-3xl font-bold mb-4 text-pink-600 drop-shadow">About</h2>
    <p className="text-lg text-gray-700">This website is made by <b className="text-blue-600">Anshika Agarwal</b>, a grade 10 student.</p>
  </div>;
}

export default function App() {
  const [user, setUser] = useState<string | null>(localStorage.getItem('user'));
  const handleAuth = (username: string) => {
    setUser(username);
    localStorage.setItem('user', username);
  };
  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-100">
      <nav className="bg-white/80 shadow-lg mb-8 sticky top-0 z-50 backdrop-blur border-b border-blue-100">
        <div className="container mx-auto px-4 py-4 flex flex-col sm:flex-row justify-between items-center">
          <div className="flex items-center gap-2 mb-2 sm:mb-0">
            <img src={logo} alt="MedInfoAI Logo" className="w-10 h-10 drop-shadow" />
            <span className="font-extrabold text-2xl text-gray-900">Medicine Web App</span>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-6 text-lg">
            <Link to="/" className="hover:text-blue-600 font-semibold transition-colors">Home</Link>
            <Link to="/tools" className="hover:text-purple-600 font-semibold transition-colors">Tools</Link>
            <Link to="/blog" className="hover:text-pink-600 font-semibold transition-colors">Awareness Blog</Link>
            <Link to="/about" className="hover:text-green-600 font-semibold transition-colors">About</Link>
            {user ? <button onClick={handleLogout} className="ml-2 text-red-600 font-semibold">Logout ({user})</button> : <Link to="/auth" className="ml-2 text-blue-600 font-semibold">Login</Link>}
          </div>
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/tools" element={user ? <Tools user={user} /> : <Auth onAuth={handleAuth} />} />
        <Route path="/about" element={<About />} />
        <Route path="/blog" element={<Blog />} />
        <Route path="/auth" element={<Auth onAuth={handleAuth} />} />
      </Routes>
    </div>
  );
}
