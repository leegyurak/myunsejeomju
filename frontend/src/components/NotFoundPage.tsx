import React from 'react';

const NotFoundPage: React.FC = () => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      padding: '20px',
      textAlign: 'center'
    }}>
      <h1 style={{
        fontSize: '48px',
        marginBottom: '20px',
        color: '#333'
      }}>
        면세주점에서 만나요!
      </h1>
      <p style={{
        fontSize: '18px',
        color: '#666',
        lineHeight: '1.6'
      }}>
        존재하지 않는 테이블이거나 잘못된 요청입니다.<br />
        올바른 QR 코드를 스캔해 주세요.
      </p>
    </div>
  );
};

export default NotFoundPage;