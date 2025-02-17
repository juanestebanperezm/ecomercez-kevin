from django.shortcuts import render
from .models import *
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
import json
import datetime
from .utils import cookieCart,cartData,guestOrder

import hashlib
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.conf import settings
from django.contrib.auth.decorators import login_required



def inicio(request):
    return render(request,'store/index.html')


def store(request):
    
    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']

    products=Product.objects.all()
    context={'products':products,'cartItems':cartItems}
    return render(request,'store/store.html',context)


def cart(request):

    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']
    

    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/cart.html',context)
    
def checkout(request):
    
    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']
    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/checkout.html', context)

def updateItem(request):
    # Information Of What User Has Done
    data = json.loads(request.body.decode('utf-8'))
    #json.loads(request.body)
    # Product To Buy ID
    productID = data['productId']
    # Action To Add To Cart Or Something Else You Do
    action = data['action']
    # Print To Make Sure It Workds
    print('Action:',action)
    # Print To Make Sure It Workds
    print('productID:', productID)
    customer = request.user.customer
    product = Product.objects.get(id=productID)
    #create the order
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    #add or delete
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    # Show The Data Above Is Chrome Console As Well
    return JsonResponse('item was added',safe=False)


def processOrder(request):
    transaction_id=datetime.datetime.now().timestamp()
    data=json.loads(request.body)
    if request.user.is_authenticated:
        customer=request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)





    else:
        customer,order = guestOrder(request,data)

    total=float(data('form')['total'])
    order.transaction_id=transaction_id

    if total == order.get_cart_total:
        order.complete=True
    order.save()

    
    if order.shipping == True:
        ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],

        )



    return JsonResponse('Payment submitted....',safe=False)

""" def processOrder(request):
    print('data',request.body)
    return JsonResponse('Payment submitted....',safe=False) """