import React, { useState } from 'react';
import { OrderHistory } from '../types/order';

interface ReceiptModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderHistory: OrderHistory;
  onResetOrderHistory: () => void;
}

const ReceiptModal: React.FC<ReceiptModalProps> = ({ isOpen, onClose, orderHistory, onResetOrderHistory }) => {
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('ko-KR', {
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const handleResetButtonClick = () => {
    setShowConfirmModal(true);
  };

  const handleConfirmReset = () => {
    setShowConfirmModal(false);
    onResetOrderHistory();
  };

  const handleCancelReset = () => {
    setShowConfirmModal(false);
  };

  return (
    <>
      <div className={`modal-overlay ${isOpen ? 'active' : ''}`} onClick={onClose}></div>
      <div className={`receipt-modal ${isOpen ? 'active' : ''}`}>
        <div className="receipt-header">
          <h2>주문 내역</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="receipt-content">
          {orderHistory.orders.length === 0 ? (
            <div className="empty-receipt">
              <div className="empty-receipt-icon">📋</div>
              <p className="empty-receipt-text">아직 주문 내역이 없습니다</p>
            </div>
          ) : (
            <>
              <div className="receipt-summary">
                <div className="total-spent">
                  <span className="label">총 결제금액</span>
                  <span className="amount">{orderHistory.totalSpent.toLocaleString()}원</span>
                </div>
                <div className="order-count">
                  <span className="count">{orderHistory.orders.length}건의 주문</span>
                </div>
              </div>
              
              <div className="receipt-orders">
                {orderHistory.orders.map((order) => (
                  <div key={order.id} className="receipt-order">
                    <div className="order-info">
                      <div className="order-date">{formatDate(order.orderDate)}</div>
                      <div className="order-status">
                        <span className={`status ${order.status}`}>
                          완료
                        </span>
                      </div>
                    </div>
                    
                    <div className="order-items">
                      {order.items.map((item, index) => (
                        <div key={index} className="receipt-item">
                          <div className="item-info">
                            <span className="item-name">{item.food.name}</span>
                            <span className="item-quantity">×{item.quantity}</span>
                          </div>
                          <div className="item-price">
                            {(item.price * item.quantity).toLocaleString()}원
                          </div>
                        </div>
                      ))}
                      {order.minusItems?.map((item, index) => (
                        <div key={`minus-${index}`} className="receipt-item minus-item">
                          <div className="item-info">
                            <span className="item-name">{item.food.name} (품절 차감)</span>
                            <span className="item-quantity">×{Math.abs(item.quantity)}</span>
                          </div>
                          <div className="item-price minus-price">
                            -{(item.price * Math.abs(item.quantity)).toLocaleString()}원
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="order-total">
                      <span className="total-label">합계</span>
                      <span className="total-amount">{order.totalAmount.toLocaleString()}원</span>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="receipt-actions">
                <button 
                  className="reset-order-history-btn"
                  onClick={handleResetButtonClick}
                >
                  <span className="reset-btn-icon">🗑️</span>
                  <span className="reset-btn-text">주문 내역 초기화</span>
                </button>
              </div>
            </>
          )}
        </div>
      </div>
      
      {/* Reset Confirmation Modal */}
      {showConfirmModal && (
        <>
          <div className="modal-overlay active reset-confirm-overlay" onClick={handleCancelReset}></div>
          <div className="reset-confirm-modal active">
            <div className="reset-confirm-content">
              <div className="reset-confirm-icon">⚠️</div>
              <h3 className="reset-confirm-title">주문 내역 초기화</h3>
              <p className="reset-confirm-message">
                모든 주문 내역을 초기화하시겠습니까?
              </p>
              <p className="reset-confirm-warning">
                이 작업은 되돌릴 수 없습니다.
              </p>
              <div className="reset-confirm-buttons">
                <button 
                  className="reset-cancel-btn"
                  onClick={handleCancelReset}
                >
                  취소
                </button>
                <button 
                  className="reset-confirm-btn"
                  onClick={handleConfirmReset}
                >
                  초기화
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default ReceiptModal;