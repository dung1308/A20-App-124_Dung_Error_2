import React, { useState, useEffect, useRef } from 'react';
import { useStore } from '../state/store';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

const ConsultantPage = () => {
  const { matchResults, userId, setUserId, role } = useStore();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

  // Initialize chat with top results if they exist
  useEffect(() => {
    if (matchResults?.top3 && messages.length === 0) {
      setMessages([
        {
          role: 'assistant',
          content: "Xin chào! Dựa trên năng lực và sở thích bạn đã cung cấp, tôi đã chọn ra 3 ngành học tiềm năng nhất tại VinUni dành cho bạn. Bạn thấy những gợi ý này thế nào?",
          type: 'recommendation',
          data: matchResults.top3
        }
      ]);
    }
  }, [matchResults, messages.length]);

  // Persist session if store is cleared on refresh
  useEffect(() => {
    const savedEmail = localStorage.getItem('user_email');
    if (!userId && savedEmail) {
      setUserId(savedEmail);
    }
  }, [userId, setUserId]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async (text = input) => {
    if (!text.trim()) return;

    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      // Prepare history for API (excluding complex data objects)
      // Only include role and content to match standard LLM/RAG expectations
      const history = messages.map(m => ({ 
        role: String(m.role), 
        content: String(m.content || "") 
      }));

      const payload = {
        userId: String(userId || "anonymous"),
        text: String(text),
        history: history
      };

      // Fallback to anonymous if no userId is present to prevent 422
      const response = await api.postChat(payload);
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Xin lỗi, tôi gặp chút trục trặc khi kết nối. Bạn có thể thử lại không?" }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="consultant-layout flex h-screen w-full overflow-hidden bg-[#f8f9ff] font-inter text-[#0d1c2e]">
      {/* Left Panel */}
      <aside className="hidden md:flex flex-col h-full w-64 border-r border-slate-200 bg-slate-50 flex-shrink-0 z-20">
        <div className="px-6 py-8">
          <h2 className="text-lg font-bold text-blue-900">Admissions Portal</h2>
          <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold mt-1">AI-Driven Success</p>
        </div>
        <nav className="flex flex-col gap-y-1 py-2">
          <Link to="/dashboard" className="text-slate-500 px-4 py-2.5 mx-2 flex items-center gap-3 font-inter text-[13px] font-semibold hover:bg-slate-100 transition-colors">
            <span className="material-symbols-outlined text-[20px]">dashboard</span>
            Dashboard
          </Link>
          <Link to="/consultant" className="bg-blue-50 text-blue-700 rounded-lg mx-2 px-4 py-2.5 flex items-center gap-3 font-inter text-[13px] font-semibold">
            <span className="material-symbols-outlined text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
            AI Consultant
          </Link>
          <a href="#" className="text-slate-500 px-4 py-2.5 mx-2 flex items-center gap-3 font-inter text-[13px] font-semibold hover:bg-slate-100 transition-colors">
            <span className="material-symbols-outlined text-[20px]">school</span>
            Major Discovery
          </a>
          <a href="#" className="text-slate-500 px-4 py-2.5 mx-2 flex items-center gap-3 font-inter text-[13px] font-semibold hover:bg-slate-100 transition-colors">
            <span className="material-symbols-outlined text-[20px]">library_books</span>
            Resources
          </a>
        </nav>
        <div className="mt-auto p-4">
          <div className="bg-[#003466] text-white rounded-xl p-4 shadow-lg shadow-blue-900/10">
            <p className="text-xs font-semibold opacity-80 mb-2">Need human advice?</p>
            <button className="w-full py-2 bg-[#fed65b] text-[#745c00] text-[12px] font-bold rounded-lg active:scale-95 transition-transform">
              Schedule Expert Call
            </button>
          </div>
          <div className="mt-6 flex items-center gap-3 px-2">
            <div className="w-10 h-10 rounded-full bg-slate-200 overflow-hidden flex-shrink-0">
              <div className="w-full h-full bg-blue-200 flex items-center justify-center text-blue-900 font-bold text-xs">AJ</div>
            </div>
            <div>
              <p className="text-sm font-bold text-slate-800">Alex Johnson</p>
              <p className="text-[10px] text-slate-500">Premium Member</p>
            </div>
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col">
        {/* Upper Panel */}
        <header className="h-16 px-8 flex justify-between items-center bg-white/95 backdrop-blur-md border-b border-slate-200 z-10 flex-shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-black tracking-tighter text-blue-900">Brilliant Mentor</h1>
            <nav className="hidden lg:flex items-center gap-6 ml-8">
              <Link to="/" className="text-sm font-medium text-slate-600 hover:text-blue-700">Home</Link>
              <a href="#" className="text-sm font-medium text-slate-600 hover:text-blue-700">Major Guide</a>
              <Link to="/consultant" className="text-sm font-medium text-blue-700 border-b-2 border-blue-700 pb-1">Consultation</Link>
            </nav>
          </div>
          <div className="hidden sm:flex items-center gap-3">
            {userId ? (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 rounded-lg">
                <div className={`w-2 h-2 rounded-full animate-pulse ${role === 'admin' ? 'bg-purple-500' : 'bg-green-500'}`}></div>
                <span className="text-xs font-semibold text-blue-900">{userId}</span>
                {role === 'admin' && (
                  <span className="ml-1 px-1.5 py-0.5 bg-purple-100 text-purple-700 text-[9px] font-black rounded uppercase tracking-tighter">Engineer</span>
                )}
              </div>
            ) : (
              <>
                <button className="px-4 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-lg">Sign In</button>
                <button className="px-5 py-2 text-sm font-semibold bg-[#003466] text-white rounded-full shadow-md active:scale-95 transition-transform">Get Started</button>
              </>
            )}
          </div>
        </header>

        {/* Chat Canvas */}
        <main ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-8 md:px-12 lg:px-24 scroll-smooth chat-scrollbar">
          <div className="max-w-4xl mx-auto space-y-8">
            {messages.map((msg, index) => (
              <div key={index} className={`flex gap-4 items-start ${msg.role === 'user' ? 'justify-end' : ''}`}>
                {msg.role === 'assistant' && (
                  <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0 border border-blue-100">
                    <span className="material-symbols-outlined text-blue-700" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
                  </div>
                )}
                
                <div className="flex-1 max-w-[85%] space-y-6">
                  <div className={`p-5 rounded-2xl shadow-sm border ${
                    msg.role === 'user' 
                      ? 'bg-[#003466] text-white rounded-tr-none' 
                      : 'bg-white text-[#0d1c2e] border-slate-200 rounded-tl-none'
                  }`}>
                    <p className="text-[16px] leading-relaxed">{msg.content}</p>
                  </div>

                  {/* Recommendation Grid for initial bot message */}
                  {msg.type === 'recommendation' && (
                    <>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {msg.data.map((major, idx) => (
                          <div key={idx} className="group bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-xl transition-all duration-300">
                            <div className="flex justify-between items-start mb-4">
                              <div className="p-2 bg-blue-50 rounded-lg text-blue-700">
                                <span className="material-symbols-outlined text-[20px]">school</span>
                              </div>
                              <span className="px-2 py-1 bg-green-50 text-green-700 text-[10px] font-bold rounded uppercase tracking-wider">{major.match_score}% Match</span>
                            </div>
                            <h4 className="font-bold text-blue-900 mb-1">{major.major_name}</h4>
                            <p className="text-xs text-slate-500 mb-6 leading-relaxed line-clamp-2">{major.match_reason || major.reason}</p>
                            <button className="w-full py-2.5 bg-slate-50 text-blue-700 font-semibold text-sm rounded-xl group-hover:bg-[#003466] group-hover:text-white transition-colors">Chi tiết</button>
                          </div>
                        ))}
                      </div>
                      <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded-r-2xl max-w-[85%]">
                        <div className="flex gap-2 items-center text-blue-900 font-bold mb-1">
                          <span className="material-symbols-outlined text-[20px]">auto_awesome</span>
                          <span className="text-sm">Mentor Insight</span>
                        </div>
                        <p className="text-sm text-blue-800 leading-relaxed italic">"Dựa trên hồ sơ của bạn, các ngành kỹ thuật và khoa học máy tính sẽ tận dụng tốt nhất thế mạnh về tư duy logic mà bạn đã thể hiện."</p>
                      </div>
                    </>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="w-10 h-10 rounded-full bg-slate-200 overflow-hidden flex-shrink-0">
                    <div className="w-full h-full bg-blue-200 flex items-center justify-center text-blue-900 font-bold">U</div>
                  </div>
                )}
              </div>
            ))}

            {isTyping && (
              <div className="flex gap-4 items-start">
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <span className="material-symbols-outlined text-blue-700" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
                </div>
                <div className="flex gap-1 items-center bg-white px-4 py-3 rounded-full border border-slate-200 shadow-sm">
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            )}
          </div>
        </main>

        {/* Input Section */}
        <div className="p-6 bg-white border-t border-slate-200">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-3 mb-4 overflow-x-auto pb-1 no-scrollbar">
              {['So sánh mức lương', 'Triển vọng nghề nghiệp', 'Phân tích hồ sơ'].map((hint) => (
                <button 
                  key={hint}
                  onClick={() => handleSend(hint)}
                  className="whitespace-nowrap px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full text-xs font-semibold hover:bg-blue-100 transition-colors border border-blue-100"
                >
                  {hint}
                </button>
              ))}
            </div>
            <div className="relative flex items-center">
              <input 
                className="w-full pl-6 pr-16 py-4 bg-slate-100 border-transparent focus:border-blue-900 focus:bg-white focus:ring-4 focus:ring-blue-900/5 rounded-2xl transition-all outline-none text-body-md shadow-inner"
                placeholder="Hỏi Mentor bất cứ điều gì về ngành học, sự nghiệp..." 
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              />
              <button 
                onClick={() => handleSend()}
                disabled={!input.trim() || isTyping}
                className="absolute right-3 w-10 h-10 bg-blue-900 text-white rounded-xl flex items-center justify-center shadow-lg shadow-blue-900/20 active:scale-95 transition-all disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>send</span>
              </button>
            </div>
            <p className="text-[10px] text-center text-slate-400 mt-4 uppercase tracking-wider font-medium">Powered by Brilliant Mentor AI • Guidance based on current 2024 academic standards</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConsultantPage;