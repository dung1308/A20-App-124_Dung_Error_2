import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../state/store';
import { api } from '../services/api';
import Step1 from '../components/Wizard/Step1';
import Step2 from '../components/Wizard/Step2';
import Step3 from '../components/Wizard/Step3';
import Step4 from '../components/Wizard/Step4';
import CVUpload from '../components/CVUpload/CVUpload';

const WizardPage = () => {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const { userId, wizardData, setWizardData, setMatchResults, cvText, cvSignals } = useStore();
  const navigate = useNavigate();

  const stepsMap = {
    0: (
      <div className="step-container">
        <h2 className="text-2xl font-black text-blue-900 mb-4">Chào mừng bạn!</h2>
        <p className="text-slate-600 mb-8">Để bắt đầu, bạn có thể tải lên CV để AI hiểu rõ hơn về năng lực và kinh nghiệm của bạn.</p>
        <CVUpload />
      </div>
    ),
    1: <Step1 data={wizardData.interests} onUpdate={setWizardData} />,
    2: <Step2 data={wizardData.strengths} onUpdate={setWizardData} />,
    3: <Step3 data={wizardData.dislikes} onUpdate={setWizardData} />,
    4: <Step4 data={wizardData.work_style} onUpdate={setWizardData} />,
  };

  /**
   * Basic validation to ensure the student has selected 
   * at least one option before proceeding.
   */
  const validateStep = () => {
    if (step === 0) return true; // CV step is optional
    if (step === 1) return wizardData.interests.length > 0;
    if (step === 2) return wizardData.strengths.length > 0;
    if (step === 3) return wizardData.dislikes.length > 0;
    if (step === 4) return wizardData.work_style !== '';
    return false;
  };

  const handleNext = () => {
    if (validateStep()) {
      setStep(s => s + 1);
    } else {
      alert("Vui lòng chọn ít nhất một lựa chọn để tiếp tục.");
    }
  };

  const handleSubmit = async () => {
    if (!validateStep()) {
      alert("Vui lòng hoàn thành bước này trước khi xem kết quả.");
      return;
    }

    setLoading(true);
    try {
      // Calls the /api/match endpoint to get structured Top 3 recommendations
      const result = await api.postMatch({ 
        user_id: userId, 
        answers: wizardData, 
        cv_text: cvText,
        cv_signals: cvSignals 
      });
      setMatchResults(result);
      navigate('/dashboard');
    } catch (err) {
      console.error("Match submission failed:", err);
      alert("Không thể tải kết quả. Vui lòng kiểm tra lại thông tin hoặc thử lại sau.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="wizard-page min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-3xl shadow-xl border border-slate-100 overflow-hidden">
        {/* Top Progress Bar */}
        <div className="h-2 bg-slate-100 w-full">
          <div 
            className="h-full bg-blue-900 transition-all duration-500" 
            style={{ width: `${(step / 4) * 100}%` }}
          ></div>
        </div>

        <div className="p-8 md:p-12">
          <div className="flex justify-between items-center mb-10">
            <span className="text-[10px] uppercase tracking-widest font-black text-blue-900/40">Step {step} of 4</span>
            <h1 className="text-sm font-bold text-blue-900">Brilliant Mentor AI</h1>
          </div>

          <div className="step-content min-h-[300px] w-full flex flex-col justify-start">
            {stepsMap[step]}
          </div>
          
          <div className="nav-buttons mt-12 flex justify-between gap-4">
            {step > 0 ? (
              <button onClick={() => setStep(step - 1)} className="px-6 py-3 text-slate-500 font-bold hover:text-blue-900 transition-colors">Quay lại</button>
            ) : <div></div>}
            
            {step < 4 ? (
              <button onClick={handleNext} className="px-10 py-3 bg-blue-900 text-white rounded-xl font-bold shadow-lg shadow-blue-900/20 active:scale-95 transition-all">Tiếp theo</button>
            ) : (
              <button onClick={handleSubmit} disabled={loading} className="px-10 py-3 bg-blue-900 text-white rounded-xl font-bold shadow-lg shadow-blue-900/20 active:scale-95 transition-all disabled:opacity-50">
                {loading ? "Đang xử lý..." : "Xem kết quả"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default WizardPage;