import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { apiService } from '../services/api';

const PaymentSuccessPage: React.FC = () => {
  const { tableId } = useParams<{ tableId: string }>();
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(true);
  const [orderData, setOrderData] = useState<{
    orderId: string;
    payerName: string;
    totalAmount: number;
  } | null>(null);

  const processSuccessfulPayment = useCallback(async (orderId: string) => {
    try {
      setIsProcessing(true);
      
      // Verify payment status first
      const paymentStatus = await apiService.checkPaymentStatus(orderId);
      
      if (paymentStatus.payment_completed) {
        // Show success message briefly then redirect
        setTimeout(() => {
          navigate(`/table/${tableId}`, { 
            state: { paymentSuccess: true },
            replace: true 
          });
        }, 3000);
      } else {
        // If payment not completed, redirect to result page for retry
        navigate(`/payment-result/${tableId}?orderId=${orderId}&payerName=${orderData?.payerName}&totalAmount=${orderData?.totalAmount}`, { replace: true });
      }
    } catch (error) {
      console.error('Payment verification failed:', error);
      // On error, redirect to result page for retry
      setTimeout(() => {
        navigate(`/payment-result/${tableId}?orderId=${orderId}&payerName=${orderData?.payerName}&totalAmount=${orderData?.totalAmount}`, { replace: true });
      }, 2000);
    } finally {
      setIsProcessing(false);
    }
  }, [navigate, tableId, orderData]);

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

    processSuccessfulPayment(orderId);
  }, [tableId, navigate, processSuccessfulPayment]);

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
        {isProcessing ? (
          <>
            <div style={{
              width: '60px',
              height: '60px',
              border: '4px solid #e9ecef',
              borderTop: '4px solid #34c759',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 24px'
            }} />
            <h2 style={{
              fontSize: '22px',
              fontWeight: '700',
              color: '#1c1c1e',
              margin: '0 0 12px 0'
            }}>
              결제 완료 처리 중...
            </h2>
            <p style={{
              fontSize: '16px',
              color: '#8e8e93',
              margin: '0 0 16px 0'
            }}>
              결제가 완료되었습니다.
            </p>
            {orderData && (
              <div style={{
                backgroundColor: '#f8f9fa',
                padding: '16px',
                borderRadius: '12px',
                marginBottom: '16px'
              }}>
                <p style={{
                  fontSize: '14px',
                  color: '#333',
                  margin: '0 0 8px 0'
                }}>
                  주문자: {orderData.payerName}
                </p>
                <p style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#34c759',
                  margin: '0'
                }}>
                  결제 금액: {orderData.totalAmount.toLocaleString()}원
                </p>
              </div>
            )}
            <p style={{
              fontSize: '14px',
              color: '#8e8e93',
              margin: '0'
            }}>
              잠시 후 주문 페이지로 이동합니다.
            </p>
          </>
        ) : (
          <>
            <div style={{
              width: '60px',
              height: '60px',
              backgroundColor: '#34c759',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 24px',
              color: 'white',
              fontSize: '24px'
            }}>
              ✓
            </div>
            <h2 style={{
              fontSize: '22px',
              fontWeight: '700',
              color: '#34c759',
              margin: '0 0 12px 0'
            }}>
              결제 완료!
            </h2>
            <p style={{
              fontSize: '16px',
              color: '#8e8e93',
              margin: '0'
            }}>
              주문 페이지로 이동 중입니다...
            </p>
          </>
        )}
        
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
};

export default PaymentSuccessPage;