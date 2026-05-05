import React from 'react';
import { useNavigate, Link } from 'react-router-dom';

const DashboardPage = () => {
  const navigate = useNavigate();

  return (
    <div className="dashboard-layout flex h-screen overflow-hidden bg-slate-50">
      {/* Left Panel */}
      <aside className="hidden md:flex flex-col w-64 border-r border-slate-200 bg-white shadow-sm">
        <div className="px-6 py-8">
          <h2 className="text-lg font-bold text-blue-900">Admissions Portal</h2>
          <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold mt-1">AI-Driven Success</p>
        </div>
        <nav className="flex flex-col gap-y-1 py-2">
          <Link to="/dashboard" className="bg-blue-50 text-blue-700 px-4 py-2.5 mx-2 rounded-lg flex items-center gap-3 font-semibold">
            Dashboard
          </Link>
          <Link to="/consultant" className="text-slate-500 hover:bg-slate-50 px-4 py-2.5 mx-2 rounded-lg flex items-center gap-3 font-semibold">
            AI Consultant
          </Link>
          <a href="#" className="text-slate-500 hover:bg-slate-50 px-4 py-2.5 mx-2 rounded-lg flex items-center gap-3 font-semibold">
            Major Discovery
          </a>
          <a href="#" className="text-slate-500 hover:bg-slate-50 px-4 py-2.5 mx-2 rounded-lg flex items-center gap-3 font-semibold">
            Resources
          </a>
        </nav>
      </aside>

      <div className="flex-1 flex flex-col">
        {/* Upper Panel */}
        <header className="h-16 px-8 flex justify-between items-center bg-white border-b border-slate-200">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-black text-blue-900">Brilliant Mentor</h1>
            <nav className="hidden lg:flex items-center gap-6 ml-8">
              <Link to="/" className="text-sm font-medium text-slate-600 hover:text-blue-700">Home</Link>
              <a href="#" className="text-sm font-medium text-slate-600 hover:text-blue-700">Major Guide</a>
              <a href="#" className="text-sm font-medium text-slate-600 hover:text-blue-700">Consultation</a>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="p-8 overflow-y-auto">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-4 text-slate-800">Chào mừng trở lại!</h2>
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
              <p className="text-slate-600 mb-6 text-lg">Bạn đã hoàn thành khảo sát định hướng. Bây giờ, hãy trò chuyện với Cố vấn AI của chúng tôi để khám phá các lựa chọn tốt nhất dành cho bạn.</p>
              <button 
                onClick={() => navigate('/consultant')}
                className="px-8 py-4 bg-blue-700 text-white rounded-xl font-bold hover:bg-blue-800 transition-all transform active:scale-95 shadow-lg shadow-blue-200"
              >
                Bắt đầu tư vấn ngay
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;