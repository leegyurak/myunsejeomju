import React, { useState, useEffect } from 'react';

interface QRModalProps {
  isOpen: boolean;
  onClose: () => void;
  tableId?: string;
}

const QRModal: React.FC<QRModalProps> = ({ isOpen, onClose, tableId }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [startY, setStartY] = useState(0);

  const handleTouchStart = (e: React.TouchEvent) => {
    setIsDragging(true);
    setStartY(e.touches[0].clientY);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;
    
    const currentY = e.touches[0].clientY;
    const deltaY = currentY - startY;
    
    if (deltaY > 50) {
      onClose();
      setIsDragging(false);
    }
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    setStartY(e.clientY);
  };

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      
      const currentY = e.clientY;
      const deltaY = currentY - startY;
      
      if (deltaY > 50) {
        onClose();
        setIsDragging(false);
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, startY, onClose]);

  return (
    <>
      <div className={`modal-overlay ${isOpen ? 'active' : ''}`} onClick={onClose}></div>
      <div className={`qr-modal ${isOpen ? 'active' : ''}`}>
        <div 
          className="qr-modal-handle"
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          onMouseDown={handleMouseDown}
        ></div>
        <h2>결제 QR 코드</h2>
        <div className="qr-code">
          QR 코드가 여기에 표시됩니다
          {tableId && <div style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>테이블 ID: {tableId}</div>}
        </div>
      </div>
    </>
  );
};

export default QRModal;