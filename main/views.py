from django.shortcuts import render
from main.models import Category , Product, Cart, CartItem, Order, Phone ,MainLogo,Sticers
from django.http import HttpResponseRedirect, JsonResponse
from main.forms import OrderForm, RegistrationForm, LoginForm ,User , EditForm,EditPassForm , EditEmail
from django.contrib.auth import login, authenticate
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from shop.settings import EMAIL_HOST_USER
import operator
import datetime


def check_len():
    len_of = len(Product.objects.all())
    return len_of

def default_check(request):
    request.session['check_qty'] = 20
    request.session['check_category'] = ['all']
    request.session['check_sort'] = 'default'
    request.session['check_list'] = 1

def try_session (request):
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.item.count()
        if not (request.session['check_qty']
                and request.session['check_list']
                and request.session['check_sort']
                and request.session['check_category']):
            default_check(request)
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
        default_check(request)
        request.session['check_len'] = check_len()
        cart = Cart.objects.get(id = cart_id)
    return cart

def get_categories():
    return Category.objects.all()

def checked_products(request):
    products_f = []
    for category in request.session['check_category']:
        if category == 'all':
            products_f += Product.objects.all()
        else:
            products_category = Product.objects.filter(category=Category.objects.get(slug=category))
            products_f += products_category

    if request.session['check_sort'] == 'default':
        pass
    if request.session['check_sort'] == 'name':
        products_f.sort(key=operator.attrgetter('title'))
    if request.session['check_sort'] == 'price':
        products_f.sort(key=operator.attrgetter('price'))

    products = [[]]

    i = j = 0
    for product in products_f:
        i += 1
        products[j].append(product)
        if i == request.session['check_qty']:
            products.append([])
            i=0
            j+=1
    if products[-1] == [] :
        products.pop(-1)
    request.session['check_len'] = len(products)
    return products

def checked_base_view(request):
    check_sort = request.GET.get('check_sort')
    check_list = int(request.GET.get('check_list'))
    check_category = request.GET.getlist('check_category[]')
    if len(check_category) == 0:
        check_category = ["all"]

    request.session['check_category'] = check_category
    request.session['check_sort'] = check_sort
    request.session['check_list'] = check_list

    request.session.save()
    return  JsonResponse({})

def base_view(request):
    cart = try_session(request)
    products = checked_products(request)
    main = MainLogo.objects.all()
    c = count(cart)
    list_qty = [i+1 for i in range(len(products))]
    if(len(products) < request.session['check_list']):
        request.session['check_list'] = 1
    if len(products) != 0:
        products = products[request.session['check_list'] - 1]
    context ={
        'list_qty': list_qty,
        'c': c,
        'main': main,
        'categories': get_categories(),
        'products': products,
        'cart': cart,

    }
    return render(request,'wrapper.html', context)




def product_view(request, product_slug):
    cart = try_session(request)
    product =Product.objects.get(slug=product_slug)
    products = Product.objects.all()
    c = count(cart)
    context = {
        'c': c,
        'product' : product,
        'categories': get_categories(),
        'products': products,
        'cart' : cart
    }
    return render(request,'product.html',context)

def category_view(request, category_slug):
    cart = try_session(request)
    category =Category.objects.get(slug=category_slug)
    products_of_category = Product.objects.all(category=category)
    c = count(cart)
    context = {
        'c': c,
        'category' : category,
        'categories':get_categories(),
        'products_of_category' : products_of_category,
        'cart' :cart
    }
    return render(request,'category.html',context)

def cart_view(request):
    cart = try_session(request)
    c = count(cart)
    context = {
        'c': c,
        'cart' : cart,
        'categories': get_categories(),
    }
    return render(request, 'cart.html', context)

def add_to_cart_view(request):
    cart = try_session(request)
    product_slug = request.GET.get('product_slug')
    product = Product.objects.get(slug=product_slug)
    items = cart.item.all()
    try:
            item = items.get(product=product)
            item_qty = item.qty
            qty = request.GET.get('product_qty')
            qty = int(item_qty) + int(qty)
            cart.change_qty(qty, item)
    except:
        cart.add_to_cart(product.slug)

    new_cart_total = 0.00
    for item in cart.item.all():
        new_cart_total += float(item.item_total)
    cart.cart_total = new_cart_total
    cart.save()
    total = count(cart)
    return JsonResponse({'cart_total':total,
                         'cart_total_price': new_cart_total,
                         })

def get_count_view(request):
    cart = try_session(request)
    total = count(cart)
    return JsonResponse({'cart_total': total})

def count(cart) :
    total = 0
    for item_on_cart in cart.item.all():
        if int(item_on_cart.qty) :
            total += item_on_cart.qty
    return total


def remove_from_cart_view(request):
    cart = try_session(request)
    product_slug = request.GET.get('product_slug')
    cart.remove_from_cart(product_slug)
    new_cart_total = 0.00
    for item in cart.item.all():
        new_cart_total += float(item.item_total)
    cart.cart_total = new_cart_total
    cart.save()
    total = count(cart)
    return JsonResponse({'cart_total': total,
                         'cart_total_price': new_cart_total
                         })

def change_item_qty (request):
    cart = try_session(request)
    qty = request.GET.get('qty')
    item_id = request.GET.get('item_id')
    cart_item = CartItem.objects.get(id=int(item_id))
    cart.change_qty(qty, cart_item)
    total = count(cart)
    return JsonResponse({'cart_total':total ,
                         'item_total': cart_item.item_total,
                         'cart_total_price':cart.cart_total
                         })

def checkout_view(request):
    cart = try_session(request)
    if count(cart) == 0:
        return HttpResponseRedirect(reverse('cart'))
    else:
        form = OrderForm(request.POST or None)
        try:
            phone = Phone.objects.get(user = request.user)
        except:
            phone = ''

        sticks_img = [j for j in Sticers.objects.all()]
        c = count(cart)
        context = {
            'c': c,
            'phone' : phone,
            'form': form,
            'cart' :cart,
            'categories' :get_categories(),
            'user' : request.user,
            'sticks_img' : sticks_img
        }
        return render(request, 'checkout.html', context)


def send_order(request, order):

    if request.user.is_authenticated:
        email = request.user.email
    else:
        email = 'Пользователь не зарегестрирован'

    header = 'Заказ №' + str(order.id) +'. От:' + str(order.date)[0:16]
    data = "Toвары заказа :"
    for item in order.items.item.all() :
        data += "\n\t"
        data += item.product.title
        data += " | Количество: " + str(item.qty)
        data += " | Цена/шт : ₴ " + str(item.product.price)
        data += " | Итого : ₴ " + str(item.item_total)
    data += "\n\n\tИтого : ₴" + str(order.items.cart_total)
    data += "\n\nИмя : " + order.firstname +" "+order.lastname
    data += "\nАдрес : " + order.address
    data += "\nНаліпка : " + str(order.sticker)
    data += "\nДата : " + str(order.datep)
    data += "\nСпосіб оплати : " + str(order.payment)
    data += "\nНомер : " + str(order.phone)
    data += "\nEmail : " +  email
    data += "\nКоментарий : " + order.comments

    send_mail(header, data, EMAIL_HOST_USER,
              [EMAIL_HOST_USER], fail_silently=False)

def make_order_view (request):
    cart = try_session(request)
    form = OrderForm(request.POST or None)

    if form.is_valid():
        name = form.cleaned_data['name']
        last_name =form.cleaned_data['last_name']
        phone = form.cleaned_data['phone']
        address = form.cleaned_data['address']
        comments = form.cleaned_data['comments']
        sticker_c = form.cleaned_data['sticker']
        payment_c = form.cleaned_data['payment']
        datep_c = form.cleaned_data['datep']

        if request.user.is_authenticated :
            user_name = request.user.username

        else:
            user_name = ''

        new_order = Order.objects.create(
            user=user_name,
            items=cart,
            total=cart.cart_total,
            firstname=name,
            lastname=last_name,
            phone=phone,
            address=address,
            date= timezone.now() ,
            comments=comments,
            sticker=sticker_c ,
            payment=payment_c ,
            datep=datep_c
            )
        new_order.save()
        send_order(request, new_order)
        del request.session['cart_id']
        del request.session['total']
        c = count(cart)
        context = {
            'c': c,
            'new_order' : new_order,
            'categories':get_categories(),
            'products' : Product.objects.all()
        }
        return render(request, 'thank_you.html', context)

def account_edit_view(request):
    cart= try_session(request)
    edit_form = EditForm(request.POST or None)
    edit_pass_form = EditPassForm(request.POST or None)
    edit_email = EditEmail(request.POST or None)
    user = User.objects.get(username=request.user)
    phone = Phone.objects.get(user=request.user)
    form_type = request.POST.get('form_type')

    if form_type=='EDIT' and edit_form.is_valid():
        user.first_name = edit_form.cleaned_data['first_name']
        user.last_name = edit_form.cleaned_data['last_name']
        phone.phone = edit_form.cleaned_data['phone']
        phone.save()
        user.save()
        return HttpResponseRedirect(reverse('account_edit'))
    c = count(cart)
    context = {
        'c': c,
        # 'edit_email' :edit_email,
        'edit_form': edit_form,
        # 'edit_pass_form': edit_pass_form,
        'user': user,
        'phone': phone.phone,
        'categories': get_categories(),
    }
    if( request.user.is_authenticated ):
        return render(request, 'account_edit.html', context)
    else :
        return render(request, 'error.html', context)

def account_view(request):
    edit_form = EditForm(request.POST or None)
    cart = try_session(request)
    order = reversed(Order.objects.filter(user=request.user))


    user = User.objects.get(username= request.user)
    try:
        phone = Phone.objects.get(user=request.user)
    except:
        phone = Phone(user = user.username , phone='')

    c = count(cart)
    context = {
        'c': c,
        'edit_form' : edit_form,
        'cart': cart,
        'user': user,
        'phone': phone.phone,
        'categories': get_categories(),
        'order': order
    }
    if( request.user.is_authenticated ):
        return render(request, 'user_account.html', context)
    else :
        return render(request, 'error.html', context)

def registration_view(request):
    if(request.user.is_authenticated):
        return HttpResponseRedirect(reverse('base'))
    else:
        cart = try_session(request)
        reg_form = RegistrationForm(request.POST or None)
        if reg_form.is_valid():
            new_user = reg_form.save(commit=False)
            username = reg_form.cleaned_data['username']
            password = reg_form.cleaned_data['password']
            new_user.username = username
            new_user.set_password(password)
            new_user.first_name = reg_form.cleaned_data['first_name']
            new_user.last_name = reg_form.cleaned_data['last_name']
            phone = Phone(user= username, phone =reg_form.cleaned_data['phone'] )
            new_user.email = reg_form.cleaned_data['email']
            new_user.save()
            phone.save()
            login_user = authenticate(username=username, password=password)
            if login_user:
                login(request, login_user)
                return HttpResponseRedirect(reverse('base'))
        c = count(cart)
        context = {
            'c': c,
            'cart': cart,
            'categories': get_categories(),
            'form' : reg_form,
            'products': Product.objects.all()
        }
        return render(request,'registration.html',context)

def login_view(request):
    if (request.user.is_authenticated):
        return HttpResponseRedirect(reverse('base'))
    else:
        cart = try_session(request)
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            login_user = authenticate(username=username, password=password)
            if login_user:
                login(request,login_user)
                return HttpResponseRedirect(reverse('base'))
        c = count(cart)
        context = {
            'c': c,
            'cart': cart,
            'categories': get_categories(),
            'form' : form,
            'products': Product.objects.all()
        }
        return render(request, 'login.html', context)

def again_view(request,  cart_id):
    order = Order.objects.get(id=cart_id)
    cart = order.items
    request.session['cart_id'] = cart.id
    print("\nookk\n")
    return HttpResponseRedirect(reverse('checkout'))


def delivery_view(request):
    cart = try_session(request)
    c = count(cart)
    context = {
        'c': c,
        'cart': cart,
    }
    return render(request, 'delivery_terms.html', context)