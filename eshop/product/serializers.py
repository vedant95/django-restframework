from rest_framework import serializers
from .models import Product, Reviews

class ProductSerializer(serializers.ModelSerializer):

    reviews = serializers.SerializerMethodField(method_name='get_reviews', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'brand', 'ratings', 'category', 'stock', 'user', 'reviews')


    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        serializer = ReviewSeializer(reviews, many=True)
        return serializer.data


class ReviewSeializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = '__all__'
