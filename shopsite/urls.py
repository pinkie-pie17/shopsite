"""
URL configuration for shopsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from shop import views

urlpatterns = [
    path('', views.home, name='home'),
    path('complete_order/<int:order_id>/', views.complete_order, name='complete_order'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('stata/', views.stata, name='stata'),
    path('items_page/', views.items_page, name='items_page'),
    path('cart_page/', views.cart_page, name='cart_page'),
    path('create_order/', views.create_order, name='create_order'),
    path('accounts/register/', views.register, name='register'),
    path('items/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    
]