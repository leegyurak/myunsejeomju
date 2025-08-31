import React, { useState, useEffect } from 'react';
import { Table } from '../types/table';
import { Order } from '../types/order';
import { apiService } from '../services/api';

const TableOrders: React.FC = () => {
  const [tables, setTables] = useState<Table[]>([]);
  const [selectedTable, setSelectedTable] = useState<Table | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTables();
  }, []);

  const fetchTables = async () => {
    try {
      const data = await apiService.getTables();
      setTables(data);
    } catch (err) {
      setError('테이블 목록을 불러오는데 실패했습니다.');
    }
  };

  const fetchTableOrders = async (table: Table) => {
    try {
      setLoading(true);
      setSelectedTable(table);
      const data = await apiService.getOrdersByTable(table.id);
      setOrders(data);
    } catch (err) {
      setError('테이블 주문 내역을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
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

  const calculateTableTotal = () => {
    return orders.reduce((total, order) => total + order.total_amount, 0);
  };

  return (
    <div>
      <h1>테이블별 주문 내역</h1>

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

      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ width: '300px' }}>
          <h3>테이블 목록</h3>
          <div style={{ 
            border: '1px solid #ddd', 
            borderRadius: '4px', 
            maxHeight: '400px', 
            overflowY: 'auto' 
          }}>
            {tables.map((table) => (
              <div
                key={table.id}
                onClick={() => fetchTableOrders(table)}
                style={{
                  padding: '15px',
                  borderBottom: '1px solid #eee',
                  cursor: 'pointer',
                  backgroundColor: selectedTable?.id === table.id ? '#e3f2fd' : 'white'
                }}
                onMouseEnter={(e) => {
                  if (selectedTable?.id !== table.id) {
                    e.currentTarget.style.backgroundColor = '#f5f5f5';
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedTable?.id !== table.id) {
                    e.currentTarget.style.backgroundColor = 'white';
                  }
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  {table.name || `테이블 ${table.id.slice(0, 8)}`}
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  ID: {table.id}
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  생성: {formatDate(table.created_at)}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ flex: 1 }}>
          {!selectedTable ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '50px', 
              color: '#666' 
            }}>
              테이블을 선택해주세요
            </div>
          ) : (
            <div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                marginBottom: '20px' 
              }}>
                <h3>{selectedTable.name || `테이블 ${selectedTable.id.slice(0, 8)}`} 주문 내역</h3>
                {orders.length > 0 && (
                  <div style={{ 
                    backgroundColor: '#f8f9fa', 
                    padding: '10px', 
                    borderRadius: '4px' 
                  }}>
                    <strong>총 매출: {calculateTableTotal().toLocaleString()}원</strong>
                  </div>
                )}
              </div>

              {loading ? (
                <div>로딩 중...</div>
              ) : orders.length === 0 ? (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '50px', 
                  color: '#666' 
                }}>
                  주문 내역이 없습니다
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                  {orders.map((order) => (
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
                            주문자: {order.payer_name}
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
                            fontSize: '18px', 
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
                                padding: '8px',
                                backgroundColor: '#f8f9fa',
                                borderRadius: '4px'
                              }}
                            >
                              <div>
                                <span style={{ fontWeight: 'bold' }}>{item.food.name}</span>
                                <span style={{ marginLeft: '10px', color: '#666' }}>
                                  x {item.quantity}
                                </span>
                              </div>
                              <div style={{ fontWeight: 'bold' }}>
                                {(item.price * item.quantity).toLocaleString()}원
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TableOrders;