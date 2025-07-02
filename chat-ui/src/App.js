import React, { useState } from 'react';
import './index.css';
import axios from 'axios';

function App() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');

  const handleSubmit = async (e) => {
  e.preventDefault();

  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
    const authSecret = import.meta.env.VITE_AUTH_SECRET || '';

    const res = await axios.post(
      `${baseUrl}/invoke?agent_id=research-assistant`,
      { message: input }, // backend expects 'message'
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authSecret}`,  // <-- added this
        },
      }
    );
    setResponse(res.data.content || 'No content');
  } catch (err) {
    console.error('Error:', err);
    setResponse('Error occurred. Check console for details.');
  }
};

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center justify-center px-4">
      <h1 className="text-3xl font-bold mb-6">💬 DealAgent007</h1>

      <form onSubmit={handleSubmit} className="w-full max-w-xl space-y-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything..."
          className="w-full p-3 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded"
        >
          Send
        </button>
      </form>

      {response && (
        <div className="mt-6 w-full max-w-xl p-4 bg-gray-800 rounded border border-gray-700">
          <h2 className="text-lg font-semibold mb-2">Response:</h2>
          <p className="whitespace-pre-line">{response}</p>
        </div>
      )}
    </div>
  );
}

export default App;
