import { OrderHistory } from '../types/order';

export const mockOrderHistory: OrderHistory = {
  orders: [
    {
      id: 'ORD-001',
      orderDate: new Date('2025-07-22T18:30:00'),
      items: [
        {
          food: {
            id: 1,
            name: '김치찌개',
            price: 8000,
            category: 'main',
            description: '얼큰한 김치찌개',
            image: 'https://images.unsplash.com/photo-1582719471127-6d4f84c4e93c?w=300&h=300&fit=crop',
            soldOut: false
          },
          quantity: 1,
          price: 8000
        },
        {
          food: {
            id: 7,
            name: '소주',
            price: 4000,
            category: 'side',
            description: '참이슬 소주',
            image: 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=300&h=300&fit=crop',
            soldOut: false
          },
          quantity: 2,
          price: 4000
        }
      ],
      totalAmount: 16000,
      status: 'completed'
    },
    {
      id: 'ORD-002',
      orderDate: new Date('2025-07-22T19:15:00'),
      items: [
        {
          food: {
            id: 2,
            name: '불고기',
            price: 12000,
            category: 'main',
            description: '달콤한 불고기',
            image: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=300&h=300&fit=crop',
            soldOut: false
          },
          quantity: 1,
          price: 12000
        },
        {
          food: {
            id: 9,
            name: '콜라',
            price: 2500,
            category: 'side',
            description: '코카콜라',
            image: 'https://images.unsplash.com/photo-1581636625402-29b2a704ef13?w=300&h=300&fit=crop',
            soldOut: false
          },
          quantity: 1,
          price: 2500
        }
      ],
      totalAmount: 14500,
      status: 'completed'
    },
    {
      id: 'ORD-003',
      orderDate: new Date('2025-07-22T20:45:00'),
      items: [
        {
          food: {
            id: 5,
            name: '비빔밥',
            price: 9000,
            category: 'main',
            description: '영양가득 비빔밥',
            image: 'https://images.unsplash.com/photo-1553979459-d2229ba7433a?w=300&h=300&fit=crop',
            soldOut: false
          },
          quantity: 2,
          price: 9000
        }
      ],
      minusItems: [
        {
          food: {
            id: 5,
            name: '비빔밥',
            price: 9000,
            category: 'main',
            description: '영양가득 비빔밥',
            image: 'https://images.unsplash.com/photo-1553979459-d2229ba7433a?w=300&h=300&fit=crop',
            soldOut: false
          },
          quantity: -1,
          price: 9000,
          reason: 'sold_out'
        }
      ],
      totalAmount: 9000,
      status: 'completed'
    },
  ],
  totalSpent: 32500
};