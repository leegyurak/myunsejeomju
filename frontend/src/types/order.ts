import { FoodItem } from './food';

export interface OrderItem {
  food: FoodItem;
  quantity: number;
  price: number; // 주문 당시 가격 (가격 변동 대비)
}

export interface MinusOrderItem {
  food: FoodItem;
  quantity: number; // 음수 값
  price: number;
  reason: 'sold_out' | 'unavailable' | 'damaged';
}

export interface Order {
  id: string;
  orderDate: Date;
  items: OrderItem[];
  minusItems?: MinusOrderItem[];
  totalAmount: number;
  status: 'completed';
}

export interface OrderHistory {
  orders: Order[];
  totalSpent: number;
}