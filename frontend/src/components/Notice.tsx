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
          <span>첫 주문 시, 메인메뉴 1개 이상 주문 필수입니다.</span>
        </div>
        <div className="notice-item">
          <span className="notice-number">2)</span>
          <span>주점 이용 시간은 첫 주문 시간으로부터 <strong>1시간 30분</strong> 입니다.</span>
        </div>
        <div className="notice-item">
          <span className="notice-number">3)</span>
          <span>테이블 자리비움은 10분까지 입니다.<br />초과 시 안내 없이 테이블 정리할 예정이오니 자리비움에 유의해 주시기 바랍니다.</span>
        </div>
      </div>
    </div>
  );
};

export default Notice;