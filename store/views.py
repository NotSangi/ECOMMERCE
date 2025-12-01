from django.shortcuts import render, get_object_or_404, redirect
from category.models import Category
from .models import Product, ReviewRating, ProductGallery
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct

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
    
    if request.user.is_authenticated:
        order_product = OrderProduct.objects.filter(user=request.user, product_id=product.id).exists()
    else:
        order_product = None
        
    reviews = ReviewRating.objects.filter(product__id=product.id, status=True)
    
    product_gallery = ProductGallery.objects.filter(product=product)
    
    context = {
        'product': product,
        'in_cart':in_cart,
        'order_product': order_product,
        'reviews': reviews,
        'product_gallery': product_gallery,
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

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thanks, your comment has been successfully updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                product = Product.objects.get(id=product_id)
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product = product
                data.user = request.user
                data.save()
                messages.success(request, 'Thanks, your comment has been successfully submitted')
                return redirect(url)