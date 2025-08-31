import React, { useState, useEffect } from 'react';
import { Food, CreateFoodRequest, UpdateFoodRequest } from '../types/food';
import { apiService } from '../services/api';

const MenuManagement: React.FC = () => {
  const [foods, setFoods] = useState<Food[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingFood, setEditingFood] = useState<Food | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState<CreateFoodRequest>({
    name: '',
    description: '',
    price: 0,
    category: 'menu',
    image: ''
  });

  useEffect(() => {
    fetchFoods();
  }, []);

  const fetchFoods = async () => {
    try {
      setLoading(true);
      const data = await apiService.getFoods();
      setFoods(data);
    } catch (err) {
      setError('음식 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createFood(formData);
      setShowCreateForm(false);
      setFormData({ name: '', description: '', price: 0, category: 'menu', image: '' });
      fetchFoods();
    } catch (err) {
      setError('음식 등록에 실패했습니다.');
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingFood) return;

    try {
      const updateData: UpdateFoodRequest = {
        name: formData.name,
        description: formData.description,
        price: formData.price,
        category: formData.category,
        image: formData.image
      };
      await apiService.updateFood(editingFood.id, updateData);
      setEditingFood(null);
      setFormData({ name: '', description: '', price: 0, category: 'menu', image: '' });
      fetchFoods();
    } catch (err) {
      setError('음식 수정에 실패했습니다.');
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;

    try {
      await apiService.deleteFood(id);
      fetchFoods();
    } catch (err) {
      setError('음식 삭제에 실패했습니다.');
    }
  };

  const toggleSoldOut = async (food: Food) => {
    try {
      await apiService.updateFood(food.id, { sold_out: !food.sold_out });
      fetchFoods();
    } catch (err) {
      setError('품절 상태 변경에 실패했습니다.');
    }
  };

  const startEdit = (food: Food) => {
    setEditingFood(food);
    setFormData({
      name: food.name,
      description: food.description,
      price: food.price,
      category: food.category,
      image: food.image
    });
    setShowCreateForm(false);
  };

  const cancelEdit = () => {
    setEditingFood(null);
    setShowCreateForm(false);
    setFormData({ name: '', description: '', price: 0, category: 'menu', image: '' });
  };

  if (loading) return <div>로딩 중...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>메뉴 관리</h1>
        <button 
          onClick={() => setShowCreateForm(true)}
          style={{
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          새 메뉴 추가
        </button>
      </div>

      {error && (
        <div style={{ 
          backgroundColor: '#f8d7da', 
          color: '#721c24', 
          padding: '10px', 
          borderRadius: '4px', 
          marginBottom: '20px' 
        }}>
          {error}
        </div>
      )}

      {(showCreateForm || editingFood) && (
        <div style={{ 
          backgroundColor: '#f8f9fa', 
          padding: '20px', 
          borderRadius: '4px', 
          marginBottom: '20px' 
        }}>
          <h3>{editingFood ? '메뉴 수정' : '새 메뉴 등록'}</h3>
          <form onSubmit={editingFood ? handleUpdate : handleCreate}>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>메뉴명:</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>설명:</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>가격:</label>
              <input
                type="number"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseInt(e.target.value) })}
                required
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>카테고리:</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value as 'menu' | 'drinks' })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              >
                <option value="menu">메뉴</option>
                <option value="drinks">음료</option>
              </select>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>이미지 URL:</label>
              <input
                type="url"
                value={formData.image}
                onChange={(e) => setFormData({ ...formData, image: e.target.value })}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>
            <div>
              <button 
                type="submit"
                style={{
                  backgroundColor: '#28a745',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  marginRight: '10px'
                }}
              >
                {editingFood ? '수정' : '등록'}
              </button>
              <button 
                type="button"
                onClick={cancelEdit}
                style={{
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                취소
              </button>
            </div>
          </form>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        {foods.map((food) => (
          <div 
            key={food.id} 
            style={{ 
              border: '1px solid #ddd', 
              borderRadius: '8px', 
              padding: '15px',
              backgroundColor: food.sold_out ? '#f8f8f8' : 'white'
            }}
          >
            {food.image && (
              <img 
                src={food.image} 
                alt={food.name}
                style={{ width: '100%', height: '150px', objectFit: 'cover', borderRadius: '4px', marginBottom: '10px' }}
              />
            )}
            <h3 style={{ margin: '0 0 10px 0', color: food.sold_out ? '#6c757d' : '#333' }}>
              {food.name}
              {food.sold_out && <span style={{ color: '#dc3545', marginLeft: '10px' }}>(품절)</span>}
            </h3>
            <p style={{ color: '#666', marginBottom: '10px' }}>{food.description}</p>
            <p style={{ fontWeight: 'bold', fontSize: '18px', marginBottom: '10px' }}>
              {food.price.toLocaleString()}원
            </p>
            <p style={{ color: '#666', marginBottom: '15px' }}>
              카테고리: {food.category === 'menu' ? '메뉴' : '음료'}
            </p>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button 
                onClick={() => startEdit(food)}
                style={{
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  padding: '5px 10px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                수정
              </button>
              <button 
                onClick={() => toggleSoldOut(food)}
                style={{
                  backgroundColor: food.sold_out ? '#28a745' : '#ffc107',
                  color: food.sold_out ? 'white' : '#212529',
                  border: 'none',
                  padding: '5px 10px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                {food.sold_out ? '재고 있음' : '품절'}
              </button>
              <button 
                onClick={() => handleDelete(food.id)}
                style={{
                  backgroundColor: '#dc3545',
                  color: 'white',
                  border: 'none',
                  padding: '5px 10px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                삭제
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MenuManagement;