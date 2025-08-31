import React, { useEffect, useState } from 'react';

interface OrderSuccessMessageProps {
  isVisible: boolean;
  onComplete: () => void;
}

const OrderSuccessMessage: React.FC<OrderSuccessMessageProps> = ({ 
  isVisible, 
  onComplete 
}) => {
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isVisible) {
      setIsAnimating(true);
      
      const timer = setTimeout(() => {
        setIsAnimating(false);
        setTimeout(onComplete, 500); // 페이드아웃 애니메이션 시간
      }, 2000); // 2초간 표시

      return () => clearTimeout(timer);
    }
  }, [isVisible, onComplete]);

  if (!isVisible && !isAnimating) return null;

  return (
    <div className={`order-success-overlay ${isAnimating ? 'active' : ''}`}>
      <div className={`order-success-message ${isAnimating ? 'active' : ''}`}>
        <div className="success-icon">
          ✅
        </div>
        <h2 className="success-title">주문이 완료되었습니다!</h2>
        <p className="success-subtitle">곧 준비해드리겠습니다</p>
      </div>
    </div>
  );
};

export default OrderSuccessMessage;