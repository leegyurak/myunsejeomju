import React, { useEffect, useState } from 'react';

interface PaymentIncompleteMessageProps {
  isVisible: boolean;
  onComplete: () => void;
  onRetry?: () => void;
}

const PaymentIncompleteMessage: React.FC<PaymentIncompleteMessageProps> = ({ 
  isVisible, 
  onComplete,
  onRetry 
}) => {
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isVisible) {
      setIsAnimating(true);
      
      const timer = setTimeout(() => {
        setIsAnimating(false);
        setTimeout(onComplete, 500); // 페이드아웃 애니메이션 시간
      }, 3000); // 3초간 표시

      return () => clearTimeout(timer);
    }
  }, [isVisible, onComplete]);

  const handleRetry = () => {
    if (onRetry) {
      setIsAnimating(false);
      setTimeout(() => {
        onComplete();
        onRetry();
      }, 500);
    }
  };

  if (!isVisible && !isAnimating) return null;

  return (
    <div className={`payment-incomplete-overlay ${isAnimating ? 'active' : ''}`}>
      <div className={`payment-incomplete-message ${isAnimating ? 'active' : ''}`}>
        <div className="incomplete-icon">
          ⚠️
        </div>
        <h2 className="incomplete-title">결제가 아직 완료되지 않은 것 같아요!</h2>
        <p className="incomplete-subtitle">결제를 다시 시도하거나 잠시 후 다시 확인해주세요</p>
        {onRetry && (
          <div className="incomplete-buttons">
            <button 
              className="incomplete-close-btn"
              onClick={() => {
                setIsAnimating(false);
                setTimeout(onComplete, 500);
              }}
            >
              닫기
            </button>
            <button 
              className="incomplete-retry-btn"
              onClick={handleRetry}
            >
              다시 결제하기
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PaymentIncompleteMessage;