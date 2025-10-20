import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Chat() {
  const { user, session, signOut } = useAuth();
  const navigate = useNavigate();
  
  const [memories, setMemories] = useState([]);
  const [selectedMemory, setSelectedMemory] = useState(null);
  const [records, setRecords] = useState([]);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [newMemoryTitle, setNewMemoryTitle] = useState('');
  const [newRecord, setNewRecord] = useState('');
  const [showNewMemory, setShowNewMemory] = useState(false);
  const [showNewRecord, setShowNewRecord] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
    } else {
      fetchMemories();
    }
  }, [user, navigate]);

  useEffect(() => {
    if (selectedMemory) {
      fetchRecords(selectedMemory.id);
      fetchMessages(selectedMemory.id);
    }
  }, [selectedMemory]);

  const apiCall = async (endpoint, method = 'GET', body = null) => {
    const token = session?.access_token;
    console.log(`🔵 API Call: ${method} ${endpoint}`, body);
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    };
    if (body) options.body = JSON.stringify(body);
    const res = await fetch(`${API_URL}/api${endpoint}`, options);
    console.log(`📡 Response: ${method} ${endpoint} - Status: ${res.status}`);
    if (!res.ok) {
      const errorText = await res.text();
      console.error(`❌ Error Response: ${errorText}`);
      throw new Error(`HTTP ${res.status}: ${errorText}`);
    }
    const data = await res.json();
    console.log(`✅ Success: ${method} ${endpoint}`, data);
    return data;
  };

  const fetchMemories = async () => {
    try {
      const data = await apiCall('/memories');
      setMemories(data);
      if (data.length > 0 && !selectedMemory) {
        setSelectedMemory(data[0]);
      }
    } catch (err) {
      console.error('Failed to fetch memories:', err);
    }
  };

  const fetchRecords = async (memoryId) => {
    try {
      const data = await apiCall(`/memories/${memoryId}/records`);
      setRecords(data);
    } catch (err) {
      console.error('Failed to fetch records:', err);
    }
  };

  const fetchMessages = async (memoryId) => {
    try {
      const data = await apiCall(`/chat/memories/${memoryId}/messages`);
      setMessages(data.reverse());
    } catch (err) {
      console.error('Failed to fetch messages:', err);
    }
  };

  const createMemory = async () => {
    if (!newMemoryTitle.trim()) {
      setError('Please enter a memory title');
      return;
    }
    
    console.log('🚀 Creating memory with title:', newMemoryTitle);
    setLoading(true);
    setError('');
    
    try {
      const mem = await apiCall('/memories', 'POST', { title: newMemoryTitle });
      console.log('✅ Memory created:', mem);
      setMemories([mem, ...memories]);
      setNewMemoryTitle('');
      setShowNewMemory(false);
      setSelectedMemory(mem);
    } catch (err) {
      console.error('❌ Failed to create memory:', err);
      setError(`Failed to create memory: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const createRecord = async () => {
    if (!newRecord.trim() || !selectedMemory) {
      setError('Please enter record content');
      return;
    }
    
    console.log('🚀 Creating record:', newRecord);
    setLoading(true);
    setError('');
    
    try {
      const rec = await apiCall(`/memories/${selectedMemory.id}/records`, 'POST', { content: newRecord });
      console.log('✅ Record created:', rec);
      setRecords([rec, ...records]);
      setNewRecord('');
      setShowNewRecord(false);
    } catch (err) {
      console.error('❌ Failed to create record:', err);
      setError(`Failed to create record: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedMemory) return;
    
    console.log('🚀 Sending message:', newMessage);
    setLoading(true);
    setError('');
    
    try {
      await apiCall('/chat/send', 'POST', { memory_id: selectedMemory.id, message: newMessage });
      console.log('✅ Message sent');
      setNewMessage('');
      fetchMessages(selectedMemory.id);
    } catch (err) {
      console.error('❌ Failed to send message:', err);
      setError(`Failed to send message: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    await signOut();
    navigate('/login');
  };

  return (
    <div className="h-screen flex bg-gray-100">
      {/* Error Toast */}
      {error && (
        <div className="fixed top-4 right-4 z-50 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg max-w-md">
          <div className="flex items-start">
            <div className="flex-1">
              <p className="font-semibold">Error</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
            <button
              onClick={() => setError('')}
              className="ml-4 text-white hover:text-gray-200"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-blue-500 text-white px-6 py-3 rounded-lg shadow-lg">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-3"></div>
            <span>Processing...</span>
          </div>
        </div>
      )}

      {/* Sidebar - Memories */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800">Memories</h2>
          <button
            onClick={() => setShowNewMemory(!showNewMemory)}
            className="mt-2 w-full bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 text-sm"
          >
            + New Memory
          </button>
          {showNewMemory && (
            <div className="mt-2">
              <input
                type="text"
                placeholder="Memory title"
                value={newMemoryTitle}
                onChange={(e) => setNewMemoryTitle(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && createMemory()}
                className="w-full px-2 py-1 border rounded text-sm"
              />
              <button
                onClick={createMemory}
                disabled={loading}
                className="mt-1 w-full bg-green-600 text-white px-2 py-1 rounded text-xs hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating...' : 'Create'}
              </button>
            </div>
          )}
        </div>
        <div className="flex-1 overflow-y-auto">
          {memories.map((mem) => (
            <div
              key={mem.id}
              onClick={() => setSelectedMemory(mem)}
              className={`p-3 cursor-pointer border-b border-gray-100 hover:bg-gray-50 ${
                selectedMemory?.id === mem.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
              }`}
            >
              <div className="font-medium text-sm text-gray-800">{mem.title}</div>
              {mem.description && (
                <div className="text-xs text-gray-500 mt-1">{mem.description}</div>
              )}
            </div>
          ))}
        </div>
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={handleSignOut}
            className="w-full bg-gray-200 text-gray-700 px-3 py-2 rounded hover:bg-gray-300 text-sm"
          >
            Sign Out
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {selectedMemory ? (
          <>
            {/* Header */}
            <div className="bg-white border-b border-gray-200 p-4">
              <h1 className="text-2xl font-bold text-gray-800">{selectedMemory.title}</h1>
              {selectedMemory.description && (
                <p className="text-sm text-gray-600 mt-1">{selectedMemory.description}</p>
              )}
            </div>

            <div className="flex-1 flex overflow-hidden">
              {/* Records Panel */}
              <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
                <div className="p-4 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-800">Memory Records</h3>
                  <button
                    onClick={() => setShowNewRecord(!showNewRecord)}
                    className="mt-2 w-full bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 text-sm"
                  >
                    + Add Record
                  </button>
                  {showNewRecord && (
                    <div className="mt-2">
                      <textarea
                        placeholder="Record content"
                        value={newRecord}
                        onChange={(e) => setNewRecord(e.target.value)}
                        className="w-full px-2 py-1 border rounded text-sm"
                        rows={3}
                      />
                      <button
                        onClick={createRecord}
                        className="mt-1 w-full bg-green-600 text-white px-2 py-1 rounded text-xs hover:bg-green-700"
                      >
                        Save
                      </button>
                    </div>
                  )}
                </div>
                <div className="flex-1 overflow-y-auto p-4">
                  {records.length === 0 && (
                    <p className="text-sm text-gray-500 italic">No records yet</p>
                  )}
                  <ul className="space-y-2">
                    {records.map((rec) => (
                      <li key={rec.id} className="text-sm text-gray-700 flex items-start">
                        <span className="mr-2">•</span>
                        <span>{rec.content}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Chat Area */}
              <div className="flex-1 flex flex-col bg-gray-50">
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.length === 0 && (
                    <p className="text-sm text-gray-500 italic text-center mt-8">
                      No messages yet. Start a conversation!
                    </p>
                  )}
                  {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div
                        className={`max-w-md px-4 py-2 rounded-lg ${
                          msg.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-gray-800 border border-gray-200'
                        }`}
                      >
                        <p className="text-sm">{msg.content}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="p-4 bg-white border-t border-gray-200">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      placeholder="Type your message..."
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={sendMessage}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 font-medium"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-gray-500">Select or create a memory to get started</p>
          </div>
        )}
      </div>
    </div>
  );
}

