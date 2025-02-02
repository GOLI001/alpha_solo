from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from carts.models import Cart, CartItem
from coupons.models import Coupons
from orders.models import Delivery_address
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from orders.forms import addressform
from django.contrib import messages

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart :
        cart = request.session.create()
    return cart



def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    # If the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass


        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    # If the user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass


        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing_variations -> database
            # current variation -> product_variation
            # item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            print(ex_var_list)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')




def remove_cart(request, product_id, cart_item_id):

    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')



    


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')




def cart(request, total=0, quantity=0, cart_items=None):
    try:
        applyed_coupen = None
        coupon  = request.session['code']
        print(coupon)
        applyed_coupen = Coupons.objects.filter(code=coupon).first()
        print(applyed_coupen)

    except :
        pass    
    
    try:
        tax = 0
        grand_total = 0
        discount_price = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
  
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total)/100
        grand_total = total + tax 
        if applyed_coupen:
            discount_price = (grand_total - (applyed_coupen.discount * grand_total)/100   )

    except ObjectDoesNotExist:
        pass

    context ={
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
        'applyed_coupen' : applyed_coupen,
        'discount_price':discount_price,
    }

    return render (request, 'cart.html', context)



@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        applyed_coupen = None
        coupon  = request.session['code']
        print(coupon)
        applyed_coupen = Coupons.objects.filter(code='test10').first()
        print(applyed_coupen)

    except :
        pass   
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            address = Delivery_address.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total)/100
        grand_total = total + tax
        applyed_coupen = Coupons.objects.filter(code='test10').first()
        discount_price = (grand_total - (applyed_coupen.discount * grand_total)/100   )
  

    except ObjectDoesNotExist:
        pass

    context ={
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
        'address': address,
        'applyed_coupen':applyed_coupen,
        'discount_price':discount_price,
    }

    return render (request, 'checkout.html', context)





@login_required(login_url='login')
def save_address(request):
    if request.method == 'POST':
            form = addressform(request.POST)
            User = request.user
            if form.is_valid:
                if User.is_authenticated:
                    user             = User
                    firstname        = request.POST['firstname']
                    lastname         = request.POST['lastname']
                    addressfield_1   = request.POST['addressfield_1']
                    addressfield_2   = request.POST['addressfield_2']
                    city             = request.POST['city']
                    state            = request.POST['state']
                    country          = request.POST['country']
                    post_code        = request.POST['post_code']
                    phonenumber      = request.POST['phonenumber']
                    email            = request.POST['email']
                    
                    address = Delivery_address.objects.create(
                        user=user,
                        firstname=firstname,
                        lastname=lastname,
                        addressfield_1=addressfield_1,
                        addressfield_2=addressfield_2,
                        city=city,
                        state=state,
                        country=country,
                        post_code=post_code,
                        phonenumber=phonenumber,
                        email=email,
                        )
                    address.save()
                    messages.success(request, "Address is saved")
                    return redirect('checkout')
                else:
                    return redirect('login')
            else:
                messages.info(request, "please enter the reqired information")
                return redirect('checkout')
    return redirect('dashboard')
  
