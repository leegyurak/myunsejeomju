import React from 'react';

interface CartButtonProps {
  onCartOpen: () => void;
  cartItemCount: number;
}

const CartButton: React.FC<CartButtonProps> = ({ onCartOpen, cartItemCount }) => {
  return (
    <button className="cart-button" onClick={onCartOpen}>
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 3H5L5.4 5M7 13H17L21 5H5.4M7 13L5.4 5M7 13L4.7 15.3C4.3 15.7 4.6 16.5 5.1 16.5H17M17 13V17C17 18.1 16.1 19 15 19H9C7.9 19 7 18.1 7 17V13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
      {cartItemCount > 0 && (
        <span className="cart-badge">{cartItemCount}</span>
      )}
    </button>
  );
};

export default CartButton;