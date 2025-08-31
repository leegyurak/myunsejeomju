import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <nav style={{ 
        width: '250px', 
        backgroundColor: '#f8f9fa', 
        padding: '20px',
        borderRight: '1px solid #dee2e6'
      }}>
        <h2 style={{ marginBottom: '30px', color: '#333' }}>숭실대축제 어드민</h2>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li style={{ marginBottom: '10px' }}>
            <Link 
              to="/menu" 
              style={{ 
                textDecoration: 'none', 
                color: isActive('/menu') ? '#007bff' : '#333',
                fontWeight: isActive('/menu') ? 'bold' : 'normal',
                display: 'block',
                padding: '10px',
                borderRadius: '4px',
                backgroundColor: isActive('/menu') ? '#e3f2fd' : 'transparent'
              }}
            >
              메뉴 관리
            </Link>
          </li>
          <li style={{ marginBottom: '10px' }}>
            <Link 
              to="/tables" 
              style={{ 
                textDecoration: 'none', 
                color: isActive('/tables') ? '#007bff' : '#333',
                fontWeight: isActive('/tables') ? 'bold' : 'normal',
                display: 'block',
                padding: '10px',
                borderRadius: '4px',
                backgroundColor: isActive('/tables') ? '#e3f2fd' : 'transparent'
              }}
            >
              테이블별 주문
            </Link>
          </li>
          <li style={{ marginBottom: '10px' }}>
            <Link 
              to="/orders" 
              style={{ 
                textDecoration: 'none', 
                color: isActive('/orders') ? '#007bff' : '#333',
                fontWeight: isActive('/orders') ? 'bold' : 'normal',
                display: 'block',
                padding: '10px',
                borderRadius: '4px',
                backgroundColor: isActive('/orders') ? '#e3f2fd' : 'transparent'
              }}
            >
              전체 주문 내역
            </Link>
          </li>
        </ul>
      </nav>
      <main style={{ flex: 1, padding: '20px' }}>
        {children}
      </main>
    </div>
  );
};

export default Layout;