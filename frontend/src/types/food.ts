export interface FoodItem {
  id: number;
  name: string;
  description: string;
  price: number;
  category: 'menu' | 'drinks';
  image: string;
  soldOut: boolean;
}