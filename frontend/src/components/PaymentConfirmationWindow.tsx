import React, { useEffect, useState, useMemo } from 'react';
import { apiService } from '../services/api';
import PaymentIncompleteMessage from './PaymentIncompleteMessage';
import { CartItem } from '../types/cart';

interface PaymentConfirmationWindowProps {
  tableId: string;
  payerName: string;
  totalAmount: number;
  cartItems: CartItem[];
  onOrderComplete: () => void;
}

const PaymentConfirmationWindow: React.FC<PaymentConfirmationWindowProps> = ({
  tableId,
  payerName,
  totalAmount,
  cartItems,
  onOrderComplete
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [redirectUrl, setRedirectUrl] = useState<string>('');
  const [orderId, setOrderId] = useState<string>('');
  const [showIncompleteMessage, setShowIncompleteMessage] = useState(false);
  const [isCheckingPayment, setIsCheckingPayment] = useState(false);

  // 모바일 환경 감지 (useMemo로 메모이제이션)
  const isMobile = useMemo(() => 
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
    []
  );

  useEffect(() => {
    // Call pre-order API in background when component mounts
    const callPreOrderAPI = async () => {
      try {
        // Convert cartItems to API format
        const orderItems = cartItems.map(item => ({
          food_id: item.food.id,
          quantity: item.quantity
        }));
        
        const response = await apiService.createPreOrder(tableId, payerName, totalAmount, orderItems);
        
        console.log('Pre-order API response:', response);
        setRedirectUrl(response.redirect_url);
        setOrderId(response.order_id);
        
        if (response.redirect_url) {
          // Automatically open payment page after API response
          if (isMobile) {
            // 모바일에서는 직접 리다이렉트
            console.log('Mobile detected: Redirecting directly to payment page:', response.redirect_url);
            window.location.href = response.redirect_url;
          } else {
            // 데스크톱에서는 새 창에서 열기
            console.log('Desktop detected: Opening payment page in new window:', response.redirect_url);
            const paymentWindow = window.open(response.redirect_url, '_blank');
            
            if (!paymentWindow) {
              alert('팝업이 차단되었습니다. 팝업을 허용하고 수동으로 결제 페이지로 이동해주세요.');
            }
          }
        } else {
          console.error('No redirect URL received from API');
          alert('결제 페이지 URL을 받지 못했습니다. 다시 시도해주세요.');
        }
        
      } catch (error) {
        console.error('Pre-order API call failed:', error);
        alert('주문 준비 중 오류가 발생했습니다. 다시 시도해주세요.');
      }
    };

    callPreOrderAPI();
  }, [tableId, payerName, totalAmount, cartItems, isMobile]);

  // 로딩 상태 제거 - 바로 결제 완료 확인 UI 표시

  const handlePaymentComplete = async () => {
    if (isSubmitting) return;
    
    // orderId가 아직 없으면 잠시 대기
    if (!orderId) {
      alert('주문 준비 중입니다. 잠시 후 다시 시도해주세요.');
      return;
    }
    
    setIsSubmitting(true);
    setIsCheckingPayment(true);
    
    try {
      // 5초 로딩 대기
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      // 결제 상태 확인
      const paymentStatus = await apiService.checkPaymentStatus(orderId);
      
      if (paymentStatus.payment_completed) {
        // 결제가 완료된 경우 - 팝업 없이 바로 완료 처리
        onOrderComplete();
        window.close();
      } else {
        // 결제가 완료되지 않은 경우 - 예쁜 메시지 표시
        setShowIncompleteMessage(true);
      }
    } catch (error) {
      console.error('Payment verification failed:', error);
      alert('결제 확인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    } finally {
      setIsSubmitting(false);
      setIsCheckingPayment(false);
    }
  };

  const handleIncompleteMessageComplete = () => {
    setShowIncompleteMessage(false);
  };

  const handleRetryPayment = () => {
    // 모바일/데스크톱에 따라 다르게 처리
    if (isMobile) {
      // 모바일에서는 직접 리다이렉트
      window.location.href = redirectUrl;
    } else {
      // 데스크톱에서는 새 창에서 열기
      window.open(redirectUrl, '_blank');
    }
  };

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
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#1c1c1e',
          marginBottom: '16px',
          margin: '0 0 16px 0'
        }}>
          결제 완료 확인
        </h2>
        
        <div style={{
          backgroundColor: '#f8f9fa',
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '24px',
          border: '1px solid #e9ecef'
        }}>
          <p style={{
            fontSize: '16px',
            color: '#333',
            marginBottom: '12px',
            margin: '0 0 12px 0'
          }}>
{isMobile ? '결제를 완료한 후 아래 버튼을 눌러주세요' : '새 창에서 결제를 완료한 후 아래 버튼을 눌러주세요'}
          </p>
          <p style={{
            fontSize: '18px',
            fontWeight: '700',
            color: '#1e40af',
            background: 'rgba(30, 64, 175, 0.1)',
            padding: '8px 16px',
            borderRadius: '8px',
            display: 'inline-block',
            margin: '0'
          }}>
            결제 금액: {totalAmount.toLocaleString()}원
          </p>
          
          {redirectUrl && (
            <div style={{ marginTop: '16px' }}>
              <p style={{
                fontSize: '12px',
                color: '#8e8e93',
                margin: '0 0 8px 0'
              }}>
                결제 페이지가 자동으로 열리지 않는 경우:
              </p>
              <button
                onClick={() => {
                  if (isMobile) {
                    window.location.href = redirectUrl;
                  } else {
                    window.open(redirectUrl, '_blank');
                  }
                }}
                style={{
                  backgroundColor: '#f8f9fa',
                  color: '#1e40af',
                  border: '1px solid #1e40af',
                  padding: '8px 16px',
                  borderRadius: '8px',
                  fontSize: '14px',
                  cursor: 'pointer',
                  textDecoration: 'none'
                }}
              >
                결제 페이지로 이동
              </button>
            </div>
          )}
        </div>

        <button
          onClick={handlePaymentComplete}
          disabled={isSubmitting}
          style={{
            width: '100%',
            backgroundColor: isSubmitting ? '#d1d1d6' : '#1e40af',
            color: 'white',
            border: 'none',
            padding: '16px 20px',
            borderRadius: '12px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: isSubmitting ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px'
          }}
          onMouseOver={(e) => {
            if (!isSubmitting) {
              (e.target as HTMLButtonElement).style.backgroundColor = '#1d4ed8';
            }
          }}
          onMouseOut={(e) => {
            if (!isSubmitting) {
              (e.target as HTMLButtonElement).style.backgroundColor = '#1e40af';
            }
          }}
        >
          {isSubmitting ? (
            <>
              <div style={{
                width: '16px',
                height: '16px',
                border: '2px solid #8e8e93',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <span>{isCheckingPayment ? '결제 확인 중...' : '준비 중...'}</span>
            </>
          ) : !orderId ? (
            '주문 준비 중...'
          ) : (
            '결제 완료 확인'
          )}
        </button>
        
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
      
      <PaymentIncompleteMessage
        isVisible={showIncompleteMessage}
        onComplete={handleIncompleteMessageComplete}
        onRetry={handleRetryPayment}
      />
    </div>
  );
};

export default PaymentConfirmationWindow;