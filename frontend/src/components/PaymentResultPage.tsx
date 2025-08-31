import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { apiService } from '../services/api';

interface PaymentIncompleteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRetry: () => void;
}

const PaymentIncompleteModal: React.FC<PaymentIncompleteModalProps> = ({
  isOpen,
  onClose,
  onRetry
}) => {
  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay active" onClick={onClose}></div>
      <div className="payment-incomplete-modal active">
        <div className="payment-incomplete-content">
          <h2>결제 확인</h2>
          <p className="payment-incomplete-message">
            결제가 아직 완료되지 않은 것 같아요!
          </p>
          <p className="payment-incomplete-submessage">
            결제를 다시 시도하거나 잠시 후 다시 확인해주세요.
          </p>
          <div className="payment-incomplete-buttons">
            <button 
              type="button" 
              className="cancel-button"
              onClick={onClose}
            >
              닫기
            </button>
            <button 
              type="button" 
              className="retry-button"
              onClick={onRetry}
            >
              다시 결제하기
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

const PaymentResultPage: React.FC = () => {
  const { tableId } = useParams<{ tableId: string }>();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [showIncompleteModal, setShowIncompleteModal] = useState(false);
  const [orderData, setOrderData] = useState<{
    orderId: string;
    payerName: string;
    totalAmount: number;
  } | null>(null);

  const checkPaymentStatus = useCallback(async (orderId: string) => {
    try {
      setIsLoading(true);
      
      // Add a small delay to allow payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const paymentStatus = await apiService.checkPaymentStatus(orderId);
      
      if (paymentStatus.payment_completed) {
        // Payment successful - redirect to table page
        navigate(`/table/${tableId}`, { 
          state: { paymentSuccess: true },
          replace: true 
        });
      } else {
        // Payment not completed - show modal
        setShowIncompleteModal(true);
      }
    } catch (error) {
      console.error('Payment status check failed:', error);
      setShowIncompleteModal(true);
    } finally {
      setIsLoading(false);
    }
  }, [navigate, tableId]);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const orderId = urlParams.get('orderId');
    const payerName = urlParams.get('payerName');
    const totalAmount = urlParams.get('totalAmount');

    if (!tableId || !orderId || !payerName || !totalAmount) {
      navigate(`/table/${tableId || 'default'}`);
      return;
    }

    setOrderData({
      orderId,
      payerName,
      totalAmount: parseInt(totalAmount)
    });

    checkPaymentStatus(orderId);
  }, [tableId, navigate, checkPaymentStatus]);

  const handleRetryPayment = () => {
    if (orderData) {
      // Navigate back to payment confirmation with the same data
      const confirmationUrl = `/payment-confirmation/${tableId}?payer_name=${encodeURIComponent(orderData.payerName)}&total_amount=${orderData.totalAmount}`;
      window.location.href = confirmationUrl;
    }
  };

  const handleCloseModal = () => {
    setShowIncompleteModal(false);
    navigate(`/table/${tableId}`, { replace: true });
  };

  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f8f9fa',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '40px',
          borderRadius: '16px',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
          textAlign: 'center',
          maxWidth: '400px',
          width: '90%'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '4px solid #e9ecef',
            borderTop: '4px solid #1e40af',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px'
          }} />
          <h2 style={{
            fontSize: '20px',
            fontWeight: '600',
            color: '#1c1c1e',
            margin: '0 0 8px 0'
          }}>
            결제 확인 중...
          </h2>
          <p style={{
            fontSize: '14px',
            color: '#8e8e93',
            margin: '0'
          }}>
            결제 상태를 확인하고 있습니다
          </p>
          
          <style>
            {`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}
          </style>
        </div>
      </div>
    );
  }

  return (
    <div>
      <PaymentIncompleteModal
        isOpen={showIncompleteModal}
        onClose={handleCloseModal}
        onRetry={handleRetryPayment}
      />
    </div>
  );
};

export default PaymentResultPage;