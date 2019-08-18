from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import  slugify
from transliterate import translit
from django.urls import reverse
from decimal import Decimal
from django.conf import settings
from django import forms

class Category(models.Model):

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('category_detail',kwargs={'category_slug': self.slug})

def pre_save_category_slug(sender, instance, *args , **kwargs):
    if not instance.slug:
        slug = slugify(translit(str(instance.name), reversed=True))
        instance.slug = slug

pre_save.connect(pre_save_category_slug, sender = Category)

class ProductManager(models.Manager):

    def all(self, *args, **kwargs):
        return super(ProductManager, self).get_queryset().filter(available=True)

def image_folder(instance, filename):
    filename = instance.slug + '.' + filename.split('.')[1]
    return "{0}/{1}".format(instance.slug, filename)

class MainLogo(models.Model):
    title = models.CharField(max_length=100)
    span = models.CharField(max_length=100)
    image = models.ImageField()
    slug = models.SlugField()
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail',kwargs={'product_slug': self.slug})

class Product(models.Model):

    category = models.ForeignKey('Category' , on_delete= models.DO_NOTHING )
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to=image_folder)
    available = models.BooleanField(default=True)
    objects= ProductManager()
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail',kwargs={'product_slug': self.slug})

class CartItem(models.Model):

    product = models.ForeignKey('Product' , on_delete= models.DO_NOTHING)
    qty = models.PositiveIntegerField(default=1)
    item_total = models.DecimalField(max_digits=9, decimal_places=2 ,default=0.00)

class Cart(models.Model):

    item = models.ManyToManyField(CartItem, blank=True)
    cart_total = models.DecimalField(max_digits=9, decimal_places=2 , default=0.00)

    def add_to_cart (self, product_slug) :
        cart = self
        product = Product.objects.get(slug=product_slug)
        new_item, _ = CartItem.objects.get_or_create(product=product, item_total=product.price)
        if new_item not in cart.item.all():
            cart.item.add(new_item)
            cart.save()

    def remove_from_cart(self, product_slug):
        cart = self
        product = Product.objects.get(slug=product_slug)
        for cart_item in cart.item.all():
            if cart_item.product == product:
                cart.item.remove(cart_item)
                cart.save()

    def change_qty(self, qty,cart_item):
        cart = self
        cart_item.qty = int(qty)
        cart_item.item_total = int(qty) * Decimal(cart_item.product.price)
        cart_item.save()
        new_cart_total = 0.00
        for item in cart.item.all():
            new_cart_total += float(item.item_total)
        cart.cart_total = new_cart_total
        cart.save()

    def __str__ (self):
        return  str(self.id)


ORDER_STATUS_CHOICES =(
    ('Принят','Принят'),
    ('Выполняется','Виполняется'),
    ('Оплачен','Оплачен')
)

class Order(models.Model):
    user = models.CharField(max_length=250, blank=True)
    items = models.ForeignKey('Cart', on_delete=models.DO_NOTHING)
    firstname = models.CharField(max_length=40)
    lastname = models.CharField(max_length=40)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField()
    total = models.DecimalField(max_digits=9, decimal_places=2,default=0)

    def __srt__(self):
        return "Заказ номер {0}".format(str(self.id))


class Phone(models.Model):

    user = models.CharField(max_length=250 , blank=False)
    phone = models.CharField(max_length=20)

    def __srt__(self):
        return  str(self.id)