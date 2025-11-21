from django.shortcuts import render, get_object_or_404, redirect
from category.models import Category
from .models import Product
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q

# Create your views here.
def store(request, category_slug=None):

    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True).order_by('-created_date')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('-created_date')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    
    context = {
        'products': paged_products,
        'product_count': product_count
    }
    
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        product = Product.objects.get(slug=product_slug, category__slug=category_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()
    except Exception as e:
        raise e
    
    context = {
        'product': product,
        'in_cart':in_cart
    }
    
    return render(request, 'store/product_detail.html', context)

def search(request):
    keyword = request.GET.get('keyword', '')

    if not keyword:
        return redirect('store')
    else:
        products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)).order_by('-created_date')
        product_count = products.count()
    
    context = {
        'products': products,
        'product_count': product_count,
    }
    
    return render(request, 'store/store.html', context)
            