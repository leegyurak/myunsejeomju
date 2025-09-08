export interface FoodItem {
  id: number;
  name: string;
  description: string;
  price: number;
  category: 'main' | 'side';
  image: string;
  soldOut: boolean;
}