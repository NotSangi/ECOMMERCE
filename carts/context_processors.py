from .models import CartItem, Cart
from .views import _cart_id

def counter(request):
    cart_count = 0
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.all().filter(cart=cart)
        
        for item in cart_items:
            cart_count += item.quantity
            
    except Cart.DoesNotExist:
        cart_count = 0
        
    return dict(cart_count=cart_count)