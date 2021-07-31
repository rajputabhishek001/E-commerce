from django.shortcuts import render,redirect
from django.views import View
from .models import *
from .forms import CustomerRegistrationForm, CustomerProfileForm
from  django.contrib import messages
from django.db.models import Q
from  django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import AuthenticationForm


# def home(request):
#  return render(request, 'app/home.html')

class ProductView(View):
    def get(self, request):
        totalitem = 0
        topwears = Product.objects.filter(category = 'TW')
        bottomwears = Product.objects.filter(category = 'BW')
        mobiles = Product.objects.filter(category = 'M')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/home.html', {'topwears':topwears,'bottomwears':bottomwears,'mobiles':mobiles,'totalitem':totalitem})



# def product_detail(request):
#  return render(request, 'app/productdetail.html')

class ProductDetailView(View):
    def get(self, request, pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        itemInCart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))

        if request.user.is_authenticated:
            itemInCart = Cart.objects.filter(Q(product=product.id) & Q(user = request.user)).exists()
        return render(request, 'app/productdetail.html',{'product':product,'itemInCart':itemInCart,'totalitem':totalitem})

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id = product_id)
    Cart(user= user, product=product).save()
    return redirect('/cart')

def show_cart(request):
    if request.user.is_authenticated:
        totalitem= 0
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount =0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))

        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount +=tempamount
                totalamount = amount + shipping_amount
            return render(request,'app/addtocart.html',{'carts':cart, 'totalamount':totalamount,'amount':amount,'totalitem':totalitem})

        else:
            return render(request, 'app/emptycart.html')

def buy_now(request):
 return render(request, 'app/buynow.html')

# def profile(request):
#  return render(request, 'app/profile.html')

# def change_password(request):
#  return render(request, 'app/changepassword.html')

def mobile(request, data = None):
 if data == None:
  mobiles = Product.objects.filter(category = 'M')
 elif data == 'Realme' or data == 'Samsung':
  mobiles = Product.objects.filter(category = 'M').filter(brand = data)
 elif data == 'below':
  mobiles = Product.objects.filter(category = 'M').filter(discounted_price__lt=10000)
 elif data == 'above':
  mobiles = Product.objects.filter(category = 'M').filter(discounted_price__gt=10000)

 return render(request, 'app/mobile.html', {'mobiles':mobiles})


def laptop(request, data = None):
    if data == None:
        laptops = Product.objects.filter(category = 'L')
    elif data == 'Dell' or data == 'Macbook':
         laptops = Product.objects.filter(category = 'L').filter(brand = data)
    elif data == 'below':
         laptops = Product.objects.filter(category = 'L').filter(discounted_price__lt=50000)
    elif data == 'above':
        laptops = Product.objects.filter(category = 'L').filter(discounted_price__gt=50000)
    return  render(request, 'app/laptop.html', {'laptops':laptops})


# def login(request):
#  return render(request, 'app/login.html')

# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')

class CustomerRegistrationView(View):
 def get(self, request):
  form = CustomerRegistrationForm()
  return render(request, 'app/customerregistration.html', {'form':form})
 def  post(self, request):
  form = CustomerRegistrationForm(request.POST)
  if form.is_valid():
   messages.success(request, 'congratulation!! Registerted Successfully')
   form.save()
  return render(request, 'app/customerregistration.html', {'form':form})


def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_item = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount +=tempamount
        totalamount = amount +shipping_amount
    return render(request, 'app/checkout.html',{'add':add, 'totalamount':totalamount,'cart_items':cart_item})


def search(request):
    qur = request.GET.get('search').lower()
    products = [item for item in Product.objects.all() if qur in item.title.lower() or qur in item.brand.lower() or qur in item.category.lower() ]
    # title_name = Product.objects.filter(title__contains = qur)
    # topwears = Product.objects.filter(title__contains = qur)
    # bottomwears = Product.objects.filter(title__contains = qur)
    # mobiles = Product.objects.filter(title__contains = qur)
    # laptops = Product.objects.filter(title__contains = qur)
    return render(request,'app/search.html', {'products':products})

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html',{'form':form, 'active':'btn-primary'})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user= user, name=name, locality=locality, city = city, state = state, zipcode=zipcode)
            reg.save()
            messages.success(request,"Congratulation your Profile is successfully Updated !")
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})

def address(request):
    add = Customer.objects.filter(user= request.user)
    return render(request, 'app/address.html',{'add':add,'active':'btn-primary'})


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product = prod_id) & Q(user= request.user))
        c.quantity += 1
        c.save()

        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount +=tempamount


        data = {
         'quantity':c.quantity,
         'amount':amount,
         'totalamount':amount + shipping_amount
            }
        return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product = prod_id) & Q(user= request.user))
        c.quantity -= 1
        c.save()

        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount -= tempamount


        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.filter(Q(product = prod_id) & Q(user= request.user))
        c.delete()

        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount +=tempamount


        data = {
            'amount':amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)
@login_required
def payment_done(request):
    user= request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id = custid)
    cart = Cart.objects.filter(user= user)
    for c in cart:
        OrderPlaced(user= user, customer= customer, product= c.product, quantity= c.quantity).save()
        c.delete()
    return redirect("orders")

@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user= request.user)
    return render(request, 'app/orders.html', {'orderplaced':op})

