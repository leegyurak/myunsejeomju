import { Food, CreateFoodRequest, UpdateFoodRequest } from '../types/food';
import { Order } from '../types/order';
import { Table } from '../types/table';

const API_BASE_URL = 'http://localhost:8000/api';

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // Food APIs
  async getFoods(): Promise<Food[]> {
    return this.request<Food[]>('/foods/');
  }

  async getFoodById(id: number): Promise<Food> {
    return this.request<Food>(`/foods/${id}/`);
  }

  async createFood(food: CreateFoodRequest): Promise<Food> {
    return this.request<Food>('/foods/', {
      method: 'POST',
      body: JSON.stringify(food),
    });
  }

  async updateFood(id: number, food: UpdateFoodRequest): Promise<Food> {
    return this.request<Food>(`/foods/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(food),
    });
  }

  async deleteFood(id: number): Promise<void> {
    await this.request(`/foods/${id}/`, {
      method: 'DELETE',
    });
  }

  // Order APIs
  async getOrders(): Promise<Order[]> {
    return this.request<Order[]>('/orders/history/');
  }

  async getOrdersByTable(tableId: string): Promise<Order[]> {
    return this.request<Order[]>(`/tables/${tableId}/orders/`);
  }

  // Table APIs
  async getTables(): Promise<Table[]> {
    return this.request<Table[]>('/tables/');
  }
}

export const apiService = new ApiService();