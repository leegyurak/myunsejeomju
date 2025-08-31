import React from 'react';
import { FoodItem } from '../types/food';

interface FoodGridProps {
  foods: FoodItem[];
  onFoodClick: (food: FoodItem) => void;
}

const FoodGrid: React.FC<FoodGridProps> = ({ foods, onFoodClick }) => {
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    e.currentTarget.src = '/logo.png';
  };

  return (
    <div className="food-grid">
      {foods.map((food) => (
        <div 
          key={food.id} 
          className={`food-item ${food.soldOut ? 'sold-out' : ''}`}
          onClick={() => !food.soldOut && onFoodClick(food)}
        >
          <img 
            src={food.image || '/logo.png'} 
            alt={food.name}
            onError={handleImageError}
          />
          {food.soldOut && <div className="sold-out-overlay">품절</div>}
          <h3>{food.name}</h3>
          <p>{food.price.toLocaleString()}원</p>
        </div>
      ))}
    </div>
  );
};

export default FoodGrid;