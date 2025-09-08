import React from 'react';
import './Notice.css';

const Notice: React.FC = () => {
  return (
    <div className="notice-container">
      <div className="notice-header">
        <span className="notice-icon">📢</span>
        <h3>이용 안내</h3>
      </div>
      <div className="notice-content">
        <div className="notice-item">
          <span className="notice-number">1)</span>
          <span>첫 주문시, 메인메뉴 1개이상 주문 부탁 드립니다.</span>
        </div>
        <div className="notice-item">
          <span className="notice-number">2)</span>
          <span>주점 이용시간은 첫 주문시간으로부터 1시간 30분 입니다.</span>
        </div>
        <div className="notice-item">
          <span className="notice-number">3)</span>
          <span>테이블 전 인원 공석이 10분 지속되는 경우 테이블 정리 진행될 예정입니다.</span>
        </div>
      </div>
    </div>
  );
};

export default Notice;