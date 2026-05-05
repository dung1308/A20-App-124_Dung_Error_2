import React, { useState } from 'react';
import { login } from '../services/auth';

const LoginPage = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await login(email, password);
      localStorage.setItem('token', data.token);
      onLoginSuccess(data.user_email);
    } catch (err) {
      setError('Email hoặc mật khẩu không chính xác');
    }
  };

  const containerStyle = {
    maxWidth: '400px',
    margin: '80px auto',
    padding: '40px 24px',
    border: '1px solid #e5e7eb',
    borderRadius: '10px',
    fontFamily: 'system-ui, -apple-system, sans-serif'
  };

  const inputStyle = {
    width: '100%',
    padding: '12px',
    marginBottom: '16px',
    border: '1px solid #e5e7eb',
    borderRadius: '6px',
    boxSizing: 'border-box'
  };

  const buttonStyle = {
    width: '100%',
    padding: '12px',
    backgroundColor: '#1a1a1a',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: '600'
  };

  return (
    <div style={containerStyle}>
      <h2 style={{ marginBottom: '24px', textAlign: 'center' }}>Đăng nhập</h2>
      {error && <p style={{ color: '#dc2626', fontSize: '14px', marginBottom: '16px' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <label style={{ display: 'block', marginBottom: '8px', color: '#6b7280' }}>Email</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} style={inputStyle} required />
        
        <label style={{ display: 'block', marginBottom: '8px', color: '#6b7280' }}>Mật khẩu</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={inputStyle} required />
        
        <button type="submit" style={buttonStyle}>Đăng nhập</button>
      </form>
    </div>
  );
};

export default LoginPage;