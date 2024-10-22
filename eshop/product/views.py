from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .serializers import ProductSerializer
from .filters import ProductsFilter

from .models import Product

# Create your views here.
@api_view(['GET'])
def get_products(request):

    filterset = ProductsFilter(request.GET, queryset=Product.objects.all().order_by('id'))

    serializer = ProductSerializer(filterset.qs, many=True)

    return Response({"Products": serializer.data})


@api_view(['GET'])
def get_product(request, id):

    product = get_object_or_404(Product, id=id)

    serializer = ProductSerializer(product, many=False)

    return Response({"Product": serializer.data})
