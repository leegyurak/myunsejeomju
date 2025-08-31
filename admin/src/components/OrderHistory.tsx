import React, { useState, useEffect } from 'react';
import { Order } from '../types/order';
import { apiService } from '../services/api';

const OrderHistory: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [filteredOrders, setFilteredOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pre_order' | 'completed'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'amount'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    fetchOrders();
  }, []);

  useEffect(() => {
    filterAndSortOrders();
  }, [orders, searchTerm, statusFilter, sortBy, sortOrder]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const data = await apiService.getOrders();
      setOrders(data);
    } catch (err) {
      setError('주문 내역을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortOrders = () => {
    let filtered = [...orders];

    // 검색 필터링
    if (searchTerm) {
      filtered = filtered.filter(order => 
        order.payer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.table.name?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // 상태 필터링
    if (statusFilter !== 'all') {
      filtered = filtered.filter(order => order.status === statusFilter);
    }

    // 정렬
    filtered.sort((a, b) => {
      let aValue: number | string;
      let bValue: number | string;

      if (sortBy === 'date') {
        aValue = new Date(a.created_at).getTime();
        bValue = new Date(b.created_at).getTime();
      } else {
        aValue = a.total_amount;
        bValue = b.total_amount;
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredOrders(filtered);
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pre_order':
        return '선주문';
      case 'completed':
        return '완료';
      default:
        return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pre_order':
        return '#ffc107';
      case 'completed':
        return '#28a745';
      default:
        return '#6c757d';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR');
  };

  const calculateTotals = () => {
    const totalRevenue = filteredOrders.reduce((sum, order) => sum + order.total_amount, 0);
    const totalOrders = filteredOrders.length;
    const completedOrders = filteredOrders.filter(order => order.status === 'completed').length;
    const preOrders = filteredOrders.filter(order => order.status === 'pre_order').length;

    return { totalRevenue, totalOrders, completedOrders, preOrders };
  };

  const { totalRevenue, totalOrders, completedOrders, preOrders } = calculateTotals();

  if (loading) return <div>로딩 중...</div>;

  return (
    <div>
      <h1>전체 주문 내역</h1>

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

      {/* 통계 정보 */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '15px', 
        marginBottom: '30px' 
      }}>
        <div style={{ 
          backgroundColor: '#f8f9fa', 
          padding: '20px', 
          borderRadius: '8px', 
          textAlign: 'center' 
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
            {totalRevenue.toLocaleString()}원
          </div>
          <div style={{ color: '#666', marginTop: '5px' }}>총 매출</div>
        </div>
        <div style={{ 
          backgroundColor: '#f8f9fa', 
          padding: '20px', 
          borderRadius: '8px', 
          textAlign: 'center' 
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
            {totalOrders}
          </div>
          <div style={{ color: '#666', marginTop: '5px' }}>총 주문 수</div>
        </div>
        <div style={{ 
          backgroundColor: '#f8f9fa', 
          padding: '20px', 
          borderRadius: '8px', 
          textAlign: 'center' 
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#17a2b8' }}>
            {completedOrders}
          </div>
          <div style={{ color: '#666', marginTop: '5px' }}>완료된 주문</div>
        </div>
        <div style={{ 
          backgroundColor: '#f8f9fa', 
          padding: '20px', 
          borderRadius: '8px', 
          textAlign: 'center' 
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ffc107' }}>
            {preOrders}
          </div>
          <div style={{ color: '#666', marginTop: '5px' }}>선주문</div>
        </div>
      </div>

      {/* 필터 및 검색 */}
      <div style={{ 
        backgroundColor: '#f8f9fa', 
        padding: '20px', 
        borderRadius: '8px', 
        marginBottom: '20px' 
      }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              검색 (이름, 주문ID, 테이블명)
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="검색어 입력..."
              style={{ 
                width: '100%', 
                padding: '8px', 
                borderRadius: '4px', 
                border: '1px solid #ddd' 
              }}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              상태 필터
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as 'all' | 'pre_order' | 'completed')}
              style={{ 
                width: '100%', 
                padding: '8px', 
                borderRadius: '4px', 
                border: '1px solid #ddd' 
              }}
            >
              <option value="all">전체</option>
              <option value="completed">완료</option>
              <option value="pre_order">선주문</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              정렬 기준
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'amount')}
              style={{ 
                width: '100%', 
                padding: '8px', 
                borderRadius: '4px', 
                border: '1px solid #ddd' 
              }}
            >
              <option value="date">주문 시간</option>
              <option value="amount">주문 금액</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              정렬 순서
            </label>
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
              style={{ 
                width: '100%', 
                padding: '8px', 
                borderRadius: '4px', 
                border: '1px solid #ddd' 
              }}
            >
              <option value="desc">내림차순</option>
              <option value="asc">오름차순</option>
            </select>
          </div>
        </div>
      </div>

      {/* 주문 목록 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {filteredOrders.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '50px', 
            color: '#666' 
          }}>
            {searchTerm || statusFilter !== 'all' ? '검색 결과가 없습니다' : '주문 내역이 없습니다'}
          </div>
        ) : (
          filteredOrders.map((order) => (
            <div
              key={order.id}
              style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '20px',
                backgroundColor: 'white'
              }}
            >
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                marginBottom: '15px' 
              }}>
                <div>
                  <strong>주문 ID: {order.id}</strong>
                  <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                    주문자: <strong>{order.payer_name}</strong>
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    테이블: {order.table.name || `테이블 ${order.table.id.slice(0, 8)}`}
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    주문 시간: {formatDate(order.created_at)}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span
                    style={{
                      backgroundColor: getStatusColor(order.status),
                      color: 'white',
                      padding: '5px 10px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: 'bold'
                    }}
                  >
                    {getStatusText(order.status)}
                  </span>
                  <div style={{ 
                    fontSize: '20px', 
                    fontWeight: 'bold', 
                    marginTop: '10px' 
                  }}>
                    {order.total_amount.toLocaleString()}원
                  </div>
                  {order.pre_order_amount > 0 && (
                    <div style={{ fontSize: '14px', color: '#666' }}>
                      선결제: {order.pre_order_amount.toLocaleString()}원
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h4 style={{ marginBottom: '10px' }}>주문 항목</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {order.items.map((item, index) => (
                    <div
                      key={index}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '10px',
                        backgroundColor: '#f8f9fa',
                        borderRadius: '4px'
                      }}
                    >
                      <div>
                        <span style={{ fontWeight: 'bold' }}>{item.food.name}</span>
                        <span style={{ marginLeft: '10px', color: '#666' }}>
                          x {item.quantity}
                        </span>
                        {item.food.category && (
                          <span style={{ 
                            marginLeft: '10px', 
                            backgroundColor: '#e9ecef', 
                            padding: '2px 6px', 
                            borderRadius: '12px', 
                            fontSize: '12px' 
                          }}>
                            {item.food.category === 'menu' ? '메뉴' : '음료'}
                          </span>
                        )}
                      </div>
                      <div style={{ fontWeight: 'bold' }}>
                        {(item.price * item.quantity).toLocaleString()}원
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default OrderHistory;