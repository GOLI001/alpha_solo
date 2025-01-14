from django.shortcuts import render, redirect
from carts.models import CartItem
from coupons.models import Coupons
from .forms import  addressform
from django.contrib.auth.decorators import login_required
from .models import Order, Payment, OrderProduct, Delivery_address
import datetime
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import razorpay
from carts.models import CartItem
from store.models import Product

# Create your views here.
@csrf_exempt
def place_order(request, total=0, quantity=0):
    try:
        applyed_coupen = None
        coupon  = request.session['code']
        print(coupon)
        applyed_coupen = Coupons.objects.filter(code=coupon).first()
        print(applyed_coupen)
    except :
        pass      

        
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = int(total + tax)*100
    applyed_coupen = Coupons.objects.filter(code='test10').first()
    discount_price = (grand_total - (applyed_coupen.discount * grand_total)/100   )
 

    if request.method == 'POST':
            print('dddddddddddd')
            id = request.POST.get('address')
            print(id)
            address = Delivery_address.objects.get(user=current_user,id=id)
            data = Order()
            data.user = current_user
            print("address",address)
            data.delivery_address = address
            data.order_note = request.POST.get('ordernote', False)
            data.order_total = grand_total/100
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')

            data.save()

            print(data.delivery_address)


            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            request.session['order_number'] = order_number
            data.order_number = order_number
            data.save()


            # create razorpay client
            client = razorpay.Client(auth=('rzp_test_7faFV5PWWZYXeb', 'PEmHIBuXxsbYfIU6XxgaiqXl'))

            # generate order
            DATA = {
                "amount": discount_price,
                "currency": "INR",
                "receipt": order_number,
                "payment_capture": 1
            }
            response_payment = client.order.create(data=DATA) 
            print(response_payment)
            payment_status = response_payment['status']
            print(payment_status)

            if payment_status == 'created':
                payment = Payment(
                    user=request.user,
                    order_id=order_number,
                    payment_method= 'razorpay',
                    amount_paid=grand_total/100,
                )
                payment.save()
                print(grand_total)
                response_payment['name'] = request.user
                context = {
                    'payment':   response_payment,
                    'grand_total':   grand_total,
                    }
                return render(request, 'payments.html', {'payment':response_payment, 'grand_total': discount_price})
            else:
                return redirect('checkout')
        


            


@csrf_exempt
def payment_status(request):
        payment_id = request.POST['razorpay_payment_id']
        order_number = request.session['order_number']
        print(payment_id)

        client = razorpay.Client(auth=('rzp_test_7faFV5PWWZYXeb', 'PEmHIBuXxsbYfIU6XxgaiqXl'))

        try:
            payment = Payment.objects.get(order_id = order_number)
            payment.payment_id = payment_id
            payment.paid       = True
            payment.save()
            print(payment,'..........................................')
            print(order_number)
            order = Order.objects.get(user=request.user,is_ordered=False,order_number=order_number)
            order.is_ordered = True
            order.status = 'Ordered'
            print(order.status)
            order.save()
            user = request.user
            cart_items = CartItem.objects.filter(user=user)
            print(cart_items)
            for cart_item in cart_items:
                pro_data = OrderProduct()
                pro_data.order = order
                pro_data.payment = payment
                pro_data.user = user
                pro_data.product = cart_item.product
                pro_data.quantity = cart_item.quantity
                pro_data.product_price = cart_item.product.price
                pro_data.ordered = True 
                pro_data.save()


                #taking product variation
                item = CartItem.objects.get(id=cart_item.id)
                product_variation = item.variations.all()
                pro_data = OrderProduct.objects.get(id=pro_data.id)
                pro_data.variations.set(product_variation)
                pro_data.save()
                

                # Reduce the quantity of the sold products
                product = Product.objects.get(id=cart_item.product_id)
                product.stock -= cart_item.quantity
                product.save()

                
            #Clear cart    
            CartItem.objects.filter(user=request.user).delete()
          
           
            return render(request,'payment_status.html',{'status':True})
        except:
            return render(request,'payment_status.html',{'status':False})







        