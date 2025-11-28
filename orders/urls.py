from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name="place_order"),
    path('payments/', views.payments, name="payments"),
    path('api/orders', views.create_paypal_order, name='create_paypal_order'),
    path('api/orders/<str:order_id>/capture', views.capture_paypal_order, name='capture_paypal_order'),
    path('order_complete/', views.order_complete, name="order_complete"),
]
