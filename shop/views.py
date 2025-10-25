from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Item, CartItem, Order, OrderItem


def is_manager(user):
    return user.groups.filter(name='manager').exists() or user.is_superuser

@login_required
@user_passes_test(is_manager)
def stata(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'stata.html', {'orders': orders})


def items_page(request):
    items = Item.objects.all()
    role = None
    if request.user.is_authenticated:
        if request.user.is_superuser:
            role = 'admin'
        elif request.user.groups.filter(name='manager').exists():
            role = 'manager'
        else:
            role = 'user'
    return render(request, 'items_page.html', {'items': items, 'role': role})


def cart_page(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    if request.method == "POST":
        action = request.POST.get("action")
        item_id = request.POST.get("item_id")
        item = get_object_or_404(Item, id=item_id)

        if action == "add":
            cart_item, created = CartItem.objects.get_or_create(user=user, item=item)
            if not created:
                cart_item.quantity += 1
            cart_item.save()
        elif action == "remove":
            cart_item = CartItem.objects.filter(user=user, item=item).first()
            if cart_item:
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
        return redirect("cart_page")

    return render(request, "cart_page.html", {"cart_items": cart_items})


def create_order(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    if not cart_items:
        return render(request, "order_error.html", {"message": "Your cart is empty."})

    order = Order.objects.create(user=user, status='new', total=0)
    total = 0

    for ci in cart_items:
        price = ci.item.price
        qty = ci.quantity
        OrderItem.objects.create(
            order=order,
            item=ci.item,
            quantity=qty,
            price=price
        )
        total += price * qty

    order.total = total
    order.save()

    cart_items.delete()

    return render(request, "order_success.html", {"order": order})