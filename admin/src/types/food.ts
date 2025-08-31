export interface Food {
  id: number;
  name: string;
  description: string;
  price: number;
  category: 'menu' | 'drinks';
  image: string;
  sold_out: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateFoodRequest {
  name: string;
  description: string;
  price: number;
  category: 'menu' | 'drinks';
  image: string;
}

export interface UpdateFoodRequest {
  name?: string;
  description?: string;
  price?: number;
  category?: 'menu' | 'drinks';
  image?: string;
  sold_out?: boolean;
}