import React, { useState, useEffect } from 'react';

/**
 * DESIGN TOKENS (from /design/academic_intelligence/DESIGN.md)
 */
const theme = {
  colors: {
    primary: '#003466',
    onPrimary: '#ffffff',
    background: '#f8f9ff',
    surface: '#ffffff',
    surfaceContainer: '#e6eeff',
    onSurface: '#0d1c2e',
    onSurfaceVariant: '#424750',
    outline: '#737781',
    error: '#ba1a1a',
    accent: '#735c00', // Academic Gold
  },
  rounded: {
    sm: '4px',
    default: '8px',
    lg: '16px',
    full: '9999px',
  },
  spacing: {
    stackSm: '8px',
    stackMd: '16px',
    stackLg: '32px',
  },
  typography: {
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
  }
};

const MajorMatchApp = () => {
  const [view, setView] = useState('splash'); // splash | wizard | loading | results
  const [step, setStep] = useState(1);
  const [sessionId] = useState(() => crypto.randomUUID());
  const [answers, setAnswers] = useState({
    interests: [],
    strengths: [],
    dislikes: [],
    work_style: ""
  });
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const options = {
    interests: ["Lập trình", "Thiết kế đồ họa", "Kinh doanh", "Nghiên cứu khoa học", "Y học", "Nghệ thuật", "Luật", "Môi trường"],
    strengths: ["Tư duy logic", "Giao tiếp", "Giải quyết vấn đề", "Sáng tạo", "Làm việc nhóm", "Phân tích số liệu", "Quản lý thời gian", "Lãnh đạo"],
    dislikes: ["Công việc lặp lại", "Làm việc ngoài trời", "Áp lực doanh số", "Viết báo cáo", "Thuyết trình", "Tính toán phức tạp", "Môi trường ồn ào", "Làm việc một mình"],
    workStyle: ["Làm việc độc lập, tập trung sâu", "Nhóm nhỏ (3-5 người)", "Tổ chức lớn, năng động", "Linh hoạt giữa các môi trường"]
  };

  const handleToggleOption = (category, option) => {
    setAnswers(prev => {
      const current = prev[category];
      const updated = current.includes(option)
        ? current.filter(i => i !== option)
        : [...current, option];
      return { ...prev, [category]: updated };
    });
  };

  const handleSubmit = async () => {
    setView('loading');
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: sessionId,
          message: `Tôi đã hoàn thành khảo sát hướng nghiệp. 
            Sở thích: ${answers.interests.join(', ')}. 
            Thế mạnh: ${answers.strengths.join(', ')}. 
            Không thích: ${answers.dislikes.join(', ')}. 
            Phong cách làm việc: ${answers.work_style}. 
            Hãy tư vấn cho tôi 3 ngành học phù hợp tại VinUni.`
        })
      });

      if (!response.ok) throw new Error('Hệ thống đang bận');
      const data = await response.json();
      
      // Mock parsing for Demo purposes as per Copilot_Guide
      // In production, the backend would return structured JSON
      setResults({
        top3: [
          { major_name: "Khoa học Máy tính", match_reason: "Dựa trên sở thích lập trình và tư duy logic của bạn...", match_score: 95 },
          { major_name: "Quản trị Kinh doanh", match_reason: "Phù hợp với khả năng lãnh đạo và giao tiếp...", match_score: 88 },
          { major_name: "Kỹ thuật Điện", match_reason: "Tận dụng thế mạnh phân tích kỹ thuật...", match_score: 82 }
        ],
        ai_response: data.response
      });
      setView('results');
    } catch (err) {
      setError(err.message);
      setView('wizard');
    }
  };

  // STYLES
  const containerStyle = {
    fontFamily: theme.typography.fontFamily,
    backgroundColor: theme.colors.background,
    color: theme.colors.onSurface,
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '40px 20px',
  };

  const cardStyle = {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.rounded.lg,
    boxShadow: '0 4px 20px rgba(0, 52, 102, 0.08)',
    width: '100%',
    maxWidth: '600px',
    padding: theme.spacing.stackLg,
    border: `1px solid ${theme.colors.surfaceContainer}`,
  };

  const buttonStyle = (variant = 'primary') => ({
    backgroundColor: variant === 'primary' ? theme.colors.primary : 'transparent',
    color: variant === 'primary' ? theme.colors.onPrimary : theme.colors.primary,
    border: variant === 'primary' ? 'none' : `1px solid ${theme.colors.primary}`,
    padding: '12px 24px',
    borderRadius: theme.rounded.default,
    fontWeight: '600',
    cursor: 'pointer',
    fontSize: '16px',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px'
  });

  const chipStyle = (isSelected) => ({
    padding: '10px 16px',
    borderRadius: theme.rounded.full,
    border: `1px solid ${isSelected ? theme.colors.primary : theme.colors.outline}`,
    backgroundColor: isSelected ? theme.colors.surfaceContainer : 'transparent',
    color: isSelected ? theme.colors.primary : theme.colors.onSurfaceVariant,
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: isSelected ? '600' : '400',
    transition: '0.2s'
  });

  const progressBarStyle = {
    width: '100%',
    height: '6px',
    backgroundColor: theme.colors.surfaceContainer,
    borderRadius: '3px',
    marginBottom: '32px',
    overflow: 'hidden'
  };

  // VIEWS
  if (view === 'splash') {
    return (
      <div style={containerStyle}>
        <div style={{ ...cardStyle, textAlign: 'center', padding: '60px 40px' }}>
          <h1 style={{ color: theme.colors.primary, fontSize: '32px', marginBottom: '16px' }}>VinUni Major Match</h1>
          <p style={{ color: theme.colors.onSurfaceVariant, lineHeight: '1.6', marginBottom: '32px' }}>
            Khám phá ngành học tương lai của bạn thông qua trí tuệ nhân tạo. 
            Hệ thống Academic Intelligence sẽ giúp bạn tìm ra sự lựa chọn hoàn hảo nhất.
          </p>
          <button onClick={() => setView('wizard')} style={{ ...buttonStyle(), width: '100%' }}>
            Bắt đầu khám phá
          </button>
        </div>
      </div>
    );
  }

  if (view === 'loading') {
    return (
      <div style={containerStyle}>
        <div style={{ ...cardStyle, textAlign: 'center', padding: '80px' }}>
          <div style={{ 
            width: '40px', height: '40px', border: `4px solid ${theme.colors.surfaceContainer}`, 
            borderTop: `4px solid ${theme.colors.primary}`, borderRadius: '50%', 
            margin: '0 auto 24px', animation: 'spin 1s linear infinite' 
          }} />
          <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
          <h3>Đang phân tích dữ liệu...</h3>
          <p>Trí tuệ nhân tạo đang đối chiếu hồ sơ của bạn với các ngành học tại VinUni.</p>
        </div>
      </div>
    );
  }

  if (view === 'results') {
    return (
      <div style={containerStyle}>
        <div style={{ maxWidth: '800px', width: '100%' }}>
          <h2 style={{ color: theme.colors.primary, marginBottom: '24px', textAlign: 'center' }}>Gợi ý ngành học dành cho bạn</h2>
          
          <div style={{ display: 'grid', gap: '20px', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', marginBottom: '32px' }}>
            {results.top3.map((m, idx) => (
              <div key={idx} style={cardStyle}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                  <h3 style={{ margin: 0, color: theme.colors.primary }}>{m.major_name}</h3>
                  <span style={{ 
                    backgroundColor: theme.colors.accent, color: '#fff', 
                    padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' 
                  }}>
                    {m.match_score}% Fit
                  </span>
                </div>
                <p style={{ fontSize: '14px', color: theme.colors.onSurfaceVariant, lineHeight: '1.5' }}>{m.match_reason}</p>
              </div>
            ))}
          </div>

          <div style={{ ...cardStyle, backgroundColor: theme.colors.surfaceContainer, maxWidth: '100%' }}>
            <h4 style={{ marginTop: 0 }}>Lời khuyên từ Advisor:</h4>
            <p style={{ fontSize: '15px', lineHeight: '1.6' }}>{results.ai_response}</p>
          </div>

          <div style={{ marginTop: '32px', textAlign: 'center' }}>
            <button onClick={() => { setView('splash'); setStep(1); }} style={buttonStyle('secondary')}>
              Thực hiện lại khảo sát
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        {/* Progress Bar */}
        <div style={progressBarStyle}>
          <div style={{ 
            width: `${(step / 4) * 100}%`, height: '100%', 
            backgroundColor: theme.colors.primary, transition: '0.3s ease' 
          }} />
        </div>

        {/* Step 1: Interests */}
        {step === 1 && (
          <div>
            <h2 style={{ marginBottom: '8px' }}>Bạn quan tâm đến điều gì?</h2>
            <p style={{ color: theme.colors.onSurfaceVariant, marginBottom: '24px' }}>Chọn ít nhất một sở thích để chúng tôi hiểu bạn hơn.</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '32px' }}>
              {options.interests.map(opt => (
                <div 
                  key={opt} 
                  onClick={() => handleToggleOption('interests', opt)}
                  style={chipStyle(answers.interests.includes(opt))}
                >
                  {opt}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Strengths */}
        {step === 2 && (
          <div>
            <h2 style={{ marginBottom: '8px' }}>Thế mạnh của bạn là gì?</h2>
            <p style={{ color: theme.colors.onSurfaceVariant, marginBottom: '24px' }}>Trí tuệ nhân tạo sẽ dựa trên kỹ năng của bạn để gợi ý ngành học.</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '32px' }}>
              {options.strengths.map(opt => (
                <div 
                  key={opt} 
                  onClick={() => handleToggleOption('strengths', opt)}
                  style={chipStyle(answers.strengths.includes(opt))}
                >
                  {opt}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Dislikes */}
        {step === 3 && (
          <div>
            <h2 style={{ marginBottom: '8px' }}>Bạn muốn tránh điều gì?</h2>
            <p style={{ color: theme.colors.onSurfaceVariant, marginBottom: '24px' }}>Biết được những điều bạn không thích giúp kết quả chính xác hơn.</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '32px' }}>
              {options.dislikes.map(opt => (
                <div 
                  key={opt} 
                  onClick={() => handleToggleOption('dislikes', opt)}
                  style={chipStyle(answers.dislikes.includes(opt))}
                >
                  {opt}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 4: Work Style */}
        {step === 4 && (
          <div>
            <h2 style={{ marginBottom: '8px' }}>Phong cách làm việc lý tưởng?</h2>
            <p style={{ color: theme.colors.onSurfaceVariant, marginBottom: '24px' }}>Bạn cảm thấy thoải mái nhất trong môi trường nào?</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '32px' }}>
              {options.workStyle.map(opt => (
                <div 
                  key={opt} 
                  onClick={() => setAnswers({ ...answers, work_style: opt })}
                  style={{
                    ...cardStyle,
                    maxWidth: 'none',
                    padding: '16px',
                    border: `1px solid ${answers.work_style === opt ? theme.colors.primary : theme.colors.outline}`,
                    backgroundColor: answers.work_style === opt ? theme.colors.surfaceContainer : 'transparent',
                    cursor: 'pointer'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ 
                      width: '20px', height: '20px', borderRadius: '50%', 
                      border: `2px solid ${theme.colors.primary}`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                      {answers.work_style === opt && <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: theme.colors.primary }} />}
                    </div>
                    <span style={{ fontWeight: answers.work_style === opt ? '600' : '400' }}>{opt}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div style={{ 
            padding: '12px', backgroundColor: '#fff5f5', color: theme.colors.error, 
            borderRadius: theme.rounded.default, marginBottom: '20px', fontSize: '14px' 
          }}>
            ⚠️ {error}. Vui lòng thử lại.
          </div>
        )}

        {/* Footer Actions */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
          {step > 1 ? (
            <button onClick={() => setStep(step - 1)} style={buttonStyle('secondary')}>
              Quay lại
            </button>
          ) : <div />}
          
          {step < 4 ? (
            <button 
              disabled={
                (step === 1 && answers.interests.length === 0) ||
                (step === 2 && answers.strengths.length === 0) ||
                (step === 3 && answers.dislikes.length === 0)
              }
              onClick={() => setStep(step + 1)} 
              style={{ 
                ...buttonStyle(),
                opacity: (
                  (step === 1 && answers.interests.length === 0) ||
                  (step === 2 && answers.strengths.length === 0) ||
                  (step === 3 && answers.dislikes.length === 0)
                ) ? 0.5 : 1
              }}
            >
              Tiếp theo
            </button>
          ) : (
            <button 
              disabled={!answers.work_style}
              onClick={handleSubmit} 
              style={{ 
                ...buttonStyle(),
                opacity: !answers.work_style ? 0.5 : 1
              }}
            >
              Xem kết quả
            </button>
          )}
        </div>
      </div>

      {/* Trust Signal (Academic Intelligence) */}
      <div style={{ marginTop: '32px', display: 'flex', alignItems: 'center', gap: '8px', opacity: 0.7 }}>
        <span style={{ fontSize: '12px', fontWeight: 'bold', color: theme.colors.accent }}>✦ AI INSIGHT</span>
        <span style={{ fontSize: '12px' }}>Powered by Academic Intelligence System</span>
      </div>
    </div>
  );
};

export default MajorMatchApp;