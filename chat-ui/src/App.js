import React, { useState } from 'react';
import './index.css';

function App() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const apiUrl = "https://dealagent007.onrender.com";
  const authToken = "pawsitive-secret-token";

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setIsLoading(true);
    setResponse('');

    try {
      const res = await fetch(`${apiUrl}/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({ message: input }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n").filter(line => line.trim() !== "");

for (let line of lines) {
  // Skip done signal
  if (line.trim() === "[DONE]") continue;

  // Strip "data: " if present
  if (line.startsWith("data: ")) {
    line = line.replace("data: ", "");
  }

  try {
    const json = JSON.parse(line);
    if (json.type === "message" && json.content?.content) {
      setResponse(prev => prev + json.content.content);
    }
  } catch (e) {
    console.warn("Skipping invalid JSON line:", line);
  }
}
      }
    } catch (error) {
      console.error('Streaming error:', error);
      setResponse(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
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
          onKeyDown={handleKeyDown}
          placeholder="Ask me anything..."
          className="w-full p-3 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded disabled:opacity-50"
          disabled={isLoading}
        >
          {isLoading ? 'Thinking...' : 'Send'}
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
