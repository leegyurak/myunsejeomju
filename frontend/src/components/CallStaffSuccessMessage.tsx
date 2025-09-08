import React, { useEffect, useState } from 'react';

interface CallStaffSuccessMessageProps {
  isVisible: boolean;
  onComplete: () => void;
}

const CallStaffSuccessMessage: React.FC<CallStaffSuccessMessageProps> = ({ 
  isVisible, 
  onComplete 
}) => {
  const [showMessage, setShowMessage] = useState(false);

  useEffect(() => {
    if (isVisible) {
      setShowMessage(true);
      const timer = setTimeout(() => {
        setShowMessage(false);
        setTimeout(onComplete, 400);
      }, 2500);

      return () => clearTimeout(timer);
    }
  }, [isVisible, onComplete]);

  if (!isVisible) return null;

  return (
    <div className={`call-staff-success-overlay ${showMessage ? 'active' : ''}`}>
      <div className={`call-staff-success-message ${showMessage ? 'active' : ''}`}>
        <div className="call-staff-success-icon">📞</div>
        <div className="call-staff-success-title">직원이 호출되었습니다!</div>
        <div className="call-staff-success-subtitle">잠시만 기다려주세요.</div>
      </div>
    </div>
  );
};

export default CallStaffSuccessMessage;