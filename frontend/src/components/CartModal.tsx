import React from 'react';
import { CartItem } from '../types/cart';

interface CartModalProps {
  isOpen: boolean;
  onClose: () => void;
  cartItems: CartItem[];
  onUpdateQuantity: (foodId: number, quantity: number) => void;
  onRemoveItem: (foodId: number) => void;
  onShowNameInput: () => void;
}

const CartModal: React.FC<CartModalProps> = ({
  isOpen,
  onClose,
  cartItems,
  onUpdateQuantity,
  onRemoveItem,
  onShowNameInput
}) => {
  const totalPrice = cartItems.reduce(
    (sum, item) => sum + item.food.price * item.quantity,
    0
  );

  const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <>
      <div 
        className={`modal-overlay ${isOpen ? 'active' : ''}`} 
        onClick={onClose}
      ></div>
      <div className={`cart-modal ${isOpen ? 'active' : ''}`}>
        <div className="cart-header">
          <h2>장바구니</h2>
          <button 
            className="close-button" 
            onClick={onClose}
          >
            ×
          </button>
        </div>
        
        <div className="cart-content">
          {cartItems.length === 0 ? (
            <div className="empty-cart">
              <div className="empty-cart-icon">🛒</div>
              <p className="empty-cart-text">장바구니가 비어있습니다</p>
            </div>
          ) : (
            <>
              <div className="cart-items">
                {cartItems.map((item) => (
                  <div key={item.food.id} className="cart-item">
                    <div className="cart-item-image">
                      {item.food.image && (
                        <img src={item.food.image} alt={item.food.name} />
                      )}
                    </div>
                    
                    <div className="cart-item-info">
                      <h3 className="cart-item-name">{item.food.name}</h3>
                      <p className="cart-item-price">
                        {item.food.price.toLocaleString()}원
                      </p>
                    </div>
                    
                    <div className="cart-item-controls">
                      <div className="quantity-controls">
                        <button
                          className="quantity-button"
                          onClick={() => onUpdateQuantity(item.food.id, item.quantity - 1)}
                        >
                          −
                        </button>
                        <span className="quantity">{item.quantity}</span>
                        <button
                          className="quantity-button"
                          onClick={() => onUpdateQuantity(item.food.id, item.quantity + 1)}
                        >
                          +
                        </button>
                      </div>
                      <button
                        className="remove-button"
                        onClick={() => onRemoveItem(item.food.id)}
                      >
                        삭제
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="cart-summary">
                <div className="cart-total">
                  <span>총 {totalItems}개</span>
                  <span>{totalPrice.toLocaleString()}원</span>
                </div>
                <button 
                  className="order-button" 
                  onClick={onShowNameInput}
                >
                  주문하기
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
};

export default CartModal;