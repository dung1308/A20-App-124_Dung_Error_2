import React, { useState, useEffect } from 'react';
import axios from 'axios';

/**
 * ProfilePage Component
 * Displays the student's academic profile and preferences fetched via the CRM service.
 */
const ProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Retrieve user_id from localStorage (synchronized with AuthPage)
  const userId = localStorage.getItem('user_email') || 'anonymous';

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await axios.get(`${baseUrl}/api/profile/${userId}`);
        setProfile(response.data);
      } catch (err) {
        console.error("Error fetching profile:", err);
        setError("Không thể tải thông tin hồ sơ. Vui lòng hoàn thành khảo sát tư vấn trước.");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [userId]);

  if (loading) return <div className="p-8 text-center">Đang tải hồ sơ...</div>;
  if (error) return <div className="p-8 text-red-500 text-center">{error}</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <header className="mb-8 border-b pb-4">
        <h1 className="text-3xl font-bold text-gray-800">Hồ sơ của tôi</h1>
        <p className="text-gray-600">Dữ liệu này giúp CRM Agent đưa ra những lời khuyên chính xác nhất cho bạn.</p>
      </header>

      {profile ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Academic Stats */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-semibold mb-4 text-blue-700">Chỉ số học tập</h2>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-500">GPA Mục tiêu/Hiện tại:</span>
              <span className="font-medium">{profile.gpa || 'Chưa cập nhật'}</span>
            </div>
            <div className="mt-4">
              <h3 className="text-sm font-bold text-gray-400 uppercase mb-2">Chứng chỉ ngoại ngữ</h3>
              {profile.test_scores ? (
                <ul className="space-y-1">
                  {Object.entries(profile.test_scores).map(([test, score]) => (
                    <li key={test} className="flex justify-between">
                      <span className="capitalize">{test}:</span>
                      <span className="font-medium text-green-600">{score}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-400 italic">Chưa có thông tin điểm số.</p>
              )}
            </div>
          </div>

          {/* Major Preferences */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-semibold mb-4 text-blue-700">Ngành học quan tâm</h2>
            {profile.preferred_majors && profile.preferred_majors.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {profile.preferred_majors.map((major) => (
                  <span key={major} className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium border border-blue-100">
                    {major}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-gray-400 italic">Bạn chưa thực hiện khảo sát chọn ngành.</p>
            )}
          </div>

          {/* Extra Profile Data */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 md:col-span-2">
            <h2 className="text-xl font-semibold mb-4 text-blue-700">Chi tiết bổ sung</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {profile.profile_data ? Object.entries(profile.profile_data).map(([key, value]) => (
                <div key={key} className="p-3 bg-gray-50 rounded-lg">
                  <span className="block text-xs font-bold text-gray-400 uppercase">{key.replace(/_/g, ' ')}</span>
                  <span className="text-gray-800">
                    {Array.isArray(value) ? value.join(', ') : String(value)}
                  </span>
                </div>
              )) : (
                <p className="text-gray-400 italic">Không có dữ liệu mở rộng.</p>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200 text-center">
          <p className="text-yellow-700">Hồ sơ của bạn hiện đang trống. Hãy bắt đầu bằng cách hoàn thành khảo sát tư vấn chọn ngành.</p>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;