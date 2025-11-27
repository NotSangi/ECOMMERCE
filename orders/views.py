from django.shortcuts import render, redirect
from django.contrib import messages
from carts.models import CartItem
from .models import Order
from .forms import OrderForm
from django.shortcuts import get_object_or_404
import datetime

#PAYPAL
import os
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient
from paypalserversdk.controllers.orders_controller import OrdersController
from paypalserversdk.models.order_request import OrderRequest
from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest
from paypalserversdk.models.amount_with_breakdown import AmountWithBreakdown
from paypalserversdk.models.paypal_experience_user_action import (
    PaypalExperienceUserAction,
)
from paypalserversdk.models.checkout_payment_intent import CheckoutPaymentIntent
from paypalserversdk.exceptions.error_exception import ErrorException
from paypalserversdk.api_helper import ApiHelper

from dotenv import load_dotenv

load_dotenv()

# Create your views here.
def place_order(request, total=0, quantity=0):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_count = cart_items.count()
    
    if cart_count == 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    
    for item in cart_items:
        total += (item.product.price * item.quantity)
        quantity += item.quantity
        
    tax = round((0.02*total), 2)
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = request.user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            year = int(datetime.date.today().strftime('%Y'))
            month = int(datetime.date.today().strftime('%m'))
            day = int(datetime.date.today().strftime('%d'))
            date = datetime.date(year,month,day)
            
            current_date = date.strftime("%Y%m%d")
            
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            request.session['order_number'] = order_number
            print(request.session.get('order_number'))
            
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
            context = {
                'order':order,
                'cart_items': cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total
            }
            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')
    return redirect('checkout')

def payments(request):
    return render(request, 'orders/payments.html')

# ----- START PAYPAL API ----- #
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")

paypal_client: PaypalServersdkClient = PaypalServersdkClient(
    client_credentials_auth_credentials=ClientCredentialsAuthCredentials(
        o_auth_client_id=PAYPAL_CLIENT_ID,
        o_auth_client_secret=PAYPAL_CLIENT_SECRET,
    )
)

orders_controller: OrdersController = paypal_client.orders


@csrf_exempt 
def create_paypal_order(request):
    if request.method == 'POST':
        try:
            order_number = request.session.get('order_number')
            if not order_number:
                return JsonResponse({"error": "Order number not found in session."}, status=400)
            
            order = get_object_or_404(Order, user=request.user, is_ordered=False, order_number=order_number)
            
            grand_total_value = f'{order.order_total:.2f}' 
            
            purchase_unit = PurchaseUnitRequest(
                amount=AmountWithBreakdown(
                    currency_code="USD",
                    value=grand_total_value,
                ),
                custom_id=order.order_number,
                soft_descriptor="TU_TIENDA_NAME",
            )
            
            order_request_body = OrderRequest(
                intent=CheckoutPaymentIntent.CAPTURE,
                purchase_units=[purchase_unit],
                application_context={
                     "shipping_preference": "NO_SHIPPING", 
                     "user_action": PaypalExperienceUserAction.PAY_NOW,
                }
            )

            paypal_order = orders_controller.create_order({"body": order_request_body})

            return JsonResponse(json.loads(ApiHelper.json_serialize(paypal_order.body)), status=201)

        except ErrorException as e:
            return JsonResponse({"error": "PayPal API Error", "details": str(e.message)}, status=e.status_code)
        except Exception as e:
            return JsonResponse({"error": "Server Error", "details": str(e)}, status=500)
    
    return HttpResponse(status=405)


@csrf_exempt
def capture_paypal_order(request, order_id):
    """
    Captura el pago de la orden de PayPal. Corresponde a /api/orders/<order_id>/capture
    """
    if request.method == 'POST':
        try:
            order = orders_controller.capture_order(
                {"id": order_id, "prefer": "return=representation"}
            )

            return JsonResponse(json.loads(ApiHelper.json_serialize(order.body)), status=200)

        except ErrorException as e:
            return JsonResponse({"error": "PayPal API Error", "details": str(e.message)}, status=e.status_code)
        except Exception as e:
            return JsonResponse({"error": "Server Error", "details": str(e)}, status=500)
    
    return HttpResponse(status=405)
    
# ----- END PAYPAL API ----- #