from product import views
from django.urls import path

urlpatterns = [
    path('products/', views.get_products, name="products"),
    path('products/<str:id>', views.get_product, name="product_details"),
]