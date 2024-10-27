from rest_framework import serializers
from .models import Product, Reviews

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class ReviewSeializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = '__all__'