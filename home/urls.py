from django.urls import path
from .views import HomeView
from . import views
from django.contrib.auth.views import LoginView

app_name='home'

urlpatterns = [
    path('', views.CategoryView.as_view(), name='category'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('category/',views.CategoryView.as_view(), name='category'),
    path('product/<int:product_id>/', views.menu_product_detail, name='menu_product_detail'),
    path('order/',views.OrderView.as_view(), name='order'),
    path('yourorder/',views.YourOrderView.as_view(), name='your_order'),
    path('cart/',views.CartView.as_view(), name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add_to_cart_detail/<int:product_id>/', views.add_to_cart_detail, name='add_to_cart_detail'),
    path('add_order/', views.add_order, name='add_order'),
    path('search/', views.search_food, name='search_food'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('profile/', views.update_profile, name='profile'),
    path('cancelled_order/<int:order_id>', views.cancelled_order, name='cancelled_order'),
    path('pay_order/<int:order_id>', views.pay_order, name='pay_order'),
    path('custom_logout/', views.custom_logout, name='custom_logout'),
    path('register/', views.register, name='register'),
    # URL cho quản lý đơn hàng
    path('admin/order/', views.AdminOrderList.as_view(), name='admin_order'),
    path('accept_order/<int:order_id>', views.accept_order, name='admin_accept_order'),
    path('reject_order/<int:order_id>', views.reject_order, name='admin_reject_order'),
    path('delete_order/<int:order_id>', views.delete_order, name='admin_delete_order'),
    # URL cho quản lý thể loại sản phẩm
    path('admin/categories/', views.AdminCategoryList.as_view(), name='admin_category_list'),
    path('delete_categories/', views.delete_categories, name='delete_categories'),
    path('admin/categories/<int:category_id>/', views.admin_category_detail, name='admin_category_detail'),
    path('admin/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/categories/<int:category_id>/update/', views.admin_category_update, name='admin_category_update'),
    # URL cho quản lý sản phẩm
    path('admin/products/', views.AdminProductList.as_view(), name='admin_product_list'),
    path('delete_products/', views.delete_products, name='delete_products'),
    path('delete_promotion/<int:promotion_id>', views.delete_promotion, name='delete_promotion'),
    path('update_promotion/', views.update_promotion, name='update_promotion'),
    path('admin/products/<int:product_id>/', views.admin_product_detail, name='admin_product_detail'),
    path('admin/products/create/', views.admin_product_create, name='admin_product_create'),
    path('admin/products/<int:product_id>/update/', views.admin_product_update, name='admin_product_update'),
    # URL cho quản lý sản phẩm
    path('admin/users/', views.AdminUserList.as_view(), name='admin_user_list'),
    path('delete_users/', views.delete_users, name='delete_users'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    #URL cho thống kê
    path('admin/statistics/', views.Statistics.as_view(), name='admin_statistics'),  
]
