from django.core.management.base import BaseCommand
from infrastructure.database.models import FoodModel


class Command(BaseCommand):
    help = 'Seed the database with initial food data'

    def handle(self, *args, **options):
        foods_data = [
            {
                'name': '김치찌개',
                'price': 8000,
                'category': 'main',
                'description': '얼큰한 김치찌개',
                'image': 'https://images.unsplash.com/photo-1582719471127-6d4f84c4e93c?w=300&h=300&fit=crop'
            },
            {
                'name': '불고기',
                'price': 12000,
                'category': 'main',
                'description': '달콤한 불고기',
                'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=300&h=300&fit=crop'
            },
            {
                'name': '된장찌개',
                'price': 7000,
                'category': 'main',
                'description': '구수한 된장찌개',
                'image': 'https://images.unsplash.com/photo-1582719471127-6d4f84c4e93c?w=300&h=300&fit=crop',
                'sold_out': True
            },
            {
                'name': '제육볶음',
                'price': 10000,
                'category': 'main',
                'description': '매콤한 제육볶음',
                'image': 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300&h=300&fit=crop'
            },
            {
                'name': '비빔밥',
                'price': 9000,
                'category': 'main',
                'description': '영양가득 비빔밥',
                'image': 'https://images.unsplash.com/photo-1553979459-d2229ba7433a?w=300&h=300&fit=crop'
            },
            {
                'name': '냉면',
                'price': 8500,
                'category': 'main',
                'description': '시원한 냉면',
                'image': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=300&h=300&fit=crop'
            },
            {
                'name': '소주',
                'price': 4000,
                'category': 'side',
                'description': '참이슬 소주',
                'image': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=300&h=300&fit=crop'
            },
            {
                'name': '맥주',
                'price': 5000,
                'category': 'side',
                'description': '시원한 맥주',
                'image': 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=300&h=300&fit=crop',
                'sold_out': True
            },
            {
                'name': '콜라',
                'price': 2500,
                'category': 'side',
                'description': '코카콜라',
                'image': 'https://images.unsplash.com/photo-1581636625402-29b2a704ef13?w=300&h=300&fit=crop'
            },
            {
                'name': '사이다',
                'price': 2500,
                'category': 'side',
                'description': '시원한 사이다',
                'image': 'https://images.unsplash.com/photo-1581636625402-29b2a704ef13?w=300&h=300&fit=crop'
            },
            {
                'name': '아이스티',
                'price': 3000,
                'category': 'side',
                'description': '달콤한 아이스티',
                'image': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=300&h=300&fit=crop'
            },
            {
                'name': '오렌지주스',
                'price': 3500,
                'category': 'side',
                'description': '신선한 오렌지주스',
                'image': 'https://images.unsplash.com/photo-1613478223719-2ab802602423?w=300&h=300&fit=crop'
            }
        ]

        # Clear existing data
        FoodModel.objects.all().delete()
        
        # Create new data
        for food_data in foods_data:
            FoodModel.objects.create(**food_data)
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {len(foods_data)} food items')
        )