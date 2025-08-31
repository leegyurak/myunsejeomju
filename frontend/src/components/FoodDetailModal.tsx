import React from 'react';
import { FoodItem } from '../types/food';

interface FoodDetailModalProps {
  food: FoodItem | null;
  isOpen: boolean;
  onClose: () => void;
  onAddToCart: (food: FoodItem) => void;
}

const FoodDetailModal: React.FC<FoodDetailModalProps> = ({ 
  food, 
  isOpen, 
  onClose, 
  onAddToCart 
}) => {
  if (!food) return null;

  const handleAddToCart = () => {
    onAddToCart(food);
    onClose();
  };

  return (
    <>
      <div 
        className={`modal-overlay ${isOpen ? 'active' : ''}`} 
        onClick={onClose}
      ></div>
      <div className={`food-detail-modal ${isOpen ? 'active' : ''}`}>
        <div className="food-detail-content">
          <button className="close-button" onClick={onClose}>×</button>
          
          {food.image && (
            <img 
              src={food.image} 
              alt={food.name} 
              className="food-detail-image"
            />
          )}
          
          <div className="food-detail-info">
            <h2 className="food-detail-name">{food.name}</h2>
            <p className="food-detail-description">{food.description}</p>
            <p className="food-detail-price">{food.price.toLocaleString()}원</p>
          </div>
          
          <button 
            className="add-to-cart-button"
            onClick={handleAddToCart}
          >
            담기
          </button>
        </div>
      </div>
    </>
  );
};

export default FoodDetailModal;