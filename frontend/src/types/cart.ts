import { FoodItem } from './food';

export interface CartItem {
  food: FoodItem;
  quantity: number;
}

export interface Cart {
  items: CartItem[];
  totalPrice: number;
  totalItems: number;
}