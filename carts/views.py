from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(
            product=product, user=current_user
        ).exists()

        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            ids = []

            for item in cart_items:
                ex_var_list.append(list(item.variations.all()))
                ids.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item = CartItem.objects.get(id=ids[index])
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(
                    product=product, quantity=1, user=current_user
                )
                item.variations.add(*product_variation)
        else:
            item = CartItem.objects.create(
                product=product, quantity=1, user=current_user
            )
            item.variations.add(*product_variation)

    else:
        # NOT authenticated user
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except:
                    pass

        cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))

        is_cart_item_exists = CartItem.objects.filter(
            product=product, cart=cart
        ).exists()

        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, cart=cart)
            ex_var_list = []
            ids = []

            for item in cart_items:
                ex_var_list.append(list(item.variations.all()))
                ids.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item = CartItem.objects.get(id=ids[index])
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(
                    product=product, quantity=1, cart=cart
                )
                item.variations.add(*product_variation)
        else:
            item = CartItem.objects.create(
                product=product, quantity=1, cart=cart
            )
            item.variations.add(*product_variation)

    return redirect('cart')


def add_cart_item(request, cart_item_id):
    if request.user.is_authenticated:
        item = CartItem.objects.filter(id=cart_item_id, user=request.user).first()
    else:
        cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
        item = CartItem.objects.filter(id=cart_item_id, cart=cart).first()

    if item:
        item.quantity += 1
        item.save()

    return redirect("cart")


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


def cart(request, total=0, quantity=0, cart_item=None):
    tax = 0
    grand_total = 0
    cart_items = []

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity

        tax = (2 * total) / 100
        grand_total = total + tax

    except ObjectDoesNotExist:
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
def checkout(request):
    total = 0
    quantity = 0
    tax = 0
    grand_total = 0
    cart_items = []

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)


        for item in cart_items:
            total += item.product.price * item.quantity
            quantity += item.quantity

        tax = (2 * total) / 100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass  # variables already set to 0

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/checkout.html', context)