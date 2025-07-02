import React, { useState } from 'react';
import './index.css';
import axios from 'axios';

function App() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [responseData, setResponseData] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  // ✅ Hardcoded to avoid env build-time issues
  const apiUrl = "https://dealagent007.onrender.com";
  const authToken = "pawsitive-secret-token";

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const { data } = await axios.post(
        `${apiUrl}/invoke`,
        { message: input },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`,
          },
        }
      );

      console.log(data);
      setResponse(data.content || "No response content found.");
      setResponseData(data);
    } catch (error) {
      console.error('Error:', error);
      setResponse(`Error: ${error.message}`);
      setResponseData(null);
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
          <p className="whitespace-pre-line mb-4">{response}</p>
          {responseData && (
            <>
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="text-sm text-indigo-400 underline"
              >
                {showDetails ? 'Hide Details' : 'Show Details'}
              </button>
              {showDetails && (
                <pre className="mt-2 text-xs text-gray-400 bg-gray-900 p-2 rounded overflow-x-auto">
                  {JSON.stringify(responseData, null, 2)}
                </pre>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
