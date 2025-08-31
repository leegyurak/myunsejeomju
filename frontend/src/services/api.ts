import { FoodItem } from '../types/food';
import { OrderHistory } from '../types/order';

const API_BASE_URL = 'https://api.myunsejujeom.shop/api';

interface Table {
  id: string;
  created_at: string;
  is_active: boolean;
}

interface OrderItem {
  food_id: number;
  quantity: number;
}

interface PreOrderResponse {
  order_id: string;
  redirect_url: string;
  message: string;
}

interface PaymentStatusResponse {
  order_id: string;
  payment_completed: boolean;
  order_status: string;
  payer_name: string;
  total_amount: number;
}

interface ApiOrder {
  id: string;
  table: {
    id: string;
    createdAt: string;
    updatedAt: string;
  };
  orderDate: string;
  items: Array<{
    food: FoodItem;
    quantity: number;
    price: number;
  }>;
  minusItems: Array<any>;
  totalAmount: number;
}

interface ApiOrderHistory {
  orders: ApiOrder[];
  totalSpent: number;
}

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Food APIs
  async getFoods(category?: string): Promise<FoodItem[]> {
    const queryParam = category ? `?category=${category}` : '';
    return this.request<FoodItem[]>(`/foods/${queryParam}`);
  }

  async getFoodById(foodId: number): Promise<FoodItem> {
    return this.request<FoodItem>(`/foods/${foodId}/`);
  }

  // Table APIs
  async getTables(): Promise<Table[]> {
    return this.request<Table[]>('/tables/');
  }

  async getTableById(tableId: string): Promise<Table> {
    return this.request<Table>(`/tables/${tableId}/`);
  }

  async createTable(): Promise<Table> {
    return this.request<Table>('/tables/create/', {
      method: 'POST',
    });
  }

  // Order APIs
  async createPreOrder(tableId: string, payerName: string, totalAmount: number, items: OrderItem[]): Promise<PreOrderResponse> {
    return this.request<PreOrderResponse>(`/orders/pre-order/${tableId}/`, {
      method: 'POST',
      body: JSON.stringify({
        payer_name: payerName,
        total_amount: totalAmount,
        items: items,
      }),
    });
  }

  async createOrder(tableId: string, items: OrderItem[]): Promise<ApiOrder> {
    return this.request<ApiOrder>('/orders/', {
      method: 'POST',
      body: JSON.stringify({
        table_id: tableId,
        items,
      }),
    });
  }

  async getOrderHistory(tableId?: string): Promise<OrderHistory> {
    const queryParam = tableId ? `?table_id=${tableId}` : '';
    const apiResponse = await this.request<ApiOrderHistory>(`/orders/history/${queryParam}`);
    return this.transformOrderHistory(apiResponse);
  }

  async getTableOrders(tableId: string): Promise<OrderHistory> {
    const apiResponse = await this.request<ApiOrderHistory>(`/tables/${tableId}/orders/`);
    return this.transformOrderHistory(apiResponse);
  }

  async checkPaymentStatus(orderId: string): Promise<PaymentStatusResponse> {
    return this.request<PaymentStatusResponse>(`/orders/${orderId}/payment-status/`);
  }

  async resetTableOrders(tableId: string): Promise<void> {
    return this.request<void>(`/tables/${tableId}/orders/reset/`, {
      method: 'DELETE',
    });
  }

  private transformOrderHistory(apiResponse: ApiOrderHistory): OrderHistory {
    return {
      orders: apiResponse.orders.map(order => {
        // Safely handle date parsing
        let orderDate: Date;
        try {
          // Add 'Z' if no timezone info is present to treat as UTC
          const dateString = order.orderDate.includes('Z') || order.orderDate.includes('+') || order.orderDate.includes('-') 
            ? order.orderDate 
            : order.orderDate + 'Z';
          orderDate = new Date(dateString);
          
          // Check if date is valid
          if (isNaN(orderDate.getTime())) {
            orderDate = new Date(); // Fallback to current date
          }
        } catch (error) {
          console.warn('Failed to parse order date:', order.orderDate, error);
          orderDate = new Date(); // Fallback to current date
        }

        return {
          id: order.id,
          orderDate,
          items: order.items.map(item => ({
            food: item.food,
            quantity: item.quantity,
            price: item.price
          })),
          totalAmount: order.totalAmount,
          status: 'completed' as const
        };
      }),
      totalSpent: apiResponse.totalSpent
    };
  }
}

export const apiService = new ApiService();
export type { FoodItem, Table, OrderItem, PreOrderResponse, PaymentStatusResponse };