import React, { useState, useEffect, useRef } from 'react';
import { useStore } from '../state/store';
import { useNavigate } from 'react-router-dom';
import { useChat } from '../hooks/useChat';
import { useAuth } from '../context/AuthContext';

const majorNameMap = {
  'cs': 'Khoa học Máy tính',
  'ee': 'Kỹ thuật Điện — Điện tử',
  'me': 'Kỹ thuật Cơ khí',
  'bme': 'Kỹ thuật Y sinh',
  'ba': 'Quản trị Kinh doanh',
  'finance': 'Tài chính',
  'data_science': 'Khoa học Dữ liệu',
  'liberal_arts': 'Khoa học Xã hội & Nhân văn',
  'architecture': 'Kiến trúc'
};

const ConsultantPage = () => {
  const { matchResults } = useStore();
  const navigate = useNavigate();
  const { userId, isAuthenticated } = useAuth(); // Moved up to ensure userId is available
  const [currentSessionId, setCurrentSessionId] = useState('new');

  const { 
    messages, 
    setMessages, 
    sendMessage, 
    loading: isTyping 
  } = useChat(userId, currentSessionId, (newId) => {
    // Transition from 'new' to a real session UUID once the first message is sent
    if (currentSessionId === 'new') setCurrentSessionId(newId);
  });

  const [input, setInput] = useState('');
  const [selectedMajor, setSelectedMajor] = useState(null);
  const scrollRef = useRef(null);

  // Initialize chat with top results if they exist
  useEffect(() => {
    if (matchResults?.top3 && messages.length === 0) {
      setMessages([
        {
          role: 'assistant',
          content: matchResults.answer || "Xin chào! Dựa trên năng lực và sở thích bạn đã cung cấp, tôi đã chọn ra 3 ngành học tiềm năng nhất tại VinUni dành cho bạn.",
          type: 'recommendation',
          data: matchResults.top3
        }
      ]);
    }
  }, [matchResults, messages.length, setMessages]);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated && !userId) navigate('/login');
  }, [isAuthenticated, userId, navigate]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = (text = input) => {
    if (!text.trim()) return;
    sendMessage(text);
    if (text === input) setInput('');
  };

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-[#f8f9ff] font-inter text-[#0d1c2e]">
      {/* Chat Canvas */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-8 md:px-12 lg:px-24 scroll-smooth chat-scrollbar">
          <div className="max-w-4xl mx-auto space-y-8">
            {messages.map((msg, index) => {
              let displayContent = msg.content;
              let recommendationData = msg.type === 'recommendation' ? msg.data : null;

              return (
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
                    <p className="text-[16px] leading-relaxed">{displayContent}</p>
                  </div>

                  {/* Recommendation Grid */}
                  {recommendationData && (
                    <>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {recommendationData.map((major, idx) => (
                          <div key={idx} className="group bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-xl transition-all duration-300">
                            <div className="flex justify-between items-start mb-4">
                              <div className="p-2 bg-blue-50 rounded-lg text-blue-700">
                                <span className="material-symbols-outlined text-[20px]">school</span>
                              </div>
                              <span className="px-2 py-1 bg-green-50 text-green-700 text-[10px] font-bold rounded uppercase tracking-wider">{major.match_score}% Match</span>
                            </div>
                            <h4 className="font-bold text-blue-900 mb-1">{major.major_name || majorNameMap[major.major_id] || major.major_id}</h4>
                            <p className="text-xs text-slate-500 mb-6 leading-relaxed line-clamp-2">{major.match_reason || major.reason || "Xem chi tiết để biết thêm thông tin."}</p>
                            <button 
                              onClick={() => setSelectedMajor(major)}
                              className="w-full py-2.5 bg-slate-50 text-blue-700 font-semibold text-sm rounded-xl group-hover:bg-[#003466] group-hover:text-white transition-colors"
                            >
                              Chi tiết
                            </button>
                          </div>
                        ))}
                      </div>
                      {msg.type === 'recommendation' && (
                        <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded-r-2xl max-w-[85%]">
                          <div className="flex gap-2 items-center text-blue-900 font-bold mb-1">
                            <span className="material-symbols-outlined text-[20px]">auto_awesome</span>
                            <span className="text-sm">Mentor Insight</span>
                          </div>
                          <p className="text-sm text-blue-800 leading-relaxed italic">"Dựa trên hồ sơ của bạn, các ngành kỹ thuật và khoa học máy tính sẽ tận dụng tốt nhất thế mạnh về tư duy logic mà bạn đã thể hiện."</p>
                        </div>
                      )}
                    </>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="w-10 h-10 rounded-full bg-slate-200 overflow-hidden flex-shrink-0">
                    <div className="w-full h-full bg-blue-200 flex items-center justify-center text-blue-900 font-bold">U</div>
                  </div>
                )}
              </div>
              );
            })}

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

      {/* Detail Modal */}
      {selectedMajor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm transition-all">
          <div className="bg-white w-full max-w-lg rounded-3xl overflow-hidden shadow-2xl animate-in fade-in zoom-in duration-200">
            <div className="p-8">
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-50 rounded-2xl text-blue-700">
                    <span className="material-symbols-outlined text-3xl">school</span>
                  </div>
                  <div>
                    <h3 className="text-2xl font-black text-blue-900">{selectedMajor.major_name || majorNameMap[selectedMajor.major_id]}</h3>
                    <div className="inline-block px-2 py-0.5 bg-green-50 text-green-700 text-[11px] font-bold rounded uppercase tracking-wider mt-1">
                      {selectedMajor.match_score}% Match Strength
                    </div>
                  </div>
                </div>
                <button 
                  onClick={() => setSelectedMajor(null)}
                  className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-400"
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>

              <div className="space-y-6">
                <div>
                  <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-2">Tại sao ngành này phù hợp?</h4>
                  <p className="text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-2xl border border-slate-100">
                    {selectedMajor.match_reason}
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-2">Sinh viên VinUni học gì?</h4>
                  <p className="text-slate-600 leading-relaxed">
                    {selectedMajor.what_students_do || "Học sinh sẽ được học về các kiến thức chuyên sâu, thực hành dự án thực tế và tham gia các kỳ thực tập tại doanh nghiệp đối tác của VinUni."}
                  </p>
                </div>
              </div>

              <div className="mt-10">
                <button onClick={() => { handleSend(`Tôi muốn tìm hiểu sâu hơn về ngành ${selectedMajor.major_name || majorNameMap[selectedMajor.major_id]}`); setSelectedMajor(null); }} className="w-full py-4 bg-[#003466] text-white font-bold rounded-2xl shadow-xl shadow-blue-900/20 hover:scale-[1.02] active:scale-95 transition-all">Hỏi thêm về ngành này</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConsultantPage;