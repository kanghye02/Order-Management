import datetime
from django.views import View, generic
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Category, Product, Cart, CartItem, CustomUser, Order, OrderDetail, Promotion
from .forms import CustomUserForm, RegistrationForm, CategoryForm, ProductForm, DeleteCategoryForm
from django.contrib.auth import logout
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponseRedirect
from .forms import CategoryForm, ProductForm, DeleteCategoryForm, DeleteProductForm, ADCustomUserForm, DeleteCustomUserForm, CustomUserDetailForm
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from datetime import date
from unidecode import unidecode
from django.db.models.functions import TruncDate, Trunc
from django.db.models import Sum, Count
from .models import Product, Review
from .forms import ReviewForm

class HomeView(View):
    def get(self, request):
        return render(request, 'homepage/index.html')

class CategoryView(generic.DetailView):
    model = Category

    def get(self, request):
        menu = Category.objects.all()
        user = request.user
        sold_filter = request.GET.get('filter_menu')
        products = Product.objects.all().order_by('name')
        if sold_filter == 'by_sold_number':
            products = products.order_by('-sold_number')
        elif sold_filter == 'by_promotion':
            products = [product for product in products if filter_promotion(product).exists()]
        if request.GET.get('food_name'):
            search_term = unidecode(request.GET.get('food_name')).lower()
            products = filter(lambda x: search_term in unidecode(_(x.name)).lower(), products)
            # return render(request, 'catalog/menu.html', {'menu': menu, 'products': productssearch})
        products_array = []
        total_quantity=0
        for product in products:
            cart_item_quantity=0
            if request.user.is_authenticated:
                try:
                    cart = Cart.objects.get(user=user)
                except Cart.DoesNotExist:
                    cart = None
                try:
                    cart_item = CartItem.objects.get(cart=cart, product=product)
                    cart_item_quantity=cart_item.quantity
                except CartItem.DoesNotExist:
                    cart_item = None
                    cart_item_quantity = 0
                total_quantity+=cart_item_quantity
            promotion = filter_promotion(product)
            if promotion.exists():
                products_array.append({'product': product, 'promotion': (100 - promotion[0].dis_percent) * product.base_price / 100, 'dis_percent': promotion[0].dis_percent,'cart_item_quantity': cart_item_quantity})
            else:
                products_array.append({'product': product, 'promotion': 0,'cart_item_quantity': cart_item_quantity})
        return render(request, 'catalog/menu.html', {'menu': menu, 'products': products, 'products_array': products_array, 'total_quantity': total_quantity})


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Changes saved'))
            return redirect('/profile')  # Sử dụng tên URL 'profile' để chuyển hướng

    else:
        form = CustomUserForm(instance=request.user)

    return render(request, 'registration/profile.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            cart = Cart.objects.create(user=user)
            cart.save()
            # Xử lý sau khi đăng ký thành công, ví dụ: chuyển hướng đến trang đăng nhập
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

class CartView(View):
    model=Cart

    def get(self, request):
        cartall = CartItem.objects.filter(cart_id=Cart.objects.get(user_id=request.user.id))
        products_array =[]
        total_price=0
        for cart in cartall:
            promotion = filter_promotion(cart.product)
            if(len(promotion)>0):
                promo_price = (100-promotion[0].dis_percent)*cart.product.base_price/100
                products_array.append({'product': cart.product,'cart': cart,'promotion': promo_price,'dis_percent': promotion[0].dis_percent})
                total_price += promo_price * cart.quantity
            else:
                products_array.append({'product': cart.product,'cart': cart,'promotion': 0})
                total_price += cart.product.base_price * cart.quantity
        return render(request, 'catalog/cart.html',{'cartall': products_array,'total_price': total_price})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)

    # Kiểm tra xem sản phẩm đã tồn tại trong giỏ hàng chưa, nếu có thì tăng số lượng
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('/category')

@login_required
def update_cart(request):

    if request.method == 'POST':
        action = request.POST.get('action')
        status = -1
        try:
            cart = CartItem.objects.get(id=request.POST.get("cart_item_id"))
            if (action=='increase'):
                cart.quantity += 1
            elif (action == 'decrease'):
                cart.quantity -= 1
            cart.save()
            status = 1
            if (action == 'delete') or (cart.quantity<1):
                cart.delete()
                status = 2
            cartall = CartItem.objects.filter(cart_id=Cart.objects.get(user_id=request.user.id))
            total_price=0
            for cartitem in cartall:
                promotion = filter_promotion(cartitem.product)
                if(len(promotion)>0):
                    promo_price = (100-promotion[0].dis_percent)*cartitem.product.base_price/100
                    total_price += promo_price * cartitem.quantity
                else:
                    total_price += cartitem.product.base_price * cartitem.quantity
            return JsonResponse({'status': status,'message': 'Cập nhật giỏ hàng thành công', 'quantity': cart.quantity,'total_price': total_price})
            
        except Cart.DoesNotExist:
            return JsonResponse({'status': -1,'message': 'Sản phẩm không tồn tại'}, status=404)
    else:
        return JsonResponse({'status': -1,'message': 'Yêu cầu không hợp lệ'}, status=400)

#views cho quản lý thể loại
@method_decorator(staff_member_required, name='dispatch')
class AdminCategoryList(ListView):
    model = Category
    template_name = 'admin/category_list.html'
    context_object_name = 'categories'
    paginate_by = 5

    ordering = ['name']

@staff_member_required 
def delete_categories(request):
    if request.method == 'POST':
        form = DeleteCategoryForm(request.POST)
        if form.is_valid():
            category_ids = form.cleaned_data['category_ids']
            Category.objects.filter(id__in=category_ids).delete()
            return redirect('home:admin_category_list')
    else:
        form = DeleteCategoryForm()

    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories, 'form': form})

@staff_member_required
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home:admin_category_list'))
    else:
        form = CategoryForm()
    return render(request, 'admin/category_form.html', {'form': form})

@staff_member_required
def admin_category_update(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('admin_category_list'))
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin/category_form.html', {'form': form})

@staff_member_required
def admin_category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    categories = Category.objects.all().order_by('name')
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _('Changes saved'))
            return redirect('home:admin_category_detail', category_id=category_id)
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin/category_detail.html', {'category': category, 'categories': categories, 'form': form})

#views cho quản lý sản phẩm
@method_decorator(staff_member_required, name='dispatch')
class AdminProductList(ListView):
    model = Product
    template_name = 'admin/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    def get_queryset(self):
        products = Product.objects.select_related('category').order_by('category__name', 'name')
        products_array =[]
        for product in products:
            promotion = filter_promotion(product)
            if(len(promotion)>0):
                products_array.append({'product':product,'promotion_id': promotion[0].id, 'promotion':(100-promotion[0].dis_percent)*product.base_price/100,'dis_percent': promotion[0].dis_percent})
            else:products_array.append({'product':product,'promotion':0})
        return products_array

@staff_member_required
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home:admin_product_list'))
    else:
        form = ProductForm()
    return render(request, 'admin/product_form.html', {'form': form})

@staff_member_required
def admin_product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('admin_product_list'))
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin/product_form.html', {'form': form})

@staff_member_required
def delete_products(request):
    if request.method == 'POST':
        form = DeleteProductForm(request.POST)
        if form.is_valid():
            product_ids = form.cleaned_data['product_ids']
            Product.objects.filter(id__in=product_ids).delete()
            return redirect('home:admin_product_list')
    else:
        form = DeleteProductForm()
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products, 'form': form})

@staff_member_required
def admin_product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    products = Product.objects.all().order_by('name')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, _('Changes saved'))
            return redirect('home:admin_product_detail', product_id=product_id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin/product_detail.html', {'product': product, 'products': products, 'form': form})

class OrderView(View):
    model = Order

    def get(self, request):
        try:
            cart = Cart.objects.get(user_id=request.user.id)
            cartall = CartItem.objects.filter(cart_id=cart)
        except Cart.DoesNotExist:
            # Xử lý khi không tìm thấy giỏ hàng
            cartall = []
        total_price = 0
        products_array =[]
        for cart in cartall:
            promotion = filter_promotion(cart.product)
            if(len(promotion)>0):
                promo_price = (100-promotion[0].dis_percent)*cart.product.base_price/100
                products_array.append({'product':cart.product,'quantity':cart.quantity,'promotion':promo_price,'dis_percent': promotion[0].dis_percent})
                total_price += promo_price * cart.quantity
            else:
                products_array.append({'product':cart.product,'quantity':cart.quantity,'promotion':0})
                total_price += cart.product.base_price * cart.quantity
            
        return render(request, 'catalog/order.html', {'cartall': products_array, 'total_price': total_price})
@transaction.atomic
def add_order(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    order = Order(cart=cart, user=user)
    order.save()
    cartall = CartItem.objects.filter(cart=Cart.objects.get(user=user))

    try:
        with transaction.atomic():
            for cartitem in cartall:
                promotion = filter_promotion(cartitem.product)
                if promotion.exists():
                    promo_price = (100 - promotion[0].dis_percent) * cartitem.product.base_price / 100
                    total_price = promo_price * cartitem.quantity
                else:
                    promo_price = cartitem.product.base_price
                    total_price = cartitem.product.base_price * cartitem.quantity
                order_detail = OrderDetail(
                    price=promo_price,
                    quantity=cartitem.quantity,
                    total_cost=total_price,
                    order=order,
                    product=cartitem.product
                )
                order_detail.save()
                order.order_cost += order_detail.total_cost
                cartitem.delete()
            order.status = 0
            order.save()
            return redirect('/yourorder/')
    except Exception as e:
        transaction.rollback()
        print(f"Transaction failed: {str(e)}")

def filter_promotion(product):
    today_format = datetime.datetime.now().isoformat()
    return Promotion.objects.filter(product=product, start_date__lt=today_format, end_date__gte=today_format)

def search_food(request):
    menu = Category.objects.all()
    products = Product.objects.all()
    return render(request, 'catalog/menu.html', {'menu': menu, 'products': products})

class YourOrderView(View):
    model = Order

    def get(self, request, status=None):
        if status is None:
            # Nếu không có trạng thái được chỉ định, mặc định là 'all'
            status = 'all'

        orders = Order.objects.order_by('-order_date')
        orderAllItem = []
        total_price=0

        for order in orders:
            orderall = OrderDetail.objects.filter(order=order)
            total_price = sum(item.price * item.quantity for item in orderall)
            tz = timezone.get_current_timezone()
            if order.order_date is not None and isinstance(order.order_date, datetime.datetime):
                formatted_date = timezone.make_aware(order.order_date, tz).strftime("%H:%M:%S %d/%m/%Y")
            else:
                formatted_date = "Invalid date"  # or any other appropriate handling for non-datetime values
            if status == 'all' or order.status == status:
                orderAllItem.append({'allItem': orderall, 'total_price': total_price, 'order': order, 'formatted_date': formatted_date})

        return render(request, 'catalog/yourorder.html', {'orderAllItem': orderAllItem, 'total_price': total_price, 'status': status})

@login_required
def cancelled_order(request, order_id):
    user = request.user
    order = get_object_or_404(Order, user=user, id=order_id, status__lt=2)
    if order.status<2 :
        order.status = 2
        order.save()
        return redirect('/yourorder/')
    else:
        return HttpResponse("Không thể hủy đơn hàng này vì đã được xử lý hoặc đã hoàn thành.")
    
#views cho quản lý người dùng
@method_decorator(staff_member_required, name='dispatch')
class AdminUserList(ListView):
    model = CustomUser
    template_name = 'admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 5


@staff_member_required
def admin_user_create(request):
    if request.method == 'POST':
        form = ADCustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home:admin_user_list'))
    else:
        form = ADCustomUserForm()
    return render(request, 'admin/user_form.html', {'form': form})

@staff_member_required
def delete_users(request):
    if request.method == 'POST':
        form = DeleteCustomUserForm(request.POST)
        if form.is_valid():
            user_ids = form.cleaned_data['user_ids']
            CustomUser.objects.filter(id__in=user_ids).delete()
            return redirect('home:admin_user_list')
    else:
        form = DeleteCustomUserForm()
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users, 'form': form})

@staff_member_required
def admin_user_detail(request, user_id):
    aduser = get_object_or_404(CustomUser, pk=user_id)
    users = CustomUser.objects.all()
    if request.method == 'POST':
        form = CustomUserDetailForm(request.POST, instance=aduser)
        if form.is_valid():
            aduser = form.save(commit=False)
            aduser.is_staff = form.cleaned_data['is_staff']
            aduser.save()
            messages.success(request, _('Changes saved'))
            return redirect('home:admin_user_detail', user_id=user_id)
    else:
        form = CustomUserDetailForm(instance=aduser)
    return render(request, 'admin/user_detail.html', {'aduser': aduser, 'users': users, 'form': form})

#views cho quản lý order
@method_decorator(staff_member_required, name='dispatch')
class AdminOrderList(View):
    model = Order

    def get(self, request, status=None):
        if status is None:
            # Nếu không có trạng thái được chỉ định, mặc định là 'all'
            status = 'all'

        orders = Order.objects.order_by('-order_date')
        orderAllItem = []
        total_price=0

        for order in orders:
            orderall = OrderDetail.objects.filter(order=order)
            total_price = sum(item.price * item.quantity for item in orderall)
            tz = timezone.get_current_timezone()
            if order.order_date is not None and isinstance(order.order_date, datetime.datetime):
                formatted_date = timezone.make_aware(order.order_date, tz).strftime("%H:%M:%S %d/%m/%Y")
            else:
                formatted_date = "Invalid date"  # or any other appropriate handling for non-datetime values
            if status == 'all' or order.status == status:
                orderAllItem.append({'allItem': orderall, 'total_price': total_price, 'order': order, 'formatted_date': formatted_date})

        return render(request, 'admin/order_list.html', {'orderAllItem': orderAllItem, 'total_price': total_price, 'status': status})

@staff_member_required
def accept_order(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        order.status = 1
        for order_detail in order.orderdetail_set.all():
            if order_detail.product.number_in_stock < order_detail.quantity:
                return redirect('home:admin_order')
        order_detail=OrderDetail.objects.filter(order=order)
        for sold_product in order_detail:
            sold_product.product.number_in_stock -= sold_product.quantity
            sold_product.product.save()
        order.save()
        order.save()
        return redirect('home:admin_order')
    except Order.DoesNotExist:
        return HttpResponse(_('Đơn đặt hàng không tồn tại'), status=404)

@staff_member_required
def reject_order(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        order.status = 3
        order.save()
        return redirect('home:admin_order')
    except Order.DoesNotExist:
        return HttpResponse(_('Đơn đặt hàng không tồn tại'), status=404)

@staff_member_required
def delete_order(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        if order.status in [2, 3, 4]:
            order.delete()
            return redirect('home:admin_order')
        else:
            return HttpResponse(_('Không thể xóa đơn đặt hàng với trạng thái này'), status=400)
    
    except Order.DoesNotExist:
        return HttpResponse(_('Đơn đặt hàng không tồn tại'), status=404)

# View dành cho thống kê
class Statistics(ListView):
    model = Order
    template_name = 'admin/statistics.html'
    paginate_by = 5
    
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        date_status=0
        today = date.today()

        if start_date and end_date:
            if(start_date>=end_date):
                date_status=0
            else:
                date_status=1
        # Kiểm tra xem start_date có giá trị không rỗng
        daily_order_totals = Order.objects.filter(status=4)
        if start_date:
            daily_order_totals = daily_order_totals.filter(order_date__gte=start_date)
        # Áp dụng điều kiện cho end_date
        if end_date:
            daily_order_totals = daily_order_totals.filter(order_date__lt=end_date)

        daily_order_totals = daily_order_totals.annotate(
            order_date_new=Trunc('order_date','day')
        ).values('order_date_new').annotate(
            total_price=Sum('order_cost'),
            count=Count('id')
        ).order_by('order_date_new')
        
        daily_summary = daily_order_totals.filter(order_date__gte=today)
        daily_summary = daily_summary.annotate(
            order_today_new=Trunc('order_date','day')
        ).values('order_today_new').annotate(
            total_price=Sum('order_cost'),
            count=Count('id')
        )

        return render(request, 'admin/statistics.html',{
            'daily_summary': daily_summary,
            'today': today,
            'orderAllItem': daily_order_totals,
            'start_date': start_date,
            'end_date': end_date, 
            'date_status': date_status})


@login_required
def pay_order(request, order_id):
    user = request.user
    order = get_object_or_404(Order, user=user, id=order_id, status__lt=2)
    if order.status<2 :
        order.status = 4
        order_detail=OrderDetail.objects.filter(order=order)
        for sold_product in order_detail:
            sold_product.product.sold_number += sold_product.quantity
            sold_product.product.save()
        order.save()
        return redirect('/yourorder/')


@staff_member_required
def update_promotion(request):
    if request.method == 'POST':
        promotion = request.POST
        print(promotion)
        new_promotion = Promotion(product_id=promotion["product_id"], dis_percent=promotion["dis_percent"], description=promotion["description"], start_date=promotion["start_promo"], end_date=promotion["end_promo"])
        new_promotion.save()
        return redirect('home:admin_product_list')

@staff_member_required
def delete_promotion(request, promotion_id):
    promotion = get_object_or_404(Promotion, id=promotion_id)
    promotion.delete()
    return redirect('home:admin_product_list')

def menu_product_detail(request, product_id):
    # Lấy sản phẩm dựa trên product_id hoặc trả về 404 nếu không tìm thấy
    product = get_object_or_404(Product, id=product_id)
    promotion = filter_promotion(product)
    user = request.user
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            cart = None
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item_quantity=cart_item.quantity
        except CartItem.DoesNotExist:
            cart_item = None
            cart_item_quantity = 0
    if promotion.exists():
        promo_price = (100 - promotion[0].dis_percent) * product.base_price / 100
        promotion_status=2
    else:
        promo_price = product.base_price
        promotion_status=0
    reviews = Review.objects.filter(product=product)
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
                return redirect('home:menu_product_detail', product_id=product_id)

        else:
            form = ReviewForm()

    else:
        form = None
        cart_item_quantity=0

    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'promo_price': promo_price,
        'promotion_status': promotion_status, 
        'cart_item_quantity' :cart_item_quantity,
        'product': product,
        'reviews': reviews,
        'review_form': form,})

@login_required
def add_to_cart_detail(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        print(request.POST.get("quantity"))

        # Kiểm tra xem sản phẩm đã tồn tại trong giỏ hàng chưa, nếu có thì tăng số lượng
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(request.POST.get("quantity"))
            cart_item.save()

    return redirect('home:menu_product_detail', product_id=product_id)