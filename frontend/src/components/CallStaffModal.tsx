import React, { useState } from 'react';

interface CallStaffModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (message: string) => void;
  tableId: string;
  isSubmitting?: boolean;
}

const CallStaffModal: React.FC<CallStaffModalProps> = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  tableId, 
  isSubmitting = false 
}) => {
  const [message, setMessage] = useState<string>('');

  const handleSubmit = () => {
    if (message.trim()) {
      onSubmit(message.trim());
      setMessage('');
    }
  };

  const handleClose = () => {
    setMessage('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay active" onClick={handleClose}></div>
      <div className="call-staff-modal active">
        <div className="call-staff-header">
          <h2>직원 호출</h2>
          <button 
            className="close-button" 
            onClick={handleClose}
            disabled={isSubmitting}
          >
            ×
          </button>
        </div>
        <div className="call-staff-form">
          <div className="call-staff-field">
            <label htmlFor="message">메시지</label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="직원에게 전달할 메시지를 입력해주세요."
              rows={4}
              disabled={isSubmitting}
            />
          </div>
          <div className="call-staff-buttons">
            <button 
              className="cancel-button" 
              onClick={handleClose}
              disabled={isSubmitting}
            >
              취소
            </button>
            <button 
              className="call-button" 
              onClick={handleSubmit}
              disabled={isSubmitting || !message.trim()}
            >
              {isSubmitting ? (
                <>
                  <span className="loading-spinner"></span>
                  호출 중...
                </>
              ) : (
                '호출하기'
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default CallStaffModal;