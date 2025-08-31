from rest_framework import serializers
from domain.entities.food import Food


class FoodSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    price = serializers.IntegerField(min_value=0)
    category = serializers.ChoiceField(choices=['menu', 'drinks'])
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    image = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    sold_out = serializers.BooleanField(default=False, source='soldOut')
    
    def to_representation(self, instance: Food):
        return {
            'id': instance.id,
            'name': instance.name,
            'price': instance.price,
            'category': instance.category.value,
            'description': instance.description,
            'image': instance.image,
            'soldOut': instance.sold_out,
        }