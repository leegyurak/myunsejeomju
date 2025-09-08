import React from 'react';

interface HeaderProps {
  activeCategory: string;
  onCategoryChange: (category: string) => void;
}

const Header: React.FC<HeaderProps> = ({ activeCategory, onCategoryChange }) => {
  const categories = [
    { id: 'main', name: '메인' },
    { id: 'side', name: '사이드' }
  ];

  return (
    <div className="header-container">
      <div className="header">
        <img 
          src="/logo.png" 
          alt="지지고 복고" 
          className="header-logo"
        />
      </div>
      <div className="category-tabs">
        {categories.map((category) => (
          <button
            key={category.id}
            className={`category-tab ${activeCategory === category.id ? 'active' : ''}`}
            onClick={() => onCategoryChange(category.id)}
          >
            {category.name}
          </button>
        ))}
      </div>
    </div>
  );
};

export default Header;