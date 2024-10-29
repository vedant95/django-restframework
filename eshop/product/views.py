from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg

from rest_framework import status

from django.shortcuts import get_object_or_404

from .serializers import ProductSerializer
from .filters import ProductsFilter

from .models import Product, Reviews

# Create your views here.
@api_view(['GET'])
def get_products(request):

    filterset = ProductsFilter(request.GET, queryset=Product.objects.all().order_by('id'))

    count  = filterset.qs.count()

    # Pagination
    resPerPage = 3

    paginator = PageNumberPagination()
    paginator.page_size = resPerPage

    queryset = paginator.paginate_queryset(filterset.qs, request)

    serializer = ProductSerializer(queryset, many=True)

    return Response({
        "Count": count,
        "Data per page": resPerPage,
        "Products": serializer.data})


@api_view(['GET'])
def get_product(request, id):

    product = get_object_or_404(Product, id=id)
    print("product", product)

    serializer = ProductSerializer(product, many=False)

    return Response({"Product": serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_product(request):

    data = request.data

    serializer = ProductSerializer(data=data)

    if serializer.is_valid():

        product = Product.objects.create(**data, user=request.user)

        res = ProductSerializer(product, many=False)

        return Response({"Product": res.data})

    else:
        return Response(serializer.errors)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_product(request, id):

    product = get_object_or_404(Product, id=id)

    if product.user != request.user:
        return Response({'Error': "You do not have permission to edit"}, status=status.HTTP_403_FORBIDDEN)

    product.name = request.data['name'] if 'name' in request.data  else product.name
    product.description = request.data['description'] if 'description' in request.data  else product.description
    product.price = request.data['price'] if 'price' in request.data  else product.price
    product.category = request.data['category'] if 'category' in request.data  else product.category
    product.brand = request.data['brand'] if 'brand' in request.data  else product.brand
    product.ratings = request.data['ratings'] if 'ratings' in request.data  else product.ratings
    product.stock = request.data['stock'] if 'stock' in request.data  else product.stock

    product.save()

    serializer = ProductSerializer(product, many=False)

    return Response({"Product": serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, id):

    user = request.user
    product = get_object_or_404(Product, id=id)
    data = request.data


    review = product.reviews.filter(user=user)

    if data['rating']<= 0 or data['rating'] > 5:
        return Response({'error': 'Please add rating between 1 to 5'}, status=status.HTTP_400_BAD_REQUEST)

    elif review.exists():

        print("Inside exists - ")

        new_review = {
            'rating': data['rating'],
            'comment': data['comment']
            }
        review.update(**new_review)

        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))

        product.ratings = rating['avg_ratings']
        product.save()

        return Response({'Detail': 'Review Updated!'})

    else:

        print("Inside New - ")

        Reviews.objects.create(
            user=user,
            product=product,
            rating = data['rating'],
            comment= data['comment']
        )

        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))

        product.ratings = rating['avg_ratings']
        product.save()

        return Response({'details': 'Review Posted!'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, id):
    user = request.user
    product = get_object_or_404(Product, id=id)

    review = product.reviews.filter(user=user)

    if review.exists():

        review.delete()

        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))

        if rating['avg_ratings'] is None:
            rating['avg_ratings'] = 0

        product.ratings = rating['avg_ratings']
        product.save()

        return Response({'details': 'Review Deleted!'})

    else:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)