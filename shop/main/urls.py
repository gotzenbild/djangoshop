from django.urls import path
from django.contrib.auth.views import LogoutView

from main.views import (base_view,
                        category_view,
                        product_view,
                        cart_view,
                        add_to_cart_view,
                        remove_from_cart_view,
                        change_item_qty,
                        checkout_view,
                        make_order_view,
                        account_view,
                        registration_view,
                        login_view,
                        get_count_view,
                        checked_base_view,
                        account_edit_view,
                        )

urlpatterns= [
    path('product/<product_slug>/',product_view, name='product_detail'),
    path('add_to_cart/', add_to_cart_view, name='add_to_cart'),
    path('change_item_qty/',change_item_qty , name='change_item_qty'),
    path('remove_from_cart/',remove_from_cart_view, name='remove_from_cart'),
    path('category/(<category_slug>/',category_view, name='category_detail'),
    path('checkout/',checkout_view, name='checkout'),
    path('thank_you', make_order_view ,name='thank_you'),
    path('cart/', cart_view, name='cart'),
    path('user_account/', account_view, name= 'user_account'),
    path('registration/',registration_view, name= 'registration'),
    path('login/',login_view, name='login'),
    path('logout/',LogoutView.as_view(next_page='base'),name='logout'),
    path('', base_view, name='base'),
    path('checked_base', checked_base_view, name='checked_base'),
    path('get_count',get_count_view,name='get_count'),
    path('account_edit',account_edit_view,name='account_edit'),
]