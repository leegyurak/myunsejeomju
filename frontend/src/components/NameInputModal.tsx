import React, { useState, useEffect } from 'react';
import { CartItem } from '../types/cart';

interface NameInputModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (name: string) => void;
  isSubmitting: boolean;
  totalAmount: number;
  tableId: string;
  cartItems: CartItem[];
}

const NameInputModal: React.FC<NameInputModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  isSubmitting,
  totalAmount,
  tableId,
  cartItems
}) => {
  const [name, setName] = useState('');
  const [showBankSelection, setShowBankSelection] = useState(false);

  useEffect(() => {
    // Listen for messages from payment confirmation window
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'ORDER_COMPLETE') {
        // Payment completed - just close modal without creating another order
        onClose();
      }
    };

    window.addEventListener('message', handleMessage);
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, [name, onConfirm, onClose]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      // Store cart items in sessionStorage for payment confirmation window
      sessionStorage.setItem('paymentCartItems', JSON.stringify(cartItems));
      
      // Open payment confirmation window
      const confirmationUrl = `/payment-confirmation/${tableId}?payer_name=${encodeURIComponent(name.trim())}&total_amount=${totalAmount}`;
      
      // Check if it's mobile device
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
      
      let newWindow;
      
      if (isMobile) {
        // On mobile, open in new tab
        newWindow = window.open(confirmationUrl, '_blank');
      } else {
        // On desktop, open as popup window
        newWindow = window.open(
          confirmationUrl,
          'payment-confirmation',
          'width=500,height=700,scrollbars=yes,resizable=yes,menubar=no,toolbar=no,location=no,status=no'
        );
      }

      if (!newWindow) {
        alert('팝업이 차단되었습니다. 팝업을 허용해주세요.');
      }
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setName('');
      setShowBankSelection(false);
      onClose();
    }
  };

  const handleBankAppPayment = () => {
    setShowBankSelection(true);
  };

  const handleBankSelect = (bankName: string) => {
    if (name.trim()) {
      // Store cart items in sessionStorage for payment confirmation window
      sessionStorage.setItem('paymentCartItems', JSON.stringify(cartItems));
      
      // Open payment confirmation window with selected bank info
      const confirmationUrl = `/payment-confirmation/${tableId}?payer_name=${encodeURIComponent(name.trim())}&total_amount=${totalAmount}&payment_method=${encodeURIComponent(bankName)}`;
      
      // Check if it's mobile device
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
      
      let newWindow;
      
      if (isMobile) {
        // On mobile, open in new tab
        newWindow = window.open(confirmationUrl, '_blank');
      } else {
        // On desktop, open as popup window
        newWindow = window.open(
          confirmationUrl,
          'payment-confirmation',
          'width=500,height=700,scrollbars=yes,resizable=yes,menubar=no,toolbar=no,location=no,status=no'
        );
      }

      if (!newWindow) {
        alert('팝업이 차단되었습니다. 팝업을 허용해주세요.');
      } else {
        // Close bank selection after opening payment window
        setShowBankSelection(false);
      }
    }
  };

  const banks = ['우리', '하나', '카카오뱅크'];

  return (
    <>
      <div 
        className={`modal-overlay ${isOpen ? 'active' : ''}`} 
        onClick={isSubmitting ? undefined : handleClose}
      ></div>
      <div className={`name-input-modal ${isOpen ? 'active' : ''}`}>
        <div className="name-input-header">
          <h2>주문자 이름 입력</h2>
          <button 
            className="close-button" 
            onClick={handleClose}
            disabled={isSubmitting}
          >
            ×
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="name-input-form">
          <div className="name-input-field">
            <label htmlFor="customerName">이름</label>
            <input
              id="customerName"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="주문자 이름을 입력해주세요"
              disabled={isSubmitting}
              autoFocus
            />
            <p className="payment-verification-message">
              주문자명은 입금자명과 동일하게 입력 부탁 드립니다.
            </p>
          </div>
          
          {!showBankSelection ? (
            <div className="name-input-buttons">
              <button 
                type="button" 
                className="cancel-button"
                onClick={handleBankAppPayment}
                disabled={!name.trim() || isSubmitting}
              >
                은행앱으로 결제하기
              </button>
              <button 
                type="submit" 
                className="confirm-button"
                disabled={!name.trim() || isSubmitting}
              >
                토스로 결제하기
              </button>
            </div>
          ) : (
            <div className="bank-selection">
              <h3>은행앱을 선택해주세요</h3>
              <div className="bank-buttons">
                {banks.map((bank) => (
                  <button
                    key={bank}
                    type="button"
                    className="bank-button"
                    onClick={() => handleBankSelect(bank)}
                    disabled={isSubmitting}
                  >
                    {bank}
                  </button>
                ))}
              </div>
              <button
                type="button"
                className="back-button"
                onClick={() => setShowBankSelection(false)}
                disabled={isSubmitting}
              >
                뒤로가기
              </button>
            </div>
          )}
        </form>
      </div>
    </>
  );
};

export default NameInputModal;