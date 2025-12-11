from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Item, CartItem, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages


def is_manager(user):
    return user.groups.filter(name='manager').exists() or user.is_superuser


def is_manager_or_admin(user):
    return user.is_staff or user.is_superuser


def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_manager)
def stata(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'stata.html', {'orders': orders})


def home(request):
    active_orders = None
    if request.user.is_authenticated:
        active_orders = Order.objects.filter(user=request.user).exclude(status='completed')
    return render(request, 'home.html', {'active_orders': active_orders})


def items_page(request):
    role = None

    if request.user.is_authenticated:
        if request.user.is_superuser:
            role = 'admin'
        elif request.user.groups.filter(name='manager').exists():
            role = 'manager'
        else:
            role = 'user'

    if request.method == 'POST' and role in ('admin', 'manager'):
        item_id = request.POST.get('item_id')
        name = request.POST.get('name')
        price = request.POST.get('price')

        if not name or not price:
            messages.error(request, 'Name and price are required.')
        else:
            try:
                price = float(price)
            except ValueError:
                messages.error(request, 'Price must be a number.')
            else:
                if item_id:  
                    try:
                        item = Item.objects.get(id=item_id)
                    except Item.DoesNotExist:
                        messages.error(request, 'Item with this ID does not exist.')
                    else:
                        item.name = name
                        item.price = price
                        item.save()
                        messages.success(request, 'Item updated successfully.')
                else:         
                    Item.objects.create(name=name, price=price)
                    messages.success(request, 'Item added successfully.')

                return redirect('items_page')

    items = Item.objects.all()
    return render(request, 'items_page.html', {'items': items, 'role': role})


@login_required
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


@login_required
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
    

@login_required
@user_passes_test(is_manager_or_admin)
def complete_order(request, order_id):
    if request.method == "POST":
        order = Order.objects.get(id=order_id)
        order.status = "completed"
        order.save()
    return redirect('stata')

@login_required
@user_passes_test(is_admin)
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    messages.success(request, "item deleted successfully.")
    return redirect('items_page')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken.')
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, 'Account created successfully! You can now log in.')
        return redirect('login')

    return render(request, 'register.html')

