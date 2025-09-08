import React from 'react';

interface MainMenuRequiredModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const MainMenuRequiredModal: React.FC<MainMenuRequiredModalProps> = ({
  isOpen,
  onClose
}) => {
  return (
    <>
      <div 
        className={`modal-overlay ${isOpen ? 'active' : ''}`} 
        onClick={onClose}
      ></div>
      <div className={`main-menu-required-modal ${isOpen ? 'active' : ''}`}>
        <div className="main-menu-required-header">
          <h2>메인메뉴가 필요해요!</h2>
          <button 
            className="close-button" 
            onClick={onClose}
          >
            ×
          </button>
        </div>
        
        <div className="main-menu-required-content">
          <div className="main-menu-required-icon">🍝</div>
          <p className="main-menu-required-message">
            메인메뉴를 하나 담아주세요!
          </p>
          <p className="main-menu-required-submessage">
            첫 주문시에는 사이드 메뉴만 주문하실 수 없어요
          </p>
        </div>
        
        <div className="main-menu-required-buttons">
          <button 
            className="main-menu-required-button"
            onClick={onClose}
          >
            확인
          </button>
        </div>
      </div>
    </>
  );
};

export default MainMenuRequiredModal;