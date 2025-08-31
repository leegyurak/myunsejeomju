import { Food } from './food';

export interface OrderItem {
  food: Food;
  quantity: number;
  price: number;
}

export interface Order {
  id: string;
  table: {
    id: string;
    name: string;
  };
  items: OrderItem[];
  total_amount: number;
  pre_order_amount: number;
  payer_name: string;
  status: 'pre_order' | 'completed';
  is_visible: boolean;
  discord_notified: boolean;
  created_at: string;
  updated_at: string;
}