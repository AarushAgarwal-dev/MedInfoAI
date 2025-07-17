import React, { useState, useEffect } from 'react';

const API = 'http://127.0.0.1:8000';

export default function Blog() {
  const [posts, setPosts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<any | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [formError, setFormError] = useState('');
  const user = localStorage.getItem('user');

  useEffect(() => {
    fetch(`${API}/blog/`)
      .then(res => res.json())
      .then(data => setPosts(data.posts || []))
      .finally(() => setLoading(false));
  }, [showForm]);

  const handleSelect = (post: any) => setSelected(post);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    if (!title.trim() || !content.trim()) {
      setFormError('Title and content required');
      return;
    }
    try {
      const res = await fetch(`${API}/blog/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content })
      });
      if (!res.ok) throw new Error('Failed to create post');
      setShowForm(false);
      setTitle('');
      setContent('');
    } catch (err: any) {
      setFormError(err.message);
    }
  };

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Awareness Blog</h2>
      {user === 'admin' && !showForm && (
        <button onClick={() => setShowForm(true)} className="mb-4 bg-blue-600 text-white px-4 py-1 rounded">New Post</button>
      )}
      {showForm && (
        <form onSubmit={handleCreate} className="mb-6 bg-white border rounded p-4">
          <input value={title} onChange={e => setTitle(e.target.value)} className="w-full border rounded px-2 py-1 mb-2" placeholder="Title" />
          <textarea value={content} onChange={e => setContent(e.target.value)} className="w-full border rounded px-2 py-1 mb-2" placeholder="Content" rows={5} />
          {formError && <div className="text-red-600 mb-2">{formError}</div>}
          <div className="flex gap-2">
            <button type="submit" className="bg-blue-600 text-white px-4 py-1 rounded">Create</button>
            <button type="button" onClick={() => setShowForm(false)} className="bg-gray-300 px-4 py-1 rounded">Cancel</button>
          </div>
        </form>
      )}
      {loading ? <div>Loading...</div> : (
        <div className="grid gap-4">
          {posts.length === 0 ? <div className="text-gray-500">No posts yet.</div> : posts.map(post => (
            <div key={post.id} className="bg-white border rounded p-4 cursor-pointer" onClick={() => handleSelect(post)}>
              <div className="font-bold text-lg">{post.title}</div>
              <div className="text-gray-600 text-sm line-clamp-2">{post.content.slice(0, 100)}{post.content.length > 100 ? '...' : ''}</div>
            </div>
          ))}
        </div>
      )}
      {selected && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded shadow-lg p-6 max-w-lg w-full relative">
            <button onClick={() => setSelected(null)} className="absolute top-2 right-2 text-gray-500">&times;</button>
            <div className="font-bold text-xl mb-2">{selected.title}</div>
            <div className="whitespace-pre-line">{selected.content}</div>
          </div>
        </div>
      )}
    </div>
  );
} 