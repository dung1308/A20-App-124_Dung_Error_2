import React, { useState } from 'react';
import { useStore } from '../state/store';
import { Link } from 'react-router-dom';
import MajorCard from '../components/Report/MajorCard';
import ChatBox from '../components/Chat/ChatBox';

const ReportPage = () => {
  const { matchResults, userId } = useStore();
  const [showChat, setShowChat] = useState(false);

  if (!matchResults) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-8">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-900 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-600 font-medium">Đang tải kết quả phân tích...</p>
          <Link to="/wizard" className="text-blue-700 text-sm mt-4 inline-block underline">Quay lại khảo sát</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="report-layout flex h-screen overflow-hidden bg-slate-50">
      {/* Sidebar matching Dashboard styling */}
      <aside className="hidden md:flex flex-col w-64 border-r border-slate-200 bg-white">
        <div className="px-6 py-8">
          <h2 className="text-lg font-bold text-blue-900">Admissions Portal</h2>
          <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold mt-1">AI-Driven Success</p>
        </div>
        <nav className="flex flex-col gap-y-1 py-2">
          <Link to="/dashboard" className="text-slate-500 hover:bg-slate-50 px-4 py-2.5 mx-2 rounded-lg flex items-center gap-3 font-semibold">Dashboard</Link>
          <Link to="/consultant" className="text-slate-500 hover:bg-slate-50 px-4 py-2.5 mx-2 rounded-lg flex items-center gap-3 font-semibold">AI Consultant</Link>
          <a href="#" className="text-slate-500 hover:bg-slate-50 px-4 py-2.5 mx-2 rounded-lg flex items-center gap-3 font-semibold">Major Discovery</a>
          <a href="#" className="text-slate-500 hover:bg-slate-50 px-4 py-2.5 mx-2 rounded-lg flex items-center gap-3 font-semibold">Resources</a>
        </nav>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 px-8 flex items-center bg-white border-b border-slate-200 flex-shrink-0">
          <h1 className="text-xl font-black text-blue-900">Gợi ý Ngành học</h1>
        </header>

        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-5xl mx-auto">
            <div className="bg-blue-900 text-white p-8 rounded-3xl mb-8 relative overflow-hidden shadow-xl shadow-blue-900/20">
              <div className="relative z-10">
                <h2 className="text-3xl font-bold mb-2">Kết quả của bạn</h2>
                <p className="text-blue-100 opacity-80 text-sm italic">{matchResults.disclaimer}</p>
              </div>
              <div className="absolute top-0 right-0 w-64 h-64 bg-blue-800 rounded-full -mr-20 -mt-20 opacity-50"></div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
              {matchResults.top3.map((major) => (
                <MajorCard key={major.major_id} major={major} />
              ))}
            </div>

            {matchResults.fallback && (
              <div className="bg-amber-50 border border-amber-200 p-6 rounded-2xl mb-12">
                <p className="text-amber-800 font-bold flex items-center gap-2 mb-1">
                  <span className="material-symbols-outlined">info</span>
                  AI chưa tìm thấy ngành phù hợp hoàn hảo
                </p>
                <p className="text-amber-700 text-sm">Hãy thử trò chuyện với cố vấn bên dưới để cung cấp thêm thông tin hoặc giải đáp thắc mắc.</p>
              </div>
            )}

            <section className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm mb-20">
              {!showChat ? (
                <div className="text-center py-6">
                  <h3 className="text-xl font-bold text-blue-900 mb-2">Bạn muốn tìm hiểu thêm?</h3>
                  <p className="text-slate-500 mb-8">Hãy trò chuyện với cố vấn AI để giải đáp các thắc mắc về ngành học và lộ trình sự nghiệp.</p>
                  <button className="px-8 py-3 bg-fed65b text-745c00 rounded-xl font-bold shadow-lg hover:shadow-xl transition-all active:scale-95" onClick={() => setShowChat(true)}>
                    Hỏi thêm câu hỏi
                  </button>
                </div>
              ) : (
                <ChatBox userId={userId} />
              )}
            </section>
          </div>
        </main>
      </div>
    </div>
  );
};

export default ReportPage;