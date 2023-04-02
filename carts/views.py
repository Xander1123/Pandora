from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import random
import string

def _cart_id(request):
    cart_id = request.session.get('cart_id')

    if cart_id is None:
        cart_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        request.session['cart_id'] = cart_id

    return cart_id

def add_cart(request, product_id):
    current_user=request.user
    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value=value)
                    product_variation.append(variation)
                except:
                    pass 

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = [] 
            id_list = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id_list.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id_list[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    user=current_user,

                )
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    for item in product_variation:
                        cart_item.variations.add(item)

                cart_item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,

            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item)
            cart_item.save()

        return redirect('cart')

    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value=value)
                    product_variation.append(variation)
                except:
                    pass

        try:
            cart=Cart.objects.get(card_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart=None

        if cart is None:
            cart=Cart.objects.create(card_id=_cart_id(request))
            cart.save()


        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            ex_var_list = [] 
            id_list = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id_list.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id_list[index]
                item = CartItem.objects.get(product=product, id_list=item_id)
                item.quantity += 1
                item.save()

            else:
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    cart=cart,

                )
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    for item in product_variation:
                        cart_item.variations.add(item)

                cart_item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,

            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item)
            cart_item.save()

        return redirect('cart')

def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user)
        else:
            cart = Cart.objects.get(card_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user)
    else:
        cart = Cart.objects.get(card_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
  
    return redirect('cart')









def cart(request):
    total = 0
    quantity = 0
    cart_items = []
    try:  
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True) 
        else:
            cart = Cart.objects.get(card_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    if cart_items is None:
        cart_items = []
    tax = 0
    grand_total = 0
    try:
        cart = Cart.objects.get(card_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax=(2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }


    return render(request,'store/checkout.html',context)
