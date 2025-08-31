import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import MenuManagement from './components/MenuManagement';
import TableOrders from './components/TableOrders';
import OrderHistory from './components/OrderHistory';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/menu" replace />} />
            <Route path="/menu" element={<MenuManagement />} />
            <Route path="/tables" element={<TableOrders />} />
            <Route path="/orders" element={<OrderHistory />} />
          </Routes>
        </Layout>
      </div>
    </Router>
  );
}

export default App;