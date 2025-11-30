from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.db import transaction
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
import requests
from orders.models import Order
from django.core.paginator import Paginator

# EMAIL IMPORTS
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage

#ASSING CART TO USER 
from carts.views import _cart_id
from carts.models import Cart, CartItem

# ----- START AUTHENTICATION ----- #
def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
                )
            
            user.phone_number = phone_number
            user.save()
            
            current_site = get_current_site(request)
            mail_subject = 'Activate your account in NotSangi Page'
            body = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            to_email = email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()
            
            messages.success(request, 'Successfully Registered User')
            
            return redirect('/accounts/login/?command=verification&email='+email)
    context = {
        'form':form
    }
    
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # Add anonymous cart to user's cart
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.DoesNotExist:
                cart = None

            if cart:
                with transaction.atomic():
                    # Bring in anonymous items and user items
                    anon_items = CartItem.objects.filter(cart=cart)
                    user_items = CartItem.objects.filter(user=user)

                    # We built a map for quick searches in the user's shopping cart
                    # key = (product_id, frozenset(variation_ids))
                    user_map = {}
                    for ui in user_items:
                        var_ids = frozenset(ui.variations.values_list('id', flat=True))
                        user_map[(ui.product_id, var_ids)] = ui

                    # We go through each anonymous item and merge/transfer it
                    for a in anon_items:
                        a_var_ids = frozenset(a.variations.values_list('id', flat=True))
                        key = (a.product_id, a_var_ids)

                        if key in user_map:
                            # An identical item already exists in the user's cart -> add quantities
                            u_item = user_map[key]
                            u_item.quantity = u_item.quantity + a.quantity
                            u_item.save()
                            # We deleted the anonymous item because it has already been merged
                            a.delete()
                        else:
                            # Does not exist -> assign the anonymous item to the user (transfer)
                            a.user = user
                            a.save()
                            # Add to map to avoid future duplications in the same loop
                            user_map[key] = a

            auth.login(request, user)
            messages.success(request, 'Has iniciado sesión correctamente.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&') if x)
                if 'next' in params:
                    return redirect(params['next'])
            except Exception:
                pass

            return redirect('dashboard')

        else:
            messages.error(request, 'Incorrect Credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have logged out')
    return redirect('login')

# ----- END AUTHENTICATION ----- #

# ----- ACTIVATE ACCOUNT VIA EMAIL ----- #
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations, your account is active')
        return redirect('login')
    else:
        messages.error(request, 'Invalid Activation')
        return redirect('register')
    
# --------------------------------------- #

# ----- USER DASHBOARD ----- #
@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user, is_ordered=True)
    orders_count = orders.count()
    context = {
        'orders_count': orders_count,
    }
    
    return render(request, 'accounts/dashboard.html', context)

def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
        'orders': paged_orders,
    }
    
    return render(request, 'accounts/my_orders.html', context)

def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your infomation has been successfuly updated')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
    }
    
    return render(request, 'accounts/edit_profile.html', context)
     
# -------------------------- #

# ----- START RESET PASSWORD ----- #

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            current_site = get_current_site(request)
            mail_subject = 'Reset Password'
            body = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
                
            to_email = email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()
            
            messages.success(request, 'We have sent you an email to reset your password')
            return redirect('login')
        
        else:
            messages.error(request, "The account doesnt exists")
            return redirect('forgot_password')
            
    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'Invalid Link')
        return redirect('login')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password has been successfully reset')
            return redirect('login')
        else:
            messages.error(request, 'Confirmation Password doesnt match')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')
    
# ----- END RESET PASSWORD ----- #