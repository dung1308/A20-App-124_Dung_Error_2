import { create } from 'zustand';

const initialState = {
  wizardData: {
    interests: [],
    strengths: [],
    dislikes: [],
    work_style: ''
  },
  cvText: '',
  matchResults: null,
};

export const useStore = create((set) => ({
  userId: localStorage.getItem('user_email') || `user_${Math.random().toString(36).substr(2, 9)}`,
  role: localStorage.getItem('user_role') || 'user',
  ...initialState,
  
  setUserId: (id) => set({ userId: id }),
  setRole: (role) => set({ role }),
  setWizardData: (data) => set((state) => ({ 
    wizardData: { ...state.wizardData, ...data } 
  })),
  setCVText: (text) => set({ cvText: text }),
  setMatchResults: (results) => set({ matchResults: results }),
  
  /**
   * Resets the wizard progress while keeping the same userId
   */
  resetWizard: () => set((state) => ({ ...initialState }))
}));