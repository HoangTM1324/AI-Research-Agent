import { useState } from 'react';
import { sendChat, uploadFile } from './api';
import { Paperclip, SendHorizontal, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [filePath, setFilePath] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const result = await uploadFile(file);
      setFilePath(result.file_path);
      alert("Đã nhận PDF: " + result.file_path);
    } catch (error) {
      alert("Lỗi upload!");
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    try {
      const response = await sendChat({ question: currentInput, file_path: filePath });
      const aiMsg: Message = { role: 'assistant', content: response.answer };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Lỗi kết nối AI." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <main className="chat-window">
        {messages.length === 0 && (
          <div className="welcome-text">How are you today?</div>
        )}
        {messages.map((msg, index) => (
          <div key={index} className={`message-row ${msg.role}`}>
            <div className="message-bubble">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {msg.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        {isLoading && <div className="loading-dots">AI is processing...</div>}
      </main>

      <footer className="input-area">
        <div className="input-wrapper">
          <input 
            type="file" 
            accept=".pdf" 
            onChange={handleFileChange} 
            id="pdf-upload" 
            hidden 
          />
          <label htmlFor="pdf-upload" className="icon-button">
            <Paperclip size={22} color={filePath ? "#4b90ff" : "#9aa0a6"} />
          </label>
          
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask me something..."
          />

          <button onClick={handleSend} disabled={isLoading || !input.trim()} className="send-button">
            {isLoading ? <Loader2 size={22} className="animate-spin" /> : <SendHorizontal size={22} />}
          </button>
        </div>
        <p className="disclaimer">Sometime it can give wrong information. We suggest you to recheck the given result.</p>
      </footer>
    </div>
  );
}

export default App;