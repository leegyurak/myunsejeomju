import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams, Navigate, useLocation } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import Notice from './components/Notice';
import FoodGrid from './components/FoodGrid';
import Footer from './components/Footer';
import CartButton from './components/CartButton';
import ReceiptButton from './components/ReceiptButton';
import FoodDetailModal from './components/FoodDetailModal';
import CartModal from './components/CartModal';
import ReceiptModal from './components/ReceiptModal';
import OrderSuccessMessage from './components/OrderSuccessMessage';
import NameInputModal from './components/NameInputModal';
import PaymentConfirmationWindow from './components/PaymentConfirmationWindow';
import PaymentResultPage from './components/PaymentResultPage';
import PaymentSuccessPage from './components/PaymentSuccessPage';
import PaymentFailPage from './components/PaymentFailPage';
import NotFoundPage from './components/NotFoundPage';
import { apiService, FoodItem } from './services/api';
import { OrderHistory } from './types/order';
import { CartItem } from './types/cart';

interface TablePageProps {
  tableId: string;
}

function TablePage({ tableId }: TablePageProps) {
  const location = useLocation();
  const [activeCategory, setActiveCategory] = useState<string>('menu');
  const [isReceiptModalOpen, setIsReceiptModalOpen] = useState<boolean>(false);
  const [selectedFood, setSelectedFood] = useState<FoodItem | null>(null);
  const [isFoodDetailOpen, setIsFoodDetailOpen] = useState<boolean>(false);
  const [isCartModalOpen, setIsCartModalOpen] = useState<boolean>(false);
  const [isNameInputModalOpen, setIsNameInputModalOpen] = useState<boolean>(false);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [isOrdering, setIsOrdering] = useState<boolean>(false);
  const [showOrderSuccess, setShowOrderSuccess] = useState<boolean>(false);
  const [orderHistory, setOrderHistory] = useState<OrderHistory | null>(null);
  const [foods, setFoods] = useState<FoodItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  const menuSectionRef = useRef<HTMLDivElement>(null);
  const drinksSectionRef = useRef<HTMLDivElement>(null);
  const isScrollingRef = useRef<boolean>(false);

  const menuFoods: FoodItem[] = foods.filter(
    (food) => food.category === 'menu'
  );
  
  const drinksFoods: FoodItem[] = foods.filter(
    (food) => food.category === 'drinks'
  );

  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        
        // Load foods first
        const foodsData = await apiService.getFoods();
        setFoods(foodsData);
        
        // Try to load order history, but don't fail if it doesn't exist
        try {
          const orderHistoryData = await apiService.getTableOrders(tableId);
          setOrderHistory(orderHistoryData);
        } catch (orderError) {
          setOrderHistory({ orders: [], totalSpent: 0 });
        }
        
      } catch (error) {
        console.error('Failed to load data:', error);
        // Still set empty data so the UI doesn't stay loading forever
        setFoods([]);
        setOrderHistory({ orders: [], totalSpent: 0 });
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [tableId]);

  // Handle payment success state and ORDER_COMPLETE messages
  useEffect(() => {
    if (location.state?.paymentSuccess) {
      setShowOrderSuccess(true);
      // Clear the state so it doesn't show again on refresh
      window.history.replaceState(null, '', window.location.pathname);
    }

    // Listen for ORDER_COMPLETE messages from payment window
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'ORDER_COMPLETE') {
        // Payment completed - refresh order history and show success
        const refreshOrderHistory = async () => {
          try {
            const updatedOrderHistory = await apiService.getTableOrders(tableId);
            setOrderHistory(updatedOrderHistory);
            setShowOrderSuccess(true);
          } catch (error) {
            console.error('Failed to refresh order history:', error);
          }
        };
        refreshOrderHistory();
      }
    };

    window.addEventListener('message', handleMessage);
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, [location.state, tableId]);

  const cartItemCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);
  const cartTotalAmount = cartItems.reduce((sum, item) => sum + item.food.price * item.quantity, 0);

  useEffect(() => {
    const handleScroll = () => {
      if (isScrollingRef.current) return;
      
      const menuSection = menuSectionRef.current;
      const drinksSection = drinksSectionRef.current;
      
      if (!menuSection || !drinksSection) return;
      
      const menuRect = menuSection.getBoundingClientRect();
      const drinksRect = drinksSection.getBoundingClientRect();
      const threshold = 200;
      
      if (menuRect.top <= threshold && menuRect.bottom > threshold) {
        setActiveCategory('menu');
      } else if (drinksRect.top <= threshold && drinksRect.bottom > threshold) {
        setActiveCategory('drinks');
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleCategoryChange = (category: string) => {
    isScrollingRef.current = true;
    setActiveCategory(category);
    
    const targetRef = category === 'menu' ? menuSectionRef : drinksSectionRef;
    const targetElement = targetRef.current;
    
    if (targetElement) {
      const offsetTop = targetElement.offsetTop - 160;
      window.scrollTo({
        top: offsetTop,
        behavior: 'smooth'
      });
      
      setTimeout(() => {
        isScrollingRef.current = false;
      }, 800);
    }
  };


  const handleReceiptOpen = () => {
    setIsReceiptModalOpen(true);
  };

  const handleReceiptClose = () => {
    setIsReceiptModalOpen(false);
  };

  const handleFoodClick = (food: FoodItem) => {
    setSelectedFood(food);
    setIsFoodDetailOpen(true);
  };

  const handleFoodDetailClose = () => {
    setIsFoodDetailOpen(false);
    setSelectedFood(null);
  };

  const handleAddToCart = (food: FoodItem) => {
    setCartItems(prevItems => {
      const existingItem = prevItems.find(item => item.food.id === food.id);
      
      if (existingItem) {
        return prevItems.map(item =>
          item.food.id === food.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        return [...prevItems, { food, quantity: 1 }];
      }
    });
  };

  const handleCartOpen = () => {
    setIsCartModalOpen(true);
  };

  const handleCartClose = () => {
    setIsCartModalOpen(false);
  };

  const handleShowNameInput = () => {
    setIsCartModalOpen(false);
    setIsNameInputModalOpen(true);
  };

  const handleNameInputClose = () => {
    setIsNameInputModalOpen(false);
  };

  const handleUpdateQuantity = (foodId: number, quantity: number) => {
    if (quantity <= 0) {
      handleRemoveItem(foodId);
      return;
    }

    setCartItems(prevItems =>
      prevItems.map(item =>
        item.food.id === foodId
          ? { ...item, quantity }
          : item
      )
    );
  };

  const handleRemoveItem = (foodId: number) => {
    setCartItems(prevItems => prevItems.filter(item => item.food.id !== foodId));
  };

  const handleOrder = async (name: string) => {
    if (cartItems.length === 0 || isOrdering) return;
    
    setIsOrdering(true);
    
    try {
      const orderItems = cartItems.map(item => ({
        food_id: item.food.id,
        quantity: item.quantity
      }));
      
      await apiService.createOrder(tableId, orderItems);
      
      // 주문 성공 처리
      setIsNameInputModalOpen(false);
      setCartItems([]);
      
      // 주문 내역 새로고침
      const updatedOrderHistory = await apiService.getTableOrders(tableId);
      setOrderHistory(updatedOrderHistory);
      
      setTimeout(() => {
        setShowOrderSuccess(true);
      }, 300);
      
    } catch (error) {
      console.error('주문 실패:', error);
      alert('주문 처리 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setIsOrdering(false);
    }
  };

  const handleOrderSuccessComplete = () => {
    setShowOrderSuccess(false);
  };

  const handleResetOrderHistory = async () => {
    try {
      await apiService.resetTableOrders(tableId);
      // Reset local order history
      setOrderHistory({ orders: [], totalSpent: 0 });
      // Close receipt modal
      setIsReceiptModalOpen(false);
    } catch (error) {
      console.error('Failed to reset order history:', error);
      alert('주문 내역 초기화 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
  };







  if (isLoading) {
    return (
      <div className="App">
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh',
          fontSize: '18px'
        }}>
          로딩 중...
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <Header 
        activeCategory={activeCategory}
        onCategoryChange={handleCategoryChange}
      />
      <Notice />
      <div className="content-sections">
        <div ref={menuSectionRef} className="category-section" data-category="menu">
          <h2 className="section-title">메뉴</h2>
          <FoodGrid 
            foods={menuFoods} 
            onFoodClick={handleFoodClick}
          />
        </div>
        <div ref={drinksSectionRef} className="category-section" data-category="drinks">
          <h2 className="section-title">주류/음료</h2>
          <FoodGrid 
            foods={drinksFoods} 
            onFoodClick={handleFoodClick}
          />
        </div>
      </div>
      <Footer />
      <ReceiptButton onReceiptOpen={handleReceiptOpen} />
      <CartButton 
        onCartOpen={handleCartOpen}
        cartItemCount={cartItemCount}
      />
      {orderHistory && (
        <ReceiptModal 
          isOpen={isReceiptModalOpen}
          onClose={handleReceiptClose}
          orderHistory={orderHistory}
          onResetOrderHistory={handleResetOrderHistory}
        />
      )}
      <FoodDetailModal 
        food={selectedFood}
        isOpen={isFoodDetailOpen}
        onClose={handleFoodDetailClose}
        onAddToCart={handleAddToCart}
      />
      <CartModal 
        isOpen={isCartModalOpen}
        onClose={handleCartClose}
        cartItems={cartItems}
        onUpdateQuantity={handleUpdateQuantity}
        onRemoveItem={handleRemoveItem}
        onShowNameInput={handleShowNameInput}
      />
      <NameInputModal 
        isOpen={isNameInputModalOpen}
        onClose={handleNameInputClose}
        onConfirm={handleOrder}
        isSubmitting={isOrdering}
        totalAmount={cartTotalAmount}
        tableId={tableId}
        cartItems={cartItems}
      />
      <OrderSuccessMessage 
        isVisible={showOrderSuccess}
        onComplete={handleOrderSuccessComplete}
      />
    </div>
  );
}

function TablePageWrapper() {
  const { tableId } = useParams<{ tableId: string }>();
  const [tableExists, setTableExists] = useState<boolean | null>(null);
  
  useEffect(() => {
    const verifyTable = async () => {
      if (!tableId) {
        setTableExists(false);
        return;
      }
      
      try {
        await apiService.getTableById(tableId);
        setTableExists(true);
      } catch (error) {
        console.error('Table not found:', error);
        setTableExists(false);
      }
    };
    
    verifyTable();
  }, [tableId]);
  
  if (!tableId) {
    return <Navigate to="/" replace />;
  }
  
  if (tableExists === null) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px'
      }}>
        로딩 중...
      </div>
    );
  }
  
  if (tableExists === false) {
    return <NotFoundPage />;
  }
  
  return <TablePage tableId={tableId} />;
}

function PaymentConfirmationWrapper() {
  const { tableId } = useParams<{ tableId: string }>();
  const urlParams = new URLSearchParams(window.location.search);
  const payerName = urlParams.get('payer_name') || '';
  const totalAmount = parseInt(urlParams.get('total_amount') || '0');

  // Get cart items from sessionStorage
  const cartItemsJson = sessionStorage.getItem('paymentCartItems');
  const cartItems = cartItemsJson ? JSON.parse(cartItemsJson) : [];

  if (!tableId || !payerName || !totalAmount) {
    return <div>잘못된 접근입니다.</div>;
  }

  const handleOrderComplete = () => {
    // Clean up sessionStorage
    sessionStorage.removeItem('paymentCartItems');
    
    // Send message to parent window
    if (window.opener) {
      window.opener.postMessage({ type: 'ORDER_COMPLETE' }, '*');
    }
  };

  return (
    <PaymentConfirmationWindow
      tableId={tableId}
      payerName={payerName}
      totalAmount={totalAmount}
      cartItems={cartItems}
      onOrderComplete={handleOrderComplete}
    />
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/table/:tableId" element={<TablePageWrapper />} />
        <Route path="/payment-confirmation/:tableId" element={<PaymentConfirmationWrapper />} />
        <Route path="/payment-result/:tableId" element={<PaymentResultPage />} />
        <Route path="/payment-success/:tableId" element={<PaymentSuccessPage />} />
        <Route path="/payment-fail/:tableId" element={<PaymentFailPage />} />
        <Route path="/" element={<Navigate to="/table/default" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;